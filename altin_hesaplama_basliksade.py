
import streamlit as st
from fpdf import FPDF
from PIL import Image
import requests

st.set_page_config(page_title="Fiyat Teklif", layout="centered")

# Logo
try:
    logo = Image.open("Siyah-PNG.png")
    st.image(logo, use_container_width=True)
except:
    st.warning("Logo yüklenemedi. 'Siyah-PNG.png' dosyasını kontrol edin.")

st.title("FİYAT TEKLİF")

firma_adi = st.text_input("Firma Adı", "EDOCAN")

@st.cache_data(ttl=300)
def get_usd_kg_from_api():
    try:
        url = "https://api.exchangerate.host/convert?from=XAU&to=USD"
        response = requests.get(url).json()
        usd_per_ounce = response["result"]
        usd_per_kg = usd_per_ounce * 32.1507
        return round(usd_per_kg, 3)
    except:
        return None

# Satış fiyatı (%0.1 fark uygulandı)
usd_kg_mid = get_usd_kg_from_api() or 104.680
satis_farki = 1.000
usd_kg_satis_otomatik = round(usd_kg_mid * satis_farki, 3)

usd_kg_satis = st.number_input(
    "USD/KG Satış Fiyatı",
    value=usd_kg_satis_otomatik,
    step=0.001,
    format="%.3f"
)

if st.button("USD/KG Güncelle"):
    st.cache_data.clear()
    st.rerun()

altin_gram = st.number_input("Altın Gram", value=1.0, step=1.0)

tip = st.selectbox("İşçilik Tipi", ["CHP", "Halat", "Gurmet", "Forse", "14 OMEGA", "18 OMEGA"])

ayar_secenekleri = {
    "14K": 0.585, "18K": 0.750, "21K": 0.875,
    "22K": 0.916, "8K": 0.333, "9K": 0.375, "10K": 0.417
}

if tip == "14 OMEGA":
    saflik = st.number_input("Milyem (Saflık)", value=0.380, step=0.001, format="%.3f")
    iscilik = st.number_input("İşçilik", value=0.000, step=0.001, format="%.3f")
    secilen_ayar = "14 OMEGA"
elif tip == "18 OMEGA":
    saflik = st.number_input("Milyem (Saflık)", value=0.450, step=0.001, format="%.3f")
    iscilik = st.number_input("İşçilik", value=0.000, step=0.001, format="%.3f")
    secilen_ayar = "18 OMEGA"
else:
    secilen_ayar = st.selectbox("Milyem (Saflık) Ayarı", list(ayar_secenekleri.keys()))
    saflik = ayar_secenekleri[secilen_ayar]

    if tip == "CHP":
        default_iscilik = 0.020
    elif tip == "Halat":
        default_iscilik = 0.045
    elif tip == "Gurmet":
        default_iscilik = 0.035
    elif tip == "Forse":
        default_iscilik = 0.015
    else:
        default_iscilik = 0.035

    iscilik = st.number_input("İşçilik", value=default_iscilik, step=0.001, format="%.3f")

gram_altin = usd_kg_satis / 1000
sadece_iscilik = iscilik * gram_altin
iscilik_dahil_fiyat = (saflik + iscilik) * gram_altin
toplam_fiyat = iscilik_dahil_fiyat * altin_gram

st.subheader("Hesaplama Sonuçları")
st.write(f"1 Gram İşçilik: **{sadece_iscilik:.4f} USD**")
st.write(f"İşçilik Dahil Gram Fiyatı: **{iscilik_dahil_fiyat:.3f} USD**")
st.write(f"Toplam Fiyat: **{toplam_fiyat:.2f} USD**")

if "veriler" not in st.session_state:
    st.session_state.veriler = []

if st.button("Hesaplamayı Kaydet"):
    st.session_state.veriler.append({
        "Gram": round(altin_gram, 2),
        "Ürün": tip + f" ({secilen_ayar})" if tip not in ["14 OMEGA", "18 OMEGA"] else tip,
        "Milyem": round(saflik, 3),
        "İşçilik": round(iscilik, 3),
        "1g İşçilik": round(sadece_iscilik, 2),
        "Toplam": round(toplam_fiyat, 2)
    })

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

        for v in st.session_state.veriler:
            pdf.cell(20, 10, f'{v["Gram"]:.2f}', 1)
            pdf.cell(25, 10, v["Ürün"], 1)
            pdf.cell(25, 10, f'{v["Milyem"]:.3f}', 1)
            pdf.cell(25, 10, f'{v["İşçilik"]:.3f}', 1)
            pdf.cell(35, 10, f'{v["1g İşçilik"]:.2f}', 1)
            pdf.cell(40, 10, f'{v["Toplam"]:.2f}', 1)
            pdf.ln()

        path = "fiyat_teklif_raporu.pdf"
        pdf.output(path)
        with open(path, "rb") as f:
            st.download_button("PDF Dosyasını İndir", f, file_name=path, mime="application/pdf")