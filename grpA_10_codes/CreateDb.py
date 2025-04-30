import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# 1. Excel Dosyasını Oku
file_path = 'C:/Users/User/Desktop/Deneme/ÖrnekVeri.xlsx' # Verilerin bulunduğu excel dosyasının yolu.
data = pd.read_excel(file_path)

# 2. İlgili Sütunları Seç
columns_to_use = ["Açıklama", "Uzun Açıklama", "Konum", "Ekipman Numarası"] #Excel dosyasında 2 tane "Açıklama" sütunu var biz ilkini kullanacağımız için diğerinin ismini "Açıklama1" yaptım.
data = data[columns_to_use]

# 3. NaN Değerleri İşle
data.fillna("", inplace=True)

# 4. Vektör Modeli Yükle
model = SentenceTransformer('all-MiniLM-L6-v2')

# 5. Chroma Ayarları
persist_directory = "C:/Users/User/Desktop/Database/chroma_db" # VectorDB'nin kaydedilmesini istediğin dosya yolunu gir.
client = chromadb.Client(Settings(
    persist_directory=persist_directory,
    anonymized_telemetry=False
))

# 6. Koleksiyon Oluştur
collection_name = "equipment_issues"  # Oluşturacağımız koleksiyonun ismi.
collection = client.get_or_create_collection(name=collection_name)

