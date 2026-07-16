"""Command-line research summarizer agent powered by Gemini and LangChain."""

import argparse
import json
import os
import re
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI


def create_llm() -> ChatGoogleGenerativeAI:
    """Create the Gemini chat model from environment configuration."""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing API key. Set GOOGLE_API_KEY or GEMINI_API_KEY before running."
        )

    return ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        google_api_key=api_key,
        temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.3")),
        max_output_tokens=int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "4096")),
    )


def call_llm(
    llm: ChatGoogleGenerativeAI,
    system_prompt: str,
    user_message: str,
) -> str:
    """Call the model and normalize string/list response content."""
    try:
        response = llm.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message),
            ]
        )

        content = response.content

        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):
            text = ""
            for block in content:
                if isinstance(block, str):
                    text += block
                elif isinstance(block, dict):
                    text += block.get("text", "")
                else:
                    text += str(block)

            return text.strip()

        return str(content).strip()

    except Exception as exc:
        print(f"\nGemini Error: {exc}")
        return ""


def parse_json(text: str) -> Any:
    """Parse JSON from model output, including fenced or extra-text responses."""
    if not text:
        raise ValueError("Empty response from model.")

    cleaned = text.strip().replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end != -1:
        try:
            return json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError:
            pass

    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        return json.loads(match.group())

    raise ValueError(f"Could not parse JSON response:\n{cleaned}")


