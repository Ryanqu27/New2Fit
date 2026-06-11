import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from Services.email_service import send_email

TEST_RECIPIENT = "Ryanqu27@gmail.com"  


success = send_email(
    to_email=TEST_RECIPIENT,
    subject="New2Fit — Email Test",
    html_content="""
    <html>
        <body style="font-family: sans-serif; color: #333; line-height: 1.6;">
            <h2>Email service is working!</h2>
        </body>
    </html>
    """
)

if success:
    print("SUCCESS: Email sent! Check your inbox.")
else:
    print("FAILED: Email was not sent. Check that EMAIL_SENDER and EMAIL_PASSWORD are set in .env")
