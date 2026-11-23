import streamlit as st
from pypdf import PdfReader
from groq import Groq

st.set_page_config(page_title="مساعد الكتب الذكي", page_icon="📚", layout="centered")

st.title("📚 مساعد الكتب الذكي")
st.write("قم برفع كتاب بصيغة PDF واسأل الذكاء الاصطناعي عنه مباشرة!")

GROQ_API_KEY = ""

pdf_files = st.file_uploader("اختر ملفات الـ PDF", type=["pdf"], accept_multiple_files=True)

extracted_texts = {}
if pdf_files:
    for pdf in pdf_files:
        reader = PdfReader(pdf)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        extracted_texts[pdf.name] = text
    st.success("✨ تم قراءة الملفات واستخراج النصوص بنجاح!")

question = st.text_input("اكتب سؤالك حول الكتاب هنا:", key="user_question")

if question and extracted_texts:
    context = "\n".join(extracted_texts.values())
    
    client = Groq(api_key=GROQ_API_KEY)
    
    with st.spinner("🔍 جاري البحث في الكتاب وصياغة الإجابة..."):
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"بناءً على النصوص التالية المستخرجة من الكتاب:\n{context}\n\nأجب بدقة عن السؤال التالي: {question}"
                }
            ],
            model="openai/gpt-oss-120b"
        )
        st.markdown("### 🤖 إجابة المساعد الذكي:")
        st.write(chat_completion.choices[0].message.content)
        import os
from groq import Groq
import streamlit as st

# قراءة المفتاح بأمان من إعدادات Streamlit
client = Groq(api_key=st.secrets["GROQ_API_KEY"])