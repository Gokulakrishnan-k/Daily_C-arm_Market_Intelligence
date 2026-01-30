import os
from dataclasses import dataclass, field
from typing import List
from dotenv import load_dotenv

load_dotenv()


@dataclass
class SearchConfig:
    """Configuration for search parameters."""

    sources: List[str] = field(default_factory=lambda: [
        "auntminnie.com",
        "massdevice.com",
        "medtechdive.com",
        "medgadget.com",
        "fiercebiotech.com",
        "devicetalks.com"
    ])

    mobileCarmKeywords: List[str] = field(default_factory=lambda: [
        "mobile C-arm surgery imaging news",
        "fluoroscopy surgical system hospital",
        "Ziehm Siemens GE Philips C-arm"
    ])

    orthopedicKeywords: List[str] = field(default_factory=lambda: [
        "orthopedic surgery robot imaging news",
        "spine surgery navigation technology",
        "Stryker Medtronic Zimmer orthopedic"
    ])

    vascularKeywords: List[str] = field(default_factory=lambda: [
        "interventional radiology vascular imaging",
        "angiography catheterization lab news",
        "hybrid OR endovascular surgery"
    ])

    resultsPerQuery: int = 15
    maxNewsAgeDays: int = 7


@dataclass
class EmailConfig:
    """Configuration for email delivery."""
    
    senderEmail: str = field(default_factory=lambda: os.getenv("GMAIL_SENDER_EMAIL", ""))
    senderPassword: str = field(default_factory=lambda: os.getenv("GMAIL_APP_PASSWORD", ""))
    recipientEmails: List[str] = field(default_factory=lambda: [
        email.strip() for email in os.getenv("RECIPIENT_EMAILS", "").split(",") if email.strip()
    ])
    smtpServer: str = "smtp.gmail.com"
    smtpPort: int = 587
    subjectTemplate: str = "C-arm & Surgical Imaging Market Intelligence - {date}"


@dataclass
class Config:
    """Main application configuration."""
    
    githubToken: str = field(default_factory=lambda: os.getenv("GITHUB_TOKEN", ""))
    githubModel: str = field(default_factory=lambda: os.getenv("GITHUB_MODEL", "gpt-4o-mini"))
    
    search: SearchConfig = field(default_factory=SearchConfig)
    email: EmailConfig = field(default_factory=EmailConfig)
    
    scheduleTime: str = "08:00"
    timezone: str = "America/New_York"
    
    temperature: float = 0.3
    maxTokens: int = 10000
    
    logLevel: str = "INFO"
    logFile: str = "carmResearchAgent.log"
    
    def validate(self) -> bool:
        """Validate required configuration."""
        if not self.githubToken:
            print("Warning: GITHUB_TOKEN not set - running in basic mode")
        if not self.email.senderEmail:
            print("Warning: Email not configured")
        return True
    
    def hasAiBackend(self) -> bool:
        """Check if GitHub token is configured."""
        return bool(self.githubToken)
    
    def canSendEmail(self) -> bool:
        """Check if email sending is configured."""
        return bool(self.email.senderEmail and self.email.senderPassword and self.email.recipientEmails)


config = Config()
