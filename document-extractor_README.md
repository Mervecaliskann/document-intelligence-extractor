# 📄 Fatura Bilgi Çıkarıcı (Document Intelligence)

Fatura / dekont gibi yarı yapılandırılmış belgelerden **yapılandırılmış bilgi** (taraf, tarih, tutar, IBAN, fatura no) çıkaran küçük bir sistem. LLM ile çıkarım + kural tabanlı doğrulama + basit arayüz.

> Örnek olarak finansal belgeler kullandım ama sistem herhangi bir belge türüne (sözleşme, form, poliçe) uyarlanabilir.

## Neden yaptım (amaç)
Bankacılık ve genel NLP rollerinde sık istenen bir iş: bir belgeyi insan tek tek okumadan, içindeki kritik alanları otomatik çıkarmak. Bu proje o yeteneği (document intelligence / information extraction) gösteriyor.

## Nasıl çalışıyor (akış)
```
PDF yükle → metni çıkar (pdfplumber) → LLM alanları JSON olarak çıkarsın
         → alanları doğrula (IBAN checksum, tarih, tutar) → tablo + JSON göster
```

## Ne yaptım (teknik)
- **Metin çıkarma:** `pdfplumber` ile PDF'ten ham metin.
- **Structured extraction:** LLM'e (Groq / Llama-3.3) JSON şemasıyla soruyorum; `response_format=json_object` ile modeli **sadece JSON** döndürmeye zorluyorum → çıktı makine-okunur.
- **Doğrulama katmanı:** LLM çıktısını körü körüne kabul etmiyorum. IBAN'ı **mod-97 checksum** ile, tarihi format ile doğruluyorum. (Bankada güven için şart.)
- **Arayüz:** Streamlit ile yükle-gör; JSON indirme.
- **Test verisi:** Gerçek banka verisi PII olduğu için `gen_invoices.py` ile **sentetik** faturalar ürettim (doğru cevaplarıyla birlikte).

## Kurulum & Çalıştırma
```bash
# 1) sanal ortam
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2) kütüphaneler
pip install -r requirements.txt

# 3) API anahtarı: .env.example -> .env yap, Groq anahtarını yaz
cp .env.example .env

# 4) örnek faturaları üret
python gen_invoices.py

# 5) arayüzü başlat
streamlit run app.py
```

## Dosyalar
| Dosya | Ne yapıyor |
|---|---|
| `gen_invoices.py` | Sentetik test faturaları (PDF) üretir |
| `extractor.py` | PDF'ten metin + LLM ile alan çıkarma |
| `validators.py` | IBAN/tarih/tutar doğrulama (mod-97) |
| `app.py` | Streamlit arayüzü |

## Sonraki adımlar (yol haritası)
- Layout-aware model (LayoutLMv3 / Donut) ile taranmış belgelerde alan çıkarma.
- Doğruluk metriği: `ground_truth.json` ile alan bazlı accuracy raporu.
- Docker + cloud (GCP Cloud Run / HF Spaces) ile canlı deploy.

## Teknolojiler
Python · pdfplumber · Groq (Llama-3.3) · Streamlit · reportlab
