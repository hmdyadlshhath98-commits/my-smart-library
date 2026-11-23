import streamlit as st
from groq import Groq
import fitz  # مكتبة PyMuPDF الخارقة للسرعة

# قراءة مفتاح الأمان من إعدادات سحابة ستريملت بدقة
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("مكتبتي الذكية للكتب 📚")

# دالة قراءة ملف الـ PDF بسرعة فائقة جداً مع التخزين المؤقت
@st.cache_data
def extract_text_from_pdf(uploaded_file):
    bytes_data = uploaded_file.read()
    doc = fitz.open(stream=bytes_data, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    return text

# صندوق لرفع ملف الـ PDF
uploaded_file = st.file_uploader("اختر ملف PDF للكتاب هنا", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("⏳ جاري قراءة وتحليل الكتاب بسرعة..."):
        book_text = extract_text_from_pdf(uploaded_file)
    
    st.success("✨ تم قراءة الملفات واستخراج النصوص بنجاح!")
    
    # مربع كتابة السؤال حول الكتاب
    user_question = st.text_input("اكتب سؤالك حول الكتاب هنا:")
    
    if user_question:
        with st.spinner("🤖 جاري صياغة الإجابة..."):
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": f"أنت مساعد ذكي. أجب عن سؤال المستخدم بناءً على النصوص المستخرجة التالية من الكتاب فقط:\n\n{book_text[:15000]}"
                    },
                    {
                        "role": "user", 
                        "content": user_question
                    }
                ]
            )
            st.write(response.choices[0].message.content)