import tkinter as tk
from tkinter import ttk
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
import threading
import webbrowser
import secrets
import os
import xml.etree.ElementTree as ET
from tkinter import messagebox

# Flask Uygulaması (OAuth İşlemleri İçin)
app = Flask(__name__)
app.secret_key = "random_secret_key"

# Flask-OAuth Kütüphanesi ile Google OAuth2.0 Ayarları
oauth = OAuth(app)
oauth.register(
    name='google',
    client_id='Client_ID.apps.googleusercontent.com',
    client_secret='Client_Secret',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
    }
)

# XML Kaydetme Fonksiyonu
def save_to_xml(user_email, query, response):
    filename = f"{user_email.replace('@', '_')}.xml"
    root = ET.Element("history") if not os.path.exists(filename) else ET.parse(filename).getroot()

    entry = ET.SubElement(root, "entry")
    ET.SubElement(entry, "query").text = query
    ET.SubElement(entry, "response").text = response

    tree = ET.ElementTree(root)
    tree.write(filename, encoding="utf-8", xml_declaration=True)

# XML Okuma Fonksiyonu
def read_xml(user_email):
    filename = f"{user_email.replace('@', '_')}.xml"
    if not os.path.exists(filename):
        return []

    root = ET.parse(filename).getroot()
    return [(entry.find("query").text, entry.find("response").text) for entry in root.findall("entry")]

# XML Temizleme Fonksiyonu
def clear_xml(user_email):
    filename = f"{user_email.replace('@', '_')}.xml"
    if os.path.exists(filename):
        os.remove(filename)




user_data = None  # Kullanıcı verilerini Tkinter ile paylaşmak için

def login():
    threading.Thread(target=lambda: webbrowser.open("http://127.0.0.1:5000/login")).start()
    check_login_status()  # Login durumunu düzenli olarak kontrol et

def check_login_status():
    global user_data
    if user_data:
        login_frame.pack_forget()
        chatbot_frame.pack(fill="both", expand=True)
        if 'email' in user_data:
            user_email_label.config(text=f"Giriş Yapan Kullanıcı: {user_data['email']}")
    else:
        root.after(1000, check_login_status)

def start_flask():
    app.run(port=5000)

