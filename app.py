import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide"
)

# ---------------- CUSTOM DESIGN ----------------
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: bold;
        margin-bottom: 0px;
    }

    .sub-title {
        text-align: center;
        font-size: 18px;
        margin-bottom: 30px;
    }

    div[data-testid="stMetric"] {
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #dddddd;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">💰 Smart Expense Tracker</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-title">Track your spending, understand your money</p>',
    unsafe_allow_html=True
)

# ---------------- SESSION STORAGE ----------------
if "expenses" not in st.session_state:
    st.session_state.expenses = []

categories = [
    "Food",
    "Travel",
    "Shopping",
    "Bills",
    "Entertainment",
    "Health",
    "Education",
    "Other"
]

# ---------------- ADD EXPENSE ----------------
with st.expander("➕ Add New Expense", expanded=True):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        name = st.text_input("Expense name", placeholder="Example: Tea")

    with col2:
        category = st.selectbox("Category", categories)

    with col3:
        expense_date = st.date_input("Expense date", value=date.today())

    with col4:
        amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            step=1.0,
            format="%.2f"
        )

    if st.button("Add Expense", use_container_width=True):
        if name.strip() != "" and amount > 0:
            st.session_state.expenses.append(
                {
                    "name": name.strip(),
                    "category": category,
                    "date": expense_date,
                    "amount": amount
                }
            )
            st.success("Expense added successfully!")
            st.rerun()
        else:
            st.warning("Please enter an expense name and amount greater than 0.")

# ---------------- NO EXPENSES ----------------
if len(st.session_state.expenses) == 0:
    st.info("No expenses added yet. Add your first expense above.")

# ---------------- EXPENSE DASHBOARD ----------------
else:
    df = pd.DataFrame(st.session_state.expenses)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.strftime("%B %Y")

    st.divider()
    st.subheader("📊 Expense Dashboard")

    # ---------------- FILTERS ----------------
    filter1, filter2, filter3 = st.columns(3)

    with filter1:
        month_options = ["All months"] + sorted(
            df["month"].unique(),
            reverse=True
        )

        selected_month = st.selectbox("Filter by month", month_options)

    with filter2:
        category_options = ["All categories"] + sorted(
            df["category"].unique()
        )

        selected_category = st.selectbox(
            "Filter by category",
            category_options
        )

    with filter3:
        search_text = st.text_input(
            "Search expense",
            placeholder="Example: Tea"
        )

    filtered_df = df.copy()

    if selected_month != "All months":
        filtered_df = filtered_df[
            filtered_df["month"] == selected_month
        ]

    if selected_category != "All categories":
        filtered_df = filtered_df[
            filtered_df["category"] == selected_category
        ]

    if search_text.strip() != "":
        filtered_df = filtered_df[
            filtered_df["name"].str.contains(
                search_text,
                case=False,
                na=False
            )
        ]

    # ---------------- SUMMARY CARDS ----------------
    total_expense = filtered_df["amount"].sum()
    expense_count = len(filtered_df)

    if expense_count > 0:
        highest_expense = filtered_df["amount"].max()
    else:
        highest_expense = 0

    card1, card2, card3 = st.columns(3)

    with card1:
        st.metric("Total Expense", f"₹{total_expense:.2f}")

    with card2:
        st.metric("Number of Expenses", expense_count)

    with card3:
        st.metric("Highest Expense", f"₹{highest_expense:.2f}")

    # ---------------- EXPENSE TABLE ----------------
    st.subheader("🧾 Your Expenses")

    display_df = filtered_df[
        ["name", "category", "date", "amount"]
    ].copy()

    display_df["date"] = display_df["date"].dt.strftime("%d-%m-%Y")
    display_df["amount"] = display_df["amount"].map(
        lambda value: f"₹{value:.2f}"
    )

    st.dataframe(display_df, use_container_width=True)

    # ---------------- DOWNLOAD CSV ----------------
    csv_data = filtered_df[
        ["name", "category", "date", "amount"]
    ].to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇ Download shown expenses as CSV",
        data=csv_data,
        file_name="my_expenses.csv",
        mime="text/csv"
    )

    # ---------------- CHARTS ----------------
    if len(filtered_df) > 0:
        st.divider()
        st.subheader("📈 Spending Analysis")

        chart1, chart2 = st.columns(2)

        category_total = filtered_df.groupby(
            "category"
        )["amount"].sum()

        with chart1:
            st.write("### Category Distribution")

            fig1, ax1 = plt.subplots()

            ax1.pie(
                category_total,
                labels=category_total.index,
                autopct="%1.1f%%",
                startangle=90
            )

            ax1.axis("equal")
            st.pyplot(fig1)

        with chart2:
            st.write("### Category Spending")

            fig2, ax2 = plt.subplots()

            ax2.bar(
                category_total.index,
                category_total.values
            )

            ax2.set_xlabel("Category")
            ax2.set_ylabel("Amount (₹)")
            plt.xticks(rotation=45)

            st.pyplot(fig2)

    # ---------------- DELETE EXPENSE ----------------
    st.divider()
    st.subheader("🗑 Delete an Expense")

    delete_options = [
        f"{index + 1}. {expense['name']} | "
        f"{expense['category']} | "
        f"₹{expense['amount']:.2f}"
        for index, expense in enumerate(st.session_state.expenses)
    ]

    selected_expense = st.selectbox(
        "Choose expense to delete",
        delete_options
    )

    delete_col, clear_col = st.columns(2)

    with delete_col:
        if st.button("Delete Selected Expense", use_container_width=True):
            selected_index = delete_options.index(selected_expense)
            deleted = st.session_state.expenses.pop(selected_index)
            st.success(f"Deleted: {deleted['name']}")
            st.rerun()

    with clear_col:
        if st.button("Clear All Expenses", use_container_width=True):
            st.session_state.expenses = []
            st.success("All expenses cleared.")
            st.rerun()
