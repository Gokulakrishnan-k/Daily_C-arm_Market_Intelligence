"""
HTML Email Template Module

Provides HTML email template and formatting utilities for the C-arm Research Agent.

Author: MedTech Intelligence Team
"""

EMAIL_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f5f5f5; font-family: Arial, Helvetica, sans-serif; -webkit-font-smoothing: antialiased;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #f5f5f5;">
        <tr>
            <td align="center" style="padding: 20px 10px;">
                <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <tr>
                        <td style="background: linear-gradient(135deg, #1a5f7a 0%, #2d7d9a 100%); padding: 35px 30px; text-align: center;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 26px; font-weight: bold; letter-spacing: -0.5px;">
                                C-arm & Surgical Imaging
                            </h1>
                            <p style="color: #b8d4e3; margin: 8px 0 0 0; font-size: 16px;">
                                Market Intelligence Report
                            </p>
                            <p style="color: #8ec0d6; margin: 12px 0 0 0; font-size: 14px; font-weight: 500;">
                                {date}
                            </p>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 25px 30px 15px 30px;">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #e8f4f8; border-radius: 6px; border-left: 4px solid #1a5f7a;">
                                <tr>
                                    <td style="padding: 20px;">
                                        <h2 style="color: #1a5f7a; margin: 0 0 12px 0; font-size: 18px;">
                                            Executive Summary
                                        </h2>
                                        <div style="color: #333333; font-size: 14px; line-height: 1.7;">
                                            {executive_summary}
                                        </div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 15px 30px;">
                            <h2 style="color: #57837b; margin: 0 0 15px 0; font-size: 18px; border-bottom: 2px solid #57837b; padding-bottom: 8px;">
                                Mobile C-arm Imaging
                            </h2>
                            <div style="color: #333333; font-size: 14px; line-height: 1.7;">
                                {mobile_carm_content}
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 0 30px;">
                            <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 10px 0;">
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 15px 30px;">
                            <h2 style="color: #57837b; margin: 0 0 15px 0; font-size: 18px; border-bottom: 2px solid #57837b; padding-bottom: 8px;">
                                Orthopedic Surgery
                            </h2>
                            <div style="color: #333333; font-size: 14px; line-height: 1.7;">
                                {orthopedic_content}
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 0 30px;">
                            <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 10px 0;">
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 15px 30px;">
                            <h2 style="color: #57837b; margin: 0 0 15px 0; font-size: 18px; border-bottom: 2px solid #57837b; padding-bottom: 8px;">
                                Interventional Vascular Surgery
                            </h2>
                            <div style="color: #333333; font-size: 14px; line-height: 1.7;">
                                {vascular_content}
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 20px 30px;">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #fff8e6; border-radius: 6px; border-left: 4px solid #e6a817;">
                                <tr>
                                    <td style="padding: 20px;">
                                        <h2 style="color: #b8860b; margin: 0 0 12px 0; font-size: 18px;">
                                            Market Watch
                                        </h2>
                                        <div style="color: #333333; font-size: 14px; line-height: 1.7;">
                                            {market_watch}
                                        </div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color: #2d3748; padding: 25px 30px; text-align: center;">
                            <p style="color: #a0aec0; margin: 0; font-size: 13px; line-height: 1.6;">
                                <strong style="color: #ffffff;">C-arm Research Agent</strong><br>
                                Automated Market Intelligence for MedTech Professionals
                            </p>
                            <p style="color: #718096; margin: 15px 0 0 0; font-size: 11px;">
                                This report was automatically generated. Sources are cited where available.<br>
                                Questions? Reply to this email.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""


def getEmailTemplate() -> str:
    """
    Return the email template.

    Returns:
        HTML email template string with placeholders.
    """
    return EMAIL_TEMPLATE


def formatListToHtml(items: list) -> str:
    """
    Convert a list of items to HTML bullet points.

    Args:
        items: List of text items to format.

    Returns:
        HTML unordered list string.
    """
    if not items:
        return "<p>No updates available.</p>"

    htmlItems = []
    for item in items:
        htmlItems.append(f'<li style="margin-bottom: 8px;">{item}</li>')

    return f'<ul style="margin: 0; padding-left: 20px;">{"".join(htmlItems)}</ul>'


def formatLink(url: str, text: str) -> str:
    """
    Format a clickable link.

    Args:
        url: Link URL.
        text: Display text.

    Returns:
        HTML anchor tag string.
    """
    return f'<a href="{url}" style="color: #1a5f7a; text-decoration: none; border-bottom: 1px solid #1a5f7a;">{text}</a>'
