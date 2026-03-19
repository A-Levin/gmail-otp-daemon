import os
import re
import time
import json
import datetime
import subprocess
import logging
from pathlib import Path
from imap_tools import MailBox, AND, A

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_PASS = os.environ["GMAIL_PASS"]
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "10"))
SEEN_FILE = Path(__file__).parent / ".seen_uids.json"
LOCK_FILE = Path("/tmp/otp-daemon.lock")
LOG_FILE = Path(__file__).parent / "otp_daemon.log"
OTP_INLINE = re.compile(
    r"(?:code|код|otp|passcode|password|пароль)[^\d]{0,30}(\d{4,8})"
    r"|(\d{4,8})[^\d]{0,20}(?:code|код|otp|password)",
    re.IGNORECASE
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ]
)
log = logging.getLogger(__name__)


def copy_to_clipboard(text):
    subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode(), check=True)


def notify(code):
    env = os.environ.copy()
    env.setdefault("DISPLAY", ":0.0")
    subprocess.run([
        "notify-send", "-t", "5000", "-i", "dialog-information",
        "OTP скопирован", code
    ], env=env)


def strip_html(text):
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text)


def extract_otp(text):
    m = OTP_INLINE.search(strip_html(text))
    if m:
        code = m.group(1) or m.group(2)
        if re.match(r"^(19|20)\d{2}$", code):
            return None
        return code
    return None


def load_seen():
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text()))
    return set()


def save_seen(seen):
    SEEN_FILE.write_text(json.dumps(list(seen)))


def main():
    import fcntl
    lock_fd = open(LOCK_FILE, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        log.error("Другой экземпляр уже запущен. Выход.")
        return

    log.info(f"Запуск OTP daemon (пользователь: {GMAIL_USER})")
    seen = load_seen()

    while True:
        try:
            with MailBox("imap.gmail.com").login(GMAIL_USER, GMAIL_PASS, "INBOX") as mb:
                since = datetime.date.today() - datetime.timedelta(days=1)
                msgs = list(mb.fetch(A(date_gte=since), mark_seen=False, limit=50, reverse=True))
                log.info(f"Проверка: {len(msgs)} писем за последние 24ч")
                for msg in msgs:
                    if msg.uid in seen:
                        continue
                    seen.add(msg.uid)
                    text = (msg.subject or "") + " " + (msg.text or "") + " " + (msg.html or "")
                    otp = extract_otp(text)
                    if otp:
                        copy_to_clipboard(otp)
                        notify(otp)
                        log.info(f"OTP скопирован: {otp} (от: {msg.from_})")
                save_seen(seen)
        except Exception as e:
            log.error(f"Ошибка: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
