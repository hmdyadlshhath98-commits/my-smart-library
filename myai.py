import streamlit as st
import random

# إعدادات وتصميم الصفحة
st.set_page_config(page_title="مكتبي الذكية للكتب", layout="centered")

st.title("📚 مكتبي الذكية للكتب")
st.write("اكتب هنا PDF أو اختر ملف")

# 1. صندوق رفع الملفات (PDF)
uploaded_file = st.file_uploader("Upload", type=["pdf"])

if uploaded_file is not None:
    st.success(f"تم رفع الملف بنجاح: {uploaded_file.name}")
    
    # قائمة الأسئلة التي تتغير في كل مرة
    questions_list = [
        "ما هي الفكرة الرئيسية في الفصل الأول من الكتاب؟",
        "اذكر باختصار أهم النقاط التي ركز عليها الكاتب.",
        "ما هو الاستنتاج الرئيسي المستفاد من هذا النص؟",
        "كيف عالج الكاتب المشكلة المطروحة في هذا الجزء؟"
    ]
    
    # حفظ السؤال الحالي في الذاكرة المؤقتة لكي لا يختفي مع التحديث العادي
    if 'current_question' not in st.session_state:
        st.session_state.current_question = random.choice(questions_list)

    st.markdown("---")
    st.subheader("💡 سؤال تفاعلي من الكتاب:")
    
    # عرض السؤال الحالي
    st.info(st.session_state.current_question)
    
    # 2. زر تغيير السؤال (لتوليد سؤال جديد في كل ضغطة)
    if st.button("🔄 تغيير السؤال / جلب سؤال جديد"):
        st.session_state.current_question = random.choice(questions_list)
        st.rerun() # تحديث الصفحة لعرض السؤال الجديد فوراً

    # خانة إدخال لإجابة المستخدم
    user_answer = st.text_input("اكتب إجابتك هنا:")
    if st.button("إرسال الإجابة"):
        if user_answer:
            st.success("تم إرسال إجابتك بنجاح! أحسنت.")
        else:
            st.warning("الرجاء كتابة إجابتك أولاً قبل الإرسال.")
else:
    st.info("الرجاء رفع ملف PDF للبدء في طرح الأسئلة والتفاعل.")