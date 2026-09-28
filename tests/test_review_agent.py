import src.review_agent as agent


def test_review_resume_with_mock(monkeypatch):
    class Message:
        content = """
        {
          "overall_score": 82,
          "ats_score": 79,
          "strengths": ["Strong Python experience"],
          "gaps": ["Add cloud deployment evidence"],
          "keyword_analysis": ["Python is present"],
          "recommendations": ["Add measurable project outcomes"],
          "rewritten_summary": "Python developer with experience building APIs.",
          "interview_focus": ["Explain API architecture"]
        }
        """

    class Choice:
        message = Message()

    class Response:
        choices = [Choice()]

    class Completions:
        def create(self, **kwargs):
            return Response()

    class Client:
        class chat:
            completions = Completions()

    monkeypatch.setenv("NVIDIA_API_KEY", "test-key")
    monkeypatch.setattr(agent, "_client", lambda: Client())

    result = agent.review_resume("Python developer", "Need Python")
    assert result["overall_score"] == 82
    assert result["ats_score"] == 79
