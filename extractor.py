"""
extractor.py
-------------
Projenin kalbi. Iki is yapiyor:
  1) PDF'ten ham metni cikar (pdfplumber)
  2) O metni LLM'e verip belirli alanlari JSON olarak cikart (structured output)
EN: The heart of the project. 1) pull raw text from the PDF, 2) send it to the
LLM and get specific fields back as JSON (structured output).
"""

import os
import json
import pdfplumber
from dotenv import load_dotenv

load_dotenv()  # .env dosyasindan GROQ_API_KEY'i oku / read the API key from .env

# cikarmak istedigim alanlar / the fields I want to extract
SCHEMA = ["fatura_no", "taraf", "musteri", "tarih", "tutar", "iban"]


def extract_text(pdf_file) -> str:
    """PDF'ten tum metni cekiyorum. pdf_file bir dosya yolu ya da yuklenen dosya olabilir.
       EN: pull all text from the PDF (path or uploaded file both work)."""
    text = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text.append(page.extract_text() or "")
    return "\n".join(text)


def extract_fields(text: str) -> dict:
    """Metni LLM'e verip alanlari JSON olarak aliyorum.
       Onemli nokta: response_format ile modeli SADECE JSON dondurmeye zorluyorum,
       boylece cikti makine-okunur oluyor (serbest metin degil).
       EN: send text to the LLM and get fields as JSON. Key trick: response_format
       forces JSON-only output, so it's machine-readable, not free text."""

    from groq import Groq  # sadece burada lazim / only needed here
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""Asagidaki fatura metninden su alanlari cikar ve SADECE gecerli JSON dondur.
Alan bulunamazsa degeri bos string "" birak. Ekstra aciklama yazma.

Istenen JSON sablonu:
{{"fatura_no": "", "taraf": "", "musteri": "", "tarih": "", "tutar": "", "iban": ""}}

Fatura metni:
\"\"\"{text}\"\"\""""

    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",           # Groq uzerinde hizli calisan model
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},    # <-- JSON'a zorla / force JSON
        temperature=0,                              # tutarli cikti icin 0 / 0 = deterministic
    )

    raw = resp.choices[0].message.content
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # cok nadir de olsa JSON bozuk gelirse bos sablon dondur / fallback
        data = {k: "" for k in SCHEMA}

    # sablonda olmayan/eksik anahtarlari duzelt / make sure all keys exist
    return {k: str(data.get(k, "")).strip() for k in SCHEMA}


# tek basina calistirinca ilk faturayi dene / quick test on the first invoice
if __name__ == "__main__":
    txt = extract_text("sample_invoices/fatura_01.pdf")
    print("--- CIKARILAN METIN ---\n", txt)
    print("\n--- LLM CIKTISI (JSON) ---")
    print(json.dumps(extract_fields(txt), ensure_ascii=False, indent=2))
