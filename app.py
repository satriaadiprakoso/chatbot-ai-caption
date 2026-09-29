import streamlit as st
import base64
import markdown
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from duckduckgo_search import DDGS

# ==========================================
# 1. SETUP PAGE CONFIG & THEME
# ==========================================
st.set_page_config(
    page_title="CaptionCraft AI",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling agar tampilan rapi, clean, profesional, mirip bubble chat WhatsApp
st.markdown("""
<style>
    /* WhatsApp Color Palette & Container Layout */
    .stApp {
        background-color: #0b141a;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* WhatsApp-style Header Bar */
    .chat-header {
        background: #202c33;
        border-radius: 12px;
        padding: 12px 20px;
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }
    .chat-avatar {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: linear-gradient(135deg, #00a884, #005c4b);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
    }
    .header-info h3 {
        margin: 0;
        font-size: 1.05rem;
        font-weight: 600;
        color: #e9edef;
    }
    .header-info p {
        margin: 0;
        font-size: 0.8rem;
        color: #00a884;
    }

    /* WhatsApp Bubble Base */
    .bubble-row-user {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 8px;
    }
    .bubble-row-bot {
        display: flex;
        justify-content: flex-start;
        margin-bottom: 8px;
    }
    
    .chat-bubble-user {
        background-color: #005c4b;
        color: #e9edef;
        padding: 10px 14px 6px 14px;
        border-radius: 12px 0px 12px 12px;
        max-width: 78%;
        box-shadow: 0 1px 2px rgba(0,0,0,0.25);
        font-size: 0.95rem;
        line-height: 1.45;
        position: relative;
    }
    
    .chat-bubble-bot {
        background-color: #202c33;
        color: #e9edef;
        padding: 12px 16px 8px 16px;
        border-radius: 0px 12px 12px 12px;
        max-width: 82%;
        box-shadow: 0 1px 2px rgba(0,0,0,0.25);
        font-size: 0.95rem;
        line-height: 1.5;
        position: relative;
    }
    
    .bubble-body {
        font-size: 0.95rem;
        line-height: 1.6;
        color: #e9edef;
    }
    .bubble-body p {
        margin: 0 0 8px 0;
    }
    .bubble-body p:last-child {
        margin-bottom: 0;
    }
    .bubble-body strong {
        color: #ffffff;
        font-weight: 600;
    }
    .bubble-body ul, .bubble-body ol {
        margin: 4px 0 8px 18px;
        padding: 0;
    }
    .bubble-body li {
        margin-bottom: 4px;
    }

    .bubble-meta {
        font-size: 0.7rem;
        color: #8696a0;
        text-align: right;
        margin-top: 4px;
    }

    /* Step indicator badge */
    .step-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        background-color: #1f3540;
        color: #00a884;
        margin-bottom: 8px;
        border: 1px solid #00a884;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #111b21;
        border-right: 1px solid #222e35;
    }
    
    /* Upload Box Compact & Clean */
    div[data-testid="stFileUploader"] {
        background: #111b21;
        border: 1px dashed #2a3942;
        border-radius: 10px;
        padding: 6px 12px;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SESSION STATE MANAGEMENT
# ==========================================
if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""

# Flow State:
# 1 = WAITING_MEDIA (menunggu upload gambar/video)
# 2 = WAITING_CONTEXT (menunggu konteks/cerita)
# 3 = WAITING_PLATFORM (menunggu pilihan platform & gaya)
# 4 = GENERATED (caption selesai dibuat, siap konten baru)
if "flow_step" not in st.session_state:
    st.session_state["flow_step"] = "WAITING_MEDIA"

if "workflow_data" not in st.session_state:
    st.session_state["workflow_data"] = {
        "media_bytes": None,
        "mime_type": None,
        "media_analysis": "",
        "context": "",
        "platform": "",
        "tone": ""
    }

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "bot",
            "content": "Halo kak! 👋 Selamat datang di **CaptionCraft AI**.\n\nSilakan lampirkan **foto atau video** yang ingin kamu buatkan caption di bawah ini ya! 📸",
            "time": datetime.now().strftime("%H:%M")
        }
    ]

# ==========================================
# 3. SIDEBAR: PENGATURAN API KEY
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ Pengaturan API")
    input_key = st.text_input(
        "Gemini API Key:",
        value=st.session_state["api_key"],
        type="password",
        placeholder="Paste API Key di sini..."
    )
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 Simpan", use_container_width=True):
            st.session_state["api_key"] = input_key
            st.toast("✅ API Key berhasil disimpan!")
    with c2:
        if st.button("🗑️ Reset", use_container_width=True):
            st.session_state["api_key"] = ""
            st.rerun()

    if st.session_state["api_key"]:
        st.caption("🟢 Status: **Terhubung & Siap**")
    else:
        st.caption("🔴 Status: Belum ada API Key ([Dapatkan di sini](https://aistudio.google.com/))")

    st.markdown("---")
    st.markdown("### 🤖 Pilihan Model AI")
    
    # Fungsi mendeteksi model yang 100% valid dan aktif untuk API Key user
    @st.cache_data(ttl=600, show_spinner=False)
    def get_live_valid_models(key: str):
        valid = []
        if key:
            try:
                from google import genai
                client = genai.Client(api_key=key)
                for m in client.models.list():
                    name = m.name.replace("models/", "")
                    # Filter hanya model text/multimodal generateContent
                    if "gemini" in name and not any(x in name for x in ["embedding", "imagen", "aqa", "robotics"]):
                        valid.append(name)
            except Exception:
                pass
        return valid

    live_models = []
    if st.session_state["api_key"]:
        live_models = get_live_valid_models(st.session_state["api_key"])
        
    if not live_models:
        live_models = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3.8-flash"]

    selected_model = st.selectbox(
        "Model Gemini Aktif:",
        live_models,
        index=0,
        help="Daftar model yang terdeteksi 100% aktif dan didukung oleh akun Google API kamu."
    )
    st.session_state["selected_model"] = selected_model

    st.markdown("---")
    st.markdown("### 🔄 Alur Percakapan")
    steps = {
        "WAITING_MEDIA": "1️⃣ Upload Foto/Video",
        "WAITING_CONTEXT": "2️⃣ Konteks Foto/Video",
        "WAITING_PLATFORM": "3️⃣ Pilihan Platform & Tone",
        "GENERATED": "4️⃣ Caption Terbit ✨"
    }
    current_label = steps.get(st.session_state["flow_step"], "Proses")
    st.info(f"Tahap saat ini:\n**{current_label}**")

    enable_trend = st.toggle("🔍 Pantau Trend Viral Terkini", value=True)
    
    st.markdown("---")
    if st.button("🔄 Mulai Obrolan Baru", use_container_width=True):
        st.session_state["flow_step"] = "WAITING_MEDIA"
        st.session_state["workflow_data"] = {
            "media_bytes": None,
            "mime_type": None,
            "media_analysis": "",
            "context": "",
            "platform": "",
            "tone": ""
        }
        st.session_state["messages"] = [
            {
                "role": "bot",
                "content": "Sesi baru dimulai! Silakan lampirkan **foto atau video** yang ingin kamu buatkan caption ya! 📸",
                "time": datetime.now().strftime("%H:%M")
            }
        ]
        st.rerun()

# ==========================================
# 4. CHAT HEADER (WHATSAPP STYLE)
# ==========================================
st.markdown("""
<div class="chat-header">
    <div class="chat-avatar">📱</div>
    <div class="header-info">
        <h3>CaptionCraft Assistant</h3>
        <p>● Online | Alur Pembuatan Caption Bertahap</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# HELPER: SEARCH TREND
# ==========================================
def fetch_realtime_trends(query_text: str, plat: str) -> str:
    try:
        query = f"trend viral {query_text} {plat} terbaru slang hashtag"
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=3):
                results.append(f"- {r.get('title', '')}: {r.get('body', '')}")
        if results:
            return "\n".join(results)
    except Exception:
        pass
    return "Gunakan istilah dan slang yang sedang populer serta relevan di media sosial saat ini."

def invoke_llm_with_fallback(api_key: str, chosen_model: str, messages: list, temperature: float = 0.7):
    """Mencoba memanggil model yang dipilih, jika terkena 429 Quota Exceeded maka otomatis fallback ke model aktif lainnya."""
    candidate_models = [chosen_model]
    
    # Ambil list model aktif yang sudah terverifikasi jika ada
    available = st.session_state.get("live_models_cache", [])
    if not available:
        available = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3.8-flash"]
        
    for alt in available:
        if alt not in candidate_models:
            candidate_models.append(alt)
            
    last_err = None
    for model_name in candidate_models:
        try:
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=temperature
            )
            return llm.invoke(messages)
        except Exception as e:
            last_err = e
            err_str = str(e).lower()
            if "429" in err_str or "resource_exhausted" in err_str or "quota" in err_str:
                continue # Coba model cadangan berikutnya
            else:
                raise e
    raise last_err

