import os
import streamlit as st
from google import genai

# إعدادات وتصميم الصفحة
st.set_page_config(page_title="مكتبي الذكية للكتب", layout="centered")

st.title("📚 مكتبي الذكية للكتب")
st.write("ارفع ملف الـ PDF وتحدث معه بسياق متصل (Chat History).")

# ضبط مفتاح الـ API (تأكد من وضعه في متغيرات البيئة أو استبداله هنا)
# os.environ["GEMINI_API_KEY"] = "YOUR_API_KEY"

# 1. صندوق رفع الملفات (PDF)
uploaded_file = st.file_uploader("Upload", type=["pdf"])

if uploaded_file is not None:
    st.success(f"تم رفع الملف بنجاح: {uploaded_file.name}")
    
    # حفظ الملف مؤقتاً لرفعه لنموذج جيميناي
    temp_file_path = f"temp_{uploaded_file.name}"
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    try:
        # تهيئة عميل جيميناي
        client = genai.Client()
        
        # رفع الملف مرة واحدة وحفظه في الذاكرة المؤقتة للجلسة
        if "gemini_file" not in st.session_state or st.session_state.get("file_name") != uploaded_file.name:
            with st.spinner("جاري معالجة الملف ورفعه..."):
                uploaded_doc = client.files.upload(file=temp_file_path)
                st.session_state.gemini_file = uploaded_doc
                st.session_state.file_name = uploaded_file.name
                # إعادة ضبط سجل الدردشة عند تغيير الملف
                st.session_state.messages = []
            st.success("تمت معالجة الكتاب وجاهز للدردشة المستمرة!")

        # تهيئة قائمة الرسائل في الـ Session State لو لم تكن موجودة
        if "messages" not in st.session_state:
            st.session_state.messages = []

        st.markdown("---")
        st.subheader("💬 الدردشة مع الكتاب:")

        # عرض سجل المحادثات السابق على الشاشة
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # خانة إدخال الرسائل الخاصة بـ Streamlit (تظهر أسفل الشاشة وتدعم Enter مباشرة)
        if user_prompt := st.chat_input("اكتب سؤالك أو طلبك عن الكتاب..."):
            
            # 1. عرض وتخزين رسالة المستخدم
            st.session_state.messages.append({"role": "user", "content": user_prompt})
            with st.chat_message("user"):
                st.markdown(user_prompt)

            # 2. توليد الرد من النموذج مع تضمين الملف وسياق المحادثة
            with st.chat_message("assistant"):
                with st.spinner("جاري التفكير..."):
                    try:
                        # بناء المحتوى ليتضمن الملف المرفوع وسجل الدردشة السابق مع السؤال الجديد
                        # نمرر الملف المرفوع في أول طلب أو مع كل رسالة لضمان معرفة النموذج له
                        chat_contents = [st.session_state.gemini_file]
                        
                        # إضافة الرسائل السابقة كسياق
                        for msg in st.session_state.messages[:-1]:
                            chat_contents.append(f"{msg['role']}: {msg['content']}")
                            
                        # إضافة السؤال الحالي
                        chat_contents.append(f"user: {user_prompt}")

                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=chat_contents
                        )
                        
                        bot_reply = response.text
                        st.markdown(bot_reply)
                        
                        # تخزين رد المساعد في سجل المحادثات
                        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                        
                    except Exception as err:
                        st.error(f"حدث خطأ أثناء توليد الرد: {err}")
                
    except Exception as e:
        st.error(f"حدث خطأ: {e}")
        
    # حذف الملف المؤقت من الجهاز المحلي
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)
        
else:
    st.info("الرجاء رفع ملف PDF للبدء في الدردشة المستمرة.")