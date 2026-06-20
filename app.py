import streamlit as st
from google import genai
import json
import os

# 1. كود إخفاء أشرطة وعناصر ستريمليت
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stAppDeployButton {display: none;}

/* تنسيق كروت قائمة الأفلام في السايد بار */
.watch-card {
    background-color: #1e1e2e;
    border-radius: 12px;
    padding: 10px 14px;
    margin-bottom: 8px;
    border-right: 4px solid #f97316;
    direction: rtl;
}
.watch-card.done {
    border-right: 4px solid #22c55e;
    opacity: 0.75;
}
.watch-title {
    font-weight: bold;
    font-size: 15px;
    color: #f1f5f9;
}
.watch-status {
    font-size: 12px;
    color: #94a3b8;
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 2. إعداد واجهة الموقع
st.set_page_config(page_title="توب سينما - المساعد الذكي", page_icon="OIP.webp")

# ----------------------------------------------------------------
# قائمة الأفلام/المسلسلات (Watchlist) - محفوظة في ملف JSON على الجهاز
# ----------------------------------------------------------------
WATCHLIST_FILE = "watchlist.json"

def load_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_watchlist(data):
    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_watchlist()

with st.sidebar:
    st.markdown("## 📺 قائمتي")
    st.caption("الأفلام والمسلسلات اللي عايز تتفرج عليها أو شفتها")

    with st.form("add_item_form", clear_on_submit=True):
        new_title = st.text_input("اسم الفيلم / المسلسل")
        new_status = st.radio("الحالة", ["عايز أتفرج عليه", "شفته"], horizontal=True)
        submitted = st.form_submit_button("➕ ضيف للقائمة")

        if submitted and new_title.strip():
            st.session_state.watchlist.append({
                "title": new_title.strip(),
                "status": new_status
            })
            save_watchlist(st.session_state.watchlist)
            st.rerun()

    st.divider()

    if not st.session_state.watchlist:
        st.info("لسه القائمة فاضية، ضيف أول فيلم! 🍿")
    else:
        for i, item in enumerate(st.session_state.watchlist):
            done = item["status"] == "شفته"
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
                    unsafe_allow_html=True
                )
            with col2:
                if st.button("🗑️", key=f"delete_{i}"):
                    st.session_state.watchlist.pop(i)
                    save_watchlist(st.session_state.watchlist)
                    st.rerun()

# ----------------------------------------------------------------
# واجهة الشات الأساسية
# ----------------------------------------------------------------
st.title("🎬 مساعد توب سينما الذكي")
st.write("نسيت اسم فيلم؟ احكيلي قصته أو الممثلين وأنا أجهزهولك")

# 3. تعريف موديل الذكاء الاصطناعي
def get_chat_model():
    if "client" not in st.session_state:
        st.session_state.client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

    if "chat" not in st.session_state:
        system_instruction = (
            "أنت مساعد ذكي مخصص لموقع أفلام اسمه (توب سينما)."
            "وظيفتك الأساسية هي مساعدة المستخدم في معرفة اسم الفيلم الذي يريده."
            "تتحدث بالعامية المصرية الودودة والذكية جداً."
            "إذا ذكر المستخدم تفاصيل صغيرة (مثل قصة، مشهد، ممثل)، قم بتخمين الفيلم."
            "لا تعطي الإجابة فوراً إذا كانت التفاصيل ناقصة، بل اسأله أسئلة ذكية ومسلية "
            "مثل: (طب فاكر البطل كان معاه حد؟) أو (الفيلم ده رعب ولا أكشن؟) "
            "حتى تصل للاسم الصحيح، وعندما تتأكد من الفيلم، قل له اسمه واكتب نبذة مشوقة عنه"
        )
        st.session_state.chat = st.session_state.client.chats.create(
            model="gemini-2.5-flash",
            config={"system_instruction": system_instruction}
        )

    return st.session_state.chat

chat = get_chat_model()

# 4. عرض رسائل الشات القديمة والجديدة
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# استقبال أسئلة المستخدم الجديدة وعرض الردود
user_input = st.chat_input("اكتب هنا...")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    response = chat.send_message(user_input)

    with st.chat_message("assistant"):
        st.write(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})
