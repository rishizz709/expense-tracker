from streamlit_option_menu import option_menu
import streamlit as st

def show_sidebar(user_email):
    with st.sidebar:

        st.markdown("# 💰 ExpenseFlow Pro")
        st.markdown("# ExpenseFlow Pro")
        st.caption(user_email)

        selected = option_menu(
            menu_title=None,
            options=[
                "Dashboard",
                "Add Transaction",
                "Transactions",
                "Analytics",
                "Goals",
                "AI Advisor",
                "Settings",
                "Logout"
            ],
            icons=[
                "house-fill",
                "wallet2",
                "bar-chart-fill",
                "bullseye",
                "robot",
                "gear-fill",
                "box-arrow-right"
            ],
            default_index=0,
        )

    return selected