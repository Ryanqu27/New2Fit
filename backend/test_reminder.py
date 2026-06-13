import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from Services.email_service import send_email

TEST_RECIPIENT = "Ryanqu27@gmail.com"  
TEST_FIRST_NAME = "Ryan"             


html_content = f"""
<html>
    <body style="font-family: sans-serif; color: #333; line-height: 1.6;">
        <h2>Time to hit the gym, {TEST_FIRST_NAME}!</h2>
        <p>It's been a full week since your last logged workout. Consistency is the key to reaching your goals.</p>
        <p>Log in to New2Fit today and log a quick session!</p>
        <br>
    </body>
</html>
"""

success = send_email(
    to_email=TEST_RECIPIENT,
    subject="We miss you at New2Fit!",
    html_content=html_content
)

if success:
    print("SUCCESS: Reminder email sent! Check your inbox to preview how it looks.")
else:
    print("FAILED: Email was not sent. Check your EMAIL_SENDER and EMAIL_PASSWORD in .env")
