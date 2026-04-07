#!/usr/bin/env python3
import json
import base64
import smtplib
from email.mime.text import MIMEText
import sys

SMTP_SERVER = 'smtp.qq.com'
SMTP_PORT = 465
SMTP_USER = '2789154625@qq.com'
SMTP_PASSWORD = 'nhmbgkbipglfdebb'
TO_EMAIL = '2789154625@qq.com'

def main():
    if len(sys.argv) < 2:
        print("Usage: python send_email.py <trending_data_base64>")
        return

    trending_data_b64 = sys.argv[1]
    
    try:
        trending_data_json = base64.b64decode(trending_data_b64).decode('utf-8')
        data = json.loads(trending_data_json)
        
        print("Trending data loaded successfully!")
        
        body = "GitHub Daily Trending\n\n"
        
        if 'githubTrending' in data:
            for lang, repos in data['githubTrending'].items():
                if lang:
                    body += f"\n{lang.upper()}:\n"
                else:
                    body += "\nAll Languages:\n"
                
                for i, repo in enumerate(repos[:10], 1):
                    body += f"{i}. {repo['title']}\n"
                    body += f"   https://github.com{repo['link']}\n"
                    if repo.get('description'):
                        body += f"   {repo['description']}\n"
                    body += f"   ⭐ {repo['stars']} | +{repo['todayStars']} today\n"
                    body += "\n"
        
        body += "\n---\n"
        body += "Sent by GitHub Actions"
        
        print("Sending email...")
        
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = 'GitHub Daily Trending'
        msg['From'] = SMTP_USER
        msg['To'] = TO_EMAIL
        
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, TO_EMAIL, msg.as_string())
        
        print("Email sent successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()