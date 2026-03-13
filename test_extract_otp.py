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

def test_saudia_alfursan():
    assert extract_otp("Please find your one-time password code below: 260051") == "260051"

def test_saudia_subject():
    assert extract_otp("Retrieve AlFursan OTP 764967") == "764967"

def test_saudia_full_snippet():
    text = "Dear AlFursan Member, Please find your one-time password code below: 260051 If you did not request a one-time password you may ignore this email."
    assert extract_otp(text) == "260051"

def test_saudia_html_separate_paragraphs():
    html = '<p>Please find your one-time password code below:</p><p style="font-size:24px">614834</p>'
    assert extract_otp(html) == "614834"

def test_saudia_html_real():
    html = '<p style="margin-bottom: 12px;">Please find your one-time password code below:</p>\r\n<p style="font-size: 24px;font-weight: 700;margin-bottom: 20px;">614834</p>'
    assert extract_otp(html) == "614834"

def test_code_in_html_tags():
    html = '<td>Your verification code</td><td>482910</td>'
    assert extract_otp(html) == "482910"
