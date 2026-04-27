import streamlit as st
import pandas as pd
import io

# ฟังก์ชันสำหรับแปลงตัวอักษรคอลัมน์ Excel ให้เป็นตัวเลข Index
def col2num(col_str):
    expn = 0
    col_num = 0
    for char in reversed(col_str.upper()):
        col_num += (ord(char) - ord('A') + 1) * (26 ** expn)
        expn += 1
    return col_num - 1

st.title("🔄 ระบบจัดฟอร์แมต Excel (เฉพาะ Sheet: Data For List in)")

# 1. อัปโหลดไฟล์ ก
uploaded_file = st.file_uploader("อัปโหลดไฟล์ Excel ต้นฉบับ (ไฟล์ ก)", type=['xlsx', 'xls'])
has_header = st.checkbox("ไฟล์ต้นฉบับมีหัวตาราง (ให้ระบบข้ามแถวแรกตอนดึงข้อมูล)", value=True)

if uploaded_file is not None:
    try:
        # --- จุดที่แก้ไข: ระบุชื่อ Sheet และดึงข้อมูล ---
        target_sheet = "Data For List in"
        
        # อ่านไฟล์เพื่อเช็คชื่อ Sheet ก่อน
        excel_file = pd.ExcelFile(uploaded_file)
        if target_sheet not in excel_file.sheet_names:
            st.error(f"❌ ไม่พบ Sheet ที่ชื่อว่า '{target_sheet}' ในไฟล์นี้")
            st.info(f"รายชื่อ Sheet ที่พบในไฟล์: {', '.join(excel_file.sheet_names)}")
        else:
            # อ่านข้อมูลเฉพาะ Sheet ที่กำหนด
            df_a = pd.read_excel(uploaded_file, sheet_name=target_sheet, header=None)
            
            # ตัดแถวแรกทิ้งถ้าผู้ใช้บอกว่ามีหัวตาราง
            start_row = 1 if has_header else 0
            data_a = df_a.iloc[start_row:].reset_index(drop=True)

            # 2. รายชื่อหัวตารางใหม่ทั้งหมด 29 คอลัมน์ (A ไปถึง AC)
            new_columns = [
                "Barcode", "Item number", "Commodity name", "Specification", 
                "Shelf life item or not", "Life Day", "Warning Day", "Lock Up Day", 
                "SN or not", "ASSET or not", "Introduction to commodities", "Cost price", 
                "Price", "Basic unit", "Level 2 unit", "Level 2 QTY", 
                "Level 2 barcode", "Level 3 unit", "Level 3 QTY", "Level 3 barcode", 
                "Remark", "PictureURL", "Enterprise category", "Brand", 
                "Alternative Barcode1", "Alternative Barcode2", "Alternative Barcode3", 
                "Alternative Barcode4", "Alternative Barcode5"
            ]
            
            # สร้าง DataFrame สำหรับ Excel ข
            df_b = pd.DataFrame(columns=new_columns, index=data_a.index)
            
            # ฟังก์ชันดึงข้อมูลแบบปลอดภัย
            def safe_get_col(col_letter):
                idx = col2num(col_letter)
                return data_a.iloc[:, idx] if idx < data_a.shape[1] else ""

            # 3. Mapping ข้อมูล (ก -> ข)
            df_b["Barcode"] = safe_get_col('AT')         # Col A <- AT
            df_b["Commodity name"] = safe_get_col('R')   # Col C <- R
            df_b["Life Day"] = safe_get_col('Y')         # Col F <- Y
            df_b["Price"] = safe_get_col('AH')           # Col M <- AH
            df_b["Level 2 QTY"] = safe_get_col('AJ')     # Col P <- AJ
            df_b["Level 2 barcode"] = safe_get_col('P')  # Col Q <- P
            df_b["Remark"] = safe_get_col('L')           # Col U <- L
            
            # 4. ใส่ค่าคงที่
            df_b["Warning Day"] = 210
            df_b["Lock Up Day"] = 180

            # จัดการค่าว่าง
            df_b = df_b.fillna("")

            st.success(f"✅ ดึงข้อมูลจาก Sheet '{target_sheet}' เรียบร้อยแล้ว!")
            st.dataframe(df_b.head(10))

            # 5. ปุ่มดาวน์โหลด
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_b.to_excel(writer, index=False, sheet_name='Data')
                
            st.download_button(
                label="📥 ดาวน์โหลดไฟล์ Excel ข",
                data=buffer.getvalue(),
                file_name="Formatted_Data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาดในการประมวลผล: {e}")
