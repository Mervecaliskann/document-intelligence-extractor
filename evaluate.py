"""
evaluate.py
------------
Modelin ne kadar dogru cikardigini OLCUYORUM. Her fatura icin LLM'in cikardigi
alanlari, dogru cevap dosyasiyla (ground_truth.json) karsilastirip alan bazli
accuracy raporu uretiyorum.
EN: I MEASURE how accurate the model is. For each invoice I compare the LLM's
extracted fields against the ground truth and produce a field-level accuracy report.

Not: ground truth sadece GELISTIRME asamasinda var (veriyi ben urettim).
Production'da dogru cevap olmaz; orada validators.py'daki checksum'lara guveniriz.
EN: Ground truth only exists in development (I generated the data). In production
there is no answer key, so we rely on the checksum validation in validators.py.
"""

import json
from pathlib import Path
from extractor import extract_text, extract_fields

SAMPLES = Path(__file__).parent / "sample_invoices"

# hangi alanlari degerlendiriyorum / which fields I evaluate
FIELDS = ["fatura_no", "taraf", "musteri", "tarih", "tutar", "iban"]


def normalize(s: str) -> str:
    """Karsilastirmadan once kucuk farklari temizliyorum (bosluk, buyuk/kucuk harf).
       EN: clean tiny differences before comparing (spaces, upper/lower case)."""
    return str(s).strip().lower().replace(" ", "")


def evaluate():
    # dogru cevaplari yukle / load ground truth
    truth = json.loads((SAMPLES / "ground_truth.json").read_text(encoding="utf-8"))

    # her alan icin dogru sayaci / correct counter per field
    correct = {f: 0 for f in FIELDS}
    total = 0

    for filename, true_fields in truth.items():
        pdf_path = SAMPLES / filename
        if not pdf_path.exists():
            continue

        # 1) LLM ile alanlari cikar / extract fields with the LLM
        text = extract_text(str(pdf_path))
        pred = extract_fields(text)
        total += 1

        # 2) her alani dogru cevapla karsilastir / compare each field with ground truth
        for f in FIELDS:
            if normalize(pred.get(f, "")) == normalize(true_fields.get(f, "")):
                correct[f] += 1

        print(f"  {filename} islendi / done")

    # 3) rapor / report
    print(f"\n=== Alan bazli dogruluk ({total} fatura) / Field-level accuracy ===")
    for f in FIELDS:
        pct = 100 * correct[f] / total if total else 0
        print(f"  {f:12s}: {pct:5.1f}%   ({correct[f]}/{total})")

    overall = 100 * sum(correct.values()) / (len(FIELDS) * total) if total else 0
    print(f"\n  GENEL / OVERALL: {overall:.1f}%")


if __name__ == "__main__":
    evaluate()
