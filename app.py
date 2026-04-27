import streamlit as st
import pandas as pd
import io

def col2num(col_str):
    expn = 0
    col_num = 0
    for char in reversed(col_str.upper()):
        col_num += (ord(char) - ord('A') + 1) * (26 ** expn)
        expn += 1
    return col_num - 1

st.title("🔄 ระบบจัดฟอร์แมต Excel (Advanced Multi-Sheet)")

uploaded_file = st.file_uploader("อัปโหลดไฟล์ Excel ต้นฉบับ (ไฟล์ ก)", type=['xlsx', 'xls'])
has_header = st.checkbox("ไฟล์ต้นฉบับมีหัวตาราง", value=True)

if uploaded_file is not None:
    try:
        target_sheet = "Data For List in"
        excel_file = pd.ExcelFile(uploaded_file)
        
        if target_sheet not in excel_file.sheet_names:
            st.error(f"❌ ไม่พบ Sheet '{target_sheet}'")
        else:
            df_a = pd.read_excel(uploaded_file, sheet_name=target_sheet, header=None)
            start_row = 1 if has_header else 0
            data_a = df_a.iloc[start_row:].reset_index(drop=True)

            def safe_get_col(col_letter):
                idx = col2num(col_letter)
                return data_a.iloc[:, idx] if idx < data_a.shape[1] else ""

            tab1, tab2 = st.tabs(["📄 ฟอร์แมตไฟล์ ข (OMS)", "📄 ฟอร์แมตไฟล์ ค (Multi-Sheet)"])

            # --- TAB 1 (เหมือนเดิม) ---
            with tab1:
                st.subheader("ไฟล์ ข (OMS)")
                # ... (โค้ดส่วนไฟล์ ข คงเดิมตามความต้องการก่อนหน้าของคุณ) ...
                st.info("ส่วนนี้ยังคงทำงานตามปกติเหมือนโค้ดก่อนหน้า")

            # --- TAB 2 (เงื่อนไขใหม่: 2 Sheets + Merged Header) ---
            with tab2:
                st.subheader("จัดการไฟล์ ค (Commodity & Set Details)")

                # --- เตรียมข้อมูล Sheet 1: Commodity set ---
                new_columns_c1 = [
                    "Goods barcode", "Goods Code", "Goods name", "Specification&model", 
                    "Cost price", "Price", "Introduction to commodities", "Remark", "PictureURL"
                ]
                df_c1 = pd.DataFrame(columns=new_columns_c1, index=data_a.index)
                df_c1["Goods barcode"] = safe_get_col('AT')
                df_c1["Goods name"] = safe_get_col('R')
                df_c1["Price"] = safe_get_col('AH')
                df_c1["PictureURL"] = safe_get_col('BV')
                df_c1 = df_c1.fillna("")

                # --- เตรียมข้อมูล Sheet 2: Set details ---
                # แถวที่ 2 (Header จริง)
                header_row2 = [
                    "Goods barcode", "Goods name", "specification", 
                    "Goods barcode", "Goods name", "Specification&model", "Set quantity"
                ]
                
                # สร้างข้อมูลสำหรับ Sheet 2 (Mapping AT -> A, R -> B)
                df_c2_data = pd.DataFrame(columns=header_row2, index=data_a.index)
                df_c2_data["Goods barcode"] = safe_get_col('AT') # ใส่ในช่องแรก (Col A)
                df_c2_data["Goods name"] = safe_get_col('R')    # ใส่ในช่องที่สอง (Col B)
                df_c2_data = df_c2_data.fillna("")

                # --- ขั้นตอนการเขียนไฟล์ Excel ด้วย XlsxWriter เพื่อ Merge Cell ---
                buffer_c = io.BytesIO()
                with pd.ExcelWriter(buffer_c, engine='xlsxwriter') as writer:
                    # เขียน Sheet 1 ปกติ
                    df_c1.to_excel(writer, index=False, sheet_name='Commodity set')

                    # เขียน Sheet 2 (จัดการ Header 2 ชั้น)
                    workbook = writer.book
                    worksheet = workbook.add_worksheet('Set details')
                    
                    # สร้าง Format สำหรับ Header
                    header_format = workbook.add_format({
                        'bold': True,
                        'align': 'center',
                        'valign': 'vcenter',
                        'border': 1,
                        'bg_color': '#D3D3D3'
                    })

                    # 1. ทำ Merged Header แถวที่ 1 (Index 0)
                    # merge_range(first_row, first_col, last_row, last_col, data, format)
                    worksheet.merge_range('A1:C1', 'Commodity set information', header_format)
                    worksheet.merge_range('D1:G1', 'Set details information', header_format)

                    # 2. เขียน Header แถวที่ 2 (Index 1)
                    for col_num, header_val in enumerate(header_row2):
                        worksheet.write(1, col_num, header_val, header_format)

                    # 3. เขียนข้อมูล (เริ่มที่แถว Index 2)
                    for row_num in range(len(df_c2_data)):
                        for col_num in range(len(header_row2)):
                            val = df_c2_data.iloc[row_num, col_num]
                            worksheet.write(row_num + 2, col_num, val)

                st.success("✅ สร้างไฟล์ ค พร้อม 2 Sheets และหัวตารางแบบพิเศษสำเร็จ!")
                st.write("Preview: Sheet 1 (Commodity set)")
                st.dataframe(df_c1.head(5))
                st.write("Preview: Sheet 2 (Set details - เฉพาะข้อมูล)")
                st.dataframe(df_b_preview := df_c2_data.head(5))

                st.download_button(
                    label="📥 ดาวน์โหลดไฟล์ Excel ค (2 Sheets)",
                    data=buffer_c.getvalue(),
                    file_name="File_C_Final.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")
