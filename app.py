"""
app.py
-------
Streamlit arayuzu. Kullanici bir fatura PDF'i yukluyor, ben metni cikariyorum,
LLM alanlari dolduruyor, validator dogruluyor ve ekranda gosteriyorum.
EN: Streamlit UI. User uploads an invoice PDF, I extract text, the LLM fills
the fields, the validator checks them, and I show the result.

Calistirmak icin / to run:  streamlit run app.py
"""

import os
import json
import streamlit as st
from extractor import extract_text, extract_fields
from validators import validate_fields

st.set_page_config(page_title="Fatura Bilgi Cikarici", page_icon="📄")

st.title("📄 Fatura Bilgi Cikarici")
st.caption("PDF yukle → LLM alanlari cikarsin → dogrulanmis sonucu gor. "
           "(Document intelligence / structured extraction demo)")

# 1) dosya yukleme kutusu / file uploader
uploaded = st.file_uploader("Fatura veya dekont yukle (PDF)", type=["pdf"])


@st.cache_data(show_spinner=False)
def run_llm(text: str) -> dict:
    """Ayni metin icin LLM'i tekrar cagirma. Streamlit her tiklamada (or. JSON indir)
       sayfayi bastan calistirir; cache olmadan her seferinde yeni API cagrisi olur.
       EN: don't call the LLM again for the same text. Streamlit reruns the page on
       every click (e.g. the download button); without a cache that is a new API call."""
    return extract_fields(text)


if not os.getenv("GROQ_API_KEY"):
    st.error("GROQ_API_KEY bulunamadi. .env dosyasina ekle. / GROQ_API_KEY is missing.")
    st.stop()

if uploaded:
    # 2) metni cikar / extract text
    with st.spinner("Metin cikariliyor..."):
        text = extract_text(uploaded)

    # taranmis (resim) PDF'te metin katmani yoktur / scanned PDFs have no text layer
    if not text.strip():
        st.warning("Bu PDF'te okunabilir metin yok (muhtemelen taranmis bir belge). "
                   "OCR destegi yol haritasinda. / No text layer found (likely a scanned PDF).")
        st.stop()

    # ham metni gormek isteyen olursa (kapali dursun) / raw text in a collapsible box
    with st.expander("Ham metni gor / show raw text"):
        st.text(text)

    # 3) LLM ile alanlari cikar / extract fields with the LLM
    with st.spinner("LLM alanlari cikariyor..."):
        try:
            fields = run_llm(text)
        except Exception as e:
            st.error(f"LLM cagrisi basarisiz / LLM call failed: {e}")
            st.stop()

    # 4) dogrula ve sonuca ekle / validate and merge into result
    checks = validate_fields(fields)

    # ekranda temiz tablo / clean table on screen
    st.subheader("Cikarilan Alanlar")
    st.table(fields)

    # dogrulama rozetleri / validation badges
    st.subheader("Dogrulama")
    c1, c2, c3 = st.columns(3)
    c1.metric("IBAN", "Gecerli ✅" if checks["iban_gecerli"] else "Gecersiz ❌")
    c2.metric("Tarih", "Gecerli ✅" if checks["tarih_gecerli"] else "Gecersiz ❌")
    c3.metric("Tutar", "Gecerli ✅" if checks["tutar_gecerli"] else "Gecersiz ❌")

    # ham JSON + indirme / raw JSON + download button
    result = {**fields, **checks}
    st.subheader("JSON Cikti")
    st.json(result)
    st.download_button("JSON indir", json.dumps(result, ensure_ascii=False, indent=2),
                       file_name="cikti.json", mime="application/json")
else:
    st.info("Baslamak icin bir PDF yukle. Ornek faturalar `sample_invoices/` klasorunde.")