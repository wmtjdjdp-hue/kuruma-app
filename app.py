import streamlit as st
import io, json, re, os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.units import mm
from pypdf import PdfReader, PdfWriter

# --- 1. フォント設定 ---
font_name = 'HeiseiKakuGo-W5'
pdfmetrics.registerFont(UnicodeCIDFont(font_name))

# --- 2. 設定の保存・読込ロジック ---
SAVE_FILE = "user_settings_v2.json"

def save_settings(data_dict):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data_dict, f, ensure_ascii=False)

def load_settings():
    default = {
        "k_name": "", "k_addr": "",
        "m_name": "",
        "s_name": "", "s_addr": "",
        "c12": "", "c2": "", "c10": ""
    }
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                return {**default, **saved}
        except:
            pass
    return default

def to_half_width(text):
    if not text: return ""
    return text.translate(str.maketrans(
        '０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ－',
        '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-'
    ))

# --- 3. 各書類の描画関数 ---

def draw_jyuuryou(can, json_data):
    cert = json_data.get("CertInfo", {})
    car_no = cert.get("EntryNoCarNo", "").replace("　", "").strip()
    app_name = cert.get("UsernameLowLevelChar", "")
    if app_name in ["＊＊＊", "", "使用者に同じ"]:
        app_name = cert.get("OwnernameLowLevelChar", "")
    app_addr = cert.get("UserAddress", "")
    if app_addr in ["＊＊＊", "", "使用者住所に同じ"]:
        app_addr = cert.get("OwnerAddressChar", "") + cert.get("OwnerAddressNumValue", "")
   
    can.setFont(font_name, 10); can.drawString(72.0 * mm, 156 * mm, car_no)
    can.setFont(font_name, 15); can.drawString(160 * mm, 165 * mm, app_name)
    can.setFont(font_name, 13); t_addr = can.beginText(160 * mm, 155 * mm); t_addr.setCharSpace(0); t_addr.textLine(app_addr); can.drawText(t_addr)
    can.showPage()

def draw_page(can, json_data, manual_name, manual_addr):
    cert = json_data.get("CertInfo", {})
    raw_car_no = cert.get("EntryNoCarNo", "").replace("　", " ").strip()
    all_parts = re.findall(r'[^\s]+', raw_car_no)
    area = all_parts[0] if len(all_parts) > 0 else ""
    code = hira = num = ""
    for p in all_parts[1:]:
        if p.isdigit() and len(p) <= 3: code = p
        elif len(p) == 1 and not p.isdigit(): hira = p
        else: num = p
    raw_vin = cert.get("CarNo", "").replace("－", "-")
    vin_last = raw_vin.split("-")[-1] if "-" in raw_vin else raw_vin
   
    app_name = cert.get("UsernameLowLevelChar", "")
    if app_name in ["＊＊＊", "", "使用者に同じ"]: app_name = cert.get("OwnernameLowLevelChar", "")
    app_addr = cert.get("UserAddress", "")
    if app_addr in ["＊＊＊", "", "使用者住所に同じ"]: app_addr = cert.get("OwnerAddressChar", "") + cert.get("OwnerAddressNumValue", "")
   
    exm_name = manual_name if manual_name else app_name
    exm_addr = manual_addr if manual_addr else app_addr
   
    can.setFont(font_name, 24); t_area = can.beginText(13.0*mm, 170.0*mm); t_area.setCharSpace(6.5); t_area.textLine(area); can.drawText(t_area)
    can.setFont(font_name, 18); t_code = can.beginText(58.5*mm, 170.5*mm); t_code.setCharSpace(-1.0); t_code.textLine(code); can.drawText(t_code)
    can.setFont(font_name, 25); can.drawString(80.5*mm, 170.0*mm, hira)
    can.setFont(font_name, 18); can.drawString(93.5*mm, 170.5*mm, num); can.drawString(131.5*mm, 170.5*mm, vin_last)
    can.setFont(font_name, 25); can.drawString(45*mm, 111*mm, app_name); can.drawString(45*mm, 72*mm, exm_name)
    can.setFont(font_name, 15); can.drawString(28*mm, 100*mm, app_addr); can.drawString(28*mm, 61*mm, exm_addr)
    can.showPage()

