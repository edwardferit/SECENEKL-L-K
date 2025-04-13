
import streamlit as st
from fpdf import FPDF
from PIL import Image
import os

st.set_page_config(page_title="Altın Hesaplama", layout="centered")

# Logo
logo = Image.open("Siyah-PNG.png")
st.image(logo, use_container_width=True)
st.title("Altın Hesaplama")

# Firma adı
firma_adi = st.text_input("Firma Adı", "EDOCAN")

# Kullanıcıdan ürün adı al
urun_adi = st.text_input("Ürün Adı (Kendi belirle)", "")

# USD/KG işlemi
usd_kg_otomatik = 104680
usd_kg_satis = st.number_input("USD/KG Satış Fiyatı", value=usd_kg_otomatik)
gram_altin = usd_kg_satis / 1000
st.write(f"Gram Altın Fiyatı (USD): **{gram_altin:.3f}**")

# Gram
altin_gram = st.number_input("Altın Gram", value=1.0, step=1.0)

# İşçilik ayarları
tip = st.selectbox("İşçilik Tipi", ["CHP", "Halat", "14 OMEGA"])
if tip == "14 OMEGA":
    saflik = 0.380
    iscilik = 0.000
    st.write("14 OMEGA seçildiği için Saflık: 0.380 | İşçilik: 0.000")
else:
    saflik = st.number_input("Milyem (Saflık)", value=0.585, step=0.001, format="%.3f")
    default_iscilik = 0.020 if tip == "CHP" else 0.045
    iscilik = st.number_input("İşçilik", value=default_iscilik, step=0.001, format="%.3f")

# Hesaplamalar
sadece_iscilik = iscilik * gram_altin
iscilik_dahil_fiyat = (saflik + iscilik) * gram_altin
toplam_fiyat = iscilik_dahil_fiyat * altin_gram

st.subheader("Hesaplama Sonuçları")
st.write(f"1 Gram İşçilik: **{sadece_iscilik:.4f} USD**")
st.write(f"İşçilik Dahil Gram Fiyatı: **{iscilik_dahil_fiyat:.3f} USD**")
st.write(f"Toplam Fiyat: **{toplam_fiyat:.2f} USD**")

# Geçici liste
if "veriler" not in st.session_state:
    st.session_state.veriler = []

# Kaydetme
if st.button("Hesaplamayı Kaydet"):
    st.session_state.veriler.append({
        "Gram": round(altin_gram, 2),
        "Ürün": urun_adi,
        "Milyem": round(saflik, 3),
        "İşçilik": round(iscilik, 3),
        "1g İşçilik": round(sadece_iscilik, 2),
        "Toplam": round(toplam_fiyat, 2)
    })

# Liste ve PDF
if st.session_state.veriler:
    st.subheader("Kayıtlı Hesaplamalar")
    st.table(st.session_state.veriler)

    if st.button("PDF İndir"):
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", uni=True)
        pdf.set_font("DejaVu", "", 16)
        pdf.cell(200, 10, firma_adi, ln=True, align="C")
        pdf.ln(5)
        pdf.set_font("DejaVu", "", 13)
        pdf.cell(200, 10, "Altın Hesaplama Raporu", ln=True, align="C")
        pdf.ln(5)

        pdf.set_font("DejaVu", "", 10)
        pdf.cell(20, 10, "Gram", 1)
        pdf.cell(25, 10, "Ürün", 1)
        pdf.cell(25, 10, "Milyem", 1)
        pdf.cell(25, 10, "İşçilik", 1)
        pdf.cell(35, 10, "1g İşçilik (USD)", 1)
        pdf.cell(40, 10, "Toplam (USD)", 1)
        pdf.ln()

        pdf.set_font("DejaVu", "", 10)
        for v in st.session_state.veriler:
            pdf.cell(20, 10, f'{v["Gram"]:.2f}', 1)
            pdf.cell(25, 10, v["Ürün"], 1)
            pdf.cell(25, 10, f'{v["Milyem"]:.3f}', 1)
            pdf.cell(25, 10, f'{v["İşçilik"]:.3f}', 1)
            pdf.cell(35, 10, f'{v["1g İşçilik"]:.2f}', 1)
            pdf.cell(40, 10, f'{v["Toplam"]:.2f}', 1)
            pdf.ln()

        path = "altin_raporu_kullanici_urun.pdf"
        pdf.output(path)
        with open(path, "rb") as f:
            st.download_button("PDF Dosyasını İndir", f, file_name=path, mime="application/pdf")
