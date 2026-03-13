# gmail-otp-daemon

Daemon that watches your Gmail inbox and automatically copies OTP codes to clipboard — like iOS/Android autofill, but on Linux.

When a new unread email arrives with a verification code, the code is instantly copied to your clipboard and a desktop notification pops up. Just Ctrl+V.

## How it works

- Polls Gmail via IMAP every 10 seconds
- Checks only the latest unread message
- Extracts codes adjacent to keywords: `code`, `otp`, `код`, `passcode`, etc.
- Copies to clipboard via `xclip`
- Sends desktop notification via `notify-send`

## Requirements

- Linux with X11
- `xclip` (`pacman -S xclip` / `apt install xclip`)
- `libnotify` for notifications
- Gmail with IMAP enabled + [App Password](https://myaccount.google.com/apppasswords)
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
git clone https://github.com/A-Levin/gmail-otp-daemon
cd gmail-otp-daemon
uv sync
```

Create a `.env` file:

```env
GMAIL_USER=you@gmail.com
GMAIL_PASS=your_app_password
```

Enable IMAP in Gmail: Settings → See all settings → Forwarding and POP/IMAP → Enable IMAP.

## Run

```bash
GMAIL_USER=you@gmail.com GMAIL_PASS=xxxx uv run otp_daemon.py
```

Or with `.env` via [direnv](https://direnv.net/) / any env loader.

## Autostart

Create `~/.config/autostart/otp-daemon.desktop`:

```ini
[Desktop Entry]
Type=Application
Name=OTP Daemon
Exec=env GMAIL_USER=you@gmail.com GMAIL_PASS=xxxx uv run --project /path/to/gmail-otp-daemon otp_daemon.py
X-GNOME-Autostart-enabled=true
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `GMAIL_USER` | required | Gmail address |
| `GMAIL_PASS` | required | App password |
| `POLL_INTERVAL` | `10` | Seconds between checks |