def draw_meigi(can, json_data, user_name, s_name, s_addr, c12, c2, c10):
    cert = json_data.get("CertInfo", {})
    raw_car_no = cert.get("EntryNoCarNo", "").replace("　", " ").strip()
    all_parts = re.findall(r'[^\s]+', raw_car_no)
    area = all_parts[0] if len(all_parts) > 0 else ""
    code = hira = num = ""
    for p in all_parts[1:]:
        if p.isdigit() and len(p) <= 3: code = p
        elif len(p) == 1 and not p.isdigit(): hira = p
        else: num = p
    raw_vin = cert.get("CarNo", "").replace("－", "-")
    vin_last = raw_vin.split("-")[-1] if "-" in raw_vin else raw_vin
   
    app_name = cert.get("UsernameLowLevelChar", "")
    if app_name in ["＊＊＊", "", "使用者に同じ"]:
        app_name = cert.get("OwnernameLowLevelChar", "")
    app_address = cert.get("UserAddress", "")
    if app_address in ["＊＊＊", "", "使用者住所に同じ"]:
        app_address = cert.get("OwnerAddressChar", "") + cert.get("OwnerAddressNumValue", "")
   
    can.setFont(font_name, 20); t_area = can.beginText(14.0*mm, 156.0*mm); t_area.setCharSpace(10.0); t_area.textLine(area); can.drawText(t_area)
    can.setFont(font_name, 18); t_code = can.beginText(58.5*mm, 156.0*mm); t_code.setCharSpace(-1.2); t_code.textLine(code); can.drawText(t_code)
    can.setFont(font_name, 20); can.drawString(82.0*mm, 156.0*mm, hira)
    can.setFont(font_name, 18); can.drawString(93.5*mm, 156.0*mm, num); t_vin = can.beginText(131.5*mm, 156.0*mm); t_vin.setCharSpace(-1.0); t_vin.textLine(vin_last); can.drawText(t_vin)
   
    can.setFont(font_name, 22)
    start_x = 23.5; y_pos = 127.0; char_interval = 11.0
    for i, char in enumerate(user_name):
        if char not in [" ", "　"]:
            can.drawString((start_x + i * char_interval) * mm, y_pos * mm, char)

    new_y = 112.3 * mm
    can.setFont(font_name, 20)
    t_12 = can.beginText(23.4*mm, new_y); t_12.setCharSpace(3.5); t_12.textLine(to_half_width(c12)); can.drawText(t_12)
    t_2 = can.beginText(98.5*mm, new_y); t_2.setCharSpace(3.5); t_2.textLine(to_half_width(c2)); can.drawText(t_2)
    t_10_val = to_half_width(c10); start_x_10 = 115.5 * mm; step_x_10 = 6.0 * mm
    for i, char in enumerate(t_10_val):
        can.drawCentredString(start_x_10 + (i * step_x_10), new_y, char)

    can.setFont(font_name, 15); can.drawString(150.0*mm, 15.0*mm, app_name)
    can.setFont(font_name, 7); t_addr = can.beginText(130.0*mm, 7.0*mm); t_addr.setCharSpace(-0.3); t_addr.textLine(app_address); can.drawText(t_addr)
   
    can.setFont(font_name, 35); can.drawString(50.0*mm, 10.0*mm, "同上"); can.drawString(160.0*mm, 30.0*mm, "同下")
    can.setFont(font_name, 15); can.drawString(50 * mm, 36 * mm, s_name); can.setFont(font_name, 10); can.drawString(22 * mm, 26 * mm, s_addr)
   
    can.setFont(font_name, 18); can.drawString(12.0*mm, 53.5*mm, "1"); can.drawString(12.0*mm, 72.5*mm, "1"); can.drawString(12.0*mm, 91.0*mm, "1")
   
    can.setFillColorRGB(0, 0, 0)
    can.setFont(font_name, 20)
    can.drawString(240 * mm, 10 * mm, "移転登録")
    can.showPage()

