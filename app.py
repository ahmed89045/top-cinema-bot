import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
import json
import os
import uuid
import requests

# ==================================================================
# 0. إعدادات عامة وملفات التخزين
# ==================================================================
WATCHLIST_FILE  = "watchlist.json"
CONVERSATIONS_FILE = "conversations.json"

st.set_page_config(page_title="Mouven AI", page_icon="OIP.webp", layout="wide")


def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ==================================================================
# 1. نظام التصميم الكامل — CSS
# ==================================================================
DESIGN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600&family=Inter:wght@300;400;500;600&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background: #080810 !important;
    color: #E8E8F0 !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header, .stAppDeployButton,
[data-testid="stToolbar"] { display: none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0D0D1A !important;
    border-right: 1px solid #1C1C2E !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 2rem;
}

/* ── Sidebar logo ── */
.mv-sidebar-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0 1rem 1.5rem 1rem;
    border-bottom: 1px solid #1C1C2E;
    margin-bottom: 1.2rem;
}
.mv-logo-text {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.5rem;
    font-weight: 600;
    color: #C8A96E;
    letter-spacing: 0.08em;
}

/* ── Sidebar section labels ── */
.mv-section-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #4A4A6A;
    padding: 0 1rem;
    margin-bottom: 0.5rem;
    margin-top: 1rem;
}

/* ── Divider ── */
.mv-divider {
    border: none;
    border-top: 1px solid #1C1C2E;
    margin: 1.2rem 0;
}

/* ── Chat history item ── */
.mv-chat-item {
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 0.8rem;
    color: #9090B0;
    cursor: pointer;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 2px;
    border: 1px solid transparent;
    transition: all 0.2s;
}
.mv-chat-item:hover {
    background: #14142A;
    border-color: #2A2A4A;
    color: #C8A96E;
}

/* ── Watchlist card ── */
.mv-watch-card {
    background: #11111E;
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 8px;
    border-left: 3px solid #C8A96E;
    display: flex;
    flex-direction: column;
    gap: 3px;
}
.mv-watch-card.done {
    border-left-color: #4CAF82;
    opacity: 0.75;
}
.mv-watch-title {
    font-size: 0.88rem;
    font-weight: 500;
    color: #E8E8F0;
}
.mv-watch-status {
    font-size: 0.72rem;
    color: #5A5A7A;
    letter-spacing: 0.04em;
}

/* ── Cast card ── */
.mv-cast-card {
    text-align: center;
    font-size: 0.72rem;
    color: #9090B0;
    line-height: 1.4;
}
.mv-cast-card img {
    border-radius: 8px;
    margin-bottom: 5px;
    width: 70px;
    object-fit: cover;
}

