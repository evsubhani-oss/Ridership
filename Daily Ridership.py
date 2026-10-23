import streamlit as st
from datetime import datetime, timedelta
import re

# Set page configuration
st.set_page_config(
    page_title="Transport Stats Dashboard",
    page_icon="🚌",
    layout="wide"
)

# ==========================================
# 🧠 TEXT PARSING FUNCTIONS
# ==========================================
def parse_raw_text(raw_text):
    """Extracts numerical data from the raw pasted EV webpage text using regex."""
    data = {}
    
    def extract_int(pattern):
        match = re.search(pattern, raw_text, re.IGNORECASE)
        return int(match.group(1).replace(',', '')) if match else 0
        
    def extract_float(pattern):
        match = re.search(pattern, raw_text, re.IGNORECASE)
        return float(match.group(1).replace(',', '')) if match else 0.0

    # Extracting EV & Bus Data (supports both reverted mixed-case and uppercase headers)
    data['ev_daily_count'] = extract_int(r"(?:Daily Count|DAILY_COUNT)\s+([\d,]+)")
    data['ev_daily_amount'] = extract_float(r"(?:Daily Amount|DAILY_AMOUNT)\s+([\d,\.]+)")
    data['total_bus'] = 180  # Hardcoded as requested
    data['working_bus'] = extract_int(r"(?:Operational Buses|Working Buses|WORKING_BUS)\s+([\d,]+)")
    
    # Extracting MST Data
    data['mst_count'] = extract_int(r"(?:MstCardCharge Count|TODAY_MSTCARD_CHARGE_CNT)\s+([\d,]+)")
    data['mst_amount'] = extract_float(r"(?:MstcardCharge Amount|TODAY_MSTCARD_CHARGE_AMT)\s+([\d,\.]+)")
    data['mst_balance'] = extract_float(r"(?:MstcardBalance Amount|TODAY_MSTCARD_BLNC_CHARGE_AMT)\s+([\d,\.]+)")
    
    # Extracting Card Charge Data
    data['card_charge_count'] = extract_int(r"(?:Daily Card Charge Count|TODAY_CARD_CHARGE_CNT)\s+([\d,]+)")
    data['card_charge_amount'] = extract_float(r"(?:Daily Card Charge Amount|TODAY_CARD_CHARGE_AMT)\s+([\d,\.]+)")
    
    # Extracting Ticket Sales Data
    data['ticket_sale_count'] = extract_int(r"(?:Total Ticket Sales Count|TOTAL_TICKET_SALES_CNT)\s+([\d,]+)")
    data['ticket_sale_amount'] = extract_float(r"(?:Total Ticket Sales Amount|TOTAL_TICKET_SALES_AMT)\s+([\d,\.]+)")

    return data

def parse_olm_text(raw_text):
    """Extracts Ridership and Revenue from the Orange Line pasted text."""
    data = {}
    
    # Match Total Ridership
    riders_match = re.search(r"Total Ridership\s+([\d,]+)", raw_text, re.IGNORECASE)
    if riders_match:
        data['olm_riders'] = int(riders_match.group(1).replace(',', ''))
        
    # Match Total Revenue (ignoring the Rs. at the end)
    revenue_match = re.search(r"Total Revenue\s+([\d,\.]+)\s*Rs\.?", raw_text, re.IGNORECASE)
    if revenue_match:
        rev_val = float(revenue_match.group(1).replace(',', ''))
        data['olm_revenue'] = rev_val
        data['olm_sales'] = rev_val  # Applies to both Revenue and Sales

    return data

# ==========================================
# 📊 UTILITY FUNCTIONS
# ==========================================
def fmt(number):
    """Format with commas."""
    if isinstance(number, (int, float)):
        return f"{number:,.0f}" if number.is_integer() else f"{number:,.2f}"
    return str(number)


# ==========================================
# 🖥️ STREAMLIT UI LAYOUT
# ==========================================
st.title("🚌 Transport Stats Dashboard")

# Initialize session state for parsed data
if "parsed_data" not in st.session_state:
    st.session_state.parsed_data = {}

# Helper to load parsed values securely
def get_val(key, default_val):
    return st.session_state.parsed_data.get(key, default_val)

# --- Row 1: Paste Area & Date Selection ---
st.markdown("### 📥 1. Input Raw Data")

col_paste, col_date = st.columns([3, 2])

