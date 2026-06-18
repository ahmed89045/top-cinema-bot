import streamlit as st
from google import genai
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stAppDeployButton {display: none;}
</style>
"""
st.markdown(hide_streamlit_style,unsafe_html=True)
st.markdown(hide_streamlit_style,unsafe_html=True)
st.set_page_config(page_title="توب سينما - المساعد الذكي", page_icon="OIP.webp")
# 1. إعداد واجهة الموقع الذكية باستخدام Streamlit
st.title("🎬 مساعد توب سينما الذكي")
st.write("نسيت اسم فيلم؟ احكيلي قصته او الممثلين و انا اجبهولك")

# 2. ربط الـ API Key (استخدم متغير بيئي بدل ما تحطه في الكود)
 # ← غير ده بـ key جديد


# تعريف موديل الذكاء الاصطناعي وتحديد شخصيته بالعامية المصرية
def get_chat_model():
    if "client" not in st.session_state:
        st.session_state.client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

    if "chat" not in st.session_state:
        system_instruction = (
            "أنت مساعد ذكي مخصص لموقع أفلام اسمه (توب سينما). "
            "وظيفتك الأساسية هي مساعدة المستخدم في معرفة اسم الفيلم الذي يريد. "
            "تتحدث بالعامية المصرية الودودة والذكية جداً. "
            "إذا ذاكر المستخدم تفاصيل صغيرة (مثل قصة، ممثل، مشهد)، قم بتخمين الفيلم. "
            "لا تعطي الإجابة فوراً إذا كانت التفاصيل ناقصة، بل اسأله أسئلة ذكية ومصلية. "
            "مثل: (طب فاكر البطل كان معاه حد؟) أو (الفيلم ده رعب ولا أكشن؟). "
            "حتى تصل للاسم الصحيح، عندما تتأكد من الفيلم، قل له اسمه واكتب نبذة مشوقة عنه."
        )

        st.session_state.chat = st.session_state.client.chats.create(
            model="gemini-2.5-flash",
            config={"system_instruction": system_instruction}
        )

    return st.session_state.chat


# تهيئة سجل المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض سجل المحادثة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["text"])

# استقبال رسالة المستخدم
user_input = st.chat_input("اكتب هنا...")

if user_input:
    # عرض رسالة المستخدم
    with st.chat_message("user"):
        st.write(user_input)

    st.session_state.messages.append({"role": "user", "text": user_input})

    # إرسال الرسالة والحصول على الرد
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        chat = get_chat_model()
        response = chat.send_message(user_input)
        response_placeholder.write(response.text)

    st.session_state.messages.append({"role": "assistant", "text": response.text})
