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
WATCHLIST_FILE = "watchlist.json"
CONVERSATIONS_FILE = "conversations.json"

st.set_page_config(page_title="Mouven", page_icon="OIP.webp")


def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ==================================================================
# 1. اللغات المتاحة + النصوص المترجمة + تعليمات الذكاء الاصطناعي
# ==================================================================
LANGS = {
    "ar": {
        "flag": "🇪🇬", "name": "العربية", "tmdb": "ar", "tts": "ar-EG",
        "app_title": "🎬 مساعد Mouven",
        "subtitle": "نسيت اسم فيلم؟ احكيلي قصته أو الممثلين وأنا أجهزهولك",
        "chat_placeholder": "اكتب هنا...",
        "watchlist_header": "📺 قائمتي",
        "watchlist_caption": "الأفلام والمسلسلات اللي عايز تتفرج عليها أو شفتها",
        "add_button": "➕ ضيف للقائمة",
        "status_watch": "عايز أتفرج عليه",
        "status_done": "شفته",
        "empty_watchlist": "لسه القائمة فاضية، ضيف أول فيلم! 🍿",
        "details_button": "🔍 تفاصيل",
        "chats_header": "المحادثات",
        "new_chat": "➕ محادثة جديدة",
        "upload_label": "📷 ارفع صورة سكرين شوت للتعرف على الفيلم",
        "voice_label": "🎤 سجل سؤالك بصوتك",
        "speak_toggle": "🔊 خلي المساعد يتكلم",
        "name_field": "اسم الفيلم / المسلسل",
        "status_field": "الحالة",
        "no_results": "معرفناش نلاقي معلومات عن الفيلم ده",
        "story": "📖 القصة",
        "cast": "🎭 الممثلين",
        "rating": "⭐ التقييم",
        "system_instruction": (
            "أنت مساعد ذكي مخصص لموقع أفلام اسمه (Mouven)."
            "وظيفتك الأساسية هي مساعدة المستخدم في معرفة اسم الفيلم الذي يريده."
            "تتحدث بالعامية المصرية الودودة والذكية جداً."
            "إذا ذكر المستخدم تفاصيل صغيرة (مثل قصة، مشهد، ممثل)، قم بتخمين الفيلم."
            "لا تعطي الإجابة فوراً إذا كانت التفاصيل ناقصة، بل اسأله أسئلة ذكية ومسلية "
            "مثل: (طب فاكر البطل كان معاه حد؟) أو (الفيلم ده رعب ولا أكشن؟) "
            "حتى تصل للاسم الصحيح، وعندما تتأكد من الفيلم، قل له اسمه واكتب نبذة مشوقة عنه. "
            "لو استلمت صورة سكرين شوت من فيلم أو صوت، حاول تتعرف على الفيلم بنفس الأسلوب."
        ),
    },
    "en": {
        "flag": "🇬🇧", "name": "English", "tmdb": "en", "tts": "en-US",
        "app_title": "🎬 Mouven",
        "subtitle": "Forgot a movie's name? Tell me the plot or actors and I'll find it.",
        "chat_placeholder": "Type here...",
        "watchlist_header": "📺 My List",
        "watchlist_caption": "Movies & shows you want to watch or already watched",
        "add_button": "➕ Add to list",
        "status_watch": "Want to watch",
        "status_done": "Watched",
        "empty_watchlist": "Your list is empty, add your first title! 🍿",
        "details_button": "🔍 Details",
        "chats_header": "Chats",
        "new_chat": "➕ New chat",
        "upload_label": "📷 Upload a screenshot to identify the movie",
        "voice_label": "🎤 Record your question",
        "speak_toggle": "🔊 Let the assistant speak",
        "name_field": "Movie / Show name",
        "status_field": "Status",
        "no_results": "Couldn't find info about this title",
        "story": "📖 Plot",
        "cast": "🎭 Cast",
        "rating": "⭐ Rating",
        "system_instruction": (
            "You are a smart assistant for a movie website called 'Mouven'. "
            "Your main job is helping the user figure out the name of a movie or show they're thinking of. "
            "Speak in a friendly, witty, conversational tone in English. "
            "If the user gives small clues (a scene, an actor, a detail), try to guess the title. "
            "Don't answer immediately if the details are incomplete - ask smart, fun follow-up questions "
            "like 'Was the main character alone?' or 'Is it horror or action?' until you're confident, "
            "then reveal the title with an exciting short blurb about it. "
            "If you receive a screenshot or audio, try to identify the movie the same way."
        ),
    },
    "fr": {
        "flag": "🇫🇷", "name": "Français", "tmdb": "fr", "tts": "fr-FR",
        "app_title": "🎬 Assistant IA Mouven",
        "subtitle": "Vous avez oublié le nom d'un film ? Racontez-moi l'histoire ou les acteurs.",
        "chat_placeholder": "Écrivez ici...",
        "watchlist_header": "📺 Ma liste",
        "watchlist_caption": "Films et séries que vous voulez voir ou avez déjà vus",
        "add_button": "➕ Ajouter à la liste",
        "status_watch": "À regarder",
        "status_done": "Vu",
        "empty_watchlist": "Votre liste est vide, ajoutez un premier titre ! 🍿",
        "details_button": "🔍 Détails",
        "chats_header": "Discussions",
        "new_chat": "➕ Nouvelle discussion",
        "upload_label": "📷 Téléchargez une capture d'écran pour identifier le film",
        "voice_label": "🎤 Enregistrez votre question",
        "speak_toggle": "🔊 Laisser l'assistant parler",
        "name_field": "Nom du film / série",
        "status_field": "Statut",
        "no_results": "Impossible de trouver des informations sur ce titre",
        "story": "📖 Histoire",
        "cast": "🎭 Acteurs",
        "rating": "⭐ Note",
        "system_instruction": (
            "Vous êtes un assistant intelligent pour un site de films appelé 'Mouven'. "
            "Votre rôle est d'aider l'utilisateur à retrouver le nom d'un film ou d'une série. "
            "Parlez en français, avec un ton amical et vif. "
            "Si l'utilisateur donne de petits indices, devinez le titre. "
            "Si les détails sont insuffisants, posez des questions amusantes et intelligentes "
            "avant de répondre, puis révélez le titre avec un court résumé captivant. "
            "Si vous recevez une capture d'écran ou un audio, essayez d'identifier le film de la même façon."
        ),
    },
    "pt": {
        "flag": "🇧🇷", "name": "Português (Brasil)", "tmdb": "pt-BR", "tts": "pt-BR",
        "app_title": "🎬 Assistente IA Mouven",
        "subtitle": "Esqueceu o nome de um filme? Conte a história ou os atores.",
        "chat_placeholder": "Digite aqui...",
        "watchlist_header": "📺 Minha lista",
        "watchlist_caption": "Filmes e séries que você quer assistir ou já assistiu",
        "add_button": "➕ Adicionar à lista",
        "status_watch": "Quero assistir",
        "status_done": "Já assisti",
        "empty_watchlist": "Sua lista está vazia, adicione o primeiro título! 🍿",
        "details_button": "🔍 Detalhes",
        "chats_header": "Conversas",
        "new_chat": "➕ Nova conversa",
        "upload_label": "📷 Envie uma captura de tela para identificar o filme",
        "voice_label": "🎤 Grave sua pergunta",
        "speak_toggle": "🔊 Deixar o assistente falar",
        "name_field": "Nome do filme / série",
        "status_field": "Status",
        "no_results": "Não foi possível encontrar informações sobre este título",
        "story": "📖 Enredo",
        "cast": "🎭 Elenco",
        "rating": "⭐ Avaliação",
        "system_instruction": (
            "Você é um assistente inteligente para um site de filmes chamado 'Mouven'. "
            "Sua função é ajudar o usuário a descobrir o nome de um filme ou série. "
            "Fale em português do Brasil, com um tom amigável e animado. "
            "Se o usuário der pequenas pistas, tente adivinhar o título. "
            "Se os detalhes forem insuficientes, faça perguntas inteligentes e divertidas "
            "antes de responder, depois revele o título com um resumo curto e envolvente. "
            "Se receber uma captura de tela ou áudio, tente identificar o filme da mesma forma."
        ),
    },
    "hi": {
        "flag": "🇮🇳", "name": "हिन्दी", "tmdb": "hi", "tts": "hi-IN",
        "app_title": "🎬 टॉप सिनेमा एआई असिस्टेंट",
        "subtitle": "किसी फिल्म का नाम भूल गए? कहानी या कलाकारों के बारे में बताएं।",
        "chat_placeholder": "यहाँ लिखें...",
        "watchlist_header": "📺 मेरी सूची",
        "watchlist_caption": "वो फ़िल्में और शोज़ जो आप देखना चाहते हैं या देख चुके हैं",
        "add_button": "➕ सूची में जोड़ें",
        "status_watch": "देखना है",
        "status_done": "देख लिया",
        "empty_watchlist": "आपकी सूची खाली है, पहली फिल्म जोड़ें! 🍿",
        "details_button": "🔍 विवरण",
        "chats_header": "बातचीत",
        "new_chat": "➕ नई बातचीत",
        "upload_label": "📷 फिल्म पहचानने के लिए स्क्रीनशॉट अपलोड करें",
        "voice_label": "🎤 अपना सवाल रिकॉर्ड करें",
        "speak_toggle": "🔊 असिस्टेंट को बोलने दें",
        "name_field": "फिल्म / शो का नाम",
        "status_field": "स्थिति",
        "no_results": "इस शीर्षक के बारे में जानकारी नहीं मिली",
        "story": "📖 कहानी",
        "cast": "🎭 कलाकार",
        "rating": "⭐ रेटिंग",
        "system_instruction": (
            "आप 'Mouven' नाम की मूवी वेबसाइट के लिए एक स्मार्ट असिस्टेंट हैं। "
            "आपका मुख्य काम यूज़र को किसी फिल्म या शो का नाम याद दिलाने में मदद करना है। "
            "हिंदी में दोस्ताना और मज़ेदार अंदाज़ में बात करें। "
            "अगर यूज़र छोटे संकेत दे, तो नाम का अंदाज़ा लगाने की कोशिश करें। "
            "जानकारी अधूरी हो तो सीधे जवाब मत दीजिए, बल्कि स्मार्ट और दिलचस्प सवाल पूछें, "
            "जब तक सही नाम पता न चल जाए, फिर नाम बताकर एक रोचक संक्षिप्त जानकारी दें। "
            "अगर स्क्रीनशॉट या ऑडियो मिले, तो उसी तरह फिल्म पहचानने की कोशिश करें।"
        ),
    },
}

