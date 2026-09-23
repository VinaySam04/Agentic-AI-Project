def test_planner_agent_creates_subquestions():
    agent = ResearchAgentSystem("What is AI?")
    agent.planner_agent()
    assert len(agent.state["sub_questions"]) == 3
    assert all(isinstance(q, str) for q in agent.state["sub_questions"])

def test_researcher_agent_answers_questions():
    agent = ResearchAgentSystem("What is AI?")
    agent.state["sub_questions"] = ["Q1?", "Q2?", "Q3?"]
    agent.researcher_agent()
    assert len(agent.state["answers"]) == 3
    assert all("answer" in item for item in agent.state["answers"])

def test_evaluator_returns_scores():
    agent = ResearchAgentSystem("What is AI?")
    agent.state["summary"] = "Test summary"
    agent.evaluator_agent()
    assert "scores" in agent.state["evaluation"]
    assert "overall" in agent.state["evaluation"]
