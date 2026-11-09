import streamlit as st
import pandas as pd
import requests
import io

# 1. Page Configuration & Dark Slate Theme
st.set_page_config(page_title="Beta Tracking Service", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: #F1F5F9; }
    
    .wireframe-panel { 
        background-color: #1E293B; 
        padding: 25px; 
        border-radius: 8px; 
        color: #F1F5F9; 
        margin-bottom: 20px; 
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .panel-title {
        font-size: 20px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0;
        margin-bottom: 20px;
        color: #38BDF8 !important;
        border-bottom: 2px solid #334155;
        padding-bottom: 8px;
    }
    
    .scorecard-box { text-align: center; margin-bottom: 10px; padding: 10px; }
    .scorecard-num { 
        font-size: 96px; 
        font-weight: 800; 
        color: #F8FAFC; 
        line-height: 1; 
        margin: 0; 
    }
    .scorecard-label { 
        font-size: 16px; 
        color: #94A3B8; 
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 10px; 
        margin-bottom: 5px; 
    }
    
    .recent-indicator-box {
        color: #94A3B8;
        font-weight: bold;
        font-size: 15px;
        text-align: center;
        margin-top: 5px;
        margin-bottom: 15px;
    }
    
    .form-btn {
        display: block;
        width: 100%;
        background-color: #38BDF8;
        color: #0F172A !important;
        text-align: center;
        padding: 14px;
        border-radius: 6px;
        font-weight: 800;
        text-decoration: none !important;
        font-size: 16px;
        letter-spacing: 0.5px;
        margin-top: 10px;
    }
    .form-btn:hover { background-color: #7DD3FC; }
    
    div[data-testid="stTextInput"] input {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border: 1px solid #475569 !important;
        border-radius: 6px !important;
        padding: 12px !important;
    }
    div[data-testid="stTextInput"] label { color: #F1F5F9 !important; font-weight: bold; font-size: 15px; }
    
    h1, h2, h3, h4 { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #FFFFFF !important; font-weight: bold; }
    .schedule-row { padding: 12px 0; border-bottom: 1px solid #334155; color: #E2E8F0; font-size: 15px; }
    .schedule-row b { color: #38BDF8; }
    .schedule-row a { color: #38BDF8 !important; text-decoration: underline !important; font-weight: bold; }
    .schedule-row a:hover { color: #FFFFFF !important; }
    </style>
""", unsafe_allow_html=True)

# 2. Universal Google Sheets Connection (Pulls directly from Sheet ID)
SHEET_ID = "1mZP0DaAhJ7MGwsr15iw63nr7TGSHXzJrlTBTa49L7IA"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
def load_live_data():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(CSV_URL, headers=headers, timeout=10)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text))
        return df, None
    except Exception as e:
        return pd.DataFrame(columns=["Student Name", "Student Email", "Date", "Hours", "Task"]), str(e)

master_df, conn_error = load_live_data()

# Show connection diagnostic at top so you always know if Windows Firewall blocked it
if conn_error:
    st.warning(f"⚠️ Local PC Firewall blocked live Google Sheet sync ({conn_error}). Upload to GitHub/Streamlit Cloud to view live sheet data.")

# Clean column names and data
if not master_df.empty:
    master_df.columns = master_df.columns.str.strip()
    for col in ["Student Name", "Student Email", "Task"]:
        if col in master_df.columns:
            master_df[col] = master_df[col].astype(str).str.strip()
    if "Hours" in master_df.columns:
        master_df["Hours"] = pd.to_numeric(master_df["Hours"], errors='coerce').fillna(0.0)

# --- TOP TWO-PANEL LAYOUT ---
left_col, right_col = st.columns([1, 1.4])

with left_col:
    st.markdown("<h2 style='color: #FFFFFF; margin-bottom: 25px;'>⚡ Beta Tracking Service</h2>", unsafe_allow_html=True)
    input_name = st.text_input("Type name here:", placeholder="e.g. John Doe").strip()
    input_email = st.text_input("Type email here:", placeholder="e.g. john.doe@school.edu").strip()
    
    st.write("") 
    
    teams_url = "https://microsoft.com"
    meet_url = "https://google.com"
    
    st.markdown(f"""
        <div class='wireframe-panel' style='min-height: 280px;'>
            <div class='panel-title'>upcoming meetings</div>
            <div class='schedule-row'>
                📅 <b>Tuesday, Nov 10, 2026 — 1:00 PM to 2:00 PM</b><br>
                ➡️ <a href='{teams_url}' target='_blank'>Official Beta Meeting</a>
            </div>
            <div class='schedule-row'>
                📅 <b>Friday, Nov 13, 2026 — 11:00 AM to 12:00 PM</b><br>
                ➡️ <a href='{meet_url}' target='_blank'>Zine Introduction Day</a>
            </div>
        </div>
    """, unsafe_allow_html=True)

with right_col:
    st.markdown("<h3 style='margin-bottom: 15px;'>📊 Club Submission Engagement Metrics</h3>", unsafe_allow_html=True)
    if not master_df.empty and "Student Name" in master_df.columns:
        submitted_count = master_df["Student Name"].nunique()
    else:
        submitted_count = 0
    not_submitted_count = max(0, 110 - submitted_count)
    
    chart_data = pd.DataFrame({
        "Status": ["Submitted", "Pending"],
        "Count": [submitted_count, not_submitted_count]
    })
    st.bar_chart(data=chart_data, x="Status", y="Count", color="#38BDF8", use_container_width=True)

st.divider()

# --- BOTTOM INTERACTIVE SECTION ---
FORM_ID = "1FAIpQLSfkj3ljVbj2dgF_YYcUPlpdouNtLqeAHoFDOrvpL6LdBpCKQA"
GOOGLE_FORM_URL = f"https://docs.google.com/forms/d/e/{FORM_ID}/viewform"

if input_name and input_email:
    if not master_df.empty and "Student Name" in master_df.columns and "Student Email" in master_df.columns:
        student_records = master_df[
            (master_df["Student Name"].str.lower() == input_name.lower()) & 
            (master_df["Student Email"].str.lower() == input_email.lower())
        ]
    else:
        student_records = pd.DataFrame(columns=["Student Name", "Student Email", "Date", "Hours", "Task"])
        
    total_hours_sum = student_records["Hours"].sum() if not student_records.empty else 0.0
    cols_to_show = [c for c in ["Date", "Task", "Hours"] if c in student_records.columns]
    display_history = student_records[cols_to_show] if not student_records.empty else student_records

    if not student_records.empty:
        recent_hours_val = student_records.iloc[-1]["Hours"]
        recent_indicator_text = f"+ {recent_hours_val:,.1f} hours added recently"
    else:
        recent_indicator_text = "+ 0 hours added recently"

    bottom_left, bottom_right = st.columns([1.2, 1])
    
    with bottom_left:
        st.markdown(f"<h3>📜 Activity History Log: {input_name}</h3>", unsafe_allow_html=True)
        
        # 15-Hour Goal Progress Pie Chart
        hours_completed = min(total_hours_sum, 15.0)
        hours_remaining = max(0.0, 15.0 - total_hours_sum)
        pct_done = (hours_completed / 15.0) * 100
        fill_color = "#22C55E" if hours_remaining == 0 else "#38BDF8"
        
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 25px; background-color: #1E293B; padding: 20px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 15px;">
                <div style="width: 130px; height: 130px; border-radius: 50%; background: conic-gradient({fill_color} 0% {pct_done}%, #EF4444 {pct_done}% 100%); flex-shrink: 0;"></div>
                <div>
                    <div style="font-size: 16px; font-weight: bold; margin-bottom: 8px; color: #F8FAFC;">15-Hour Goal Progress</div>
                    <div style="color: {fill_color}; font-weight: bold; font-size: 14px;">■ Completed: {hours_completed:,.1f} hrs</div>
                    <div style="color: #EF4444; font-weight: bold; font-size: 14px;">■ Remaining: {hours_remaining:,.1f} hrs</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if display_history.empty:
            st.info("No matching hours found yet for this name and email.")
        else:
            st.dataframe(display_history, use_container_width=True, hide_index=True)
            
    with bottom_right:
        st.markdown(f"""
            <div class='scorecard-box'>
                <p class='scorecard-num'>{total_hours_sum:,.0f}</p>
                <p class='scorecard-label'>hours logged</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f"<div class='recent-indicator-box'>{recent_indicator_text}</div>", unsafe_allow_html=True)
        st.markdown(f"<a href='{GOOGLE_FORM_URL}' target='_blank' class='form-btn'>➕ LOG NEW HOURS HERE</a>", unsafe_allow_html=True)
else:
    st.markdown("<div style='background-color: #1E293B; padding: 20px; border-radius: 8px; border-left: 4px solid #38BDF8; color: #94A3B8; font-size: 15px;'>💡 Type your full name and registered school email address in the left panel to load your live hours card ledger summary.</div>", unsafe_allow_html=True)


