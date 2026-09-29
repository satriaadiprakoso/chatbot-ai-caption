# 📱 CaptionCraft AI Chatbot

Asisten Chatbot Cerdas berbasis **Multimodal Vision (Foto/Video)**, **Real-Time Trend Search**, dan **Multi-Turn Interactive Chat History** untuk menghasilkan caption media sosial yang viral, menarik, dan terstruktur rapi.

---

## ✨ Fitur Unggulan

1. **💬 WhatsApp-Style Chat UI**: Antarmuka interaktif yang rapi, clean, dan mudah dipahami oleh siapa pun.
2. **📸 Analisis Multimodal (Foto & Video)**: Menggunakan model Gemini Vision untuk mendeteksi suasana, objek visual, dan mood dari media yang diunggah secara akurat.
3. **🔍 Real-Time Trend Analysis**: Mengambil referensi tren, slang, dan hashtag viral secara backend terkini.
4. **🧠 Memory & Mode Revisi Interaktif**: Mengingat seluruh riwayat percakapan sehingga pengguna dapat meminta revisi spesifik tanpa mengulang dari nol.
5. **⚙️ Manajemen Model & Fallback Cerdas**: Mendeteksi model aktif secara real-time dari Google AI Studio dan otomatis berpindah model jika kuota rate limit (429) tercapai.

---

## 🛠️ Instalasi & Menjalankan Lokal

1. **Clone repository ini:**
   ```bash
   git clone https://github.com/satriaadiprakoso/chatbot-ai-caption.git
   cd chatbot-ai-caption
   ```

2. **Install dependensi:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Jalankan aplikasi:**
   ```bash
   python -m streamlit run app.py
   ```

4. **Konfigurasi API Key:**
   - Masukkan Google Gemini API Key di sidebar dan klik **Simpan**. API Key gratis bisa didapatkan di [Google AI Studio](https://aistudio.google.com/).
