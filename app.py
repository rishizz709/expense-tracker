import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from datetime import date

# ---------------- PAGE ----------------
st.set_page_config(
    page_title="Smart Expense Tracker",
    page_icon="💸",
    layout="wide"
)

# ---------------- STYLE ----------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a, #172554, #111827);
        color: white;
    }

    h1, h2, h3, p, label {
        color: #f8fafc !important;
    }

    .hero {
        text-align: center;
        padding: 18px 0 8px 0;
    }

    .hero h1 {
        font-size: 48px;
        margin-bottom: 0;
    }

    .hero p {
        color: #cbd5e1 !important;
        font-size: 18px;
    }

    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.10);
        border: 1px solid rgba(255, 255, 255, 0.15);
        padding: 18px;
        border-radius: 16px;
    }

    div[data-testid="stMetricLabel"] {
        color: #cbd5e1 !important;
    }

    div[data-testid="stMetricValue"] {
        color: white !important;
    }

    div.stButton > button {
        border-radius: 10px;
        font-weight: bold;
        border: none;
        padding: 10px 18px;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("expenses.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    expense_date TEXT NOT NULL,
    amount REAL NOT NULL,
    notes TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS settings (
    setting_name TEXT PRIMARY KEY,
    setting_value TEXT
)
""")

conn.commit()


def add_expense(name, category, expense_date, amount, notes):
    cursor.execute(
        """
        INSERT INTO expenses (name, category, expense_date, amount, notes)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, category, str(expense_date), amount, notes)
    )
    conn.commit()


def get_expenses():
    return pd.read_sql_query(
        """
        SELECT id, name, category, expense_date, amount, notes
        FROM expenses
        ORDER BY expense_date DESC, id DESC
        """,
        conn
    )


def delete_expense(expense_id):
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()


def update_expense(expense_id, name, category, expense_date, amount, notes):
    cursor.execute(
        """
        UPDATE expenses
        SET name = ?, category = ?, expense_date = ?, amount = ?, notes = ?
        WHERE id = ?
        """,
        (name, category, str(expense_date), amount, notes, expense_id)
    )
    conn.commit()


def clear_all_expenses():
    cursor.execute("DELETE FROM expenses")
    conn.commit()


def get_budget():
    cursor.execute(
        "SELECT setting_value FROM settings WHERE setting_name = 'monthly_budget'"
    )
    result = cursor.fetchone()

    if result:
        return float(result[0])

    return 5000.0


def save_budget(budget):
    cursor.execute(
        """
        INSERT OR REPLACE INTO settings (setting_name, setting_value)
        VALUES ('monthly_budget', ?)
        """,
        (str(budget),)
    )
    conn.commit()


# ---------------- HEADER ----------------
st.markdown("""
<div class="hero">
    <h1>💸 Smart Expense Tracker</h1>
    <p>Track spending. Control your budget. Build better money habits.</p>
</div>
""", unsafe_allow_html=True)

categories = [
    "Food",
    "Travel",
    "Shopping",
    "Bills",
    "Entertainment",
    "Health",
    "Education",
    "Rent",
    "Other"
]

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("⚙️ Settings")

    saved_budget = get_budget()

    monthly_budget = st.number_input(
        "Monthly Budget (₹)",
        min_value=0.0,
        value=float(saved_budget),
        step=500.0
    )

    if st.button("Save Budget", use_container_width=True):
        save_budget(monthly_budget)
        st.success("Budget saved!")

    st.divider()
    st.caption("Your expense data is stored in SQLite.")

# ---------------- ADD EXPENSE ----------------
with st.expander("➕ Add New Expense", expanded=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        name = st.text_input("Expense name", placeholder="Example: Tea")

    with col2:
        category = st.selectbox("Category", categories)

    with col3:
        expense_date = st.date_input("Expense date", value=date.today())

    col4, col5 = st.columns([1, 2])

    with col4:
        amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            step=1.0,
            format="%.2f"
        )

    with col5:
        notes = st.text_input(
            "Notes (optional)",
            placeholder="Example: Evening snack"
        )

    if st.button("➕ Add Expense", use_container_width=True):
        if name.strip() and amount > 0:
            add_expense(
                name.strip(),
                category,
                expense_date,
                amount,
                notes.strip()
            )
            st.success("Expense saved successfully!")
            st.rerun()
        else:
            st.warning("Enter an expense name and amount greater than 0.")

# ---------------- LOAD DATA ----------------
df = get_expenses()

if df.empty:
    st.info("No expenses yet. Add your first expense above.")

