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


def get_max_uid(mb):
    msgs = list(mb.fetch(AND(all=True), mark_seen=False, limit=1, reverse=True, headers_only=True))
    return msgs[0].uid if msgs else None


def main():
    log.info(f"Запуск OTP daemon (пользователь: {GMAIL_USER})")

    with MailBox("imap.gmail.com").login(GMAIL_USER, GMAIL_PASS, "INBOX") as mb:
        last_uid = get_max_uid(mb)
        log.info(f"Стартовый UID: {last_uid}")

    while True:
        time.sleep(POLL_INTERVAL)
        try:
            with MailBox("imap.gmail.com").login(GMAIL_USER, GMAIL_PASS, "INBOX") as mb:
                current_uid = get_max_uid(mb)
                if current_uid is None or current_uid == last_uid:
                    continue

                msgs = list(mb.fetch(
                    AND(uid=f"{last_uid}:*"),
                    mark_seen=False,
                    reverse=True
                ))

                for msg in msgs:
                    if msg.uid <= last_uid:
                        continue
                    text = (msg.subject or "") + " " + (msg.text or "") + " " + (msg.html or "")
                    otp = extract_otp(text)
                    if otp:
                        copy_to_clipboard(otp)
                        notify(otp)
                        log.info(f"OTP скопирован: {otp} (от: {msg.from_})")

                last_uid = current_uid

        except Exception as e:
            log.error(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