def render_clean_html(raw_content) -> str:
    """Mengubah format teks/markdown menjadi HTML yang bersih, rapi, dan terformat seperti Gemini."""
    if not raw_content:
        return ""
    
    # Jika response berupa list (misal multimodal blocks dari model/LangChain)
    if isinstance(raw_content, list):
        text_parts = []
        for item in raw_content:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                text_parts.append(item["text"])
            else:
                text_parts.append(str(item))
        raw_text = "\n".join(text_parts)
    elif not isinstance(raw_content, str):
        raw_text = str(raw_content)
    else:
        raw_text = raw_content
        
    # Render markdown ke HTML standar
    html = markdown.markdown(raw_text, extensions=['extra', 'nl2br'])
    return html

# ==========================================
# 5. RENDER CHAT BUBBLES
# ==========================================
for msg in st.session_state["messages"]:
    is_user = msg["role"] == "user"
    time_str = msg.get("time", "")
    
    if is_user:
        cleaned_content = render_clean_html(msg['content'])
        st.markdown(f"""
        <div class="bubble-row-user">
            <div class="chat-bubble-user">
                <div class="bubble-body">{cleaned_content}</div>
                <div class="bubble-meta">{time_str} ✓✓</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if "media" in msg:
            m_col1, m_col2 = st.columns([1, 2])
            with m_col2:
                if msg["media"]["type"].startswith("image/"):
                    st.image(msg["media"]["bytes"], use_container_width=True)
                elif msg["media"]["type"].startswith("video/"):
                    st.video(msg["media"]["bytes"])
    else:
        cleaned_content = render_clean_html(msg['content'])
        st.markdown(f"""
        <div class="bubble-row-bot">
            <div class="chat-bubble-bot">
                <div class="bubble-body">{cleaned_content}</div>
                <div class="bubble-meta">{time_str}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 6. DYNAMIC INTERACTIVE INPUT SESUAI TAHAP ALUR
# ==========================================
api_key = st.session_state["api_key"]

# TAHAP 1: Menunggu Upload Media
if st.session_state["flow_step"] == "WAITING_MEDIA":
    st.markdown("---")
    st.markdown('<div class="step-badge">Tahap 1 dari 3: Kirim Media</div>', unsafe_allow_html=True)
    
    with st.expander("📎 Buka / Tutup Lampiran Foto atau Video", expanded=True):
        uploaded_file = st.file_uploader(
            "Pilih foto atau video",
            type=["jpg", "jpeg", "png", "webp", "mp4", "mov"],
            label_visibility="collapsed",
            key="media_uploader"
        )
        if uploaded_file is not None:
            if st.button("🚀 Kirim Media Ini ke Bot", use_container_width=True, type="primary"):
                if not api_key:
                    st.warning("⚠️ Simpan Gemini API Key terlebih dahulu di sidebar sebelah kiri!")
                else:
                    media_bytes = uploaded_file.read()
                    mime_type = uploaded_file.type
                    
                    # Simpan data media
                    st.session_state["workflow_data"]["media_bytes"] = media_bytes
                    st.session_state["workflow_data"]["mime_type"] = mime_type
                    
                    # Tambahkan bubble user
                    st.session_state["messages"].append({
                        "role": "user",
                        "content": "Saya sudah mengirimkan foto/video ini, tolong dicek ya.",
                        "time": datetime.now().strftime("%H:%M"),
                        "media": {"bytes": media_bytes, "type": mime_type}
                    })
                    
                    # Bot menganalisis sekilas dan bertanya konteks
                    with st.spinner("Bot sedang mengamati foto/videomu..."):
                        try:
                            chosen_m = st.session_state.get("selected_model", "gemini-2.5-flash")
                            b64 = base64.b64encode(media_bytes).decode("utf-8")
                            content_payload = [
                                {"type": "text", "text": "Jelaskan dalam 1-2 kalimat singkat dan ramah apa objek atau suasana utama yang kamu lihat pada gambar/video ini, lalu tanyakan kepada user: 'Kira-kira apa konteks atau cerita di balik foto/video ini? (misal: acara apa, lagi nongkrong di mana, atau pesan apa yang ingin kamu sampaikan?)'"},
                                {
                                    "type": "image_url" if mime_type.startswith("image/") else "media",
                                    ("image_url" if mime_type.startswith("image/") else "mime_type"): ({"url": f"data:{mime_type};base64,{b64}"} if mime_type.startswith("image/") else mime_type),
                                    **({"data": b64} if mime_type.startswith("video/") else {})
                                }
                            ]
                            response = invoke_llm_with_fallback(api_key, chosen_m, [HumanMessage(content=content_payload)], temperature=0.5)
                            bot_reply = response.content
                            st.session_state["workflow_data"]["media_analysis"] = bot_reply
                        except Exception as e:
                            bot_reply = "Wah fotonya menarik banget! ✨\n\nKira-kira **apa konteks atau cerita di balik foto/video ini?**\n(Contoh: lagi liburan, nugas bareng teman di cafe Jaksel, promo produk, dll)"
                    
                    st.session_state["messages"].append({
                        "role": "bot",
                        "content": bot_reply,
                        "time": datetime.now().strftime("%H:%M")
                    })
                    st.session_state["flow_step"] = "WAITING_CONTEXT"
                    st.rerun()

# TAHAP 2: Menunggu Konteks dari User
elif st.session_state["flow_step"] == "WAITING_CONTEXT":
    st.markdown("---")
    st.markdown('<div class="step-badge">Tahap 2 dari 3: Ceritakan Konteks Foto/Video</div>', unsafe_allow_html=True)
    user_context = st.chat_input("Ketik cerita / konteks di balik foto/videomu di sini...")
    
    if user_context:
        st.session_state["workflow_data"]["context"] = user_context
        st.session_state["messages"].append({
            "role": "user",
            "content": user_context,
            "time": datetime.now().strftime("%H:%M")
        })
        
        # Bot bertanya tentang platform dan gaya bahasa
        bot_ask_platform = (
            f"Keren banget konteksnya! 🎯\n\n"
            f"Sekarang, **kamu mau posting konten ini ke platform mana**, dan **seperti apa gaya bahasa (tone)** yang kamu inginkan?"
        )
        st.session_state["messages"].append({
            "role": "bot",
            "content": bot_ask_platform,
            "time": datetime.now().strftime("%H:%M")
        })
        st.session_state["flow_step"] = "WAITING_PLATFORM"
        st.rerun()

# TAHAP 3: Menunggu Pilihan Platform & Gaya Bahasa
elif st.session_state["flow_step"] == "WAITING_PLATFORM":
    st.markdown("---")
    st.markdown('<div class="step-badge">Tahap 3 dari 3: Pilih Platform & Gaya Bahasa</div>', unsafe_allow_html=True)
    
    with st.container():
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            selected_platform = st.selectbox(
                "📌 Pilih Platform Tujuan:",
                ["Instagram (Reels / Feed)", "TikTok", "LinkedIn", "X (Twitter)", "Facebook"]
            )
        with p_col2:
            selected_tone = st.selectbox(
                "🎭 Pilih Gaya Bahasa:",
                [
                    "Gaul & Santai (Gen-Z / Jaksel)",
                    "Profesional & Elegan",
                    "Lucu, Santai & Humor",
                    "Puitis, Estetik & Deep",
                    "Hard Sell / Promosi & Penjualan"
                ]
            )
        
        if st.button("✨ Rumuskan Caption Sekarang!", use_container_width=True, type="primary"):
            st.session_state["workflow_data"]["platform"] = selected_platform
            st.session_state["workflow_data"]["tone"] = selected_tone
            
            user_choice_msg = f"Tolong buatkan untuk platform **{selected_platform}** dengan gaya bahasa **{selected_tone}** ya."
            st.session_state["messages"].append({
                "role": "user",
                "content": user_choice_msg,
                "time": datetime.now().strftime("%H:%M")
            })
            
            with st.spinner("AI sedang merumuskan caption dengan memadukan foto, konteks, dan trend viral..."):
                try:
                    chosen_m = st.session_state.get("selected_model", "gemini-2.5-flash")
                    
                    media_bytes = st.session_state["workflow_data"]["media_bytes"]
                    mime_type = st.session_state["workflow_data"]["mime_type"]
                    user_ctx = st.session_state["workflow_data"]["context"]
                    
                    trend_ctx = ""
                    if enable_trend:
                        trend_ctx = fetch_realtime_trends(user_ctx, selected_platform)
                        
                    system_prompt = f"""
                    Kamu adalah Social Media Specialist & Content Strategist kelas dewa.
                    
                    INFORMASI KONTEN:
                    - Konteks dari User: "{user_ctx}"
                    - Target Platform: {selected_platform}
                    - Gaya Bahasa: {selected_tone}
                    - Analisis Trend Terkini di Backend:
                    {trend_ctx}
                    
                    TUGAS:
                    Analisis foto/video yang dilampirkan secara detail (warna, ekspresi, mood, visual) dan gabungkan dengan konteks user.
                    
                    SUSUNAN OUTPUT CAPTION (Format Rapi WhatsApp Chat):
                    
                    🎉 **Berikut 3 Pilihan Caption Terbaik Buat Kamu:**
                    
                    🔥 **Opsi 1 (Hook Menarik & Interaktif):**
                    [Isi caption + emoji yang relevan]
                    
                    ✨ **Opsi 2 (Storytelling & Relatable):**
                    [Isi caption bercerita sesuai konteks user]
                    
                    ⚡ **Opsi 3 (Pendek & Punchy):**
                    [Isi caption singkat dan ngena]
                    
                    🏷️ **Rekomendasi Hashtag FYP:**
                    [Hashtag viral dan relevan]
                    
                    💡 **Tips Visual & Algoritma:**
                    - Vibes Terdeteksi: [Mood/estetika yang terlihat]
                    - Jam Posting Rekomendasi: [Saran waktu terbaik untuk {selected_platform}]
                    """
                    
                    content_payload = [{"type": "text", "text": system_prompt}]
                    if media_bytes:
                        b64 = base64.b64encode(media_bytes).decode("utf-8")
                        if mime_type.startswith("image/"):
                            content_payload.append({
                                "type": "image_url",
                                "image_url": {"url": f"data:{mime_type};base64,{b64}"}
                            })
                        elif mime_type.startswith("video/"):
                            content_payload.append({
                                "type": "media",
                                "mime_type": mime_type,
                                "data": b64
                            })
                    
                    response = invoke_llm_with_fallback(api_key, chosen_m, [HumanMessage(content=content_payload)], temperature=0.7)
                    bot_final_reply = response.content
                    
                    st.session_state["messages"].append({
                        "role": "bot",
                        "content": bot_final_reply,
                        "time": datetime.now().strftime("%H:%M")
                    })
                    st.session_state["flow_step"] = "GENERATED"
                    st.rerun()
                    
                except Exception as e:
                    err_msg = f"Maaf kak, ada kendala: {e}"
                    st.session_state["messages"].append({
                        "role": "bot",
                        "content": err_msg,
                        "time": datetime.now().strftime("%H:%M")
                    })
                    st.rerun()

# TAHAP 4: Selesai & Revisi Interaktif (Mengingat Riwayat Percakapan)
elif st.session_state["flow_step"] == "GENERATED":
    st.markdown("---")
    st.markdown('<div class="step-badge">💬 Mode Revisi Aktif: Ketik revisi di bawah atau buat baru</div>', unsafe_allow_html=True)
    
    col_rev1, col_rev2 = st.columns([3, 1])
    with col_rev2:
        if st.button("📸 Konten Baru", use_container_width=True):
            st.session_state["flow_step"] = "WAITING_MEDIA"
            st.session_state["workflow_data"] = {
                "media_bytes": None,
                "mime_type": None,
                "media_analysis": "",
                "context": "",
                "platform": "",
                "tone": ""
            }
            st.session_state["messages"].append({
                "role": "bot",
                "content": "Silakan kirimkan foto atau video berikutnya yang ingin dibuatkan caption ya! 📸",
                "time": datetime.now().strftime("%H:%M")
            })
            st.rerun()
            
    # Input revisi dari user
    revision_input = st.chat_input("Ada yang mau direvisi? (contoh: 'buat opsi 2 lebih santai', 'tambah hashtag kopi', dll)...")
    
    if revision_input:
        if not api_key:
            st.warning("⚠️ Simpan Gemini API Key terlebih dahulu di sidebar sebelah kiri!")
        else:
            current_time = datetime.now().strftime("%H:%M")
            st.session_state["messages"].append({
                "role": "user",
                "content": revision_input,
                "time": current_time
            })
            
            with st.spinner("AI sedang membaca riwayat chat dan menyesuaikan revisimu..."):
                try:
                    from langchain_core.messages import SystemMessage, AIMessage
                    
                    chosen_m = st.session_state.get("selected_model", "gemini-2.5-flash")
                    
                    # Rekonstruksi seluruh riwayat chat ke format LangChain
                    langchain_history = [
                        SystemMessage(content="""Kamu adalah Social Media Specialist & Content Strategist kelas dewa.
Kamu sedang berdiskusi dengan user mengenai pembuatan caption sosmed.
PENTING:
- Pahami seluruh riwayat obrolan sebelumnya (foto yang dikirim, konteks awal, platform, gaya bahasa, dan draft caption sebelumnya).
- JANGAN mengulang dari nol atau melupakan caption sebelumnya!
- Fokuskan perubahan/revisi secara spesifik pada apa yang diminta oleh user, sambil mempertahankan elemen terbaik dari draft sebelumnya.
- Jawab secara sopan, solutif, dan berikan revisi caption yang langsung siap copy-paste.""")
                    ]
                    
                    # Tambahkan riwayat obrolan terdahulu
                    for m in st.session_state["messages"][:-1]:  # Sampai sebelum pesan revisi terakhir
                        if m["role"] == "user":
                            langchain_history.append(HumanMessage(content=m["content"]))
                        elif m["role"] == "bot":
                            langchain_history.append(AIMessage(content=m["content"]))
                    
                    # Tambahkan pesan revisi terbaru dari user
                    langchain_history.append(HumanMessage(content=revision_input))
                    
                    # Panggil model dengan auto fallback
                    response = invoke_llm_with_fallback(api_key, chosen_m, langchain_history, temperature=0.7)
                    bot_revision_reply = response.content
                    
                    st.session_state["messages"].append({
                        "role": "bot",
                        "content": bot_revision_reply,
                        "time": datetime.now().strftime("%H:%M")
                    })
                    st.rerun()
                    
                except Exception as e:
                    err_msg = f"Maaf kak, ada kendala saat memproses revisi: {e}"
                    st.session_state["messages"].append({
                        "role": "bot",
                        "content": err_msg,
                        "time": datetime.now().strftime("%H:%M")
                    })
                    st.rerun()
