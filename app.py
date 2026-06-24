import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from datetime import date

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide"
)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("expenses.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    expense_date TEXT NOT NULL,
    amount REAL NOT NULL
)
""")
conn.commit()


def add_expense(name, category, expense_date, amount):
    cursor.execute(
        """
        INSERT INTO expenses (name, category, expense_date, amount)
        VALUES (?, ?, ?, ?)
        """,
        (name, category, str(expense_date), amount)
    )
    conn.commit()


def get_expenses():
    return pd.read_sql_query(
        "SELECT id, name, category, expense_date, amount FROM expenses ORDER BY expense_date DESC, id DESC",
        conn
    )


def delete_expense(expense_id):
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()


def clear_all_expenses():
    cursor.execute("DELETE FROM expenses")
    conn.commit()


# ---------------- DESIGN ----------------
st.markdown("""
<style>
.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    margin-bottom: 0;
}
.sub-title {
    text-align: center;
    font-size: 18px;
    margin-bottom: 30px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<p class="main-title">💰 Smart Expense Tracker</p>',
    unsafe_allow_html=True
)
st.markdown(
    '<p class="sub-title">Your expenses are saved automatically</p>',
    unsafe_allow_html=True
)

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
            add_expense(name.strip(), category, expense_date, amount)
            st.success("Expense saved successfully!")
            st.rerun()
        else:
            st.warning("Enter an expense name and amount greater than 0.")

# ---------------- LOAD EXPENSES ----------------
df = get_expenses()

if len(df) == 0:
    st.info("No expenses saved yet. Add your first expense above.")

else:
    df["expense_date"] = pd.to_datetime(df["expense_date"])
    df["month"] = df["expense_date"].dt.strftime("%B %Y")

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

    # ---------------- SUMMARY ----------------
    total_expense = filtered_df["amount"].sum()
    expense_count = len(filtered_df)
    highest_expense = (
        filtered_df["amount"].max()
        if expense_count > 0
        else 0
    )

    card1, card2, card3 = st.columns(3)
    card1.metric("Total Expense", f"₹{total_expense:.2f}")
    card2.metric("Number of Expenses", expense_count)
    card3.metric("Highest Expense", f"₹{highest_expense:.2f}")

    # ---------------- TABLE ----------------
    st.subheader("🧾 Your Expenses")

    display_df = filtered_df[
        ["id", "name", "category", "expense_date", "amount"]
    ].copy()

    display_df["expense_date"] = display_df["expense_date"].dt.strftime(
        "%d-%m-%Y"
    )
    display_df["amount"] = display_df["amount"].map(
        lambda value: f"₹{value:.2f}"
    )

    st.dataframe(
        display_df.rename(columns={"expense_date": "date"}),
        use_container_width=True,
        hide_index=True
    )

    # ---------------- DOWNLOAD CSV ----------------
    csv_data = filtered_df[
        ["name", "category", "expense_date", "amount"]
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
        category_total = filtered_df.groupby("category")["amount"].sum()

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
            ax2.bar(category_total.index, category_total.values)
            ax2.set_xlabel("Category")
            ax2.set_ylabel("Amount (₹)")
            plt.xticks(rotation=45)
            st.pyplot(fig2)

    # ---------------- DELETE ----------------
    st.divider()
    st.subheader("🗑 Delete an Expense")

    delete_options = {
        f"{row['name']} | {row['category']} | "
        f"₹{row['amount']:.2f} | "
        f"{row['expense_date'].strftime('%d-%m-%Y')}": row["id"]
        for _, row in df.iterrows()
    }

    selected_label = st.selectbox(
        "Choose expense to delete",
        list(delete_options.keys())
    )

    delete_col, clear_col = st.columns(2)

    with delete_col:
        if st.button("Delete Selected Expense", use_container_width=True):
            delete_expense(delete_options[selected_label])
            st.success("Expense deleted.")
            st.rerun()

    with clear_col:
        if st.button("Clear All Expenses", use_container_width=True):
            clear_all_expenses()
            st.success("All expenses cleared.")
            st.rerun()
