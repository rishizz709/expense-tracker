import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from datetime import date

# -------------------------------------------------
# PAGE SETTINGS
# -------------------------------------------------
st.set_page_config(
    page_title="Smart Expense Tracker",
    page_icon="💸",
    layout="wide"
)

# -------------------------------------------------
# DARK PREMIUM DESIGN
# -------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background:
            radial-gradient(circle at 15% 10%, rgba(59, 130, 246, 0.20), transparent 28%),
            radial-gradient(circle at 85% 15%, rgba(168, 85, 247, 0.18), transparent 30%),
            linear-gradient(135deg, #060b18 0%, #0b1224 45%, #111827 100%);
        color: #f8fafc;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, h4, p, label {
        color: #f8fafc !important;
    }

    .hero {
        text-align: center;
        padding: 18px 0 24px 0;
    }

    .hero h1 {
        font-size: 48px;
        font-weight: 800;
        margin-bottom: 6px;
        letter-spacing: -1px;
    }

    .hero p {
        color: #aab7cf !important;
        font-size: 18px;
    }

    div[data-testid="stMetric"] {
        background: rgba(20, 30, 55, 0.78);
        border: 1px solid rgba(148, 163, 184, 0.20);
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.22);
    }

    div[data-testid="stMetricLabel"] {
        color: #aab7cf !important;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        padding: 10px 18px;
    }

    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.35);
    }

    div[data-testid="stExpander"] {
        background: rgba(20, 30, 55, 0.60);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 16px;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0b1224, #111827);
        border-right: 1px solid rgba(148, 163, 184, 0.16);
    }

    hr {
        border-color: rgba(148, 163, 184, 0.20);
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# DATABASE
# -------------------------------------------------
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

# Fix old database versions that do not have notes column
try:
    cursor.execute("ALTER TABLE expenses ADD COLUMN notes TEXT")
except sqlite3.OperationalError:
    pass

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


def delete_expense(expense_id):
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()


def clear_all_expenses():
    cursor.execute("DELETE FROM expenses")
    conn.commit()


def get_budget():
    cursor.execute(
        "SELECT setting_value FROM settings WHERE setting_name = 'monthly_budget'"
    )
    result = cursor.fetchone()
    return float(result[0]) if result else 5000.0


def save_budget(budget):
    cursor.execute(
        """
        INSERT OR REPLACE INTO settings (setting_name, setting_value)
        VALUES ('monthly_budget', ?)
        """,
        (str(budget),)
    )
    conn.commit()


# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown("""
<div class="hero">
    <h1>💸 Smart Expense Tracker</h1>
    <p>Your personal finance dashboard — clear, simple, and powerful.</p>
</div>
""", unsafe_allow_html=True)

categories = [
    "Food", "Travel", "Shopping", "Bills",
    "Entertainment", "Health", "Education",
    "Rent", "Other"
]

# -------------------------------------------------
# SIDEBAR SETTINGS
# -------------------------------------------------
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
    st.caption("Expenses are saved in SQLite database.")

# -------------------------------------------------
# ADD EXPENSE
# -------------------------------------------------
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

# -------------------------------------------------
# LOAD EXPENSES
# -------------------------------------------------
df = get_expenses()

if df.empty:
    st.info("No expenses yet. Add your first expense above.")

else:
    df["expense_date"] = pd.to_datetime(df["expense_date"])
    df["month"] = df["expense_date"].dt.strftime("%B %Y")

    # -------------------------------------------------
    # FILTERS
    # -------------------------------------------------
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
        selected_category = st.selectbox(
            "Category filter",
            category_options
        )

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
        filtered_df = filtered_df[
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
        ]

    # -------------------------------------------------
    # MONTHLY BUDGET
    # -------------------------------------------------
    current_month = pd.Timestamp.today().strftime("%B %Y")
    current_month_total = df[
        df["month"] == current_month
    ]["amount"].sum()

    remaining = monthly_budget - current_month_total

    st.divider()
    st.subheader("🎯 Monthly Budget")

    b1, b2, b3 = st.columns(3)
    b1.metric("Budget", f"₹{monthly_budget:,.2f}")
    b2.metric("Spent This Month", f"₹{current_month_total:,.2f}")
    b3.metric("Remaining", f"₹{remaining:,.2f}")

    if monthly_budget > 0:
        st.progress(min(current_month_total / monthly_budget, 1.0))

        if current_month_total >= monthly_budget:
            st.error("Budget exceeded. Reduce spending this month.")
        elif current_month_total >= monthly_budget * 0.8:
            st.warning("You have used more than 80% of your budget.")
        else:
            st.success("You are within your monthly budget.")

    # -------------------------------------------------
    # DASHBOARD CARDS
    # -------------------------------------------------
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

    # -------------------------------------------------
    # EXPENSE TABLE
    # -------------------------------------------------
    st.divider()
    st.subheader("🧾 Expenses")

    table_df = filtered_df[
        ["id", "name", "category", "expense_date", "amount", "notes"]
    ].copy()

    table_df["expense_date"] = table_df["expense_date"].dt.strftime("%d-%m-%Y")
    table_df["amount"] = table_df["amount"].map(
        lambda value: f"₹{value:,.2f}"
    )

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

    # -------------------------------------------------
    # CHARTS
    # -------------------------------------------------
    if not filtered_df.empty:
        st.divider()
        st.subheader("📈 Spending Analysis")

        category_total = filtered_df.groupby(
            "category"
        )["amount"].sum()

        c1, c2 = st.columns(2)

        with c1:
            st.write("### Category Distribution")

            fig1, ax1 = plt.subplots()
            fig1.patch.set_facecolor("#111827")
            ax1.set_facecolor("#111827")

            ax1.pie(
                category_total,
                labels=category_total.index,
                autopct="%1.1f%%",
                startangle=90,
                textprops={"color": "white"}
            )

            ax1.axis("equal")
            st.pyplot(fig1)

        with c2:
            st.write("### Category Spending")

            fig2, ax2 = plt.subplots()
            fig2.patch.set_facecolor("#111827")
            ax2.set_facecolor("#111827")

            ax2.bar(category_total.index, category_total.values)
            ax2.set_xlabel("Category", color="white")
            ax2.set_ylabel("Amount (₹)", color="white")
            ax2.tick_params(colors="white")
            plt.xticks(rotation=45)

            st.pyplot(fig2)

        st.write("### Spending Over Time")

        daily_total = filtered_df.groupby(
            "expense_date"
        )["amount"].sum().sort_index()

        fig3, ax3 = plt.subplots()
        fig3.patch.set_facecolor("#111827")
        ax3.set_facecolor("#111827")

        ax3.plot(daily_total.index, daily_total.values, marker="o")
        ax3.set_xlabel("Date", color="white")
        ax3.set_ylabel("Amount (₹)", color="white")
        ax3.tick_params(colors="white")
        plt.xticks(rotation=45)

        st.pyplot(fig3)

    # -------------------------------------------------
    # EDIT EXPENSE
    # -------------------------------------------------
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

    # -------------------------------------------------
    # DELETE / CLEAR
    # -------------------------------------------------
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
