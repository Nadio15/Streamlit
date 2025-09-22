import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

# Set page config
st.set_page_config(page_title="Dashboard", layout="wide")

# Sidebar
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", ["Dashboard", "Reports", "Settings"])

# Header
st.markdown("""
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <h2>Hi, Welcome back!</h2>
        <button style='padding: 6px 12px; background-color: #4CAF50; color: white; border: none; border-radius: 6px;'>Import</button>
    </div>
""", unsafe_allow_html=True)

# Top metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Users", "33,956", "-2.12%")
with col2:
    st.metric("Projects", "50.36%", "+9.12%")
with col3:
    st.write("### Total Sales")
    st.text("Revenue: 13,956  |  Returns: 27,219  |  Queries: 03,386  |  Invoices: 04,739")

# Downloads & Sales chart
col4, col5 = st.columns([1,2])
with col4:
    st.write("#### Downloads")
    st.progress(0.78, text="Offline: 45,324")
    st.progress(0.22, text="Online: 12,236")

with col5:
    st.write("#### Sales Overview")
    x = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    y1 = np.random.randint(100, 400, len(x))
    y2 = np.random.randint(100, 400, len(x))
    fig = px.line(x=x, y=[y1, y2], labels={"x": "Day", "value": "Sales"}, title="Sales Trend")
    st.plotly_chart(fig, use_container_width=True)

# Cards row
col6, col7, col8, col9 = st.columns(4)
with col6:
    st.info("Total Sales: $508 this month")
with col7:
    st.success("Total Purchases: $387 this month")
with col8:
    st.warning("Total Orders: $161 this month")
with col9:
    st.error("Total Growth: $231 this month")

# Tickets & Updates
col10, col11 = st.columns([2,1])
with col10:
    st.write("### Tickets")
    data = {
        "Name": ["Alta Lucas", "Teresa Shaw", "Rosa Underwood", "Vilson Rowa", "Teresa Shaw"],
        "Date": ["31 Aug 2018", "13 May 2018", "02 Jan 2018", "05 Nov 2018", "13 May 2018"],
        "Projects": ["6770 Verner Burgs", "1300 Gideon Divide Apt. 400", "9576 Rempel Extension", "1072 Orion Expansion", "1300 Gideon Divide Apt. 400"]
    }
    df = pd.DataFrame(data)
    st.table(df)

with col11:
    st.write("### Updates")
    st.success("User confirmation - 7 months ago")
    st.info("Continuous evaluation - 7 months ago")
    st.warning("Promotion - 7 months ago")

# Distribution & Sale Report
col12, col13, col14 = st.columns([1,2,1])
with col12:
    st.write("### Distribution")
    dist = pd.DataFrame({"State": ["Texas", "Utah", "Georgia"], "Value": [40, 20, 40]})
    fig = px.pie(dist, values="Value", names="State")
    st.plotly_chart(fig)

with col13:
    st.write("### Sale Report")
    sales = pd.DataFrame({"Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"], "Value": np.random.randint(5000, 30000, 6)})
    fig = px.bar(sales, x="Month", y="Value")
    st.plotly_chart(fig)

with col14:
    st.write("### Sales Report Overview")
    st.text("Downloads: 13,956")
    st.text("Purchases: 55,123")
    st.text("Users: 29,829")

# Open invoices
st.write("### Open Invoices")
invoices = pd.DataFrame({
    "Invoice": [50014, 50015, 50016, 50017, 50018, 50019],
    "Customer": ["David Grey", "Stella Johnson", "Marina Michel", "John Doe", "Stella Johnson", "David Grey"],
    "Ship": ["Italy", "Brazil", "Japan", "India", "Brazil", "Italy"],
    "Best Price": [6300, 4500, 4300, 6400, 4500, 6300],
    "Purchased Price": [2100, 4300, 6440, 2200, 4300, 2100],
    "Status": ["Progress", "Open", "On hold", "Progress", "Open", "Progress"]
})
st.dataframe(invoices, use_container_width=True)
