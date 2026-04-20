import streamlit as st
import pandas as pd

st.title("ระบบกรองข้อมูลอัตโนมัติ")

# 1. ส่วนการอัปโหลดไฟล์
uploaded_file = st.file_uploader("เลือกไฟล์ Excel หรือ CSV", type=['csv', 'xlsx'])

if uploaded_file is not None:
    # อ่านข้อมูล
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    st.write("ตัวอย่างข้อมูลต้นฉบับ:", df.head())

    # 2. เลือกคอลัมน์ที่ต้องการ
    all_columns = df.columns.tolist()
    selected_columns = st.multiselect("เลือกคอลัมน์ที่ต้องการเก็บไว้", all_columns, default=all_columns)

    # 3. ตั้งเงื่อนไขการกรอง (ตัวอย่าง: กรองตามชื่อคอลัมน์ที่เลือก)
    filter_col = st.selectbox("เลือกคอลัมน์ที่จะใช้เป็นเงื่อนไขกรอง", all_columns)
    keyword = st.text_input(f"พิมพ์ข้อความที่ต้องการค้นหาในคอลัมน์ {filter_col}")

    if st.button("ประมวลผลข้อมูล"):
            # กรองข้อมูลจากตารางหลัก (df) ก่อน
            filtered_df = df.copy()
            if keyword:
                # แก้ไขโดยเติม .str. เข้าไป
                filtered_df = filtered_df[filtered_df[filter_col].astype(str).str.contains(keyword, na=False)]
            
            # หลังจากกรองเสร็จ ค่อยตัดคอลัมน์ตามที่ผู้ใช้เลือก
            new_df = filtered_df[selected_columns]
            
            st.write("ข้อมูลใหม่ที่ได้:", new_df)

            # 4. ปุ่มดาวน์โหลด
            csv = new_df.to_csv(index=False).encode('utf-8')
            st.download_button("ดาวน์โหลดไฟล์ใหม่ (CSV)", csv, "filtered_data.csv", "text/csv")
