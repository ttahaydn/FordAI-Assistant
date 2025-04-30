import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re

# Kategorileri tanımlayın
categories = {
    "Kapı Sorunları": ["kapı sıkışık", "kapı kapanmıyor", "kapı zor açılıyor"],
    "Motor Sorunları": ["motor çalışmıyor", "motor ses yapıyor", "motor sensör arızası"],
    "Elektrik Sorunları": ["elektrik kesintisi", "kablo kopuk"],
    "Takım Sorunları": ["takım değiştirme hatası", "takım sıkma sökme hatası"],
    "Atc Sorunları": ["atc arızası", "atc kol arızası", "atc arızası takım değiştirilemiyor", "atc arızası tezgah başlatılamıyor", "atc kapak arızası" , "atc kapı arızası", "atc takım hatası"],
    "Diğer": ["magazin hatası","robot arızası", "tezgah alarm", "tool clamper arızası", "pot takılacak", "shifter takılacak", "spındıl takılacak"]
}

# Veri temizleme fonksiyonu: "arizasi"yi "arızası" olarak düzeltir ve büyük I harfini düşürürken ı olarak düzenler
def clean_text(text):
    text = text.replace("I", "ı")  # Büyük I harfini ı olarak düzelt
    text = re.sub(r'arizasi', 'arızası', text, flags=re.IGNORECASE)
    text = text.lower()  # Tüm harfleri küçük yap
    return text

# Veri yükleme
file_path = "veri.xlsx" #ornek verinin yolu, klasor icinde yer alıyor 
data = pd.read_excel(file_path)

# Temizleme işlemi
data['Açıklama'] = data['Açıklama'].apply(clean_text)

# SentenceTransformer modeli yükleme
model = SentenceTransformer('all-MiniLM-L6-v2')

# Açıklamaları vektöre dönüştürme
data['aciklama_vector'] = data['Açıklama'].apply(model.encode)

# Kategori vektörleri oluşturma
category_vectors = {category: model.encode(' '.join(phrases)) for category, phrases in categories.items()}

# Açıklamaları kategorilere ayırma
def assign_category(row):
    similarities = {cat: cosine_similarity([row['aciklama_vector']], [vec]).item() for cat, vec in category_vectors.items()}
    return max(similarities, key=similarities.get)  # En yüksek benzerlik skoru olan kategoriyi döndür
data['Category'] = data.apply(assign_category, axis=1)

# Vektör sütunlarını kaldırma
data = data.drop(columns=['aciklama_vector'])

# Kategori sütununu Açıklama sütunundan sonra yerleştirme
cols = list(data.columns)
cols.insert(cols.index('Açıklama') + 1, cols.pop(cols.index('Category')))
data = data[cols]

# Kategorize edilmiş veriyi kaydetme
data.to_excel("categorized_veri.xlsx", index=False)

# Sonuçları yazdırma
print("Kategorilere atanış açıklamalar:")
print(data[['Açıklama', 'Category']].head())
