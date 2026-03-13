import os
import re
import time
import subprocess
import logging
from imap_tools import MailBox, AND

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_PASS = os.environ["GMAIL_PASS"]
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "10"))
OTP_INLINE = re.compile(
    r"(?:code|код|otp|passcode|пароль)[^\d]{0,30}(\d{4,8})"
    r"|(\d{4,8})[^\d]{0,20}(?:code|код|otp)",
    re.IGNORECASE
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def copy_to_clipboard(text):
    subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode(), check=True)


def notify(code):
    subprocess.run([
        "notify-send", "-t", "5000", "-i", "dialog-information",
        "OTP скопирован", code
    ])


def extract_otp(text):
    m = OTP_INLINE.search(text)
    if m:
        return m.group(1) or m.group(2)
    return None


def main():
    log.info(f"Запуск OTP daemon (пользователь: {GMAIL_USER})")
    last_uid = None

    while True:
        try:
            with MailBox("imap.gmail.com").login(GMAIL_USER, GMAIL_PASS, "INBOX") as mb:
                msgs = list(mb.fetch(AND(seen=False), mark_seen=False, limit=1, reverse=True))
                if msgs:
                    msg = msgs[0]
                    if msg.uid != last_uid:
                        last_uid = msg.uid
                        text = (msg.subject or "") + " " + (msg.text or "") + " " + (msg.html or "")
                        otp = extract_otp(text)
                        if otp:
                            copy_to_clipboard(otp)
                            notify(otp)
                            log.info(f"OTP скопирован: {otp} (от: {msg.from_})")
        except Exception as e:
            log.error(f"Ошибка: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