class ResearchAgentSystem:
    """Four-agent research workflow with planner, researcher, synthesizer, evaluator."""

    def __init__(self, question: str, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        self.state = {
            "question": question,
            "sub_questions": [],
            "answers": [],
            "summary": "",
            "evaluation": {},
            "iteration": 1,
            "max_iterations": 2,
        }

    def log_state(self, message: str) -> None:
        print("\n[STATE]")
        print(message)

    def log_agent(self, agent: str) -> None:
        print(f"\n[{agent}]")

    def log_decision(self, message: str) -> None:
        print("\n[DECISION]")
        print(message)

    def planner_agent(self) -> None:
        self.log_agent("AGENT 1 - Planner")
        print("Generating research plan...")

        prompt = """
        You are a research planning agent.

        You must follow these rules exactly:

        1. Output ONLY valid JSON.
        2. Output MUST contain EXACTLY one key named "sub_questions".
        3. Generate EXACTLY 3 sub-questions.
        4. Do NOT include any other keys.
        5. Do NOT include explanations, markdown, or extra text.

        Output format:

        {
        "sub_questions": [
            "Question 1",
            "Question 2",
            "Question 3"
        ]
        }

        Each sub-question must:
        - be clear
        - be specific
        - be answerable with factual research
        - be ONE short sentence (maximum 15 words)
        - avoid unnecessary dates or details
        """

        result = call_llm(self.llm, prompt, f"Research Question: {self.state['question']}")
        data = parse_json(result)
        self.state["sub_questions"] = data["sub_questions"]

        self.log_decision(f"{len(self.state['sub_questions'])} sub-questions created.")
        print("\nSub Questions:")

        for index, question in enumerate(self.state["sub_questions"], start=1):
            print(f"{index}. {question}")

    def researcher_agent(self) -> None:
        self.log_agent("AGENT 2 - Researcher")
        print("Researching each sub-question...")

        prompt = """
        You are a research agent.

        Answer each sub-question with a factual paragraph.

        Return ONLY JSON:

        {
        "answers":[
            {
            "question":"...",
            "answer":"..."
            }
        ]
        }

        No markdown.
        """

        result = call_llm(
            self.llm,
            prompt,
            json.dumps({"sub_questions": self.state["sub_questions"]}),
        )

        data = parse_json(result)
        self.state["answers"] = data["answers"]
        self.log_state(f"Research completed for {len(self.state['answers'])} questions.")

        print("\nResearch Results:\n")
        for item in self.state["answers"]:
            print(f"Question: {item['question']}")
            print(f"Answer: {item['answer']}\n")

    def synthesizer_agent(self) -> None:
        self.log_agent("AGENT 3 - Synthesizer")
        print("Synthesizing research into a final summary...")

        prompt = """
        You are a synthesis agent.

        Create a coherent research summary using the research answers.

        You must follow these rules exactly:

        1. Output ONLY valid JSON.
        2. Output EXACTLY one key named "summary".
        3. Do NOT include markdown or explanations.
        4. Escape all newline characters as \\n.
        5. Do NOT use literal line breaks inside the JSON string.

        Output format:

        {
        "summary": "Paragraph 1.\\n\\nParagraph 2.\\n\\nParagraph 3."
        }
        """

        result = call_llm(
            self.llm,
            prompt,
            json.dumps(
                {
                    "question": self.state["question"],
                    "answers": self.state["answers"],
                }
            ),
        )

        data = parse_json(result)
        self.state["summary"] = data["summary"]
        self.log_state("Research summary generated.")

    def evaluator_agent(self) -> None:
        self.log_agent("AGENT 4 - Evaluator")
        print("Evaluating research summary...")

        prompt = """
        You are a critical evaluation agent.

        Evaluate the summary.

        Score:

        - coverage
        - accuracy
        - clarity
        - depth

        Each score is 1-10.

        Pass if overall score >= 7.

        Return ONLY JSON:

        {
            "scores":{
                "coverage":0,
                "accuracy":0,
                "clarity":0,
                "depth":0
            },
            "overall":0,
            "verdict":"pass",
            "verdict_reason":"",
            "gaps":[]
        }

        No markdown.
        """

        result = call_llm(
            self.llm,
            prompt,
            json.dumps(
                {
                    "question": self.state["question"],
                    "summary": self.state["summary"],
                }
            ),
        )

        self.state["evaluation"] = parse_json(result)
        evaluation = self.state["evaluation"]

        print("\nEvaluation Results")
        print("------------------")
        print(json.dumps(evaluation, indent=4))
        self.log_decision(f"Overall Score: {evaluation['overall']}")
        self.log_decision(f"Verdict: {evaluation['verdict'].upper()}")

    def refine_summary(self) -> None:
        self.log_agent("REFINEMENT")
        gaps = self.state["evaluation"].get("gaps", [])

        if not gaps:
            print("No refinement gaps returned.")
            return

        print("Evaluator identified missing information:")
        for gap in gaps:
            print(f"- {gap}")

        self.state["answers"].append(
            {
                "question": "Additional Information",
                "answer": "; ".join(gaps),
            }
        )

        self.log_state("Shared state updated with evaluator feedback.")

    def run(self) -> str:
        print("\n===================================")
        print("     Research Summarizer Agent")
        print("===================================")

        self.log_state("Question received.")
        print(f"\nResearch Question:\n{self.state['question']}")

        self.planner_agent()
        self.researcher_agent()

        while self.state["iteration"] <= self.state["max_iterations"]:
            print(f"\n========== Iteration {self.state['iteration']} ==========")

            self.synthesizer_agent()
            self.evaluator_agent()

            verdict = self.state["evaluation"]["verdict"].lower()

            if verdict == "pass":
                self.log_decision("Evaluation passed. Workflow complete.")
                break

            self.log_decision("Evaluation failed. Starting refinement...")
            self.refine_summary()
            self.state["iteration"] += 1

        print("\n===================================")
        print("         FINAL SUMMARY")
        print("===================================\n")
        print(self.state["summary"])
        return self.state["summary"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the research summarizer agent.")
    parser.add_argument("question", nargs="*", help="Research question to summarize.")
    args = parser.parse_args()

    question = " ".join(args.question).strip() or input("\nEnter research question: ")
    system = ResearchAgentSystem(question=question, llm=create_llm())
    system.run()


if __name__ == "__main__":
    main()
