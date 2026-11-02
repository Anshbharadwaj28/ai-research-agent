import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class Query_planner:

    def __init__ (self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")
        self.client = genai.Client(api_key = api_key)
        self.model = "gemini-2.5-flash"

    def generate_queries(self,research_question:str):

        prompt = f"""
        You are an expert academic research planner.

        Break the following research question into
        3 to 5 focused search queries.

        Each query should explore a different aspect
        of the original research question.

        Return only a numbered list of search queries.

        Research question:
        {research_question}
        """
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        return response.text
    