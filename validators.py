"""
validators.py
--------------
LLM'in cikardigi alanlari oldugu gibi kabul etmiyorum, dogruluyorum.
Bankada en onemli kisim bu: model uydurmus olabilir, kontrol sart.
EN: I don't blindly trust the LLM output — I validate it. In banking this
matters most: the model might hallucinate, so checks are a must.
"""

import re
from datetime import datetime


def is_valid_iban(iban: str) -> bool:
    """IBAN gecerli mi? Uluslararasi mod-97 checksum ile kontrol.
       (Bu mantigi banking agent projemde de kullanmistim.)
       EN: Is the IBAN valid? Checked with the international mod-97 checksum."""
    if not iban:
        return False
    iban = iban.replace(" ", "").upper()

    # temel format: 2 harf ulke kodu + rakamlar / basic format check
    if not re.match(r"^[A-Z]{2}\d{2}[A-Z0-9]+$", iban):
        return False

    # mod-97 kurali: ilk 4 karakteri sona at, harfleri sayiya cevir, %97 == 1 olmali
    # EN: mod-97 rule -> move first 4 chars to the end, letters->numbers, %97 must be 1
    rearranged = iban[4:] + iban[:4]
    digits = "".join(str(int(ch, 36)) for ch in rearranged)  # A=10 ... Z=35
    return int(digits) % 97 == 1


def is_valid_date(date_str: str) -> bool:
    """Tarih GG.AA.YYYY formatinda ve mantikli mi? / date format + basic sanity."""
    if not date_str:
        return False
    # strptime gercek takvimi kontrol eder: 31.02.2024 gibi tarihleri reddeder
    # EN: strptime checks the real calendar, so dates like 31.02.2024 are rejected
    try:
        d = datetime.strptime(date_str.strip(), "%d.%m.%Y")
    except ValueError:
        return False
    return 2000 <= d.year <= 2100


def is_valid_amount(amount_str: str) -> bool:
    """Tutar icinde gercek bir sayi var mi? / does the amount contain a real number?"""
    if not amount_str:
        return False
    # sayi + istege bagli para birimi: "55.028 TL", "1.250,50 TL", "3000"
    # EN: a number with optional thousand dots, optional decimals and an optional currency
    pattern = r"^\d{1,3}(\.\d{3})*(,\d{1,2})?\s*(TL|TRY|EUR|USD|€|\$)?$|^\d+(,\d{1,2})?\s*(TL|TRY|EUR|USD|€|\$)?$"
    return re.match(pattern, amount_str.strip(), re.IGNORECASE) is not None


def validate_fields(fields: dict) -> dict:
    """Tum alanlari tek seferde dogrulayip yanina gecerli/gecersiz bayragi ekliyorum.
       EN: validate all fields at once and attach a valid/invalid flag."""
    return {
        "iban_gecerli": is_valid_iban(fields.get("iban", "")),
        "tarih_gecerli": is_valid_date(fields.get("tarih", "")),
        "tutar_gecerli": is_valid_amount(fields.get("tutar", "")),
    }


# hizli kendi kendine test / quick self-test
if __name__ == "__main__":
    # gecerli bir IBAN ornegi (mod-97 gecen) / a known-valid IBAN
    print("Gecerli IBAN testi:", is_valid_iban("TR330006100519786457841326"))
    print("Bozuk IBAN testi:  ", is_valid_iban("TR000000000000000000000000"))
    print("Tarih testi:       ", is_valid_date("18.05.2024"))
    print("Olmayan tarih:     ", is_valid_date("31.02.2024"))   # False olmali
    print("Tutar testi:       ", is_valid_amount("55.028 TL"))
    print("Bozuk tutar:       ", is_valid_amount("abc 12"))     # False olmali