else:
    df["expense_date"] = pd.to_datetime(df["expense_date"])
    df["month"] = df["expense_date"].dt.strftime("%B %Y")

    # ---------------- FILTERS ----------------
    st.divider()
    st.subheader("🔎 Filters")

    f1, f2, f3 = st.columns(3)

    with f1:
        month_options = ["All months"] + sorted(
            df["month"].unique(),
            reverse=True
        )
        selected_month = st.selectbox("Month", month_options)

    with f2:
        category_options = ["All categories"] + sorted(
            df["category"].unique()
        )
        selected_category = st.selectbox("Category filter", category_options)

    with f3:
        search_text = st.text_input(
            "Search expense",
            placeholder="Search by name or note"
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

    if search_text.strip():
        search_mask = (
            filtered_df["name"].str.contains(
                search_text,
                case=False,
                na=False
            )
            |
            filtered_df["notes"].fillna("").str.contains(
                search_text,
                case=False,
                na=False
            )
        )
        filtered_df = filtered_df[search_mask]

    # ---------------- CURRENT MONTH BUDGET ----------------
    current_month = pd.Timestamp.today().strftime("%B %Y")
    current_month_df = df[df["month"] == current_month]
    current_month_total = current_month_df["amount"].sum()

    remaining = monthly_budget - current_month_total

    st.divider()
    st.subheader("🎯 Monthly Budget")

    b1, b2, b3 = st.columns(3)
    b1.metric("Budget", f"₹{monthly_budget:,.2f}")
    b2.metric("Spent This Month", f"₹{current_month_total:,.2f}")
    b3.metric("Remaining", f"₹{remaining:,.2f}")

    if monthly_budget > 0:
        progress = min(current_month_total / monthly_budget, 1.0)
        st.progress(progress)

        if current_month_total >= monthly_budget:
            st.error("Budget exceeded. Reduce spending this month.")
        elif current_month_total >= monthly_budget * 0.8:
            st.warning("You have used more than 80% of your budget.")
        else:
            st.success("You are within your monthly budget.")

    # ---------------- DASHBOARD ----------------
    st.divider()
    st.subheader("📊 Dashboard")

    total_expense = filtered_df["amount"].sum()
    expense_count = len(filtered_df)
    highest_expense = filtered_df["amount"].max() if expense_count else 0
    daily_average = (
        total_expense / filtered_df["expense_date"].nunique()
        if expense_count else 0
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Expense", f"₹{total_expense:,.2f}")
    m2.metric("Transactions", expense_count)
    m3.metric("Highest Expense", f"₹{highest_expense:,.2f}")
    m4.metric("Daily Average", f"₹{daily_average:,.2f}")

    # ---------------- TABLE ----------------
    st.divider()
    st.subheader("🧾 Expenses")

    table_df = filtered_df[
        ["id", "name", "category", "expense_date", "amount", "notes"]
    ].copy()

    table_df["expense_date"] = table_df["expense_date"].dt.strftime("%d-%m-%Y")
    table_df["amount"] = table_df["amount"].map(lambda x: f"₹{x:,.2f}")

    st.dataframe(
        table_df.rename(columns={"expense_date": "date"}),
        use_container_width=True,
        hide_index=True
    )

    csv_data = filtered_df[
        ["name", "category", "expense_date", "amount", "notes"]
    ].to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇ Download filtered expenses as CSV",
        data=csv_data,
        file_name="expense_report.csv",
        mime="text/csv"
    )

    # ---------------- CHARTS ----------------
    if not filtered_df.empty:
        st.divider()
        st.subheader("📈 Spending Analysis")

        category_total = filtered_df.groupby("category")["amount"].sum()

        c1, c2 = st.columns(2)

        with c1:
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

        with c2:
            st.write("### Category Spending")
            fig2, ax2 = plt.subplots()
            ax2.bar(category_total.index, category_total.values)
            ax2.set_xlabel("Category")
            ax2.set_ylabel("Amount (₹)")
            plt.xticks(rotation=45)
            st.pyplot(fig2)

        st.write("### Spending Over Time")

        daily_total = filtered_df.groupby(
            "expense_date"
        )["amount"].sum().sort_index()

        fig3, ax3 = plt.subplots()
        ax3.plot(daily_total.index, daily_total.values, marker="o")
        ax3.set_xlabel("Date")
        ax3.set_ylabel("Amount (₹)")
        plt.xticks(rotation=45)
        st.pyplot(fig3)

    # ---------------- EDIT ----------------
    st.divider()
    st.subheader("✏️ Edit an Expense")

    edit_options = {
        f"#{row['id']} | {row['name']} | ₹{row['amount']:,.2f}": row["id"]
        for _, row in df.iterrows()
    }

    selected_edit_label = st.selectbox(
        "Choose expense to edit",
        list(edit_options.keys())
    )

    selected_edit_id = edit_options[selected_edit_label]
    selected_row = df[df["id"] == selected_edit_id].iloc[0]

    e1, e2, e3 = st.columns(3)

    with e1:
        edit_name = st.text_input(
            "Edit name",
            value=selected_row["name"]
        )

    with e2:
        edit_category = st.selectbox(
            "Edit category",
            categories,
            index=categories.index(selected_row["category"])
        )

    with e3:
        edit_date = st.date_input(
            "Edit date",
            value=selected_row["expense_date"].date()
        )

    e4, e5 = st.columns([1, 2])

    with e4:
        edit_amount = st.number_input(
            "Edit amount",
            min_value=0.0,
            value=float(selected_row["amount"]),
            step=1.0
        )

    with e5:
        edit_notes = st.text_input(
            "Edit notes",
            value=selected_row["notes"] if selected_row["notes"] else ""
        )

    if st.button("Save Changes", use_container_width=True):
        if edit_name.strip() and edit_amount > 0:
            update_expense(
                selected_edit_id,
                edit_name.strip(),
                edit_category,
                edit_date,
                edit_amount,
                edit_notes.strip()
            )
            st.success("Expense updated!")
            st.rerun()
        else:
            st.warning("Enter a valid name and amount.")

    # ---------------- DELETE ----------------
    st.divider()
    st.subheader("🗑 Manage Expenses")

    d1, d2 = st.columns(2)

    with d1:
        delete_options = {
            f"#{row['id']} | {row['name']} | ₹{row['amount']:,.2f}": row["id"]
            for _, row in df.iterrows()
        }

        selected_delete_label = st.selectbox(
            "Choose expense to delete",
            list(delete_options.keys())
        )

        if st.button("Delete Selected Expense", use_container_width=True):
            delete_expense(delete_options[selected_delete_label])
            st.success("Expense deleted.")
            st.rerun()

    with d2:
        st.write("")
        st.write("")
        if st.button("⚠️ Clear All Expenses", use_container_width=True):
            clear_all_expenses()
            st.success("All expenses cleared.")
            st.rerun()

st.divider()
st.caption("Built with Python, Streamlit, SQLite, Pandas and Matplotlib.")
