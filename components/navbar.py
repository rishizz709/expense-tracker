import streamlit as st
from datetime import datetime

def show_navbar(user_name="Rishi"):
    hour = datetime.now().hour

    if hour < 12:
        greeting = "Good Morning ☀️"
    elif hour < 17:
        greeting = "Good Afternoon 🌤️"
    else:
        greeting = "Good Evening 🌙"

    st.markdown(f"""
    <div style="
        background:linear-gradient(135deg,#2563eb,#0f766e);
        padding:25px;
        border-radius:20px;
        color:white;
        margin-bottom:20px;
        box-shadow:0 10px 30px rgba(0,0,0,.3);
    ">
        <h1 style="margin:0;">💰 ExpenseFlow Pro</h1>
        <h3 style="margin-top:10px;">{greeting}, {user_name} 👋</h3>
        <p>Track Smarter • Save Better • Grow Wealth</p>
    </div>
    """, unsafe_allow_html=True)