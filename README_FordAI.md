
# 🤖 FordAI Assistant – Chatbot for Production Line Support

This repository contains a production-ready intelligent chatbot system developed to support Ford Otosan’s manufacturing staff by enabling natural language interaction with their production and maintenance data. The system integrates Google Gemini LLM, Chroma Vector Database, and Google OAuth authentication.

## 📌 Project Overview

The chatbot is designed to help workers query historical production errors and intervention records efficiently. The system:

- Uses **LLM + RAG architecture**
- Handles **authentication via Google accounts**
- Embeds and stores production data in **Chroma Vector DB**
- Provides responses using **Google Gemini API**
- Offers an interactive **Tkinter GUI** with query history and clearing options

---

## 🛠️ Technologies Used

- **Python** (Tkinter, Flask, Threading)
- **LLM**: Google Gemini via `google.generativeai`
- **Vector DB**: ChromaDB
- **Embeddings**: `sentence-transformers`
- **Authentication**: Google OAuth
- **Similarity Matching**: `cosine_similarity` (from `sklearn`)

---

## 💡 System Architecture

- **Frontend**: Tkinter GUI
- **Backend**: Flask server running in parallel with UI (via Threading)
- **Data**: Extracted from Excel, cleaned, embedded, and categorized
- **Storage**: Vectorized using Sentence Transformers, indexed in ChromaDB
- **Query Flow**: 
    1. User inputs a query via GUI
    2. Query is vectorized → searched in ChromaDB
    3. Relevant document is retrieved
    4. Google Gemini LLM generates response
    5. Result is displayed on UI

---

## ✅ Features

- Google OAuth login support
- Error handling with user-friendly feedback
- Query history + "Clear History" button
- Categorization of equipment errors
- Automatic data cleaning and transformation
- Modular design for future DB or LLM integrations

---

### 🔧 Requirements

```bash
pip install flask chromadb sentence-transformers google-generativeai pandas sklearn
```

### ▶️ Start the App

```bash
python chatbot.py
```

*Make sure to run it with proper Google API credentials and ChromaDB config paths set.*

---


## 👥 Team Members

- **Kadriye Harmancı** – Database & API integration
- **Abdullah Taha Aydın** – Vector DB and RAG system design
- **Elif Suna Gegin** – Requirements analysis and database modeling
- **Umay Ece Mantar** – UI design and documentation

> 💼 Developed for the course **Database Management Systems**, Fall 2024-2025, Eskisehir Osmangazi University  
> 🏢 With collaboration from **Ford Otosan** (Contact: Ömer Ersoy Alanyalı)

---

## 🔮 Future Improvements

- Dockerization for deployment
- Admin dashboard with analytics
- Integration of fine-tuned open-source LLMs
- Real-time retraining pipeline for feedback-based refinement

---

## 🧾 License

This project was developed under educational collaboration with Ford Otosan. Any production use must comply with the agreed NDA and data sharing policies.

