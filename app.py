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

st.title("🔄 ระบบจัดฟอร์แมต Excel (OMS & Product Set)")

# 1. ส่วนการอัปโหลดไฟล์
uploaded_file = st.file_uploader("อัปโหลดไฟล์ Excel ต้นฉบับ (ไฟล์ ก)", type=['xlsx', 'xls'])
has_header = st.checkbox("ไฟล์ต้นฉบับมีหัวตาราง (ให้ระบบข้ามแถวแรกตอนดึงข้อมูล)", value=True)

if uploaded_file is not None:
    try:
        target_sheet = "Data For List in"
        
        # อ่านไฟล์เพื่อเช็คชื่อ Sheet
        excel_file = pd.ExcelFile(uploaded_file)
        if target_sheet not in excel_file.sheet_names:
            st.error(f"❌ ไม่พบ Sheet ที่ชื่อว่า '{target_sheet}' ในไฟล์นี้")
            st.info(f"รายชื่อ Sheet ที่พบ: {', '.join(excel_file.sheet_names)}")
        else:
            # อ่านข้อมูลไฟล์ ก แค่ครั้งเดียว
            df_a = pd.read_excel(uploaded_file, sheet_name=target_sheet, header=None)
            
            start_row = 1 if has_header else 0
            data_a = df_a.iloc[start_row:].reset_index(drop=True)

            def safe_get_col(col_letter):
                idx = col2num(col_letter)
                return data_a.iloc[:, idx] if idx < data_a.shape[1] else ""

            # 2. สร้างเมนูแบบแท็บ (Tabs)
            tab1, tab2 = st.tabs(["📄 ฟอร์แมตไฟล์ ข (OMS)", "📄 ฟอร์แมตไฟล์ ค (Commodity Set)"])
            
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
                    label="📥 ดาวน์โหลดไฟล์ Excel OMS (Packเดี่ยว)",
                    data=buffer_b.getvalue(),
                    file_name="File_B_OMS.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            # --- ส่วนของแท็บที่ 2 (ไฟล์ ค: Multi-Sheet + Merged Header) ---
            with tab2:
                st.subheader("จัดการไฟล์ ค (Commodity set & Set details)")

                # เตรียมข้อมูล Sheet 1: Commodity set
                columns_sheet1 = [
                    "Goods barcode", "Goods Code", "Goods name", "Specification&model", 
                    "Cost price", "Price", "Introduction to commodities", "Remark", "PictureURL"
                ]
                df_c1 = pd.DataFrame(columns=columns_sheet1, index=data_a.index)
                df_c1["Goods barcode"] = safe_get_col('AT')
                df_c1["Goods name"] = safe_get_col('R')
                df_c1["Price"] = safe_get_col('AH')
                df_c1["PictureURL"] = safe_get_col('BV')
                df_c1 = df_c1.fillna("")

                # ชื่อ Column แบบไม่ซ้ำกัน เพื่อให้ Streamlit พรีวิวได้ไม่พัง
                columns_sheet2_preview = [
                    "Goods barcode (1)", "Goods name (1)", "specification", 
                    "Goods barcode (2)", "Goods name (2)", "Specification&model", "Set quantity"
                ]
                
                # ชื่อ Column แบบซ้ำกัน (ของจริง) ที่จะเอาไปเขียนลงไฟล์ Excel
                columns_sheet2_excel = [
                    "Goods barcode", "Goods name", "specification", 
                    "Goods barcode", "Goods name", "Specification&model", "Set quantity"
                ]

                # โหลดข้อมูลใส่ DataFrame แบบ Preview
                df_c2 = pd.DataFrame(columns=columns_sheet2_preview, index=data_a.index)
                df_c2.iloc[:, 0] = safe_get_col('AT') # Column A
                df_c2.iloc[:, 1] = safe_get_col('R')  # Column B
                df_c2 = df_c2.fillna("")

                buffer_c = io.BytesIO()
                with pd.ExcelWriter(buffer_c, engine='xlsxwriter') as writer:
                    # เขียน Sheet 1
                    df_c1.to_excel(writer, index=False, sheet_name='Commodity set')

                    # เขียน Sheet 2
                    workbook = writer.book
                    worksheet = workbook.add_worksheet('Set details')
                    
                    header_format = workbook.add_format({
                        'bold': True,
                        'align': 'center',
                        'valign': 'vcenter',
                        'border': 1,
                        'bg_color': '#F0F0F0'
                    })

                    # --- แถวที่ 1: Merged Headers ---
                    worksheet.merge_range('A1:C1', 'Commodity set information', header_format)
                    worksheet.merge_range('D1:G1', 'Set details information', header_format)

                    # --- แถวที่ 2: ใช้ชื่อ Column ของจริง ---
                    for col_num, value in enumerate(columns_sheet2_excel):
                        worksheet.write(1, col_num, value, header_format)

                    # --- ข้อมูลแถวที่ 3 เป็นต้นไป ---
                    for row_num, row_data in enumerate(df_c2.values):
                        for col_num, cell_value in enumerate(row_data):
                            worksheet.write(row_num + 2, col_num, cell_value)

                st.success("✅ สร้างไฟล์ ค พร้อม 2 Sheet และรวมหัวตารางสำเร็จ!")
                
                # --- พรีวิวตาราง ---
                st.write("ตัวอย่าง Sheet 1 (Commodity set):")
                st.dataframe(df_c1.head(10))
                
                st.write("ตัวอย่าง Sheet 2 (Set details):")
                st.dataframe(df_c2.head(10)) 

                # --- ปุ่มดาวน์โหลด ---
                st.download_button(
                    label="📥 ดาวน์โหลดไฟล์ Excel OMS (Pack2&ยกลัง)",
                    data=buffer_c.getvalue(),
                    file_name="File_C_CommoditySet.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")
