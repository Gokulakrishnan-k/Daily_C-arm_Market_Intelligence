import html
import logging
from typing import Dict, Any
from datetime import datetime

from .baseAgent import BaseAgent


logger = logging.getLogger(__name__)


class HTMLEditorAgent(BaseAgent):
    """
    Agent responsible for converting text reports into beautiful,
    email-ready HTML newsletters.
    """

    def __init__(self, **kwargs):
        """Initialize the HTML Editor Agent."""
        super().__init__(name="HTML Editor Agent", **kwargs)

    @property
    def systemPrompt(self) -> str:
        """Return the system prompt for HTML email design."""
        return """You are an expert HTML email designer specializing in professional newsletters.

Your HTML must be:
- Email-client compatible (works in Gmail, Outlook, Apple Mail)
- Mobile-responsive (readable on phones)
- Clean and professional design
- Uses inline CSS (no external stylesheets)
- Uses tables for layout (email compatibility)
- Accessible with good contrast ratios
- NEVER use markdown syntax (**, *, [text](url)) - always use proper HTML tags
- Article titles should use <strong> tags for bold
- URLs should be direct <a href="url">descriptive text</a> links, NOT [Link](url) format

Design guidelines:
- Color scheme: Professional blues and grays
- Primary color: #1a5f7a (dark blue)
- Secondary color: #57837b (teal)
- Background: #f5f5f5 (light gray)
- Text: #333333 (dark gray)
- Maximum width: 600px (email standard)
- Font: Arial, Helvetica, sans-serif (web-safe)

Structure:
- Header with logo/title
- Executive summary box
- Category sections with clear headings
- Clickable links
- Footer with unsubscribe placeholder"""

    def run(self, textReport: str, title: str = None) -> str:
        """
        Convert text report to HTML email format.

        Args:
            textReport: Plain text report from ReportWriterAgent.
            title: Optional custom title.

        Returns:
            HTML formatted email content.
        """
        logger.info("HTML Editor Agent formatting report")

        today = datetime.now().strftime("%B %d, %Y")
        if not title:
            title = "C-arm & Surgical Imaging Market Intelligence"

        prompt = f"""Convert the following text report into a beautiful HTML email newsletter.

REPORT TITLE: {title}
DATE: {today}

TEXT REPORT:
{textReport}

Requirements:
1. Use inline CSS only (no <style> tags in head)
2. Use tables for layout (max-width: 600px, centered)
3. Create a professional header with the title and date
4. Use the color scheme:
   - Header background: #1a5f7a
   - Section headers: #57837b
   - Body background: #f5f5f5
   - Card background: #ffffff
   - Text: #333333
5. Make all URLs clickable links (styled in #1a5f7a)
6. Add section dividers between categories
7. Create a clean footer
8. Ensure bullet points are properly formatted
9. Add appropriate padding and margins for readability

CRITICAL FORMATTING RULES:
- Article titles must use <strong> tags for bold text, NOT markdown **asterisks**
- URLs must be direct clickable links using <a href="URL">Source Name</a> or <a href="URL">Read Article</a>
- Do NOT use [Link](url) markdown format - convert all to proper HTML anchor tags
- Each article should be in a card-style div with: title (bold), date, summary paragraph, and clickable source link
- Remove any markdown syntax like **, *, or [text](url) and replace with proper HTML

SPACING AND LAYOUT:
- Add generous spacing between articles (margin-bottom: 25px minimum)
- Add padding inside each article card (padding: 15px 20px)
- Add line-height: 1.6 for better readability
- Add margin-top: 10px between the date, summary, and link elements
- Use clear visual separation between sections

CONTENT RULES:
- If any text ends with "..." or is truncated, write a COMPLETE sentence based on the context
- NEVER leave sentences incomplete or ending with "..."
- Summaries should be full, readable sentences

Return ONLY the complete HTML code, starting with <!DOCTYPE html>"""

        try:
            htmlContent = self.generate(prompt, self.systemPrompt)
            htmlContent = self._cleanHtmlResponse(htmlContent)
            logger.info("HTML email formatted successfully")
            return htmlContent
        except Exception as e:
            logger.error(f"HTML generation failed: {e}")
            return self._createFallbackHtml(textReport, title, today)

    def _cleanHtmlResponse(self, htmlContent: str) -> str:
        """
        Clean up AI-generated HTML response.

        Args:
            htmlContent: Raw HTML from AI generation.

        Returns:
            Cleaned HTML string.
        """
        import re
        
        if "```html" in htmlContent:
            htmlContent = htmlContent.split("```html")[1]
        if "```" in htmlContent:
            htmlContent = htmlContent.split("```")[0]

        htmlContent = htmlContent.strip()

        if not htmlContent.lower().startswith("<!doctype"):
            doctypePos = htmlContent.lower().find("<!doctype")
            if doctypePos > 0:
                htmlContent = htmlContent[doctypePos:]
            elif htmlContent.lower().startswith("<html"):
                htmlContent = "<!DOCTYPE html>\n" + htmlContent

        # Clean up any remaining markdown syntax
        # Convert **text** to <strong>text</strong>
        htmlContent = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', htmlContent)
        
        # Convert [Link](url) or [text](url) to proper HTML links
        htmlContent = re.sub(
            r'\[([^\]]+)\]\(([^)]+)\)',
            r'<a href="\2" style="color: #1a5f7a;">\1</a>',
            htmlContent
        )
        
        # Remove any remaining literal [Link] text followed by URLs
        htmlContent = re.sub(r'\[Link\]\s*', '', htmlContent)

        return htmlContent

    def _createFallbackHtml(self, textReport: str, title: str, date: str) -> str:
        """
        Create a basic HTML email if AI generation fails.

        Args:
            textReport: Plain text report content.
            title: Report title.
            date: Report date string.

        Returns:
            Basic HTML email template.
        """
        safeContent = html.escape(textReport)

        lines = safeContent.split('\n')
        htmlLines = []

        for line in lines:
            if line.startswith('# '):
                htmlLines.append(f'<h1 style="color: #1a5f7a;">{line[2:]}</h1>')
            elif line.startswith('## '):
                htmlLines.append(f'<h2 style="color: #57837b;">{line[3:]}</h2>')
            elif line.startswith('### '):
                htmlLines.append(f'<h3 style="color: #57837b;">{line[4:]}</h3>')
            elif line.startswith('- '):
                htmlLines.append(f'<li>{line[2:]}</li>')
            elif line.strip() == '---':
                htmlLines.append('<hr style="border: 1px solid #ddd; margin: 20px 0;">')
            elif line.strip():
                htmlLines.append(f'<p>{line}</p>')

        content = '\n'.join(htmlLines)

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f5f5f5; font-family: Arial, Helvetica, sans-serif;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #f5f5f5;">
        <tr>
            <td align="center" style="padding: 20px;">
                <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden;">
                    <tr>
                        <td style="background-color: #1a5f7a; padding: 30px; text-align: center;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 24px;">{title}</h1>
                            <p style="color: #b8d4e3; margin: 10px 0 0 0;">{date}</p>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 30px; color: #333333; line-height: 1.6;">
                            {content}
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color: #f0f0f0; padding: 20px; text-align: center; font-size: 12px; color: #666666;">
                            <p style="margin: 0;">C-arm Research Agent | Automated Market Intelligence</p>
                            <p style="margin: 5px 0 0 0;">You received this email because you are subscribed to daily updates.</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

    def createTestEmail(self) -> str:
        """
        Create a test HTML email to verify formatting.

        Returns:
            Test HTML email content.
        """
        testReport = """# Executive Summary
- Test item 1: This is a test of the email system
- Test item 2: Checking formatting and layout
- Test item 3: Verifying HTML rendering

## Mobile C-arm Imaging
No test data for this category.

## Orthopedic Surgery
No test data for this category.

## Vascular Surgery
No test data for this category.

---
This is a test email generated by the C-arm Research Agent."""

        return self.run(testReport, "Test Email - C-arm Research Agent")
