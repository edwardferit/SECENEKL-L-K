
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Altın Hesaplama", layout="centered")

# Logo göster (.png uzantısı)
logo = Image.open("Siyah-PNG.png")
st.image(logo, use_container_width=True)

st.title("Altın Hesaplama")

# Otomatik USD/KG fiyatı (örnek değer)
usd_kg_otomatik = 104680

# Kullanıcı isterse düzenleyebilir
usd_kg_satis = st.number_input("USD/KG Satış Fiyatı (otomatik veya manuel)", value=usd_kg_otomatik)
gram_altin = usd_kg_satis / 1000
st.write(f"Gram Altın Fiyatı (USD): **{gram_altin:.3f}**")

# Altın gramı
altin_gram = st.number_input("Altın Gram", value=1.0, step=1.0)

# İşçilik tipi seçimi
tip = st.selectbox("İşçilik Tipi", ["CHP", "Halat", "14 OMEGA"])

# 14 OMEGA için özel işlem
if tip == "14 OMEGA":
    saflik = 0.380
    iscilik = 0.000
    st.write("14 OMEGA seçildiği için Saflık: 0.380 | İşçilik: 0.000")
else:
    # Diğerleri için giriş alanları
    saflik = st.number_input("Saflık (Milyem)", value=0.585, step=0.001, format="%.3f")
    default_iscilik = 0.020 if tip == "CHP" else 0.045
    iscilik = st.number_input("İşçilik (Milyem)", value=default_iscilik, step=0.001, format="%.3f")

# Hesaplamalar
sadece_iscilik = iscilik * gram_altin
iscilik_dahil_fiyat = (saflik + iscilik) * gram_altin
toplam_fiyat = iscilik_dahil_fiyat * altin_gram

# Sonuçlar
st.subheader("Sonuçlar")
st.write(f"1 Gram Sadece İşçilik (USD): **{sadece_iscilik:.4f}**")
st.write(f"İşçilik Dahil Gram Fiyatı (USD): **{iscilik_dahil_fiyat:.3f}**")
st.write(f"Toplam Fiyat (USD): **{toplam_fiyat:.2f}**")