with col_paste:
    raw_pasted_text = st.text_area("Paste EV Webpage Text Here: (ctrl+A on gen stats/ confirm numbers with gen charge)", height=100, placeholder="Paste the raw text from the EV portal here...")
    raw_olm_text = st.text_area("Paste Orange Line Text Here: ((ctrl+A on AFC TAP)", height=100, placeholder="Paste the raw text from the Orange Line dashboard here...")
    
    if st.button("🔍 Parse Pasted Data", type="primary"):
        parsed_any = False
        
        # Parse EV Data
        if raw_pasted_text.strip():
            ev_data = parse_raw_text(raw_pasted_text)
            st.session_state.parsed_data.update(ev_data)
            parsed_any = True
            
        # Parse OLM Data
        if raw_olm_text.strip():
            olm_data = parse_olm_text(raw_olm_text)
            st.session_state.parsed_data.update(olm_data)
            parsed_any = True
            
        if parsed_any:
            st.success("✅ Data successfully parsed!")
        else:
            st.warning("Please paste some text into at least one of the boxes first.")

with col_date:
    yesterday = datetime.now() - timedelta(days=1)
    selected_date = st.date_input("Select Report Date", yesterday)
    date_str = selected_date.strftime("%Y-%m-%d")
    day_str = selected_date.strftime("%A")
    st.text_input("Day", value=day_str, disabled=True)

    st.markdown("---")
    st.markdown("#### 📱 QR Mobile (Manual Entry)")
    qr_count = st.number_input("Total QR Tickets", value=int(get_val("qr_count", 0)), step=1)
    
    # Warning if QR Tickets are zero
    if qr_count == 0:
        st.warning("⚠️ Warning: QR Tickets are currently 0. Don't forget to manually enter them!")


# --- Row 2: Data Inputs (3 Columns) ---
st.markdown("---")
st.markdown("### 📝 2. Review & Edit Statistics")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🎫 Daily Boarding (EV)")
    ev_daily_count = st.number_input("Daily Count", value=int(get_val("ev_daily_count", 0)), step=1)
    ev_daily_amount = st.number_input("Daily Amount", value=float(get_val("ev_daily_amount", 0.0)), step=10.0)

    st.markdown("#### 🚌 Daily Bus Count")
    total_bus = st.number_input("Total Bus", value=180, step=1, disabled=True)
    working_bus = st.number_input("Working Buses", value=int(get_val("working_bus", 0)), step=1)

    st.markdown("#### 💳 MST Card Charge")
    mst_count = st.number_input("Charge Count (MST)", value=int(get_val("mst_count", 0)), step=1)
    mst_amount = st.number_input("Charge Amount (MST)", value=float(get_val("mst_amount", 0.0)), step=10.0)
    mst_balance = st.number_input("Balance Amount (MST)", value=float(get_val("mst_balance", 0.0)), step=10.0)

with col2:
    st.markdown("#### 💳 Daily Card Charge")
    card_charge_count = st.number_input("Charge Count (Card)", value=int(get_val("card_charge_count", 0)), step=1)
    card_charge_amount = st.number_input("Charge Amount (Card)", value=float(get_val("card_charge_amount", 0.0)), step=10.0)

    st.markdown("#### 🎟️ Daily Ticket Sales")
    ticket_sale_count = st.number_input("Ticket Sale Count", value=int(get_val("ticket_sale_count", 0)), step=1)
    ticket_sale_amount = st.number_input("Ticket Sale Amount", value=float(get_val("ticket_sale_amount", 0.0)), step=10.0)

with col3:
    st.markdown("#### 🍊 Orange Line Metro")
    olm_riders = st.number_input("Total Riders (OLM)", value=int(get_val("olm_riders", 0)), step=1)
    olm_revenue = st.number_input("Total Revenue (OLM)", value=float(get_val("olm_revenue", 0.0)), step=10.0)
    olm_sales = st.number_input("Total Sales (OLM)", value=float(get_val("olm_sales", 0.0)), step=10.0)


# ==========================================
# 📊 CALCULATIONS & GENERATION
# ==========================================
qr_amount = qr_count * 50
grand_total_riders = olm_riders + qr_count + ticket_sale_count
grand_total_sales = olm_sales + qr_amount + ticket_sale_amount
feeder_routes_riders = qr_count + ticket_sale_count

