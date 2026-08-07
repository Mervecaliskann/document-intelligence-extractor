"""
validators.py
--------------
LLM'in cikardigi alanlari oldugu gibi kabul etmiyorum, dogruluyorum.
Bankada en onemli kisim bu: model uydurmus olabilir, kontrol sart.
EN: I don't blindly trust the LLM output — I validate it. In banking this
matters most: the model might hallucinate, so checks are a must.
"""

import re


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
    m = re.match(r"^(\d{2})\.(\d{2})\.(\d{4})$", date_str.strip())
    if not m:
        return False
    d, mo, y = map(int, m.groups())
    return 1 <= d <= 31 and 1 <= mo <= 12 and 2000 <= y <= 2100


def is_valid_amount(amount_str: str) -> bool:
    """Tutar icinde gercek bir sayi var mi? / does the amount contain a real number?"""
    if not amount_str:
        return False
    # sadece rakamlari al (nokta/virgul/TL at) ve sayi mi diye bak
    digits = re.sub(r"[^\d]", "", amount_str)
    return len(digits) > 0


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
    print("Tutar testi:       ", is_valid_amount("55.028 TL"))