@app.route('/login')
def flask_login():
    nonce = secrets.token_urlsafe(16)
    session['nonce'] = nonce
    redirect_uri = url_for('authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri, nonce=nonce)

@app.route('/authorize')
def authorize():
    global user_data
    try:
        token = oauth.google.authorize_access_token()
        nonce = session.pop('nonce', None)
        if not nonce:
            return "Nonce eksik!", 400
        user_data = oauth.google.parse_id_token(token, nonce=nonce)
        session['user'] = user_data
        return redirect('/success')
    except Exception as e:
        return f"Bir hata oluştu: {e}", 500

@app.route('/success')
def success():
    return "Giriş Başarılı! Bu pencereyi kapatabilirsiniz."

@app.route('/logout')
def logout():
    global user_data
    user_data = None
    session.pop('user', None)
    return redirect('/')

# Google Generative AI API anahtarını yapılandır
genai.configure(api_key="GOOGLE_API_KEY")  # Buraya kendi API anahtarınızı girin

def build_chatBot(system_instruction):
    model = genai.GenerativeModel('gemini-1.5-flash-latest', system_instruction=system_instruction)
    chat = model.start_chat(history=[])
    return chat

def generate_LLM_answer(prompt, context, chat):
    response = chat.send_message( prompt + context)
    return response.text

def generateRAG_LLM(prompt):
    RAG_LLM = build_chatBot(system_prompt)
    return RAG_LLM

system_prompt= """ You are a technical support assistant. 

Your primary role is to provide concise, actionable solutions to technical problems based on provided context and historical problem records. Here's how to respond:

1. You will receive a user query alongside two historical problem records that are similar to the current issue. Analyze the query and the records to provide a solution.
2. Based on the information provided, deliver a response in bullet points with clear steps (maximum 5-6 points) on how the problem can be solved.
3. If no historical problem records are provided, or if the query does not match any known issues, respond with: "Bu sorunla daha önce hiç karşılaşılmamış. Lütfen yetkili teknik destek sorumlusuna ulaşınız."
4. Ensure responses are concise and fully in Turkish.
5. In some cases, you might be asked questions about the chat session itself (e.g., summarizing, listing questions). For these, do not refer to the user query or historical records, but answer based on the specific session-related request.

Your goal is to deliver accurate, context-aware technical support while maintaining brevity and clarity.

"""

RAG_LLM = generateRAG_LLM(system_prompt)

# ChromaDB bağlantısını oluştur
client = chromadb.PersistentClient(path="C:/Users/User/Desktop/Database/chroma_db") # Vektör veri tabanının dizin yolunu gir.
collection_name = "equipment_issues"
collection = client.get_collection(name=collection_name)

# Model Yükle
model = SentenceTransformer('all-MiniLM-L6-v2')

def handle_query():
    user_query = query_input.get().strip()  # Kullanıcı sorgusunu alın ve boşlukları temizleyin
    if not user_query:
        update_response("Lütfen bir sorgu girin.")
        return

    update_response("Cevaplanıyor...")  # "Cevaplanıyor..." mesajını göster
    root.update()  # GUI'yi güncelle
    

    try:
        query_vector = model.encode(user_query)
        results = collection.query(query_texts=[user_query], n_results=2)

        if results['documents'][0]:
            context = "\n\n".join(results["documents"][0])
            prompt = f"Sorgu: {user_query}"
            gemini_response = generate_LLM_answer(prompt, context, RAG_LLM)

            response = "CHATBOT YANITI:\n" + gemini_response if gemini_response else "Gemini API'den sonuç alınamadı."
            save_to_xml(user_data['email'], query_input.get(), response)  # Sorguyu ve yanıtı XML dosyasına kaydedin
        else:
            prompt = f"Sorgu: {user_query}\n\nDaha önce böyle bir sorun yaşanmadı, bunu belirt ve genel bir çözüm öner."
            gemini_response = generate_LLM_answer(prompt, "", RAG_LLM)

            response = "ChromaDB'den sonuç bulunamadı.\n" + (gemini_response if gemini_response else "Gemini API'den sonuç alınamadı.")
            save_to_xml(user_data['email'], query_input.get(), response)  # Sorguyu ve yanıtı XML dosyasına kaydedin
    except Exception as e:
        response = f"Hata oluştu: {str(e)}"

    update_response(response)

def update_response(text):
    response_text.config(state="normal")  # Metni düzenlenebilir hale getirin
    response_text.delete("1.0", tk.END)   # Önceki metni silin

    if not isinstance(text, str):
        text = str(text)  # Eğer metin değilse, string'e çevirin

    response_text.insert(tk.END, text)    # Yeni metni ekleyin
    response_text.config(state="disabled")  # Metni salt okunur hale getirin
    

# Geçmişi Gösterme
def show_history():
    if not user_data:
        messagebox.showerror("Hata", "Lütfen önce giriş yapın.")
        return

    history = read_xml(user_data['email'])
    if not history:
        messagebox.showinfo("Geçmiş", "Geçmişte sorgu bulunamadı.")
        return

    history_window = tk.Toplevel(root)
    history_window.title("Geçmiş Sorgular")
    history_window.geometry("600x400")

    text = tk.Text(history_window, wrap="word", padx=10, pady=10)
    text.pack(fill="both", expand=True)

    for query, response in history:
        text.insert(tk.END, f"Sorgu: {query}\nYanıt: {response}\n\n")

    text.config(state="disabled")

# Geçmişi Temizleme
def clear_history():
    if not user_data:
        messagebox.showerror("Hata", "Lütfen önce giriş yapın.")
        return

    clear_xml(user_data['email'])
    messagebox.showinfo("Başarılı", "Geçmiş başarıyla temizlendi.")



root = tk.Tk()
root.title("Ford Otosan Akıllı Bakım Asistanı")
root.geometry("1000x400")
root.resizable(False, False)

login_frame = tk.Frame(root)
login_frame.pack(fill="both", expand=True)

chatbot_frame = tk.Frame(root)

login_label = tk.Label(login_frame, text="Ford Otosan Akıllı Bakım Asistanı\nGoogle ile giriş yaparak devam edin.", font=("Arial", 14), pady=20)
login_label.pack()

login_button = tk.Button(login_frame, text="Google ile Giriş Yap", font=("Arial", 12), command=login, bg="#007bff", fg="white", padx=10, pady=5)
login_button.pack()

# Chatbot Arayüzü
header_frame = tk.Frame(chatbot_frame, bg="#f4f4f4", pady=10)
header_frame.pack(fill="x")
header_label = tk.Label(header_frame, text="Ford Otosan Akıllı Bakım Asistanı", font=("Arial", 16, "bold"), bg="#f4f4f4", fg="#333")
header_label.pack()
sub_label = tk.Label(header_frame, text="Not: Ford Otosan Akıllı Bakım Asistanı geliştirme aşamasında olan bir çalışmadır.", font=("Arial", 10), bg="#f4f4f4", fg="#555")
sub_label.pack()

user_email_label = tk.Label(header_frame, text="Giriş Yapan Kullanıcı: -", font=("Arial", 10), bg="#f4f4f4", fg="#555")
user_email_label.pack()

input_frame = tk.Frame(chatbot_frame, pady=10, padx=10)
input_frame.pack(fill="x", padx=20)

query_label = tk.Label(input_frame, text="Sorgunuzu buraya yazınız:", font=("Arial", 12))
query_label.grid(row=0, column=0, sticky="w", pady=5)

query_input = tk.Entry(input_frame, font=("Arial", 12), width=50)
query_input.grid(row=1, column=0, pady=5, sticky="w")

query_button = tk.Button(input_frame, text="Gönder", font=("Arial", 12), command=handle_query, bg="#007bff", fg="white", padx=10, pady=5)
query_button.grid(row=1, column=1, padx=10)

history_button = tk.Button(input_frame, text="Geçmiş", font=("Arial", 12), command=show_history, bg="#007bff", fg="white", padx=14, pady=5)
history_button.grid(row=1, column=2, padx=10)

clear_button = tk.Button(input_frame, text="Geçmişi Sil", font=("Arial", 12), command=clear_history, bg="#007bff", fg="white", padx=18, pady=5)
clear_button.grid(row=1, column=3, padx=10)


response_frame = tk.Frame(chatbot_frame, pady=20, padx=20)
response_frame.pack(fill="both", expand=True)

response_text = tk.Text(response_frame, font=("Arial", 12), wrap="word", bg="#eaf7ea", fg="#333", padx=10, pady=10)
response_text.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(response_frame, command=response_text.yview)
scrollbar.pack(side="right", fill="y")

response_text.config(yscrollcommand=scrollbar.set)
update_response("Cevap burada görünecek.")

if __name__ == '__main__':
    threading.Thread(target=start_flask).start()  # Flask uygulamasını arka planda başlat
    root.mainloop()

RAG_LLM.history.clear()
