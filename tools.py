from langchain_tavily import TavilySearch
from langchain.tools import StructuredTool


# Web-search tool
tavily_search = TavilySearch(max_results=2, description="Only for retrieving online information like uptodate and real-time information.")


# Evaluation tool for structure output
def format_evaluation(score: int, explanation: str):
    return {
        "score": score,
        "explanation": explanation
    }

evaluation_format = StructuredTool.from_function(
    func=format_evaluation,
    name="evaluation_format",
    description="Return the evaluation in json format. The evaluation score should be an integer from 1 to 10.",
)