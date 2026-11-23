import os
import streamlit as st
from groq import Groq
from pypdf import PdfReader

# إعدادات الصفحة
st.set_page_config(page_title="مكتبي الذكية للكتب", layout="centered")

st.title("📚 مكتبي الذكية للكتب (محادثة مستمرة)")
st.write("ارفع ملف الـ PDF وتحدث معه بسياق متصل مثل ChatGPT تماماً.")

# سحب مفتاح Groq بسرية تامة من Streamlit Secrets أو متغيرات البيئة
groq_api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")

if not groq_api_key:
    st.error("⚠️ تنبيه: لم يتم العثور على مفتاح Groq API. الرجاء إضافته في إعدادات Secrets الخاصة بـ Streamlit.")
    st.stop()

# صندوق رفع الملفات
uploaded_file = st.file_uploader("Upload", type=["pdf"])

if uploaded_file is not None:
    # التحقق من تغيير الملف لإعادة ضبط المحادثة
    if "current_file_name" not in st.session_state or st.session_state.current_file_name != uploaded_file.name:
        st.session_state.current_file_name = uploaded_file.name
        st.session_state.messages = []
        st.session_state.pdf_text_content = ""

    # استخراج نص الـ PDF إذا لم يكن مستخرجاً مسبقاً لهذه الجلسة
    if not st.session_state.pdf_text_content:
        with st.spinner("جاري قراءة وتحليل ملف الـ PDF..."):
            try:
                reader = PdfReader(uploaded_file)
                extracted_text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        extracted_text += page_text + "\n"
                
                st.session_state.pdf_text_content = extracted_text
                
                # رسالة النظام الأولى لتوجيه النموذج بالاعتماد على الكتاب
                st.session_state.messages.append({
                    "role": "system", 
                    "content": f"أنت مساعد ذكي ومحترف تجيب حصرياً بناءً على محتوى الكتاب التالي:\n\n{st.session_state.pdf_text_content[:20000]}"
                })
                st.success("تم رفع الملف وتحليله بنجاح! يمكنك البدء بالأسئلة الآن.")
            except Exception as e:
                st.error(f"حدث خطأ أثناء قراءة الملف: {e}")

    st.markdown("---")
    st.subheader("💬 نافذة المحادثة:")

    # عرض سجل المحادثات السابق (تخطي رسالة النظام System Prompt)
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # خانة إدخال الرسائل والمحادثة التفاعلية من الأسفل
    if user_prompt := st.chat_input("اكتب سؤالك أو اطلب شرح جزء معين من الكتاب..."):
        
        # 1. إضافة وتخزين رسالة المستخدم وعرضها
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # 2. توليد الرد من خلال Groq مع الحفاظ على سياق المحادثة الكامل
        with st.chat_message("assistant"):
            with st.spinner("جاري التفكير وصياغة الرد..."):
                try:
                    client = Groq(api_key=groq_api_key)
                    completion = client.chat.completions.create(
                        model="llama-3.3-70b-8192",  # الاسم الصحيح والمعتمد ليعمل بدون أخطاء
                        messages=st.session_state.messages,
                        temperature=0.7,
                        max_tokens=1500,
                    )
                    
                    bot_reply = completion.choices[0].message.content
                    st.markdown(bot_reply)
                    
                    # 3. تخزين رد المساعد في سجل المحادثات لضمان استمرار السياق
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                    
                except Exception as err:
                    st.error(f"حدث خطأ أثناء الاتصال بالخادم: {err}")

else:
    # في حال لم يتم رفع ملف
    st.info("الرجاء رفع ملف PDF من بالأعلى للبدء في الدردشة.")
    if "messages" in st.session_state:
        st.session_state.messages = []
    if "pdf_text_content" in st.session_state:
        st.session_state.pdf_text_content = ""