def draw_massho(can, json_data, m_name_manual, s_addr_manual):
    cert = json_data.get("CertInfo", {})
    raw_car_no = cert.get("EntryNoCarNo", "").replace("　", " ").strip()
    all_parts = re.findall(r'[^\s]+', raw_car_no)
    area = all_parts[0] if all_parts else ""
    code = hira = num = ""
    for p in all_parts[1:]:
        if p.isdigit() and len(p) <= 3: code = p
        elif len(p) == 1 and not p.isdigit(): hira = p
        else: num = p
    raw_vin = cert.get("CarNo", "").replace("－", "-")
    vin_last = raw_vin.split("-")[-1] if "-" in raw_vin else raw_vin
    vin_7 = vin_last[-7:] if len(vin_last) >= 7 else vin_last

    u_name = cert.get("UsernameLowLevelChar", "")
    u_addr = cert.get("UserAddress", "")
    if u_name in ["＊＊＊", "", "所有者に同じ"]:
        u_name = cert.get("OwnernameLowLevelChar", "")
    if u_addr in ["＊＊＊", "", "所有者住所に同じ"]:
        u_addr = cert.get("OwnerAddressChar", "") + cert.get("OwnerAddressNumValue", "")

    can.setFont(font_name, 24)
    t_area = can.beginText(13.0 * mm, 170.0 * mm); t_area.setCharSpace(6.5); t_area.textLine(area); can.drawText(t_area)
    can.setFont(font_name, 18)
    t_code = can.beginText(58.5 * mm, 170.5 * mm); t_code.setCharSpace(-1.0); t_code.textLine(code); can.drawText(t_code)
    can.setFont(font_name, 25); can.drawString(80.5 * mm, 170.0 * mm, hira)
    can.setFont(font_name, 18); can.drawString(93.5 * mm, 170.5 * mm, num)
    can.setFont(font_name, 18); can.drawString(131.5 * mm, 170.5 * mm, vin_7)

    can.setFont(font_name, 25); can.drawString(45.0 * mm, 133.0 * mm, u_name)
    can.setFont(font_name, 10); can.drawString(28.0 * mm, 118.0 * mm, u_addr)

    can.setFont(font_name, 35)
    can.drawString(65.0 * mm, 90.0 * mm, "同上")
    can.showPage()

def draw_shinsa(can, json_data):
    cert = json_data.get("CertInfo", {})
    car_no = cert.get("EntryNoCarNo", "").replace("　", " ").strip()
    user_name = cert.get("UsernameLowLevelChar", "")
    if user_name in ["＊＊＊", "", "使用者に同じ", "所有者に同じ"]:
        user_name = cert.get("OwnernameLowLevelChar", "")

    can.setFont(font_name, 18)
    can.drawString(60.0 * mm, 140.0 * mm, user_name)
    can.drawString(170.0 * mm, 140.0 * mm, car_no)
    can.showPage()

# --- 4. Streamlit UI ---
st.set_page_config(page_title="書類作成アプリ", layout="centered")

st.markdown("""
<style>
    .stButton>button { width: 100%; height: 3em; font-size: 1.2rem; }
    [data-testid="stSidebar"] { min-width: 300px; }
</style>
""", unsafe_allow_html=True)

saved_data = load_settings()

st.title("🚜 車両登録書類 作成ツール")

