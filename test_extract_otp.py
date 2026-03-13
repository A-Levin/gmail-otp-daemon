import pytest
import os
os.environ.setdefault("GMAIL_USER", "test@gmail.com")
os.environ.setdefault("GMAIL_PASS", "test")

from otp_daemon import extract_otp


# --- должен поймать ---

def test_github():
    assert extract_otp("Here is your GitHub sudo authentication code: 65971473") == "65971473"

def test_saudia_4digit():
    assert extract_otp("Verification code Dear Vladimir, Please use this verification code: 3856") == "3856"

def test_uber():
    assert extract_otp("You'll need this code to finish logging in. Your code: 482910") == "482910"

def test_namecheap():
    assert extract_otp("Your confirmation code is 7823") == "7823"

def test_otp_keyword():
    assert extract_otp("Your OTP is 293847") == "293847"

def test_russian_kod():
    assert extract_otp("Ваш код подтверждения: 481920") == "481920"

def test_russian_parol():
    assert extract_otp("Одноразовый пароль: 5519") == "5519"

def test_code_before_number():
    assert extract_otp("Enter code 129483 to confirm") == "129483"

def test_passcode():
    assert extract_otp("passcode: 88291") == "88291"

def test_8digit():
    assert extract_otp("authentication code: 81753309") == "81753309"

def test_code_with_spaces():
    assert extract_otp("Your verification code:   473829") == "473829"

def test_code_in_subject_only():
    assert extract_otp("[GitHub] Sudo email verification code 65971473") == "65971473"

def test_multiline():
    text = "Hello,\n\nYour code:\n482910\n\nDo not share."
    assert extract_otp(text) == "482910"


# --- не должен поймать ---

def test_no_keyword():
    assert extract_otp("Your order #482910 has been shipped.") is None

def test_newsletter_year():
    assert extract_otp("Top stories of 2024 for you") is None

def test_newsletter_price():
    assert extract_otp("Get 50% off — save 1500 today") is None

def test_no_numbers():
    assert extract_otp("Please verify your email address by clicking the link.") is None

def test_empty():
    assert extract_otp("") is None

def test_long_gap_between_code_and_number():
    assert extract_otp("Your code will be sent separately. Meanwhile enjoy our newsletter. Offer: 4829") is None
