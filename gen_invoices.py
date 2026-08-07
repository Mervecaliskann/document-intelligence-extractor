"""
gen_invoices.py
----------------
Sahte ama gerçekçi fatura PDF'leri üretiyorum. Gerçek banka verisi gizli/PII
olduğu için kendi test verimi üretmek en temizi (hem doğru cevabı da biliyorum).
EN: I generate fake-but-realistic invoice PDFs. Real bank data is private,
so making my own test data is cleanest (and I know the correct answers).

Çıktı / output:
  - sample_invoices/*.pdf   -> test faturaları
  - sample_invoices/ground_truth.json -> her faturanın doğru alanları (test için)
"""

import json
import random
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

OUT = Path(__file__).parent / "sample_invoices"
OUT.mkdir(exist_ok=True)

# rastgele veri üretmek için küçük havuzlar / small pools for random data
# not: varsayilan PDF fontu Turkce ı/ş/ğ bozdugu icin sade karakterli isimler sectim
# EN: default PDF font breaks some Turkish chars, so I picked ASCII-clean names
FIRMS = ["Ada Yazilim A.S.", "Meric Tekstil Ltd.", "Kuzey Insaat A.S.",
         "Deniz Lojistik", "Ege Gida San. Tic.", "Marmara Enerji A.S."]
NAMES = ["Ayse Kaya", "Mehmet Demir", "Zeynep Yilmaz", "Can Ozturk",
         "Elif Sahin", "Burak Aydin"]


def random_iban():
    # GECERLI bir TR IBAN uretiyorum: once 22 haneli hesap kismi, sonra
    # mod-97 ile dogru 2 kontrol hanesini hesapliyorum. Boylece validator "gecerli" der.
    # EN: I generate a VALID TR IBAN: 22-digit body + correct 2 check digits via mod-97.
    bban = "".join(str(random.randint(0, 9)) for _ in range(22))
    # kontrol hanesi hesabi: (bban + "TR00") -> harfleri sayiya cevir -> 98 - (x % 97)
    tmp = bban + "2927" + "00"          # TR=2927 (T=29, R=27), gecici kontrol 00
    check = 98 - (int(tmp) % 97)
    return f"TR{check:02d}{bban}"


def make_invoice(i):
    """Tek bir fatura PDF'i çiziyorum ve doğru alanlarını geri döndürüyorum.
       EN: draw one invoice PDF and return its correct fields."""
    data = {
        "fatura_no": f"INV-2024-{random.randint(1000, 9999)}",
        "taraf": random.choice(FIRMS),
        "musteri": random.choice(NAMES),
        "tarih": f"{random.randint(1,28):02d}.{random.randint(1,12):02d}.2024",
        "tutar": f"{random.randint(1000, 90000):,} TL".replace(",", "."),
        "iban": random_iban(),
    }

    path = OUT / f"fatura_{i:02d}.pdf"
    c = canvas.Canvas(str(path), pagesize=A4)
    w, h = A4

    # başlık / header
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, h - 60, "FATURA")

    # firma bilgisi / company info
    c.setFont("Helvetica", 11)
    c.drawString(50, h - 100, f"Satici: {data['taraf']}")
    c.drawString(50, h - 120, f"Musteri: {data['musteri']}")

    # sağ üstte fatura no + tarih / invoice no + date top-right
    c.drawString(380, h - 100, f"Fatura No: {data['fatura_no']}")
    c.drawString(380, h - 120, f"Tarih: {data['tarih']}")

    # çizgi / line
    c.line(50, h - 140, w - 50, h - 140)

    # ödeme bilgisi / payment info
    c.setFont("Helvetica", 11)
    c.drawString(50, h - 200, "Aciklama: Danismanlik hizmeti")
    c.drawString(50, h - 230, f"IBAN: {data['iban']}")

    # toplam tutar (kalın) / total amount (bold)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, h - 280, f"Toplam Tutar: {data['tutar']}")

    c.save()
    return data


if __name__ == "__main__":
    truth = {}
    for i in range(1, 16):          # 15 fatura üret / make 15 invoices
        truth[f"fatura_{i:02d}.pdf"] = make_invoice(i)

    # doğru cevapları kaydet (sonra modelin çıktısıyla karşılaştırmak için)
    # EN: save ground truth to later compare with the model output
    with open(OUT / "ground_truth.json", "w", encoding="utf-8") as f:
        json.dump(truth, f, ensure_ascii=False, indent=2)

    print(f"{len(truth)} fatura uretildi -> {OUT}")
