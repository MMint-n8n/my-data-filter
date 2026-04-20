import streamlit as st
import pandas as pd
import io

st.title("ระบบกรองข้อมูลอัตโนมัติ")

# 1. สร้างตัวแปรความจำ (Session State) เพื่อไม่ให้ข้อมูลหายตอนรีเฟรช
if 'filtered_data' not in st.session_state:
    st.session_state.filtered_data = None

# ส่วนการอัปโหลดไฟล์
uploaded_file = st.file_uploader("เลือกไฟล์ Excel หรือ CSV", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # อ่านข้อมูล
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.write("ตัวอย่างข้อมูลต้นฉบับ:", df.head())

        # เลือกคอลัมน์ที่ต้องการ
        all_columns = df.columns.tolist()
        selected_columns = st.multiselect("เลือกคอลัมน์ที่ต้องการเก็บไว้", all_columns, default=all_columns)

        # ตั้งเงื่อนไขการกรอง
        filter_col = st.selectbox("เลือกคอลัมน์ที่จะใช้เป็นเงื่อนไขกรอง", all_columns)
        keyword = st.text_input(f"พิมพ์ข้อความที่ต้องการค้นหาในคอลัมน์ {filter_col}")

        # ----------------------------------------
        # 2. สร้างปุ่มกด ระบบจะประมวลผลก็ต่อเมื่อกดปุ่มนี้เท่านั้น
        # ----------------------------------------
        if st.button("🔍 เริ่มกรองข้อมูล"):
            filtered_df = df.copy()
            if keyword:
                filtered_df = filtered_df[filtered_df[filter_col].astype(str).str.contains(keyword, na=False, case=False)]
            
            # เก็บผลลัพธ์ที่ได้ลงใน Session State
            st.session_state.filtered_data = filtered_df[selected_columns]

        # ----------------------------------------
        # 3. แสดงผลและดาวน์โหลด (ทำงานเมื่อมีความจำใน Session State แล้ว)
        # ----------------------------------------
        if st.session_state.filtered_data is not None:
            new_df = st.session_state.filtered_data
            st.write(f"ข้อมูลใหม่ที่ได้ (จำนวน {len(new_df)} แถว):", new_df)

            st.markdown("---")
            st.subheader("📥 ดาวน์โหลดข้อมูล")
            
            # ให้ผู้ใช้งานเลือกประเภทไฟล์ที่ต้องการดาวน์โหลด
            export_format = st.radio("เลือกฟอร์แมตไฟล์ที่ต้องการ:", ["CSV", "Excel (XLSX)"], horizontal=True)
            
            # สร้างปุ่มดาวน์โหลดตามฟอร์แมตที่เลือก
            if export_format == "CSV":
                csv = new_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 กดเพื่อดาวน์โหลดไฟล์ CSV", 
                    data=csv, 
                    file_name="filtered_data.csv", 
                    mime="text/csv"
                )
                
            elif export_format == "Excel (XLSX)":
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    new_df.to_excel(writer, index=False, sheet_name='FilteredData')
                
                st.download_button(
                    label="📥 กดเพื่อดาวน์โหลดไฟล์ Excel", 
                    data=buffer.getvalue(), 
                    file_name="filtered_data.xlsx", 
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    except ImportError:
        st.error("❌ ไม่สามารถอ่านหรือสร้างไฟล์ Excel ได้")
        st.info("💡 กรุณาติดตั้งไลบรารีโดยพิมพ์คำสั่ง: **pip install openpyxl xlsxwriter**")
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")
