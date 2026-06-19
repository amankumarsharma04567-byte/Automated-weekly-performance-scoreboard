import streamlit as st
import requests
from fpdf import FPDF
from datetime import datetime

# ─────────────────────────────────────────
# Safely load API key
# ─────────────────────────────────────────
if "GEMINI_API_KEY" not in st.secrets:
    st.error(
        "GEMINI_API_KEY is missing from Streamlit Secrets. "
        "Go to Manage App → Settings → Secrets and add it."
    )
    st.stop()

API_KEY = st.secrets["GEMINI_API_KEY"]

# ─────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Weekly Performance Scoreboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Automated Weekly Performance Scoreboard")
st.markdown("Enter your weekly performance data below to generate insights and a PDF report.")

# ─────────────────────────────────────────
# Input Form
# ─────────────────────────────────────────
st.header("📝 Enter Weekly Data")

with st.form("performance_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        restaurant_name = st.text_input("Restaurant Name", value="My Restaurant")
        week_start = st.date_input("Week Start Date")
        week_end = st.date_input("Week End Date")

    with col2:
        total_orders = st.number_input("Total Orders", min_value=0, value=500)
        total_revenue = st.number_input("Total Revenue ($)", min_value=0.0, value=15000.0, step=100.0)
        avg_order_value = st.number_input("Average Order Value ($)", min_value=0.0, value=30.0, step=1.0)

    with col3:
        avg_rating = st.number_input("Average Customer Rating (out of 5)", min_value=0.0, max_value=5.0, value=4.2, step=0.1)
        new_customers = st.number_input("New Customers", min_value=0, value=120)
        repeat_customers = st.number_input("Repeat Customers", min_value=0, value=380)

    st.markdown("---")

    top_item_1 = st.text_input("Top Selling Item #1", value="Burger")
    top_item_2 = st.text_input("Top Selling Item #2", value="Pizza")
    top_item_3 = st.text_input("Top Selling Item #3", value="Pasta")

    submitted = st.form_submit_button("🚀 Generate Scoreboard")

# ─────────────────────────────────────────
# Generate Insights — Try both methods
# ─────────────────────────────────────────
def generate_insights(performance_data):
    prompt = f"""
You are a professional restaurant business analyst.
Based on the weekly performance data below, generate a short, professional 4 to 5 sentence insight summary.
Mention key strengths, areas to improve, and one actionable recommendation.

Restaurant Name: {performance_data['restaurant_name']}
Week: {performance_data['week_start']} to {performance_data['week_end']}
Total Orders: {performance_data['total_orders']}
Total Revenue: ${performance_data['total_revenue']}
Average Order Value: ${performance_data['avg_order_value']}
Average Customer Rating: {performance_data['avg_rating']} / 5
New Customers: {performance_data['new_customers']}
Repeat Customers: {performance_data['repeat_customers']}
Top Selling Items: {performance_data['top_item_1']}, {performance_data['top_item_2']}, {performance_data['top_item_3']}
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    headers_json = {"Content-Type": "application/json"}

    # Method 1 — Standard API key as URL param (AIzaSy... keys)
    url_with_key = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    response = requests.post(url_with_key, headers=headers_json, json=payload)

    if response.status_code == 200:
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]

    # Method 2 — Auth key as Bearer token (AQ.A... keys)
    url_no_key = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers_bearer = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    response2 = requests.post(url_no_key, headers=headers_bearer, json=payload)

    if response2.status_code == 200:
        result2 = response2.json()
        return result2["candidates"][0]["content"]["parts"][0]["text"]

    raise Exception(f"Both auth methods failed.\nMethod 1: {response.status_code}\nMethod 2: {response2.status_code} — {response2.text}")


# ─────────────────────────────────────────
# Generate PDF Report
# ─────────────────────────────────────────
def generate_pdf(performance_data, ai_insight):
    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Arial", "B", 20)
    pdf.set_fill_color(41, 128, 185)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 15, "Weekly Performance Scoreboard", ln=True, align="C", fill=True)

    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

    # Restaurant Info
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Restaurant: {performance_data['restaurant_name']}", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Week: {performance_data['week_start']} to {performance_data['week_end']}", ln=True)
    pdf.cell(0, 8, f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(5)

    # Divider
    pdf.set_draw_color(41, 128, 185)
    pdf.set_line_width(0.8)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    # Performance Metrics
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Performance Metrics", ln=True)
    pdf.set_font("Arial", "", 12)

    metrics = [
        ("Total Orders", str(performance_data['total_orders'])),
        ("Total Revenue", f"${performance_data['total_revenue']:,.2f}"),
        ("Average Order Value", f"${performance_data['avg_order_value']:,.2f}"),
        ("Average Customer Rating", f"{performance_data['avg_rating']} / 5"),
        ("New Customers", str(performance_data['new_customers'])),
        ("Repeat Customers", str(performance_data['repeat_customers'])),
    ]

    for label, value in metrics:
        pdf.set_fill_color(235, 245, 255)
        pdf.cell(95, 9, f"  {label}", border=1, fill=True)
        pdf.cell(95, 9, f"  {value}", border=1, ln=True)

    pdf.ln(5)

    # Top Selling Items
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Top Selling Items", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"  1. {performance_data['top_item_1']}", ln=True)
    pdf.cell(0, 8, f"  2. {performance_data['top_item_2']}", ln=True)
    pdf.cell(0, 8, f"  3. {performance_data['top_item_3']}", ln=True)
    pdf.ln(5)

    # Divider
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    # AI Insights
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "AI-Generated Insights", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.set_fill_color(245, 255, 245)
    clean_insight = ai_insight.encode("latin-1", errors="replace").decode("latin-1")
    pdf.multi_cell(0, 8, clean_insight, border=1, fill=True)

    # Footer
    pdf.ln(10)
    pdf.set_font("Arial", "I", 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 8, "Generated by Automated Weekly Performance Scoreboard App", align="C", ln=True)

    return bytes(pdf.output())


# ─────────────────────────────────────────
# Display Results After Form Submit
# ─────────────────────────────────────────
if submitted:
    performance_data = {
        "restaurant_name": restaurant_name,
        "week_start": str(week_start),
        "week_end": str(week_end),
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "avg_order_value": avg_order_value,
        "avg_rating": avg_rating,
        "new_customers": new_customers,
        "repeat_customers": repeat_customers,
        "top_item_1": top_item_1,
        "top_item_2": top_item_2,
        "top_item_3": top_item_3,
    }

    # ── Metrics Dashboard ──
    st.markdown("---")
    st.header("📈 Performance Dashboard")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Orders", f"{total_orders:,}")
    col2.metric("Total Revenue", f"${total_revenue:,.2f}")
    col3.metric("Avg Order Value", f"${avg_order_value:,.2f}")
    col4.metric("Avg Rating", f"{avg_rating} / 5")

    col5, col6 = st.columns(2)
    col5.metric("New Customers", f"{new_customers:,}")
    col6.metric("Repeat Customers", f"{repeat_customers:,}")

    st.markdown("---")
    st.subheader("🍽️ Top Selling Items")
    st.markdown(f"1. **{top_item_1}**")
    st.markdown(f"2. **{top_item_2}**")
    st.markdown(f"3. **{top_item_3}**")

    # ── AI Insights ──
    st.markdown("---")
    st.header("🤖 AI-Generated Insights")

    with st.spinner("Generating insights using Gemini AI..."):
        try:
            ai_insight = generate_insights(performance_data)
            st.success(ai_insight)
        except Exception as e:
            ai_insight = "AI insights could not be generated at this time."
            st.error(f"Error generating insights: {e}")

    # ── PDF Download ──
    st.markdown("---")
    st.header("📄 Download PDF Report")

    with st.spinner("Generating PDF..."):
        try:
            pdf_bytes = generate_pdf(performance_data, ai_insight)
            st.download_button(
                label="⬇️ Download Weekly Scoreboard PDF",
                data=pdf_bytes,
                file_name=f"scoreboard_{restaurant_name.replace(' ', '_')}_{str(week_start)}.pdf",
                mime="application/pdf"
            )
            st.success("PDF ready to download!")
        except Exception as e:
            st.error(f"Error generating PDF: {e}")
