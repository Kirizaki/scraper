import os
from pathlib import Path
from datetime import datetime
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText

link = "http://13.48.13.46/"
body = f"""\
<html>
    <body>
        <p>Pojawiły się nowe oferty mieszkań!<br>
        <a href="{link}">http://13.48.13.46/</a>.
        </p>
    </body>
</html>
"""


def send_email_notification():
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    recipient = os.getenv('EMAIL_RECIPIENT')

    subject = "[SCRAPER] 📢 Nowe oferty mieszkań!"

    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = recipient

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        print("✅ E-mail wysłany.")


def send_whatsapp_notification():
    account_sid = os.getenv('TWILIO_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_whatsapp = os.getenv('TWILIO_WHATSAPP_FROM')
    to_whatsapp = os.getenv('TWILIO_WHATSAPP_TO')

    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=f'🆕 Nowe oferty mieszkań!\nSprawdź tutaj: {link}',
        from_=from_whatsapp,
        to=to_whatsapp
    )
    print(f"✅ WhatsApp wysłany. SID: {message.sid}")


def main():
    # Zapisz czas aktualizacji do pliku
    with open("last_update.txt", "w") as f:
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    if Path('notify.flag').exists():
        send_email_notification()
        send_whatsapp_notification()
        Path('notify.flag').unlink()
    else:
        print("Brak nowych ofert.")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    main()
