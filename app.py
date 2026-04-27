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

# อัปโหลดไฟล์ ก (ทำแค่ครั้งเดียว ใช้ได้ทั้ง 2 แท็บ)
uploaded_file = st.file_uploader("อัปโหลดไฟล์ Excel ต้นฉบับ (ไฟล์ ก)", type=['xlsx', 'xls'])
has_header = st.checkbox("ไฟล์ต้นฉบับมีหัวตาราง (ให้ระบบข้ามแถวแรกตอนดึงข้อมูล)", value=True)

if uploaded_file is not None:
    try:
        target_sheet = "Data For List in"
        
        # อ่านไฟล์เพื่อเช็คชื่อ Sheet ก่อน
        excel_file = pd.ExcelFile(uploaded_file)
        if target_sheet not in excel_file.sheet_names:
            st.error(f"❌ ไม่พบ Sheet ที่ชื่อว่า '{target_sheet}' ในไฟล์นี้")
            st.info(f"รายชื่อ Sheet ที่พบในไฟล์: {', '.join(excel_file.sheet_names)}")
        else:
            # อ่านข้อมูลต้นฉบับเก็บไว้ (ใช้อ้างอิงได้ทั้งไฟล์ OMS และ ไฟล์ ค)
            df_a = pd.read_excel(uploaded_file, sheet_name=target_sheet, header=None)
            
            start_row = 1 if has_header else 0
            data_a = df_a.iloc[start_row:].reset_index(drop=True)

            def safe_get_col(col_letter):
                idx = col2num(col_letter)
                return data_a.iloc[:, idx] if idx < data_a.shape[1] else ""

            # ---------------------------------------------------------
            # สร้างระบบ Tabs เพื่อแยกหน้าการทำงาน
            # ---------------------------------------------------------
            tab1, tab2 = st.tabs(["📄 สร้างไฟล์ Excel OMS", "📄 สร้างไฟล์ ค"])

            # ==========================================
            # TAB 1: สำหรับไฟล์ OMS (โค้ดเดิมของคุณ)
            # ==========================================
            with tab1:
                st.subheader("พรีวิวข้อมูล: ไฟล์ Excel OMS")
                
                new_columns_oms = [
                    "Barcode", "Item number", "Commodity name", "Specification", 
                    "Shelf life item or not", "Life Day", "Warning Day", "Lock Up Day", 
                    "SN or not", "ASSET or not", "Introduction to commodities", "Cost price", 
                    "Price", "Basic unit", "Level 2 unit", "Level 2 QTY", 
                    "Level 2 barcode", "Level 3 unit", "Level 3 QTY", "Level 3 barcode", 
                    "Remark", "PictureURL", "Enterprise category", "Brand", 
                    "Alternative Barcode1", "Alternative Barcode2", "Alternative Barcode3", 
                    "Alternative Barcode4", "Alternative Barcode5"
                ]
                
                df_oms = pd.DataFrame(columns=new_columns_oms, index=data_a.index)
                
                df_oms["Barcode"] = safe_get_col('AT')         
                df_oms["Commodity name"] = safe_get_col('R')   
                df_oms["Life Day"] = safe_get_col('Y')         
                df_oms["Price"] = safe_get_col('AH')           
                df_oms["Level 2 QTY"] = safe_get_col('AJ')     
                df_oms["Level 2 barcode"] = safe_get_col('P')  
                df_oms["Remark"] = safe_get_col('L')           
                df_oms["Warning Day"] = 210
                df_oms["Lock Up Day"] = 180

                df_oms = df_oms.fillna("")

                st.success(f"✅ ดึงข้อมูลสำเร็จพร้อมดาวน์โหลด!")
                st.dataframe(df_oms.head(10))

                buffer_oms = io.BytesIO()
                with pd.ExcelWriter(buffer_oms, engine='openpyxl') as writer:
                    df_oms.to_excel(writer, index=False, sheet_name='Data')
                    
                st.download_button(
                    label="📥 ดาวน์โหลดไฟล์ Excel OMS",
                    data=buffer_oms.getvalue(),
                    file_name="Formatted_Data_OMS.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            # ==========================================
            # TAB 2: สำหรับไฟล์ ค (รอใส่เงื่อนไข)
            # ==========================================
            with tab2:
                st.subheader("พรีวิวข้อมูล: ไฟล์ ค")
                st.info("กำลังรอเงื่อนไขการดึงข้อมูลสำหรับไฟล์ ค ...")
                
                # โค้ดส่วนนี้จะทำงานเหมือนแท็บแรก แต่เปลี่ยนหัวคอลัมน์และการดึงตัวอักษร
                # ...

    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาดในการประมวลผล: {e}")
