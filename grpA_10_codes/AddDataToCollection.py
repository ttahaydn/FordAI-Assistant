import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

client = chromadb.PersistentClient(path="C:/Users/User/Desktop/Database/chroma_db")
collection_name = "equipment_issues"
collection = client.get_or_create_collection(name=collection_name)
file_path = 'C:/Users/User/Desktop/Deneme/ÖrnekVeri.xlsx' #Verilerin bulunduğu excel dosyasının dizin yolunu gir.
data = pd.read_excel(file_path)

model = SentenceTransformer('all-MiniLM-L6-v2')

# 7. Vektörlere Dönüştür ve Depola
for index, row in data.iterrows():
    combined_text = f"{row['Uzun Açıklama']}"
    vector = model.encode(combined_text)
    collection.add(
        documents=[combined_text],
        metadatas=[{
            "Konum": row["Konum"],
            "Ekipman Numarası": row["Ekipman Numarası"],
            "Açıklama": row["Açıklama"]
        }],
        ids=[str(index)]
    )

print(f"Koleksiyonda toplam {collection.count()} kayıt var.")