/* ── Main area headings ── */
h1 {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 2.4rem !important;
    font-weight: 300 !important;
    color: #F0F0FA !important;
    letter-spacing: 0.04em !important;
    margin-bottom: 0.2rem !important;
}
h2, h3 {
    font-family: 'Cormorant Garamond', serif !important;
    color: #C8A96E !important;
    font-weight: 400 !important;
}
p, li, span { color: #9090B0; }

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: #11111E !important;
    border-radius: 12px !important;
    border: 1px solid #1C1C2E !important;
    padding: 1rem 1.2rem !important;
    margin-bottom: 0.6rem !important;
}
[data-testid="stChatMessage"] p { color: #D8D8EC !important; }

/* ── Chat input bar ── */
[data-testid="stChatInput"] textarea {
    background: #11111E !important;
    border: 1px solid #2A2A4A !important;
    border-radius: 12px !important;
    color: #E8E8F0 !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #C8A96E !important;
    box-shadow: 0 0 0 2px rgba(200,169,110,0.15) !important;
}
[data-testid="stChatInput"] button {
    background: #C8A96E !important;
    border-radius: 8px !important;
}

/* ── Buttons ── */
.stButton > button {
    background: transparent !important;
    border: 1px solid #2A2A4A !important;
    color: #9090B0 !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.03em !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    border-color: #C8A96E !important;
    color: #C8A96E !important;
    background: rgba(200,169,110,0.06) !important;
}

/* ── Gold CTA button ── */
.mv-btn-gold > button {
    background: #C8A96E !important;
    border-color: #C8A96E !important;
    color: #080810 !important;
    font-weight: 600 !important;
}
.mv-btn-gold > button:hover {
    background: #D4B87C !important;
    color: #080810 !important;
}

/* ── Text inputs in sidebar ── */
.stTextInput input {
    background: #11111E !important;
    border: 1px solid #2A2A4A !important;
    border-radius: 8px !important;
    color: #E8E8F0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
}
.stTextInput input:focus {
    border-color: #C8A96E !important;
    box-shadow: 0 0 0 2px rgba(200,169,110,0.12) !important;
}
.stTextInput label { color: #5A5A7A !important; font-size: 0.75rem !important; }

/* ── Radio buttons ── */
.stRadio label { color: #7A7A9A !important; font-size: 0.8rem !important; }
[data-testid="stRadio"] > div { gap: 8px !important; }

/* ── Toggle ── */
.stToggle label { color: #7A7A9A !important; font-size: 0.8rem !important; }

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #11111E !important;
    border: 1px dashed #2A2A4A !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
}
[data-testid="stFileUploader"] label { color: #5A5A7A !important; font-size: 0.75rem !important; }

/* ── Audio input ── */
[data-testid="stAudioInput"] {
    background: #11111E !important;
    border-radius: 10px !important;
    border: 1px solid #2A2A4A !important;
}

/* ── Expander ── */
details {
    background: #11111E !important;
    border: 1px solid #1C1C2E !important;
    border-radius: 8px !important;
    padding: 4px 8px !important;
    margin-top: 4px !important;
}
summary { color: #5A5A7A !important; font-size: 0.78rem !important; }

/* ── Info / warning boxes ── */
[data-testid="stInfo"] {
    background: #11111E !important;
    border: 1px solid #2A2A4A !important;
    border-radius: 8px !important;
    color: #6A6A8A !important;
}
[data-testid="stWarning"] {
    border-radius: 8px !important;
}

/* ── Form submit button ── */
[data-testid="stFormSubmitButton"] > button {
    background: #C8A96E !important;
    border-color: #C8A96E !important;
    color: #080810 !important;
    font-weight: 600 !important;
    width: 100% !important;
    margin-top: 0.5rem !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2A2A4A; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #C8A96E; }

/* ── Language selection screen ── */
.mv-lang-screen {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1rem;
}
.mv-lang-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 3.5rem;
    font-weight: 300;
    color: #F0F0FA;
    letter-spacing: 0.12em;
    text-align: center;
}
.mv-lang-sub {
    font-size: 0.85rem;
    color: #4A4A6A;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    text-align: center;
    margin-bottom: 1.5rem;
}
.mv-film-reel {
    margin-bottom: 1rem;
}

/* ── Subtitle in main area ── */
.mv-subtitle {
    font-size: 0.88rem;
    color: #4A4A6A;
    letter-spacing: 0.06em;
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid #1C1C2E;
}

/* ── Rating display ── */
.mv-rating {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #11111E;
    border: 1px solid #2A2A4A;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 0.8rem;
    color: #C8A96E;
    font-weight: 500;
}

/* ── Details section ── */
.mv-detail-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #4A4A6A;
    margin-bottom: 6px;
    margin-top: 14px;
}
</style>
"""

# SVG: film reel logo for language screen
FILM_REEL_SVG = """
<svg width="72" height="72" viewBox="0 0 72 72" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="36" cy="36" r="34" stroke="#C8A96E" stroke-width="1.5" fill="none" opacity="0.5"/>
  <circle cx="36" cy="36" r="22" stroke="#C8A96E" stroke-width="1.5" fill="none"/>
  <circle cx="36" cy="36" r="6" fill="#C8A96E" opacity="0.8"/>
  <circle cx="36" cy="14" r="4" fill="#1C1C2E" stroke="#C8A96E" stroke-width="1"/>
  <circle cx="36" cy="58" r="4" fill="#1C1C2E" stroke="#C8A96E" stroke-width="1"/>
  <circle cx="14" cy="36" r="4" fill="#1C1C2E" stroke="#C8A96E" stroke-width="1"/>
  <circle cx="58" cy="36" r="4" fill="#1C1C2E" stroke="#C8A96E" stroke-width="1"/>
  <circle cx="20.1" cy="20.1" r="4" fill="#1C1C2E" stroke="#C8A96E" stroke-width="1"/>
  <circle cx="51.9" cy="51.9" r="4" fill="#1C1C2E" stroke="#C8A96E" stroke-width="1"/>
  <circle cx="51.9" cy="20.1" r="4" fill="#1C1C2E" stroke="#C8A96E" stroke-width="1"/>
  <circle cx="20.1" cy="51.9" r="4" fill="#1C1C2E" stroke="#C8A96E" stroke-width="1"/>
</svg>
"""

# SVG: small icon for sidebar logo
SIDEBAR_ICON_SVG = """
<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="14" cy="14" r="13" stroke="#C8A96E" stroke-width="1.2" fill="none"/>
  <circle cx="14" cy="14" r="8" stroke="#C8A96E" stroke-width="1.2" fill="none"/>
  <circle cx="14" cy="14" r="2.5" fill="#C8A96E"/>
  <circle cx="14" cy="6" r="1.8" fill="#C8A96E" opacity="0.6"/>
  <circle cx="14" cy="22" r="1.8" fill="#C8A96E" opacity="0.6"/>
  <circle cx="6" cy="14" r="1.8" fill="#C8A96E" opacity="0.6"/>
  <circle cx="22" cy="14" r="1.8" fill="#C8A96E" opacity="0.6"/>
</svg>
"""

# SVG: empty watchlist illustration
EMPTY_LIST_SVG = """
<svg width="80" height="80" viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="12" y="18" width="56" height="44" rx="4" stroke="#2A2A4A" stroke-width="1.5" fill="none"/>
  <rect x="12" y="18" width="56" height="10" rx="4" fill="#1C1C2E"/>
  <circle cx="20" cy="23" r="2" fill="#C8A96E" opacity="0.5"/>
  <circle cx="28" cy="23" r="2" fill="#4A4A6A"/>
  <circle cx="36" cy="23" r="2" fill="#4A4A6A"/>
  <line x1="22" y1="38" x2="58" y2="38" stroke="#2A2A4A" stroke-width="1.5" stroke-linecap="round"/>
  <line x1="22" y1="48" x2="50" y2="48" stroke="#2A2A4A" stroke-width="1.5" stroke-linecap="round"/>
  <line x1="22" y1="58" x2="44" y2="58" stroke="#2A2A4A" stroke-width="1.5" stroke-linecap="round"/>
</svg>
"""

# ==================================================================
# 2. اللغات
# ==================================================================
LANGS = {
    "ar": {
        "flag": "AR", "name": "العربية", "tmdb": "ar", "tts": "ar-EG",
        "app_title": "Mouven AI",
        "subtitle": "نسيت اسم فيلم؟ احكيلي قصته أو الممثلين وأنا أجهزهولك",
        "chat_placeholder": "اكتب هنا...",
        "watchlist_header": "قائمتي",
        "watchlist_caption": "الأفلام والمسلسلات اللي عايز تتفرج عليها أو شفتها",
        "add_button": "اضف للقائمة",
        "status_watch": "عايز أتفرج عليه",
        "status_done": "شفته",
        "empty_watchlist": "القائمة فاضية — ابدأ بأول فيلم",
        "details_button": "تفاصيل",
        "chats_header": "المحادثات",
        "new_chat": "محادثة جديدة",
        "upload_label": "ارفع صورة للتعرف على الفيلم",
        "voice_label": "سجل سؤالك",
        "speak_toggle": "صوت المساعد",
        "name_field": "اسم الفيلم أو المسلسل",
        "status_field": "الحالة",
        "no_results": "لم نجد معلومات عن هذا العنوان",
        "story": "القصة",
        "cast": "الممثلون",
        "rating": "التقييم",
        "choose_lang": "اختر لغتك",
        "system_instruction": (
            "أنت مساعد ذكي مخصص لموقع أفلام اسمه Mouven AI."
            "وظيفتك مساعدة المستخدم في معرفة اسم الفيلم الذي يريده."
            "تتحدث بالعامية المصرية الودودة والذكية جداً."
            "إذا ذكر المستخدم تفاصيل صغيرة قم بتخمين الفيلم."
            "لا تعطي الإجابة فوراً إذا كانت التفاصيل ناقصة بل اسأله أسئلة ذكية ومسلية "
            "حتى تصل للاسم الصحيح وعندما تتأكد قل له اسمه واكتب نبذة مشوقة عنه."
            "لو استلمت صورة سكرين شوت من فيلم أو صوت حاول تتعرف على الفيلم بنفس الأسلوب."
        ),
    },
    "en": {
        "flag": "EN", "name": "English", "tmdb": "en", "tts": "en-US",
        "app_title": "Mouven AI",
        "subtitle": "Forgot a movie name? Describe the plot or cast and I'll find it.",
        "chat_placeholder": "Type here...",
        "watchlist_header": "My List",
        "watchlist_caption": "Titles you want to watch or have already seen",
        "add_button": "Add to list",
        "status_watch": "Want to watch",
        "status_done": "Watched",
        "empty_watchlist": "Your list is empty — add your first title",
        "details_button": "Details",
        "chats_header": "Chats",
        "new_chat": "New chat",
        "upload_label": "Upload a screenshot to identify the movie",
        "voice_label": "Record your question",
        "speak_toggle": "Assistant voice",
        "name_field": "Movie or show title",
        "status_field": "Status",
        "no_results": "No information found for this title",
        "story": "Plot",
        "cast": "Cast",
        "rating": "Rating",
        "choose_lang": "Choose your language",
        "system_instruction": (
            "You are a smart assistant for a movie website called Mouven AI. "
            "Your main job is helping the user figure out the name of a movie or show. "
            "Speak in a friendly, witty, conversational tone in English. "
            "If the user gives small clues try to guess the title. "
            "Don't answer immediately if the details are incomplete; ask smart fun follow-up questions "
            "until you are confident, then reveal the title with an exciting short blurb. "
            "If you receive a screenshot or audio, try to identify the movie the same way."
        ),
    },
    "fr": {
        "flag": "FR", "name": "Français", "tmdb": "fr", "tts": "fr-FR",
        "app_title": "Mouven AI",
        "subtitle": "Vous avez oublié le nom d'un film ? Décrivez l'histoire ou les acteurs.",
        "chat_placeholder": "Écrivez ici...",
        "watchlist_header": "Ma liste",
        "watchlist_caption": "Films et séries à voir ou déjà vus",
        "add_button": "Ajouter à la liste",
        "status_watch": "À regarder",
        "status_done": "Vu",
        "empty_watchlist": "Votre liste est vide — ajoutez un premier titre",
        "details_button": "Détails",
        "chats_header": "Discussions",
        "new_chat": "Nouvelle discussion",
        "upload_label": "Importez une capture d'écran pour identifier le film",
        "voice_label": "Enregistrez votre question",
        "speak_toggle": "Voix de l'assistant",
        "name_field": "Titre du film ou de la série",
        "status_field": "Statut",
        "no_results": "Aucune information trouvée pour ce titre",
        "story": "Histoire",
        "cast": "Acteurs",
        "rating": "Note",
        "choose_lang": "Choisissez votre langue",
        "system_instruction": (
            "Vous êtes un assistant intelligent pour un site de films appelé Mouven AI. "
            "Votre rôle est d'aider l'utilisateur à retrouver le nom d'un film ou d'une série. "
            "Parlez en français avec un ton amical et vif. "
            "Si l'utilisateur donne de petits indices devinez le titre. "
            "Si les détails sont insuffisants posez des questions amusantes avant de répondre "
            "puis révélez le titre avec un court résumé captivant. "
            "Si vous recevez une capture d'écran ou un audio essayez d'identifier le film."
        ),
    },
    "pt": {
        "flag": "PT", "name": "Português", "tmdb": "pt-BR", "tts": "pt-BR",
        "app_title": "Mouven AI",
        "subtitle": "Esqueceu o nome de um filme? Descreva a história ou os atores.",
        "chat_placeholder": "Digite aqui...",
        "watchlist_header": "Minha lista",
        "watchlist_caption": "Filmes e séries para assistir ou já assistidos",
        "add_button": "Adicionar à lista",
        "status_watch": "Quero assistir",
        "status_done": "Já assisti",
        "empty_watchlist": "Sua lista está vazia — adicione o primeiro título",
        "details_button": "Detalhes",
        "chats_header": "Conversas",
        "new_chat": "Nova conversa",
        "upload_label": "Envie uma captura de tela para identificar o filme",
        "voice_label": "Grave sua pergunta",
        "speak_toggle": "Voz do assistente",
        "name_field": "Nome do filme ou série",
        "status_field": "Status",
        "no_results": "Nenhuma informação encontrada para este título",
        "story": "Enredo",
        "cast": "Elenco",
        "rating": "Avaliação",
        "choose_lang": "Escolha seu idioma",
        "system_instruction": (
            "Você é um assistente inteligente para um site de filmes chamado Mouven AI. "
            "Sua função é ajudar o usuário a descobrir o nome de um filme ou série. "
            "Fale em português do Brasil com tom amigável e animado. "
            "Se o usuário der pequenas pistas tente adivinhar o título. "
            "Se os detalhes forem insuficientes faça perguntas inteligentes e divertidas "
            "depois revele o título com um resumo envolvente. "
            "Se receber captura de tela ou áudio tente identificar o filme."
        ),
    },
    "hi": {
        "flag": "HI", "name": "हिन्दी", "tmdb": "hi", "tts": "hi-IN",
        "app_title": "Mouven AI",
        "subtitle": "किसी फिल्म का नाम भूल गए? कहानी या कलाकारों के बारे में बताएं।",
        "chat_placeholder": "यहाँ लिखें...",
        "watchlist_header": "मेरी सूची",
        "watchlist_caption": "वो फिल्में और शोज़ जो देखने हैं या देख चुके हैं",
        "add_button": "सूची में जोड़ें",
        "status_watch": "देखना है",
        "status_done": "देख लिया",
        "empty_watchlist": "सूची खाली है — पहली फिल्म जोड़ें",
        "details_button": "विवरण",
        "chats_header": "बातचीत",
        "new_chat": "नई बातचीत",
        "upload_label": "फिल्म पहचानने के लिए स्क्रीनशॉट अपलोड करें",
        "voice_label": "अपना सवाल रिकॉर्ड करें",
        "speak_toggle": "असिस्टेंट की आवाज़",
        "name_field": "फिल्म या शो का नाम",
        "status_field": "स्थिति",
        "no_results": "इस शीर्षक के बारे में जानकारी नहीं मिली",
        "story": "कहानी",
        "cast": "कलाकार",
        "rating": "रेटिंग",
        "choose_lang": "अपनी भाषा चुनें",
        "system_instruction": (
            "आप Mouven AI नाम की मूवी वेबसाइट के लिए एक स्मार्ट असिस्टेंट हैं। "
            "आपका मुख्य काम यूज़र को किसी फिल्म या शो का नाम याद दिलाने में मदद करना है। "
            "हिंदी में दोस्ताना और मज़ेदार अंदाज़ में बात करें। "
            "अगर यूज़र छोटे संकेत दे तो नाम का अंदाज़ा लगाने की कोशिश करें। "
            "जानकारी अधूरी हो तो स्मार्ट और दिलचस्प सवाल पूछें "
            "जब तक सही नाम पता न चल जाए फिर नाम बताकर रोचक जानकारी दें। "
            "अगर स्क्रीनशॉट या ऑडियो मिले तो उसी तरह फिल्म पहचानने की कोशिश करें।"
        ),
    },
}

# ==================================================================
# 3. شاشة اختيار اللغة
# ==================================================================
st.markdown(DESIGN_CSS, unsafe_allow_html=True)

if "lang" not in st.session_state:
    st.markdown(
        f"""
        <div style="display:flex;flex-direction:column;align-items:center;
                    justify-content:center;min-height:80vh;gap:0.5rem;">
            <div class="mv-film-reel">{FILM_REEL_SVG}</div>
            <div class="mv-lang-title">MOUVEN</div>
            <div class="mv-lang-sub">Choose your language</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns(len(LANGS))
    for col, (code, data) in zip(cols, LANGS.items()):
        with col:
            if st.button(
                f"{data['flag']}  {data['name']}",
                key=f"lang_{code}",
                use_container_width=True,
            ):
                st.session_state.lang = code
                st.rerun()
    st.stop()

L = LANGS[st.session_state.lang]

# ==================================================================
# 4. TMDb
# ==================================================================
TMDB_KEY = st.secrets.get("TMDB_API_KEY", None)


def tmdb_search(title, lang_code):
    if not TMDB_KEY:
        return None
    try:
        r = requests.get(
            "https://api.themoviedb.org/3/search/multi",
            params={"api_key": TMDB_KEY, "query": title, "language": lang_code},
            timeout=8,
        )
        results = r.json().get("results", [])
        for item in results:
            if item.get("media_type") in ("movie", "tv"):
                return item
        return None
    except Exception:
        return None


def tmdb_details(item, lang_code):
    if not TMDB_KEY:
        return None
    media_type = item.get("media_type")
    item_id = item.get("id")
    try:
        r = requests.get(
            f"https://api.themoviedb.org/3/{media_type}/{item_id}",
            params={"api_key": TMDB_KEY, "language": lang_code, "append_to_response": "credits"},
            timeout=8,
        )
        return r.json()
    except Exception:
        return None


def render_movie_details(title, lang_code, texts):
    info = tmdb_search(title, lang_code)
    if not info:
        st.caption(texts["no_results"])
        return
    details = tmdb_details(info, lang_code)
    if not details:
        st.caption(texts["no_results"])
        return

    poster_path = details.get("poster_path")
    if poster_path:
        st.image(f"https://image.tmdb.org/t/p/w300{poster_path}", width=140)

    overview = details.get("overview")
    if overview:
        st.markdown(f'<div class="mv-detail-label">{texts["story"]}</div>', unsafe_allow_html=True)
        st.caption(overview)

    rating = details.get("vote_average")
    if rating:
        st.markdown(
            f'<div class="mv-rating">{round(rating,1)} / 10</div>',
            unsafe_allow_html=True,
        )

    cast = details.get("credits", {}).get("cast", [])[:5]
    if cast:
        st.markdown(f'<div class="mv-detail-label">{texts["cast"]}</div>', unsafe_allow_html=True)
        cast_cols = st.columns(len(cast))
        for c, actor in zip(cast_cols, cast):
            with c:
                profile = actor.get("profile_path")
                img_url = (
                    f"https://image.tmdb.org/t/p/w185{profile}"
                    if profile
                    else "https://via.placeholder.com/70x100/11111E/4A4A6A?text=?"
                )
                st.markdown(
                    f'<div class="mv-cast-card">'
                    f'<img src="{img_url}"><br>{actor.get("name","")}'
                    f"</div>",
                    unsafe_allow_html=True,
                )


# ==================================================================
# 5. Text-to-Speech
# ==================================================================
def speak_text(text, tts_lang):
    safe_text = json.dumps(text)
    components.html(
        f"""<script>
        if(window.speechSynthesis){{
            window.speechSynthesis.cancel();
            var m=new SpeechSynthesisUtterance({safe_text});
            m.lang="{tts_lang}";
            window.speechSynthesis.speak(m);
        }}</script>""",
        height=0,
    )


# ==================================================================
# 6. إدارة المحادثات
# ==================================================================
if "conversations" not in st.session_state:
    st.session_state.conversations = load_json(CONVERSATIONS_FILE, [])
if "current_conv_id" not in st.session_state:
    st.session_state.current_conv_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_chats_panel" not in st.session_state:
    st.session_state.show_chats_panel = False
if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_json(WATCHLIST_FILE, [])
if "speak_enabled" not in st.session_state:
    st.session_state.speak_enabled = True


def save_current_conversation():
    if not st.session_state.messages:
        return
    title = st.session_state.messages[0]["content"][:35]
    convs = st.session_state.conversations
    existing = next((c for c in convs if c["id"] == st.session_state.current_conv_id), None)
    if existing:
        existing["title"] = title
        existing["messages"] = st.session_state.messages
    else:
        convs.append({
            "id": st.session_state.current_conv_id,
            "title": title,
            "messages": st.session_state.messages,
        })
    save_json(CONVERSATIONS_FILE, convs)


def start_new_chat():
    save_current_conversation()
    st.session_state.current_conv_id = str(uuid.uuid4())
    st.session_state.messages = []
    if "chat" in st.session_state:
        del st.session_state["chat"]


def load_conversation(conv):
    save_current_conversation()
    st.session_state.current_conv_id = conv["id"]
    st.session_state.messages = conv["messages"]
    if "chat" in st.session_state:
        del st.session_state["chat"]


# ==================================================================
# 7. القائمة الجانبية
# ==================================================================
with st.sidebar:
    # Logo
    st.markdown(
        f'<div class="mv-sidebar-logo">{SIDEBAR_ICON_SVG}'
        f'<span class="mv-logo-text">MOUVEN</span></div>',
        unsafe_allow_html=True,
    )

    # Chats section
    st.markdown(
        f'<div class="mv-section-label">{L["chats_header"]}</div>',
        unsafe_allow_html=True,
    )

    if st.button(L["new_chat"], key="new_chat_btn", use_container_width=True):
        start_new_chat()
        st.rerun()

    for conv in reversed(st.session_state.conversations[-8:]):
        label = (conv["title"] or "...")[:32]
        if st.button(label, key=f"conv_{conv['id']}", use_container_width=True):
            load_conversation(conv)
            st.rerun()

    st.markdown('<hr class="mv-divider">', unsafe_allow_html=True)

    # Watchlist section
    st.markdown(
        f'<div class="mv-section-label">{L["watchlist_header"]}</div>',
        unsafe_allow_html=True,
    )
    st.caption(L["watchlist_caption"])

    with st.form("add_item_form", clear_on_submit=True):
        new_title = st.text_input(L["name_field"], label_visibility="collapsed",
                                  placeholder=L["name_field"])
        new_status = st.radio(L["status_field"], [L["status_watch"], L["status_done"]],
                              horizontal=True, label_visibility="collapsed")
        submitted = st.form_submit_button(L["add_button"], use_container_width=True)
        if submitted and new_title.strip():
            st.session_state.watchlist.append(
                {"title": new_title.strip(), "status": new_status}
            )
            save_json(WATCHLIST_FILE, st.session_state.watchlist)
            st.rerun()

    st.markdown('<hr class="mv-divider">', unsafe_allow_html=True)

    if not st.session_state.watchlist:
        st.markdown(
            f'<div style="display:flex;flex-direction:column;align-items:center;'
            f'gap:10px;padding:1rem 0;opacity:0.5;">'
            f'{EMPTY_LIST_SVG}'
            f'<span style="font-size:0.75rem;color:#4A4A6A;">{L["empty_watchlist"]}</span>'
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        for i, item in enumerate(st.session_state.watchlist):
            done = item["status"] == L["status_done"]
            card_class = "mv-watch-card done" if done else "mv-watch-card"
            dot_color = "#4CAF82" if done else "#C8A96E"

            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(
                    f'<div class="{card_class}">'
                    f'<div class="mv-watch-title">'
                    f'<span style="display:inline-block;width:7px;height:7px;'
                    f'border-radius:50%;background:{dot_color};'
                    f'margin-right:7px;vertical-align:middle;"></span>'
                    f'{item["title"]}</div>'
                    f'<div class="mv-watch-status">{item["status"]}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
            with col2:
                if st.button("×", key=f"del_{i}"):
                    st.session_state.watchlist.pop(i)
                    save_json(WATCHLIST_FILE, st.session_state.watchlist)
                    st.rerun()

            with st.expander(L["details_button"]):
                render_movie_details(item["title"], L["tmdb"], L)


# ==================================================================
# 8. موديل Gemini
# ==================================================================
def get_chat_model():
    if "client" not in st.session_state:
        st.session_state.client = genai.Client(
            api_key=st.secrets["GEMINI_API_KEY"]
        )
    if "chat" not in st.session_state:
        history = []
        for m in st.session_state.messages:
            role = "user" if m["role"] == "user" else "model"
            history.append(
                types.Content(role=role, parts=[types.Part(text=m["content"])])
            )
        st.session_state.chat = st.session_state.client.chats.create(
            model="gemini-2.5-flash",
            config={"system_instruction": L["system_instruction"]},
            history=history,
        )
    return st.session_state.chat


try:
    chat = get_chat_model()
except Exception as e:
    st.error(f"Connection error: {e}")
    st.stop()


# ==================================================================
# 9. الواجهة الرئيسية
# ==================================================================
st.markdown(
    f'<h1>{L["app_title"]}</h1>'
    f'<div class="mv-subtitle">{L["subtitle"]}</div>',
    unsafe_allow_html=True,
)

st.session_state.speak_enabled = st.toggle(
    L["speak_toggle"], value=st.session_state.speak_enabled
)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# شريط الإدخال — صورة + صوت + كتابة
bar_cols = st.columns([1, 1, 8])
with bar_cols[0]:
    uploaded_image = st.file_uploader(
        L["upload_label"], type=["png", "jpg", "jpeg"],
        key="img_uploader", label_visibility="collapsed"
    )
with bar_cols[1]:
    audio_value = None
    try:
        if hasattr(st, "audio_input"):
            audio_value = st.audio_input(
                L["voice_label"], key="voice_input", label_visibility="collapsed"
            )
    except Exception:
        pass

user_input = st.chat_input(L["chat_placeholder"])

new_user_message_parts = None
display_text = None

if user_input:
    display_text = user_input
    new_user_message_parts = [user_input]
elif (
    uploaded_image is not None
    and st.session_state.get("last_image_id") != uploaded_image.file_id
):
    st.session_state.last_image_id = uploaded_image.file_id
    img_bytes = uploaded_image.getvalue()
    display_text = "[صورة مرفوعة]"
    new_user_message_parts = [
        types.Part.from_bytes(data=img_bytes, mime_type=uploaded_image.type),
        "حاول تتعرف على الفيلم أو المسلسل من الصورة دي",
    ]
elif (
    audio_value is not None
    and st.session_state.get("last_audio_id") != audio_value.file_id
):
    st.session_state.last_audio_id = audio_value.file_id
    audio_bytes = audio_value.getvalue()
    display_text = "[رسالة صوتية]"
    new_user_message_parts = [
        types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"),
    ]

if new_user_message_parts:
    with st.chat_message("user"):
        st.write(display_text)
    st.session_state.messages.append({"role": "user", "content": display_text})
    try:
        response = chat.send_message(new_user_message_parts)
        with st.chat_message("assistant"):
            st.write(response.text)
        st.session_state.messages.append(
            {"role": "assistant", "content": response.text}
        )
        save_current_conversation()
        if st.session_state.speak_enabled:
            speak_text(response.text, L["tts"])
    except Exception as e:
        st.error(f"Error: {e}")