# ==================================================================
# 2. شاشة اختيار اللغة (تظهر مرة واحدة فقط عند فتح التطبيق)
# ==================================================================
if "lang" not in st.session_state:
    st.markdown(
        """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<h1 style='text-align:center;'>🎬 Mouven</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>Choose your language / اختر اللغة</h3>", unsafe_allow_html=True)
    st.write("")
    cols = st.columns(len(LANGS))
    for col, (code, data) in zip(cols, LANGS.items()):
        with col:
            if st.button(f"{data['flag']}\n{data['name']}", key=f"lang_{code}", use_container_width=True):
                st.session_state.lang = code
                st.rerun()
    st.stop()

L = LANGS[st.session_state.lang]

# ==================================================================
# 3. ستايل عام (إخفاء عناصر ستريمليت + تنسيق كروت القائمة)
# ==================================================================
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display: none;}

    .watch-card {
        background-color: #1e1e2e;
        border-radius: 12px;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-right: 4px solid #f97316;
    }
    .watch-card.done {
        border-right: 4px solid #22c55e;
        opacity: 0.8;
    }
    .watch-title { font-weight: bold; font-size: 15px; color: #f1f5f9; }
    .watch-status { font-size: 12px; color: #94a3b8; }

    .chat-history-item {
        padding: 6px 8px;
        border-radius: 8px;
        font-size: 13px;
        color: #cbd5e1;
        margin-bottom: 2px;
    }
    .thin-divider {
        border: none;
        border-top: 1px solid #333344;
        margin: 10px 0;
    }
    .cast-card {
        text-align: center;
        font-size: 12px;
        color: #e2e8f0;
    }
    .cast-card img {
        border-radius: 10px;
        margin-bottom: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==================================================================
# 4. TMDb - دوال البحث عن الأفلام/المسلسلات وجلب التفاصيل
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
        st.warning(texts["no_results"])
        return
    details = tmdb_details(info, lang_code)
    if not details:
        st.warning(texts["no_results"])
        return

    poster_path = details.get("poster_path")
    if poster_path:
        st.image(f"https://image.tmdb.org/t/p/w300{poster_path}", width=160)

    overview = details.get("overview")
    if overview:
        st.markdown(f"**{texts['story']}**")
        st.write(overview)

    rating = details.get("vote_average")
    if rating:
        st.markdown(f"**{texts['rating']}:** ⭐ {round(rating, 1)} / 10")

    cast = details.get("credits", {}).get("cast", [])[:6]
    if cast:
        st.markdown(f"**{texts['cast']}**")
        cast_cols = st.columns(len(cast))
        for c, actor in zip(cast_cols, cast):
            with c:
                profile = actor.get("profile_path")
                img_url = (
                    f"https://image.tmdb.org/t/p/w185{profile}"
                    if profile
                    else "https://via.placeholder.com/100x140?text=?"
                )
                st.markdown(
                    f"""
                    <div class="cast-card">
                        <img src="{img_url}" width="80">
                        <div>{actor.get('name', '')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ==================================================================
# 5. تحويل النص لصوت (Text To Speech) عبر متصفح المستخدم
# ==================================================================
def speak_text(text, tts_lang):
    safe_text = json.dumps(text)
    components.html(
        f"""
        <script>
        if (window.speechSynthesis) {{
            window.speechSynthesis.cancel();
            var msg = new SpeechSynthesisUtterance({safe_text});
            msg.lang = "{tts_lang}";
            window.speechSynthesis.speak(msg);
        }}
        </script>
        """,
        height=0,
    )


# ==================================================================
# 6. إدارة المحادثات المحفوظة (Chat History)
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
    title = st.session_state.messages[0]["content"][:30]
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
# 7. القائمة الجانبية: محادثات + خط فاصل + قائمة الأفلام
# ==================================================================
with st.sidebar:
    menu_col1, menu_col2 = st.columns([1, 4])
    with menu_col1:
        if st.button("☰", key="hamburger_btn"):
            st.session_state.show_chats_panel = not st.session_state.show_chats_panel
            st.rerun()
    with menu_col2:
        st.markdown(f"### {L['chats_header']}")

    if st.session_state.show_chats_panel:
        if st.button(L["new_chat"], key="new_chat_btn", use_container_width=True):
            start_new_chat()
            st.rerun()

        for conv in reversed(st.session_state.conversations):
            label = conv["title"] if conv["title"] else "..."
            if st.button(f"💬 {label}", key=f"conv_{conv['id']}", use_container_width=True):
                load_conversation(conv)
                st.rerun()

    st.markdown("<hr class='thin-divider'>", unsafe_allow_html=True)

    st.markdown(f"## {L['watchlist_header']}")
    st.caption(L["watchlist_caption"])

    with st.form("add_item_form", clear_on_submit=True):
        new_title = st.text_input(L["name_field"])
        new_status = st.radio(L["status_field"], [L["status_watch"], L["status_done"]], horizontal=True)
        submitted = st.form_submit_button(L["add_button"])

        if submitted and new_title.strip():
            st.session_state.watchlist.append({"title": new_title.strip(), "status": new_status})
            save_json(WATCHLIST_FILE, st.session_state.watchlist)
            st.rerun()

    st.divider()

    if not st.session_state.watchlist:
        st.info(L["empty_watchlist"])
    else:
        for i, item in enumerate(st.session_state.watchlist):
            done = item["status"] == L["status_done"]
            card_class = "watch-card done" if done else "watch-card"
            icon = "✅" if done else "🕒"

            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(
                    f"""
                    <div class="{card_class}">
                        <div class="watch-title">{icon} {item['title']}</div>
                        <div class="watch-status">{item['status']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col2:
                if st.button("🗑️", key=f"delete_{i}"):
                    st.session_state.watchlist.pop(i)
                    save_json(WATCHLIST_FILE, st.session_state.watchlist)
                    st.rerun()

            details_key = f"show_details_{i}"
            if details_key not in st.session_state:
                st.session_state[details_key] = False

            if st.button(L["details_button"], key=f"details_btn_{i}"):
                st.session_state[details_key] = not st.session_state[details_key]

            if st.session_state[details_key]:
                with st.spinner("..."):
                    render_movie_details(item["title"], L["tmdb"], L)

# ==================================================================
# 9. موديل الذكاء الاصطناعي (Gemini)
# ==================================================================
def get_chat_model():
    if "client" not in st.session_state:
        st.session_state.client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

    if "chat" not in st.session_state:
        history = []
        for m in st.session_state.messages:
            role = "user" if m["role"] == "user" else "model"
            history.append(types.Content(role=role, parts=[types.Part(text=m["content"])]))

        st.session_state.chat = st.session_state.client.chats.create(
            model="gemini-2.5-flash",
            config={"system_instruction": L["system_instruction"]},
            history=history,
        )

    return st.session_state.chat


try:
    chat = get_chat_model()
except Exception as e:
    st.error(f"❌ خطأ في الاتصال بالذكاء الاصطناعي: {e}")
    st.stop()

# ==================================================================
# 10. واجهة الشات الرئيسية
# ==================================================================
st.title(L["app_title"])
st.write(L["subtitle"])

st.session_state.speak_enabled = st.toggle(
    L["speak_toggle"], value=st.session_state.speak_enabled
)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --- رفع صورة سكرين شوت ---
uploaded_image = st.file_uploader(
    L["upload_label"], type=["png", "jpg", "jpeg"], key="img_uploader"
)

# --- تسجيل صوتي (اختياري) ---
audio_value = None
try:
    if hasattr(st, "audio_input"):
        audio_value = st.audio_input(L["voice_label"], key="voice_input")
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
    display_text = "📷 [صورة سكرين شوت]"
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
    display_text = "🎤 [رسالة صوتية]"
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
        st.error(f"❌ خطأ في إرسال الرسالة: {e}")