main_template = f"""*General Statistics - EV & HEV Buses*
Date: {date_str}
Day: {day_str}
*Daily Boarding*
Daily Count: {fmt(ev_daily_count)}
Daily Amount: {fmt(ev_daily_amount)}
*Daily Bus Count*
Total Bus: 180
Working Buses: {fmt(working_bus)}
*Daily MST Card Charge Info*
MST Card Charge Count: {fmt(mst_count)}
MST Card Charge Amount: {fmt(mst_amount)}
MST Card Balance Amount: {fmt(mst_balance)}
*Daily Card Charge*
Daily Card Charge Count: {fmt(card_charge_count)}
Daily Card Charge Amount: {fmt(card_charge_amount)}
*Daily Ticket Sales*
Total Tickets Sale Count: {fmt(ticket_sale_count)}
Total Tickets Sale Amount: {fmt(ticket_sale_amount)}
*QR Mobile*
Total QR Tickets: {fmt(qr_count)}
Total QR Tickets Amount: {fmt(qr_amount)}
*General Statistics - Orange Line Metro*
Date: {date_str}
Day: {day_str}
Total Riders: {fmt(olm_riders)}
Total Revenue: {fmt(olm_revenue)}
Total Sales: {fmt(olm_sales)}
*Grand Total*
Total Ridership Count: {fmt(grand_total_riders)}
Total Sale Amount: {fmt(grand_total_sales)}"""

summary_template = f"""*Ridership Details*
Date: {date_str}
Day: {day_str} 

*Orange Line Metro* = {fmt(olm_riders)}
*Feeder Routes* = {fmt(feeder_routes_riders)}

*Total Ridership* = {fmt(grand_total_riders)}
*Total Sale Amount* = {fmt(grand_total_sales)}"""

# --- Row 3: Output Templates ---
st.markdown("---")
st.markdown("### 📋 3. Generated Reports")

col_out1, col_out2 = st.columns(2)

with col_out1:
    st.subheader("Main Template")
    st.text_area("Copy this text:", value=main_template, height=450, key="main_text")
    
with col_out2:
    st.subheader("Short Summary")
    st.text_area("Copy this text:", value=summary_template, height=200, key="summary_text")


# ==========================================
# 🔄 QUICK CONVERTER SECTION
# ==========================================
st.markdown("---")
st.markdown("### ⚡ 4. Quick Converter (Main Format ➡️ Short Summary)")
st.caption("Paste a complete Main Format text below to immediately transform it into a Short Summary.")

converter_pasted_text = st.text_area("Paste Main Format Here:", height=150, placeholder="Paste the fully generated main report here...")

if converter_pasted_text.strip():
    try:
        date_match = re.search(r"Date:\s*(.+)", converter_pasted_text)
        day_match = re.search(r"Day:\s*(.+)", converter_pasted_text)
        olm_match = re.search(r"Total Riders:\s*([\d,]+)", converter_pasted_text)
        total_riders_match = re.search(r"Total Ridership Count:\s*([\d,]+)", converter_pasted_text)
        total_sales_match = re.search(r"Total Sale Amount:\s*([\d,\.]+)", converter_pasted_text)

        if not (date_match and olm_match and total_riders_match and total_sales_match and day_match):
            st.error("⚠️ Invalid format. Could not parse all required metrics.")
        else:
            c_date_val = date_match.group(1).strip()
            c_day_val = day_match.group(1).strip()
            c_olm_str = olm_match.group(1)
            c_total_riders_str = total_riders_match.group(1)
            c_total_sales_str = total_sales_match.group(1)

            c_olm_riders_int = int(c_olm_str.replace(",", ""))
            c_total_riders_int = int(c_total_riders_str.replace(",", ""))
            c_feeder_routes_int = c_total_riders_int - c_olm_riders_int

            converted_summary = f"""*Ridership Details*
Date: {c_date_val}
Day: {c_day_val}

*Orange Line Metro* = {c_olm_riders_int:,}
*Feeder Routes* = {c_feeder_routes_int:,}

*Total Ridership* = {c_total_riders_int:,}
*Total Sale Amount* = {c_total_sales_str}"""

            st.success("✅ Conversion Successful!")
            st.text_area("Converted Short Summary", value=converted_summary, height=200, key="converted_text")
            
    except Exception as e:
        st.error(f"Error parsing text: {str(e)}")