
import streamlit as st
from fpdf import FPDF
from PIL import Image

# Sayfa ayarı
st.set_page_config(page_title="Altın Hesaplama", layout="centered")

# Logo
logo = Image.open("Siyah-PNG.png")
st.image(logo, use_container_width=True)
st.title("Altın Hesaplama ve PDF Raporlama")

# Otomatik USD/KG fiyatı
usd_kg_otomatik = 104680
usd_kg_satis = st.number_input("USD/KG Satış Fiyatı", value=usd_kg_otomatik)
gram_altin = usd_kg_satis / 1000
st.write(f"Gram Altın Fiyatı (USD): **{gram_altin:.3f}**")

# Altın gramı
altin_gram = st.number_input("Altın Gram", value=1.0, step=1.0)

# İşçilik tipi
tip = st.selectbox("İşçilik Tipi", ["CHP", "Halat", "14 OMEGA"])
if tip == "14 OMEGA":
    saflik = 0.380
    iscilik = 0.000
    st.write("14 OMEGA seçildiği için Saflık: 0.380 | İşçilik: 0.000")
else:
    saflik = st.number_input("Saflık (Milyem)", value=0.585, step=0.001, format="%.3f")
    default_iscilik = 0.020 if tip == "CHP" else 0.045
    iscilik = st.number_input("İşçilik (Milyem)", value=default_iscilik, step=0.001, format="%.3f")

# Hesaplamalar
sadece_iscilik = iscilik * gram_altin
iscilik_dahil_fiyat = (saflik + iscilik) * gram_altin
toplam_fiyat = iscilik_dahil_fiyat * altin_gram

st.subheader("Hesaplama Sonuçları")
st.write(f"1 Gram Sadece İşçilik: **{sadece_iscilik:.4f} USD**")
st.write(f"İşçilik Dahil Gram Fiyatı: **{iscilik_dahil_fiyat:.3f} USD**")
st.write(f"Toplam Fiyat: **{toplam_fiyat:.2f} USD**")

# Geçici hafıza
if "veriler" not in st.session_state:
    st.session_state.veriler = []

# Kaydetme
if st.button("Bu Hesaplamayı Kaydet"):
    st.session_state.veriler.append({
        "Gram": altin_gram,
        "Type": tip,
        "Purity": saflik,
        "Labor": iscilik,
        "1g Labor": sadece_iscilik,
        "Price": toplam_fiyat
    })

# Liste göster
if st.session_state.veriler:
    st.subheader("Kayıtlı Hesaplamalar")
    st.table(st.session_state.veriler)

    # PDF oluşturma
    if st.button("PDF Olarak İndir"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, "Gold Calculation Report", ln=True, align="C")

        pdf.set_font("Arial", "B", 10)
        pdf.cell(20, 10, "Gram", 1)
        pdf.cell(25, 10, "Type", 1)
        pdf.cell(25, 10, "Purity", 1)
        pdf.cell(25, 10, "Labor", 1)
        pdf.cell(35, 10, "1g Labor (USD)", 1)
        pdf.cell(40, 10, "Total Price (USD)", 1)
        pdf.ln()

        pdf.set_font("Arial", "", 10)
        for v in st.session_state.veriler:
            pdf.cell(20, 10, str(v["Gram"]), 1)
            pdf.cell(25, 10, v["Type"], 1)
            pdf.cell(25, 10, f'{v["Purity"]:.3f}', 1)
            pdf.cell(25, 10, f'{v["Labor"]:.3f}', 1)
            pdf.cell(35, 10, f'{v["1g Labor"]:.3f}', 1)
            pdf.cell(40, 10, f'{v["Price"]:.2f}', 1)
            pdf.ln()

        pdf_path = "gold_calculation_report.pdf"
        pdf.output(pdf_path)
        with open(pdf_path, "rb") as f:
            st.download_button("PDF Dosyasını İndir", f, file_name=pdf_path, mime="application/pdf")
