import argparse
import logging
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from utils import WebSearchClient, EmailSender, setupLogger
from agents import ResearchAgent, FactCheckAgent, ReportWriterAgent, HTMLEditorAgent


def formatArticleDate(dateStr: str) -> str:
    """
    Convert ISO 8601 date format to readable format.
    
    Args:
        dateStr: Date string like '2026-01-23T17:55:00+00:00'
    
    Returns:
        Formatted string like 'Jan 23, 2026 - 5:55 PM'
    """
    if not dateStr or dateStr == 'Date not available':
        return 'Date not available'
    
    try:
        # Try parsing ISO 8601 format
        if 'T' in dateStr:
            # Handle timezone offset
            if '+' in dateStr:
                dateStr = dateStr.rsplit('+', 1)[0]
            elif dateStr.endswith('Z'):
                dateStr = dateStr[:-1]
            
            dt = datetime.fromisoformat(dateStr)
            return dt.strftime("%b %d, %Y - %I:%M %p")
        else:
            # Try other common formats
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]:
                try:
                    dt = datetime.strptime(dateStr, fmt)
                    return dt.strftime("%b %d, %Y")
                except ValueError:
                    continue
            # Return as-is if no format matches
            return dateStr
    except Exception:
        return dateStr


class CarmResearchOrchestrator:
    """Main orchestrator for the multi-agent research pipeline."""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.logger = setupLogger(
            logLevel=self.config.logLevel,
            logFile=self.config.logFile
        )
        
        self.config.validate()
        self.webSearch = WebSearchClient()
        self.hasAi = self.config.hasAiBackend()
        
        if self.hasAi:
            agentKwargs = {
                "githubToken": self.config.githubToken,
                "modelName": self.config.githubModel,
                "temperature": self.config.temperature,
                "maxTokens": self.config.maxTokens
            }
            
            self.logger.info(f"AI Backend: GitHub Models ({self.config.githubModel})")
            
            self.researchAgent = ResearchAgent(**agentKwargs)
            self.factCheckAgent = FactCheckAgent(webSearchClient=self.webSearch, **agentKwargs)
            self.reportWriter = ReportWriterAgent(**agentKwargs)
            self.htmlEditor = HTMLEditorAgent(**agentKwargs)
            self.logger.info("AI agents initialized")
        else:
            self.researchAgent = None
            self.factCheckAgent = None
            self.reportWriter = None
            self.htmlEditor = None
            self.logger.info("Running in basic mode (no AI)")
        
        if self.config.canSendEmail():
            self.emailSender = EmailSender(
                senderEmail=self.config.email.senderEmail,
                senderPassword=self.config.email.senderPassword,
                smtpServer=self.config.email.smtpServer,
                smtpPort=self.config.email.smtpPort
            )
        else:
            self.emailSender = None
            self.logger.warning("Email not configured")
    
    def runPipeline(self, saveLocal: bool = True) -> dict:
        """Execute the full research and report pipeline."""
        self.logger.info("=" * 60)
        self.logger.info("Starting C-arm Research Agent Pipeline")
        self.logger.info("=" * 60)
        
        results = {
            "success": False,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Stage 1: Web Search
            self.logger.info("\n[STAGE 1] Gathering news...")
            rawArticles = self._gatherNews()
            totalArticles = sum(len(v) for v in rawArticles.values())
            self.logger.info(f"Found {totalArticles} articles")
            
            if not self.hasAi:
                self.logger.info("\n[BASIC MODE] Saving raw results...")
                textReport = self._createBasicReport(rawArticles)
                htmlReport = self._createBasicHtml(rawArticles)
                if saveLocal:
                    self._saveReports(textReport, htmlReport)
                results["success"] = True
                self.logger.info("\n[SUCCESS] Basic report saved")
                return results

            # Stage 2: Direct Report Generation (simplified pipeline)
            self.logger.info("\n[STAGE 2] Analyzing articles...")
            textReport = self._createDirectReport(rawArticles)

            # Stage 3: HTML Formatting
            self.logger.info("\n[STAGE 3] Formatting HTML...")
            htmlReport = self.htmlEditor.run(textReport)
            
            if saveLocal:
                self._saveReports(textReport, htmlReport)
            
            # Stage 6: Email Delivery
            if self.emailSender:
                self.logger.info("\n[STAGE 6] Sending email...")
                emailSent = self.emailSender.sendReport(
                    recipientEmail=self.config.email.recipientEmail,
                    htmlReport=htmlReport,
                    subjectTemplate=self.config.email.subjectTemplate
                )
                if emailSent:
                    self.logger.info(f"Email sent to {self.config.email.recipientEmail}")
            else:
                self.logger.info("\n[STAGE 6] Skipped (email not configured)")
            
            results["success"] = True
            self.logger.info("\n" + "=" * 60)
            self.logger.info("[SUCCESS] Pipeline completed")
            self.logger.info("=" * 60)
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}", exc_info=True)
            results["error"] = str(e)
        
        return results

    def _gatherNews(self) -> dict:
        """Gather news articles using web search."""
        topics = {
            "mobileCarm": self.config.search.mobileCarmKeywords,
            "orthopedic": self.config.search.orthopedicKeywords,
            "vascular": self.config.search.vascularKeywords
        }
        return self.webSearch.search_multiple_topics(
            topics=topics,
            results_per_query=self.config.search.resultsPerQuery
        )

    def _createDirectReport(self, rawArticles: dict) -> str:
        """Create a report directly from raw articles using AI."""
        today = datetime.now().strftime("%B %d, %Y")

        # Format all articles into a single text block
        allArticles = []
        categoryNames = {
            "mobileCarm": "Mobile C-arm Imaging",
            "orthopedic": "Orthopedic Surgery",
            "vascular": "Interventional Vascular Surgery"
        }

        for category, articles in rawArticles.items():
            displayName = categoryNames.get(category, category)
            for article in articles[:15]:
                # Extract and format date
                rawDate = article.get('date', '')
                articleDate = formatArticleDate(rawDate) if rawDate else 'Date not available'
                
                allArticles.append(f"""
Category: {displayName}
Title: {article.get('title', 'No title')}
Source: {article.get('source', 'Unknown')}
Publication Date: {articleDate}
Content Preview: {article.get('snippet', '')}
URL: {article.get('link', '')}
---""")

        articlesText = "\n".join(allArticles)

        systemPrompt = """You are a MedTech news reporter creating executive briefings.

CRITICAL RULES:
1. Report EVERY article - each one is important news
2. For EACH article, you MUST include ALL of these elements:
   - Title (bold)
   - Publication Date (from the article's date field - ALWAYS include this)
   - Summary (2-3 sentences based on the content preview, explaining key points and relevance)
   - Source name
   - Full clickable URL
3. Group by category (Mobile C-arm, Orthopedic, Vascular)
4. Write concise but informative summaries based on the content provided
5. NEVER skip the date or summary for any article"""

        prompt = f"""Create a detailed news brief for {today} from these {len(allArticles)} articles:

{articlesText}

FORMAT FOR EACH ARTICLE (MANDATORY - follow exactly):
**[Article Title]**  
📅 Published: [Publication Date from the article]  
📝 Summary: [2-3 sentences explaining what the article is about, the key developments, companies involved, and why it matters to MedTech executives]  
🔗 Source: [Source name]  
🌐 URL: [Full URL]

REPORT STRUCTURE:
1. EXECUTIVE SUMMARY - 3 bullet points of the most important stories
2. MOBILE C-ARM IMAGING - All related articles with FULL details (date, summary, source, URL)
3. ORTHOPEDIC SURGERY - All related articles with FULL details (date, summary, source, URL)
4. VASCULAR SURGERY - All related articles with FULL details (date, summary, source, URL)
5. MARKET WATCH - Key market trends and insights

CRITICAL: Every single article MUST have:
- The publication date (use the date provided, or "Date not available" if missing)
- A meaningful 2-3 sentence summary explaining the news content
- Source attribution
- Full URL link"""

        try:
            report = self.researchAgent.generate(prompt, systemPrompt)
            return report
        except Exception as e:
            self.logger.error(f"Direct report failed: {e}")
            return self._createBasicReport(rawArticles)
    
    def _createBasicReport(self, rawArticles: dict) -> str:
        """Create a basic text report from raw articles."""
        today = datetime.now().strftime("%B %d, %Y")
        
        relevantKeywords = [
            'c-arm', 'fluoroscopy', 'imaging', 'surgical', 'orthopedic',
            'spine', 'vascular', 'radiology', 'siemens', 'philips', 
            'ge healthcare', 'ziehm', 'stryker', 'medtronic', 'zimmer', 
            'robot', 'navigation', 'angiography', 'interventional'
        ]
        
        excludeKeywords = [
            'nfl', 'draft', 'football', 'basketball', 'baseball',
            'exercise', 'workout', 'fitness', 'movie', 'entertainment'
        ]
        
        def isRelevant(article):
            text = f"{article.get('title', '')} {article.get('snippet', '')}".lower()
            for kw in excludeKeywords:
                if kw in text:
                    return False
            for kw in relevantKeywords:
                if kw in text:
                    return True
            return False
        
        report = f"# C-arm & Surgical Imaging Market Intelligence\n## {today}\n\n---\n\n"
        
        categoryNames = {
            "mobileCarm": "Mobile C-arm Imaging",
            "orthopedic": "Orthopedic Surgery",
            "vascular": "Interventional Vascular Surgery"
        }
        
        for category, articles in rawArticles.items():
            displayName = categoryNames.get(category, category)
            report += f"### {displayName}\n\n"
            
            relevantArticles = [a for a in articles if isRelevant(a)] if articles else []
            
            if not relevantArticles:
                report += "No relevant articles found.\n\n"
                continue
            
            for i, article in enumerate(relevantArticles[:10], 1):
                title = article.get("title", "No title")
                source = article.get("source", "Unknown")
                snippet = article.get("snippet", "")[:200]
                link = article.get("link", "")
                rawDate = article.get("date", "")
                articleDate = formatArticleDate(rawDate) if rawDate else "Date not available"
                
                report += f"**{i}. {title}**\n"
                report += f"   - 📅 Date: {articleDate}\n"
                report += f"   - 📝 Summary: {snippet}...\n" if snippet else ""
                report += f"   - 🔗 Source: {source}\n"
                if link:
                    report += f"   - 🌐 URL: [{source}]({link})\n"
                report += "\n"
            
            report += "---\n\n"
        
        return report
    
    def _createBasicHtml(self, rawArticles: dict) -> str:
        """Create a basic HTML report from raw articles."""
        import html as htmlModule
        today = datetime.now().strftime("%B %d, %Y")
        
        relevantKeywords = [
            'c-arm', 'fluoroscopy', 'imaging', 'surgical', 'orthopedic',
            'spine', 'vascular', 'radiology', 'siemens', 'philips', 
            'ge healthcare', 'ziehm', 'stryker', 'medtronic', 'zimmer', 
            'robot', 'navigation', 'angiography', 'interventional'
        ]
        
        excludeKeywords = [
            'nfl', 'draft', 'football', 'basketball', 'baseball',
            'exercise', 'workout', 'fitness', 'movie', 'entertainment'
        ]
        
        def isRelevant(article):
            text = f"{article.get('title', '')} {article.get('snippet', '')}".lower()
            for kw in excludeKeywords:
                if kw in text:
                    return False
            for kw in relevantKeywords:
                if kw in text:
                    return True
            return False
        
        categoryNames = {
            "mobileCarm": "Mobile C-arm Imaging",
            "orthopedic": "Orthopedic Surgery",
            "vascular": "Interventional Vascular Surgery"
        }
        
        sectionsHtml = ""
        for category, articles in rawArticles.items():
            name = categoryNames.get(category, category)
            relevantArticles = [a for a in articles if isRelevant(a)] if articles else []
            
            articlesHtml = ""
            if not relevantArticles:
                articlesHtml = '<p style="color: #666;">No relevant articles found.</p>'
            else:
                for i, article in enumerate(relevantArticles[:10], 1):
                    title = htmlModule.escape(article.get("title", "No title"))
                    source = htmlModule.escape(article.get("source", "Unknown"))
                    snippet = htmlModule.escape(article.get("snippet", "")[:200])
                    link = article.get("link", "")
                    rawDate = article.get("date", "")
                    articleDate = htmlModule.escape(formatArticleDate(rawDate) if rawDate else "Date not available")
                    
                    articlesHtml += f'''
                    <div style="margin-bottom: 15px; padding: 12px; background: #f9f9f9; border-radius: 6px; border-left: 3px solid #1a5f7a;">
                        <strong style="color: #1a5f7a;">{i}. {title}</strong><br>
                        <span style="font-size: 11px; color: #888;">📅 {articleDate}</span><br>
                        <span style="font-size: 12px; color: #666;">🔗 {source}</span><br>
                        <p style="margin: 8px 0; font-size: 13px; color: #444;">📝 {snippet}...</p>
                        {f'<a href="{link}" style="color: #1a5f7a; font-size: 12px;">🌐 Read full article</a>' if link else ''}
                    </div>'''
            
            sectionsHtml += f'''
                <tr>
                    <td style="padding: 20px 30px;">
                        <h2 style="color: #57837b; margin: 0 0 15px 0; font-size: 18px; border-bottom: 2px solid #57837b; padding-bottom: 8px;">{name}</h2>
                        {articlesHtml}
                    </td>
                </tr>'''
        
        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>C-arm Market Intelligence - {today}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f5f5f5; font-family: Arial, sans-serif;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #f5f5f5;">
        <tr>
            <td align="center" style="padding: 20px;">
                <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden;">
                    <tr>
                        <td style="background: linear-gradient(135deg, #1a5f7a 0%, #2d7d9a 100%); padding: 30px; text-align: center;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 24px;">C-arm & Surgical Imaging</h1>
                            <p style="color: #b8d4e3; margin: 8px 0 0 0;">Market Intelligence Report</p>
                            <p style="color: #8ec0d6; margin: 8px 0 0 0; font-size: 14px;">{today}</p>
                        </td>
                    </tr>
                    {sectionsHtml}
                    <tr>
                        <td style="background-color: #2d3748; padding: 20px; text-align: center;">
                            <p style="color: #a0aec0; margin: 0; font-size: 12px;">C-arm Research Agent</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>'''
    
    def _saveReports(self, textReport: str, htmlReport: str):
        """Save reports locally."""
        outputDir = Path("output")
        outputDir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        textPath = outputDir / f"report_{timestamp}.md"
        textPath.write_text(textReport, encoding="utf-8")
        self.logger.info(f"Text report saved: {textPath}")
        
        htmlPath = outputDir / f"report_{timestamp}.html"
        htmlPath.write_text(htmlReport, encoding="utf-8")
        self.logger.info(f"HTML report saved: {htmlPath}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="C-arm Research Agent - MedTech Market Intelligence")
    parser.add_argument("--run", action="store_true", help="Run the pipeline once")
    
    args = parser.parse_args()
    
    try:
        orchestrator = CarmResearchOrchestrator()
        
        if args.run:
            results = orchestrator.runPipeline()
            if results["success"]:
                print("\nReport generated successfully!")
                print("Check the 'output' folder for saved reports.")
            else:
                print(f"\nPipeline failed: {results.get('error', 'Unknown error')}")
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
