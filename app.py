import streamlit as st
import pandas as pd
import io

# ฟังก์ชันสำหรับแปลงตัวอักษรคอลัมน์ Excel ให้เป็นตัวเลข Index (เช่น A=0, B=1, ..., AT=45)
def col2num(col_str):
    expn = 0
    col_num = 0
    for char in reversed(col_str.upper()):
        col_num += (ord(char) - ord('A') + 1) * (26 ** expn)
        expn += 1
    return col_num - 1

st.title("🔄 ระบบจัดฟอร์แมต Excel (OMS & Product List)")

# 1. ส่วนการอัปโหลดไฟล์ (อัปโหลดครั้งเดียวใช้ได้ทุกแท็บ)
uploaded_file = st.file_uploader("อัปโหลดไฟล์ Excel ต้นฉบับ (ไฟล์ ก)", type=['xlsx', 'xls'])
has_header = st.checkbox("ไฟล์ต้นฉบับมีหัวตาราง (ให้ระบบข้ามแถวแรกตอนดึงข้อมูล)", value=True)

if uploaded_file is not None:
    try:
        # กำหนดชื่อ Sheet เป้าหมาย
        target_sheet = "Data For List in"
        
        # อ่านไฟล์เพื่อเช็คชื่อ Sheet
        excel_file = pd.ExcelFile(uploaded_file)
        if target_sheet not in excel_file.sheet_names:
            st.error(f"❌ ไม่พบ Sheet ที่ชื่อว่า '{target_sheet}' ในไฟล์นี้")
            st.info(f"รายชื่อ Sheet ที่พบ: {', '.join(excel_file.sheet_names)}")
        else:
            # อ่านข้อมูลไฟล์ ก แค่ครั้งเดียว
            df_a = pd.read_excel(uploaded_file, sheet_name=target_sheet, header=None)
            
            # ตัดแถวแรกทิ้งถ้ามีหัวตาราง
            start_row = 1 if has_header else 0
            data_a = df_a.iloc[start_row:].reset_index(drop=True)

            # ฟังก์ชันดึงข้อมูลแบบปลอดภัยตามชื่อคอลัมน์ Excel
            def safe_get_col(col_letter):
                idx = col2num(col_letter)
                return data_a.iloc[:, idx] if idx < data_a.shape[1] else ""

            # 2. สร้างเมนูแบบแท็บ (Tabs)
            tab1, tab2 = st.tabs(["📄 ฟอร์แมตไฟล์ ข (OMS)", "📄 ฟอร์แมตไฟล์ ค (Goods List)"])
            
            # --- ส่วนของแท็บที่ 1 (ไฟล์ ข เดิม) ---
            with tab1:
                st.subheader("จัดการไฟล์ ข (รูปแบบ OMS)")
                
                new_columns_b = [
                    "Barcode", "Item number", "Commodity name", "Specification", 
                    "Shelf life item or not", "Life Day", "Warning Day", "Lock Up Day", 
                    "SN or not", "ASSET or not", "Introduction to commodities", "Cost price", 
                    "Price", "Basic unit", "Level 2 unit", "Level 2 QTY", 
                    "Level 2 barcode", "Level 3 unit", "Level 3 QTY", "Level 3 barcode", 
                    "Remark", "PictureURL", "Enterprise category", "Brand", 
                    "Alternative Barcode1", "Alternative Barcode2", "Alternative Barcode3", 
                    "Alternative Barcode4", "Alternative Barcode5"
                ]
                
                df_b = pd.DataFrame(columns=new_columns_b, index=data_a.index)
                df_b["Barcode"] = safe_get_col('AT')
                df_b["Commodity name"] = safe_get_col('R')
                df_b["Life Day"] = safe_get_col('Y')
                df_b["Price"] = safe_get_col('AH')
                df_b["Level 2 QTY"] = safe_get_col('AJ')
                df_b["Level 2 barcode"] = safe_get_col('P')
                df_b["Remark"] = safe_get_col('L')
                df_b["Warning Day"] = 210
                df_b["Lock Up Day"] = 180
                df_b = df_b.fillna("")

                st.dataframe(df_b.head(10))
                
                buffer_b = io.BytesIO()
                with pd.ExcelWriter(buffer_b, engine='openpyxl') as writer:
                    df_b.to_excel(writer, index=False, sheet_name='Data')
                
                st.download_button(
                    label="📥 ดาวน์โหลดไฟล์ Excel (OMS)",
                    data=buffer_b.getvalue(),
                    file_name="File_B_OMS.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            # --- ส่วนของแท็บที่ 2 (ไฟล์ ค ใหม่ตามเงื่อนไข) ---
            with tab2:
                st.subheader("จัดการไฟล์ ค (รูปแบบ Goods List)")
                
                # 1. กำหนดชื่อ Column ตามเงื่อนไข
                new_columns_c = [
                    "Goods barcode", "Goods Code", "Goods name", "Specification&model", 
                    "Cost price", "Price", "Introduction to commodities", "Remark", "PictureURL"
                ]
                
                # 2. สร้าง DataFrame ว่าง
                df_c = pd.DataFrame(columns=new_columns_c, index=data_a.index)
                
                # 3. Mapping ข้อมูล (ก -> ค)
                # A <- AT, C <- R, F <- AH, I <- BV
                df_c["Goods barcode"] = safe_get_col('AT')
                df_c["Goods name"] = safe_get_col('R')
                df_c["Price"] = safe_get_col('AH')
                df_c["PictureURL"] = safe_get_col('BV')
                
                df_c = df_c.fillna("") # จัดการค่าว่าง

                st.write("ตัวอย่างข้อมูลไฟล์ ค:")
                st.dataframe(df_c.head(10))

                # 4. ปุ่มดาวน์โหลดไฟล์ ค
                buffer_c = io.BytesIO()
                with pd.ExcelWriter(buffer_c, engine='openpyxl') as writer:
                    df_c.to_excel(writer, index=False, sheet_name='GoodsData')
                
                st.download_button(
                    label="📥 ดาวน์โหลดไฟล์ Excel (Goods List)",
                    data=buffer_c.getvalue(),
                    file_name="File_C_GoodsList.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาดในการประมวลผล: {e}")
