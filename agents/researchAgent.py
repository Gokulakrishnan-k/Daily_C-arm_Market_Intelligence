import logging
from typing import Dict, List, Any

from .baseAgent import BaseAgent


logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """Agent for gathering and organizing MedTech news."""

    def __init__(self, **kwargs):
        """Initialize the Research Agent."""
        super().__init__(name="ResearchAgent", **kwargs)

    @property
    def systemPrompt(self) -> str:
        """Return the system prompt for research analysis."""
        return """You are an expert MedTech market research analyst. Your job is to find and report REAL NEWS from the articles provided.

IMPORTANT: Each article headline IS a news item. Report what you find, even if it seems minor.

Focus areas:
- Mobile C-arm imaging systems (Ziehm, Siemens, GE, Philips)
- Orthopedic surgery technology (robots, navigation, joint replacement)
- Interventional vascular surgery and imaging

What counts as news:
- Product launches or announcements
- Company investments or expansions
- Clinical study results
- Regulatory approvals
- Acquisitions or partnerships
- New technology developments
- Market expansions

ALWAYS report the actual news from articles. Do NOT say "no developments" if articles exist."""

    def run(self, rawArticles: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Process raw search results and extract key insights.

        Args:
            rawArticles: Dictionary of category -> list of raw article data.

        Returns:
            Structured research findings by category.
        """
        logger.info(f"Processing {sum(len(v) for v in rawArticles.values())} articles")

        findings = {}

        for category, articles in rawArticles.items():
            if not articles:
                findings[category] = {
                    "summary": "No recent news found.",
                    "keyItems": [],
                    "sources": []
                }
                continue

            articlesText = self._formatArticlesForAnalysis(articles)

            prompt = f"""Analyze these {len(articles)} news articles about {category}.

ARTICLES:
{articlesText}

INSTRUCTIONS:
1. Each article headline represents a real news item - report it
2. Extract the key information from each article
3. Include company names, products, locations mentioned
4. Cite the source for each finding

Respond with:
SUMMARY: [Overview of the main news items found]

KEY FINDINGS:
1. [First news item with source link]
2. [Second news item with source link]
3. [Third news item with source link]
(Continue for all relevant articles)

COMPANIES MENTIONED: [List all companies]"""

            try:
                response = self.generate(prompt, self.systemPrompt)
                findings[category] = {
                    "analysis": response,
                    "articleCount": len(articles),
                    "rawArticles": articles[:10]
                }
                logger.info(f"Analyzed {len(articles)} articles for: {category}")
            except Exception as e:
                logger.error(f"Failed to analyze {category}: {e}")
                findings[category] = {
                    "summary": f"Analysis failed: {str(e)}",
                    "keyItems": [],
                    "sources": []
                }
        
        return findings
    
    def _formatArticlesForAnalysis(self, articles: List[Dict], maxArticles: int = 15) -> str:
        """Format articles into text for AI analysis."""
        formatted = []
        
        for i, article in enumerate(articles[:maxArticles], 1):
            title = article.get("title", "No title")
            source = article.get("source", "Unknown")
            date = article.get("date", "")
            snippet = article.get("snippet", "")
            link = article.get("link", "")
            
            formatted.append(f"""
Article {i}:
Title: {title}
Source: {source} | {date}
Content: {snippet}
URL: {link}
---""")
        
        return "\n".join(formatted)
