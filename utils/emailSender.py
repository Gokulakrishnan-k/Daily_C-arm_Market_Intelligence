import smtplib
import re
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Union

logger = logging.getLogger(__name__)


class EmailSender:
    """Gmail email sender for delivering reports."""
    
    def __init__(self, senderEmail: str, senderPassword: str, smtpServer: str = "smtp.gmail.com", smtpPort: int = 587):
        """
        Initialize email sender.
        
        Args:
            senderEmail: Gmail address to send from
            senderPassword: Gmail App Password
            smtpServer: SMTP server address
            smtpPort: SMTP server port
        """
        self.senderEmail = senderEmail
        self.senderPassword = senderPassword
        self.smtpServer = smtpServer
        self.smtpPort = smtpPort
    
    def sendHtmlEmail(self, recipientEmails: Union[str, List[str]], subject: str, htmlContent: str, plainText: str = None) -> bool:
        """
        Send an HTML email to one or multiple recipients (using BCC for privacy).
        
        Args:
            recipientEmails: Recipient's email address(es) - can be a string or list of strings
            subject: Email subject
            htmlContent: HTML content of the email
            plainText: Plain text fallback (optional)
        
        Returns:
            True if sent successfully, False otherwise
        """
        # Normalize to list
        if isinstance(recipientEmails, str):
            recipients = [recipientEmails]
        else:
            recipients = recipientEmails
        
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.senderEmail
            message["To"] = self.senderEmail 
            message["Bcc"] = ", ".join(recipients)
            
            if plainText:
                textPart = MIMEText(plainText, "plain")
                message.attach(textPart)
            
            htmlPart = MIMEText(htmlContent, "html")
            message.attach(htmlPart)
            
            with smtplib.SMTP(self.smtpServer, self.smtpPort) as server:
                server.starttls()
                server.login(self.senderEmail, self.senderPassword)
                server.sendmail(self.senderEmail, recipients, message.as_string())
            
            logger.info(f"Email sent successfully (BCC) to {len(recipients)} recipient(s)")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Gmail authentication failed: {e}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def sendReport(self, recipientEmails: Union[str, List[str]], htmlReport: str, subjectTemplate: str = "C-arm & Surgical Imaging Market Intelligence - {date}") -> bool:
        """
        Send the market intelligence report to one or multiple recipients.
        
        Args:
            recipientEmails: Recipient's email address(es) - can be a string or list of strings
            htmlReport: HTML formatted report
            subjectTemplate: Subject line template with {date} placeholder
        
        Returns:
            True if sent successfully, False otherwise
        """
        subject = subjectTemplate.format(date=datetime.now().strftime("%B %d, %Y"))
        plainText = self._htmlToPlainText(htmlReport)
        
        return self.sendHtmlEmail(
            recipientEmails=recipientEmails,
            subject=subject,
            htmlContent=htmlReport,
            plainText=plainText
        )
    
    def _htmlToPlainText(self, html: str) -> str:
        """Convert HTML to plain text."""
        text = re.sub(r'<[^>]+>', '', html)
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        return text.strip()
    
    def testConnection(self) -> bool:
        """Test the email connection."""
        try:
            with smtplib.SMTP(self.smtpServer, self.smtpPort) as server:
                server.starttls()
                server.login(self.senderEmail, self.senderPassword)
            logger.info("Email connection test successful")
            return True
        except Exception as e:
            logger.error(f"Email connection test failed: {e}")
            return False
