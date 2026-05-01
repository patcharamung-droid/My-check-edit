import streamlit as st
import google.generativeai as genai
import os

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="Thai Proofreader AI", page_icon="📝")
st.title("📝 ระบบตรวจคำผิดบทความภาษาไทย")
st.subheader("วิเคราะห์ด้วย AI เพื่อความถูกต้องและสละสลวย")

# 2. การเชื่อมต่อ API (ดึงจาก Secrets ของ Streamlit)
# ถ้าคุณรันในเครื่องตัวเอง ให้เปลี่ยนเป็น API Key ตรงๆ หรือใช้ os.getenv
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. ส่วนรับข้อมูล
user_input = st.text_area("วางบทความของคุณที่นี่:", height=300, placeholder="พิมพ์หรือวางข้อความที่ต้องการตรวจ...")

if st.button("ตรวจคำผิดและเกลาประโยค"):
    if user_input.strip() == "":
        st.warning("กรุณาใส่ข้อความก่อนครับ")
    else:
        with st.spinner('กำลังวิเคราะห์...'):
            try:
                # Prompt สำหรับ AI
                prompt = f"""
                คุณคือบรรณาธิการมืออาชีพ จงตรวจคำผิด คำทับศัพท์ และไวยากรณ์ภาษาไทยในบทความนี้
                พร้อมทั้งเกลาประโยคให้สละสลวยสำหรับงานเขียนทั่วไป แต่ยังรักษาเนื้อหาเดิมไว้ครบถ้วน
                
                บทความที่ต้องการตรวจ:
                "{user_input}"
                
                กรุณาตอบกลับในรูปแบบ:
                1. ข้อความที่แก้ไขแล้ว
                2. รายการคำที่สะกดผิด (ถ้ามี)
                """
                
                response = model.generate_content(prompt)
                
                # แสดงผลลัพธ์
                st.success("ตรวจเสร็จเรียกว่า!")
                st.markdown("### ✨ ผลลัพธ์ที่แนะนำ:")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")

st.markdown("---")
st.caption("Powered by Gemini AI & Streamlit")
