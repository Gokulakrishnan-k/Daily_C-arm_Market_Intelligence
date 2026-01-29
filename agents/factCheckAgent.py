import logging
from typing import Dict, List, Any

from .baseAgent import BaseAgent


logger = logging.getLogger(__name__)


class FactCheckAgent(BaseAgent):
    """Agent for verifying and organizing research findings."""

    def __init__(self, webSearchClient=None, **kwargs):
        """Initialize the Fact-Check Agent."""
        super().__init__(name="FactCheckAgent", **kwargs)
        self.webSearch = webSearchClient

    @property
    def systemPrompt(self) -> str:
        """Return the system prompt for fact-checking."""
        return 

    def run(self, researchFindings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify and organize research findings.

        Args:
            researchFindings: Output from ResearchAgent.

        Returns:
            Verified and organized findings.
        """
        logger.info("Verifying findings")

        verifiedFindings = {}

        for category, data in researchFindings.items():
            analysis = data.get("analysis", "")
            rawArticles = data.get("rawArticles", [])

            if not analysis or analysis.startswith("Analysis failed"):
                verifiedFindings[category] = {
                    "verifiedContent": "No verified content available.",
                    "confidence": "Low"
                }
                continue

            sourcesContext = self._buildSourcesContext(rawArticles)

            prompt = f"""Organize and verify this research analysis:

ANALYSIS:
{analysis}

SOURCES:
{sourcesContext}

Tasks:
1. Keep ALL news items found - do not filter them out
2. Mark each with [VERIFIED] if a source URL exists
3. Organize by company or topic

Output format:
VERIFIED FINDINGS:
- [Finding 1 with source]
- [Finding 2 with source]
(Include ALL findings from the analysis)

CONFIDENCE: High (if sources provided) / Medium (if partial sources) / Low (if no sources)"""

            try:
                response = self.generate(prompt, self.systemPrompt)
                verifiedFindings[category] = {
                    "verifiedContent": response,
                    "originalAnalysis": analysis,
                    "articleCount": len(rawArticles)
                }
                logger.info(f"Verified: {category}")
            except Exception as e:
                logger.error(f"Fact-check failed for {category}: {e}")
                verifiedFindings[category] = {
                    "verifiedContent": analysis,
                    "confidence": "Low",
                    "error": str(e)
                }
        
        return verifiedFindings
    
    def _buildSourcesContext(self, articles: List[Dict], maxArticles: int = 10) -> str:
        """Build context string from source articles."""
        if not articles:
            return "No source articles available."
        
        contextParts = []
        for i, article in enumerate(articles[:maxArticles], 1):
            title = article.get("title", "Unknown")
            source = article.get("source", "Unknown")
            date = article.get("date", "")
            link = article.get("link", "")
            contextParts.append(f"{i}. \"{title}\" - {source} ({date})\n   URL: {link}")
        
        return "\n".join(contextParts)
