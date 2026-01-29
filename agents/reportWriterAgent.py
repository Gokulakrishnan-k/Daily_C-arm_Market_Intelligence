import logging
from typing import Dict, Any
from datetime import datetime

from .baseAgent import BaseAgent


logger = logging.getLogger(__name__)


class ReportWriterAgent(BaseAgent):
    """
    Agent responsible for creating professional, executive-ready news briefs
    from verified research findings.
    """

    def __init__(self, **kwargs):
        """Initialize the Report Writer Agent."""
        super().__init__(name="Report Writer Agent", **kwargs)

    @property
    def systemPrompt(self) -> str:
        """Return the system prompt for report writing."""
        return """You are an expert business writer creating MedTech industry reports.

IMPORTANT: Report ALL news items provided to you. Even if news seems minor, include it.

Your writing style:
- Executive-ready: Clear, concise, and professional
- Comprehensive: Include ALL news items from the input
- Well-structured: Use clear headings and bullet points
- Source-cited: Always include source links
- Factual: Report what was found, don't add speculation

Target audience: MedTech executives tracking C-arm and surgical imaging market."""

    def run(self, verifiedFindings: Dict[str, Any]) -> str:
        """
        Create a comprehensive news brief from verified findings.

        Args:
            verifiedFindings: Output from FactCheckAgent containing verified content.

        Returns:
            Formatted text report ready for distribution.
        """
        logger.info("Report Writer Agent creating news brief")

        allContent = self._compileContent(verifiedFindings)
        today = datetime.now().strftime("%B %d, %Y")

        prompt = f"""Create an executive news brief for {today} based on the following verified research findings.

VERIFIED FINDINGS BY CATEGORY:

{allContent}

Create a professional news brief with:

1. EXECUTIVE SUMMARY
   - 3 bullet points highlighting the most important developments across all categories
   - Focus on actionable intelligence

2. MOBILE C-ARM IMAGING
   - Key developments and news
   - Competitive moves
   - Include source links

3. ORTHOPEDIC SURGERY (Trauma, Spine, Joint Replacement)
   - Key developments and news
   - Technology innovations
   - Include source links

4. INTERVENTIONAL VASCULAR SURGERY
   - Key developments and news
   - Market trends
   - Include source links

5. MARKET WATCH
   - Brief analysis of overall market trends
   - Companies to watch
   - Upcoming events or regulatory deadlines (if mentioned)

Guidelines:
- Keep each section concise (3-5 bullet points max)
- Use clear, professional language
- Include [Source: Name] citations
- If no news in a category, note "No significant developments this period"
- Total length: 500-800 words"""

        try:
            report = self.generate(prompt, self.systemPrompt)
            logger.info("News brief created successfully")
            return report
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return self._createFallbackReport(verifiedFindings, today)

    def _compileContent(self, verifiedFindings: Dict[str, Any]) -> str:
        """
        Compile all verified content into a single text block.

        Args:
            verifiedFindings: Dictionary of verified findings by category.

        Returns:
            Formatted string with all content sections.
        """
        sections = []

        categoryMap = {
            "mobile_carm": "Mobile C-arm Imaging",
            "orthopedic": "Orthopedic Surgery",
            "vascular": "Vascular Surgery"
        }

        for category, data in verifiedFindings.items():
            displayName = categoryMap.get(category, category)
            content = data.get("verified_content", "No content available")
            sections.append(f"=== {displayName.upper()} ===\n{content}\n")

        return "\n".join(sections)

    def _createFallbackReport(self, findings: Dict[str, Any], date: str) -> str:
        """
        Create a basic report if AI generation fails.

        Args:
            findings: Raw findings dictionary.
            date: Report date string.

        Returns:
            Basic formatted report.
        """
        report = f"""# C-arm & Surgical Imaging Market Intelligence
## {date}

---

### Executive Summary
Report generation encountered issues. Please review raw findings below.

"""
        for category, data in findings.items():
            content = data.get("verified_content", data.get("original_analysis", "No data"))
            report += f"### {category.replace('_', ' ').title()}\n{content}\n\n---\n"

        return report

    def createSummaryOnly(self, verifiedFindings: Dict[str, Any]) -> str:
        """
        Create just an executive summary (shorter version).

        Args:
            verifiedFindings: Dictionary of verified findings.

        Returns:
            Brief executive summary text.
        """
        allContent = self._compileContent(verifiedFindings)

        prompt = f"""Based on the following MedTech news findings, create a brief executive summary
(3-5 bullet points) highlighting only the most critical developments:

{allContent}

Format as bullet points. Focus on: Major product launches, acquisitions, FDA approvals, and competitive moves."""

        try:
            return self.generate(prompt, self.systemPrompt)
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return "Executive summary generation failed. Please review full report."
