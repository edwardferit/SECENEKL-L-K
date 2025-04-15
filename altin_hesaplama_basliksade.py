import streamlit as st
from fpdf import FPDF
from PIL import Image
import requests
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="Fiyat Teklif", layout="centered")

# Logo yükleme
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
        usd_per_gram = usd_per_ounce / 31.1035
        return round(usd_per_gram, 3)
    except:
        return None

usd_gram_otomatik = get_usd_kg_from_api() or 104.680
usd_gram_satis = st.number_input("Gram Altın Fiyatı (USD)", value=usd_gram_otomatik, step=0.001, format="%.3f")

if st.button("Gram Fiyatı Güncelle"):
    st.cache_data.clear()
    st.rerun()

altin_gram = st.number_input("Altın Gram", value=1.0, step=1.0)

# İşçilik listesi
iscilik_listesi = {
    "HALAT": 0.040, "İÇİBOŞ FORCE": 0.040, "DOC": 0.040,
    "GURMET": 0.040, "KALZE": 0.020, "POPCORN": 0.040,
    "FLEXİ": 0.040, "ETRUŞKA": 0.040, "SİNGAPUR": 0.030,
    "DOLU GURMET": 0.030, "TIRNAK ÇAKISI": 0.030,
    "ATAÇ": 0.035, "BOYLANMIÇ FORCE": 0.020, "KİLİT": 0.020,
    "PRES ÜRÜNLER": 0.020, "TOP": 0.025, "TAŞLI SU YOLU": 0.550,
    "14 OMEGA": 0.340, "18 OMEGA": 0.440, "21 OMEGA": 0.540,
    "8MM 14 OMEGA": 0.440, "8MM 18 OMEGA": 0.540, "8MM 21 OMEGA": 0.640
}

tip = st.selectbox("İşçilik Tipi", list(iscilik_listesi.keys()))

ayar_secenekleri = {
    "14K": 0.585, "18K": 0.750, "21K": 0.875,
    "22K": 0.916, "8K": 0.333, "9K": 0.375, "10K": 0.417
}

# OMEGA özel durumu
if "OMEGA" in tip:
    if "14" in tip:
        saflik = st.number_input("Milyem (Saflık)", value=0.380, step=0.001, format="%.3f")
    elif "18" in tip:
        saflik = st.number_input("Milyem (Saflık)", value=0.450, step=0.001, format="%.3f")
    elif "21" in tip:
        saflik = st.number_input("Milyem (Saflık)", value=0.875, step=0.001, format="%.3f")
    else:
        saflik = st.number_input("Milyem (Saflık)", value=0.750, step=0.001, format="%.3f")
    secilen_ayar = tip
else:
    secilen_ayar = st.selectbox("Milyem (Saflık) Ayarı", list(ayar_secenekleri.keys()))
    saflik = ayar_secenekleri[secilen_ayar]

# İşçilik otomatik geliyor ama kullanıcı değiştirebilir
iscilik = st.number_input("İşçilik", value=iscilik_listesi[tip], step=0.001, format="%.3f")

# Hesaplamalar
sadece_iscilik = iscilik * usd_gram_satis
iscilik_dahil_fiyat = (saflik + iscilik) * usd_gram_satis
toplam_fiyat = iscilik_dahil_fiyat * altin_gram

st.subheader("Hesaplama Sonuçları")
st.write(f"1 Gram İşçilik: **{sadece_iscilik:.4f} USD**")
st.write(f"İşçilik Dahil Gram Fiyatı: **{iscilik_dahil_fiyat:.3f} USD**")
st.write(f"Toplam Fiyat: **{toplam_fiyat:.2f} USD**")

# Geçici veri listesi
if "veriler" not in st.session_state:
    st.session_state.veriler = []

if st.button("Hesaplamayı Kaydet"):
    urun_adi = tip if "OMEGA" in tip else f"{tip} ({secilen_ayar})"
    st.session_state.veriler.append({
        "Gram": round(altin_gram, 2),
        "Ürün": urun_adi,
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
        font_path = str(Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
        pdf.add_page()
        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.set_font("DejaVu", "", 16)
        pdf.cell(200, 10, firma_adi, ln=True, align="C")
        pdf.set_font("DejaVu", "", 12)
        pdf.cell(200, 10, f"Altın Hesaplama Raporu - {datetime.now().strftime('%d.%m.%Y')}", ln=True, align="C")
        pdf.ln(5)

        pdf.set_font("DejaVu", "", 10)
        pdf.cell(20, 10, "Gram", 1)
        pdf.cell(45, 10, "Ürün", 1)
        pdf.cell(20, 10, "Milyem", 1)
        pdf.cell(20, 10, "İşçilik", 1)
        pdf.cell(35, 10, "1g İşçilik", 1)
        pdf.cell(40, 10, "Toplam", 1)
        pdf.ln()

        for v in st.session_state.veriler:
            pdf.cell(20, 10, f'{v["Gram"]:.2f}', 1)
            pdf.cell(45, 10, v["Ürün"], 1)
            pdf.cell(20, 10, f'{v["Milyem"]:.3f}', 1)
            pdf.cell(20, 10, f'{v["İşçilik"]:.3f}', 1)
            pdf.cell(35, 10, f'{v["1g İşçilik"]:.2f}', 1)
            pdf.cell(40, 10, f'{v["Toplam"]:.2f}', 1)
            pdf.ln()

        path = "fiyat_teklif_raporu.pdf"
        pdf.output(path)
        with open(path, "rb") as f:
            st.download_button("PDF Dosyasını İndir", f, file_name=path, mime="application/pdf")