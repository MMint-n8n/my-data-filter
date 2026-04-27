import streamlit as st
import pandas as pd
import io

# ==========================================
# 🚀 ตั้งค่าหน้าเว็บ (Page Config)
# ==========================================
st.set_page_config(
    page_title="NEO-OMS Data Core",
    page_icon="🌌",
    layout="wide"
)

# ==========================================
# 🛸 ฝังโค้ด CSS สไตล์ Sci-Fi (Cyberpunk / Neon)
# ==========================================
st.markdown("""
    <style>
    /* เปลี่ยนสีพื้นหลังหลัก (ทำงานได้ดีสุดเมื่อตั้ง Theme ของ Streamlit เป็น Dark mode ด้วย) */
    .stApp {
        background-color: #0b0f19;
        color: #00f0ff;
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* ตกแต่งหัวข้อให้มีแสงเรืองแสง (Neon Glow) */
    h1, h2, h3 {
        color: #00f0ff !important;
        text-shadow: 0px 0px 8px rgba(0, 240, 255, 0.8), 0px 0px 15px rgba(0, 240, 255, 0.5);
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* ตกแต่งปุ่มดาวน์โหลดและปุ่มทั่วไป */
    .stDownloadButton > button, .stButton > button {
        background-color: rgba(0, 240, 255, 0.1) !important;
        color: #00f0ff !important;
        border: 1px solid #00f0ff !important;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.4) !important;
        border-radius: 4px !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
        font-weight: bold;
    }
    
    /* เอฟเฟกต์ตอนเอาเมาส์ชี้ปุ่ม */
    .stDownloadButton > button:hover, .stButton > button:hover {
        background-color: #00f0ff !important;
        color: #0b0f19 !important;
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.8) !important;
    }

    /* ตกแต่งกล่องข้อความแจ้งเตือน (Success / Error / Info) */
    div[data-testid="stAlert"] {
        background-color: rgba(11, 15, 25, 0.8);
        border-left: 4px solid #00f0ff;
        color: #e0e0e0;
    }
    
    /* ตกแต่งแท็บ (Tabs) */
    button[data-baseweb="tab"] {
        color: #7a8b9a !important;
        font-family: 'Courier New', Courier, monospace;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #00f0ff !important;
        border-bottom-color: #00f0ff !important;
        text-shadow: 0px 0px 5px rgba(0, 240, 255, 0.5);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# ⚙️ โค้ดส่วนการประมวลผลหลัก
# ==========================================

# ฟังก์ชันสำหรับแปลงตัวอักษรคอลัมน์ Excel ให้เป็นตัวเลข Index
def col2num(col_str):
    expn = 0
    col_num = 0
    for char in reversed(col_str.upper()):
        col_num += (ord(char) - ord('A') + 1) * (26 ** expn)
        expn += 1
    return col_num - 1

st.title("🌌 ระบบประมวลผลข้อมูล NEO-OMS")
st.markdown("---")

# 1. ส่วนการอัปโหลดไฟล์
uploaded_file = st.file_uploader("📂 อัปโหลดไฟล์ Excel ต้นฉบับ (ไฟล์ ก)", type=['xlsx', 'xls'])
has_header = st.checkbox("⚙️ ไฟล์ต้นฉบับมีหัวตาราง (ให้ระบบข้ามแถวแรกตอนดึงข้อมูล)", value=True)

if uploaded_file is not None:
    try:
        target_sheet = "Data For List in"
        
        excel_file = pd.ExcelFile(uploaded_file)
        if target_sheet not in excel_file.sheet_names:
            st.error(f"❌ ระบบล้มเหลว: ไม่พบ Sheet ที่ชื่อว่า '{target_sheet}' ในฐานข้อมูล")
            st.info(f"รายชื่อ Sheet ที่ตรวจพบ: {', '.join(excel_file.sheet_names)}")
        else:
            df_a = pd.read_excel(uploaded_file, sheet_name=target_sheet, header=None)
            
            start_row = 1 if has_header else 0
            data_a = df_a.iloc[start_row:].reset_index(drop=True)

            def safe_get_col(col_letter):
                idx = col2num(col_letter)
                return data_a.iloc[:, idx] if idx < data_a.shape[1] else ""

            # 2. สร้างเมนูแบบแท็บ (Tabs)
            tab1, tab2 = st.tabs(["💾 ประมวลผล OMS (Pack เดี่ยว)", "📦 ประมวลผล OMS (Pack2 & ยกลัง)"])
            
            # --- ส่วนของแท็บที่ 1 ---
            with tab1:
                st.subheader("TERMINAL: รูปแบบ OMS (Pack เดี่ยว)")
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
                    label="🚀 ดึงข้อมูล Excel OMS (Pack เดี่ยว)",
                    data=buffer_b.getvalue(),
                    file_name="File_B_OMS.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            # --- ส่วนของแท็บที่ 2 ---
            with tab2:
                st.subheader("TERMINAL: รูปแบบ Commodity set & Set details")

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

                columns_sheet2_preview = [
                    "Goods barcode (1)", "Goods name (1)", "specification", 
                    "Goods barcode (2)", "Goods name (2)", "Specification&model", "Set quantity"
                ]
                
                columns_sheet2_excel = [
                    "Goods barcode", "Goods name", "specification", 
                    "Goods barcode", "Goods name", "Specification&model", "Set quantity"
                ]

                df_c2 = pd.DataFrame(columns=columns_sheet2_preview, index=data_a.index)
                df_c2.iloc[:, 0] = safe_get_col('AT') 
                df_c2.iloc[:, 1] = safe_get_col('R')  
                df_c2 = df_c2.fillna("")

                buffer_c = io.BytesIO()
                with pd.ExcelWriter(buffer_c, engine='xlsxwriter') as writer:
                    df_c1.to_excel(writer, index=False, sheet_name='Commodity set')

                    workbook = writer.book
                    worksheet = workbook.add_worksheet('Set details')
                    
                    header_format = workbook.add_format({
                        'bold': True,
                        'align': 'center',
                        'valign': 'vcenter',
                        'border': 1,
                        'bg_color': '#1f2937',
                        'font_color': '#00f0ff'
                    })

                    worksheet.merge_range('A1:C1', 'Commodity set information', header_format)
                    worksheet.merge_range('D1:G1', 'Set details information', header_format)

                    for col_num, value in enumerate(columns_sheet2_excel):
                        worksheet.write(1, col_num, value, header_format)

                    for row_num, row_data in enumerate(df_c2.values):
                        for col_num, cell_value in enumerate(row_data):
                            worksheet.write(row_num + 2, col_num, cell_value)

                st.success("✅ ระบบประมวลผลเสร็จสิ้น: โครงสร้างไฟล์ถูกเข้ารหัสพร้อมดาวน์โหลด")
                
                st.write(">> ตัวอย่างข้อมูล Sheet 1 (Commodity set):")
                st.dataframe(df_c1.head(10))
                
                st.write(">> ตัวอย่างข้อมูล Sheet 2 (Set details):")
                st.dataframe(df_c2.head(10)) 

                st.download_button(
                    label="🚀 ดึงข้อมูล Excel OMS (Pack2 & ยกลัง)",
                    data=buffer_c.getvalue(),
                    file_name="File_C_CommoditySet.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาดในระบบประมวลผล: {e}")
