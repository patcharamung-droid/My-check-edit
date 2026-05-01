import streamlit as st
import google.generativeai as genai
import os

# --- 1. ตั้งค่าหน้าจอ (Theme & Layout) ---
st.set_page_config(
    page_title="Thai Proofreader AI | พิสูจน์อักษร", 
    page_icon="📝",
    layout="wide", # ใช้เต็มหน้าจอเพื่อให้มีพื้นที่แสดงผลเปรียบเทียบ
    initial_sidebar_state="expanded"
)

# Custom CSS เพื่อตกแต่งเพิ่มเติม
st.markdown("""
<style>
    /* ปรับแต่งหัวข้อ */
    .big-font {
        font-size:30px !important;
        font-weight: bold;
        color: #0068C9;
    }
    /* ปรับแต่งกล่องข้อความผลลัพธ์ */
    .result-box {
        background-color: #F0F2F6;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #D1D5DB;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)


# --- 2. การเชื่อมต่อ API (ดึงจาก Secrets ของ Streamlit) ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ ไม่พบ API Key! กรุณาตั้งค่า 'GEMINI_API_KEY' ใน Secrets ของ Streamlit Cloud ครับ")
    st.stop()

api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# แนะนำให้ใช้รุ่น 'gemini-3-flash-preview' สำหรับปี 2026 ครับ 
# ฉลาด รวดเร็ว ประหยัด Token เหมาะกับงานตรวจคำผิด
model = genai.GenerativeModel('gemini-3-flash-preview')


# --- 3. ส่วน UI - Sidebar (รับข้อมูล) ---
with st.sidebar:
    st.image("https://res.cloudinary.com/dnl6bhmku/image/upload/v1736757350/samples/cup-on-a-table.jpg") # ไอคอนสวยๆ
    st.markdown('<p class="big-font">📝 เมนูการตรวจ</p>', unsafe_allow_html=True)
    st.write("วางบทความของคุณลงในช่องด้านล่าง แล้วกดปุ่มเพื่อเริ่มตรวจครับ")

    # ส่วนรับข้อมูล
    user_input = st.text_area("✍️ บทความต้นฉบับ:", height=400, placeholder="พิมพ์หรือวางข้อความที่ต้องการตรวจ...")
    
    st.markdown("---")
    check_button = st.button("🚀 เริ่มตรวจคำผิดและเกลาประโยค", use_container_width=True)


# --- 4. ส่วน UI - Main Area (แสดงผลลัพธ์) ---
st.markdown('<p class="big-font">📝 ผลลัพธ์การตรวจพิสูจน์อักษร</p>', unsafe_allow_html=True)
st.write("---")

if check_button:
    if user_input.strip() == "":
        st.warning("⚠️ กรุณาใส่ข้อความในแถบด้านข้างก่อนครับ")
    else:
        with st.spinner('🛸 AI กำลังวิเคราะห์และเรียบเรียง... (อาจใช้เวลา 5-10 วินาที)'):
            try:
                # Prompt สำหรับ AI (ปรับปรุงให้ฉลาดขึ้นและคุม Format)
                prompt = f"""
                คุณคือบรรณาธิการมืออาชีพ ผู้เชี่ยวชาญภาษาไทยอย่างลึกซึ้ง จงปฏิบัติหน้าที่ดังนี้:
                1. ตรวจสอบและแก้ไขคำสะกดผิด คำทับศัพท์ให้ถูกต้องตามมาตรฐาน (หรือตามความนิยมในงานเขียนทั่วไปที่ถูกกาลเทศะ)
                2. ตรวจสอบไวยากรณ์ การใช้คำเชื่อม และโครงสร้างประโยค
                3. เกลาประโยคให้สละสลวย อ่านง่าย ลื่นไหล โดยต้องรักษาเนื้อหาเดิมและความหมายเดิมไว้ 100%
                4. ปรับระดับภาษาให้เหมาะสมกับ "งานเขียนทั่วไป/บทความออนไลน์" (ไม่เป็นทางการเกินไป แต่ก็ไม่ดูหลวม)

                จงตอบกลับ **เฉพาะ** ในรูปแบบต่อไปนี้เท่านั้น (ไม่ต้องมีข้อความเกริ่นนำ):

                {user_input}

                ===REVISED===
                <ข้อความที่แก้ไขและเกลาแล้วทั้งหมด>

                ===CHANGES===
                - <รายการที่แก้ไขที่ 1>: <เหตุผลสั้นๆ หรือคำที่แก้>
                - <รายการที่แก้ไขที่ 2>: <เหตุผลสั้นๆ หรือคำที่แก้>
                (ถ้าไม่มีรายการที่แก้ไข ให้ใส่คำว่า 'ไม่มีคำผิด')
                """
                
                response = model.generate_content(prompt)
                full_response = response.text

                # Parse ผลลัพธ์
                parts = full_response.split("===REVISED===")
                if len(parts) > 1:
                    revised_and_changes = parts[1].split("===CHANGES===")
                    revised_text = revised_and_changes[0].strip()
                    changes_list = revised_and_changes[1].strip() if len(revised_and_changes) > 1 else "ไม่มีคำผิด"
                else:
                    st.error("เกิดข้อผิดพลาดในการอ่านผลลัพธ์จาก AI")
                    st.stop()
                
                st.success("✅ ตรวจและเกลาประโยคเสร็จเรียบร้อย!")

                # --- ส่วนแสดงผลแบบมืออาชีพ ---
                
                # 1. กล่องข้อความที่แก้แล้ว (มีปุ่ม Copy)
                st.markdown("#### ✨ บทความที่ได้รับการตรวจสอบและเกลาแล้ว:")
                st.text_area("📋 ก๊อปปี้ไปใช้งานได้เลย:", value=revised_text, height=350, key="revised_output")
                st.caption("ℹ️ ระบบ text_area ของ Streamlit มีปุ่ม Copy ในตัวอยู่แล้ว (เมื่อเอาเมาส์ไปชี้ที่มุมขวาบน)")

                st.markdown("---")

                # 2. รายการแก้ไข (ใส่ใน Expander เพื่อให้ดูเป็นระเบียบ)
                with st.expander("🔎 ดูรายละเอียดการแก้ไข (Changes Log)", expanded=True):
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.markdown("**🔹 บทความต้นฉบับ:**")
                        st.caption(user_input)
                    with col2:
                        st.markdown("**🟢 รายการแก้ไขโดย AI:**")
                        st.markdown(changes_list if changes_list else "ไม่มีการแก้ไข")

            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาดทางเทคนิค: {e}")

else:
    # แสดงหน้าจอต้อนรับเมื่อเปิดแอปครั้งแรก
    st.info("👈 กรุณาวางบทความที่ต้องการตรวจที่แถบด้านข้าง แล้วกดปุ่มเริ่มตรวจครับ")
    
    # เพิ่มตัวอย่างสั้นๆ เพื่อให้เห็นภาพ
    with st.expander("💡 ดูตัวอย่าง"):
        st.write("ลองวางข้อความนี้ดูครับ:")
        st.code("พนักงานไหม่ควรทำการอัพเดทซอฟแวร์ไห้เปนเวอชั่นล่าสุดเสมอ เลยจะทำไห้งานเสร็จเร็วขึ้น")

st.markdown("---")
col_footer1, col_footer2 = st.columns([1, 1])
with col_footer1:
    st.caption("Powered by **Gemini 3 Flash** AI & Streamlit")
with col_footer2:
    st.caption("Thai Proofreader AI v2.0 | พัฒนาโดยคุณเอง")