with st.sidebar:
    st.header("⚙️ 固定情報の設定")
    with st.expander("継続申請用"):
        k_name = st.text_input("受検者 氏名", value=saved_data["k_name"])
        k_addr = st.text_area("受検者 住所", value=saved_data["k_addr"])
   
    with st.expander("名義変更・抹消用"):
        m_name = st.text_input("新使用者 氏名(カナ)", value=saved_data["m_name"])
        s_name = st.text_input("申請者 氏名", value=saved_data["s_name"])
        s_addr = st.text_area("申請者 住所", value=saved_data["s_addr"])
        c12 = st.text_input("12桁コード", value=saved_data["c12"])
        c2 = st.text_input("2桁コード", value=saved_data["c2"])
        c10 = st.text_input("10桁コード", value=saved_data["c10"])

    if st.button("設定を保存", type="primary"):
        save_settings({
            "k_name": k_name, "k_addr": k_addr, "m_name": m_name,
            "s_name": s_name, "s_addr": s_addr, "c12": c12, "c2": c2, "c10": c10
        })
        st.success("保存しました！")
        st.rerun()

st.subheader("1. 作成する書類を選択")
col1, col2 = st.columns(2)
with col1:
    do_jyu = st.checkbox("重量税納付書")
    do_shi = st.checkbox("申請審査書")
    do_kei = st.checkbox("継続検査申請書(2号)")
with col2:
    do_mei = st.checkbox("名義変更(1号)")
    do_mas = st.checkbox("一時抹消(3号)")

st.subheader("2. 車検証JSONをアップロード")
up_files = st.file_uploader("JSONファイルを選択 (複数可)", type=['json'], accept_multiple_files=True)

if up_files:
    if st.button("🚀 PDFを作成する", type="primary", use_container_width=True):
        try:
            out = PdfWriter()
            page_added = False
           
            for f in up_files:
                f.seek(0)
                data = json.load(f)
               
                if do_jyu:
                    p = io.BytesIO(); c = canvas.Canvas(p, pagesize=(297*mm, 210*mm)); draw_jyuuryou(c, data); c.save()
                    p.seek(0); bg = PdfReader("重量税納付書.pdf").pages[0]; bg.merge_page(PdfReader(p).pages[0]); out.add_page(bg); page_added = True
               
                if do_shi:
                    p = io.BytesIO(); c = canvas.Canvas(p, pagesize=(297*mm, 210*mm)); draw_shinsa(c, data); c.save()
                    p.seek(0); bg = PdfReader("軽自動車申請審査書.pdf").pages[0]; bg.merge_page(PdfReader(p).pages[0]); out.add_page(bg); page_added = True
               
                if do_kei:
                    p = io.BytesIO(); c = canvas.Canvas(p, pagesize=(210*mm, 297*mm)); draw_page(c, data, k_name, k_addr); c.save()
                    p.seek(0); bg = PdfReader("軽専用2号様式PDF.pdf").pages[0]; bg.merge_page(PdfReader(p).pages[0]); out.add_page(bg); page_added = True
               
                if do_mei:
                    p = io.BytesIO(); c = canvas.Canvas(p, pagesize=(297*mm, 210*mm)); draw_meigi(c, data, m_name, s_name, s_addr, c12, c2, c10); c.save()
                    p.seek(0); 
                    # --- ここを実際のGitHub上のファイル名に修正 ---
                    bg = PdfReader("軽タイトル変更.pdf").pages[0] 
                    bg.merge_page(PdfReader(p).pages[0]); out.add_page(bg); page_added = True
               
                if do_mas:
                    p = io.BytesIO(); c = canvas.Canvas(p, pagesize=(297*mm, 210*mm)); draw_massho(c, data, m_name, s_addr); c.save()
                    p.seek(0); 
                    # --- ここを実際のGitHub上のファイル名に修正 ---
                    bg = PdfReader("軽自動車一時消去.pdf").pages[0] 
                    bg.merge_page(PdfReader(p).pages[0]); out.add_page(bg); page_added = True

            if page_added:
                buf = io.BytesIO()
                out.write(buf)
                st.success("PDFが完成しました！")
                st.download_button(label="📥 PDFをダウンロード", data=buf.getvalue(), file_name="registration_docs.pdf", mime="application/pdf", use_container_width=True)
            else:
                st.warning("書類が一つも選択されていません。")
               
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")