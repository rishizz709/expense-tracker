import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from datetime import date

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="ExpenseFlow",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =================================================
# PREMIUM DARK UI
# =================================================
st.markdown("""
<style>
    .stApp {
        background:
            radial-gradient(circle at 10% 5%, rgba(37, 99, 235, 0.20), transparent 30%),
            radial-gradient(circle at 92% 10%, rgba(124, 58, 237, 0.18), transparent 28%),
            linear-gradient(135deg, #050816, #0b1020 55%, #111827);
    }

    .block-container {
        max-width: 1300px;
        padding-top: 1.7rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, h4, p, label, span {
        color: #f8fafc !important;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #070b18, #10182c);
        border-right: 1px solid rgba(148, 163, 184, 0.16);
    }

    .app-title {
        font-size: 42px;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 3px;
    }

    .app-subtitle {
        color: #aab7cf !important;
        font-size: 16px;
        margin-bottom: 22px;
    }

    .glass-card {
        background: rgba(19, 29, 52, 0.76);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 12px;
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.20);
    }

    .creator-card {
        background: linear-gradient(
            135deg,
            rgba(37, 99, 235, 0.18),
            rgba(124, 58, 237, 0.18)
        );
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 18px;
        padding: 20px;
        margin-top: 12px;
    }

    .small-muted {
        color: #aab7cf !important;
        font-size: 14px;
    }

    .insight-title {
        font-size: 17px;
        font-weight: 700;
        margin-bottom: 6px;
    }

    div[data-testid="stMetric"] {
        background: rgba(19, 29, 52, 0.76);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.20);
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
        border-radius: 11px;
        font-weight: 700;
        padding: 10px 18px;
    }

    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.35);
    }

    div[data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
    }

    hr {
        border-color: rgba(148, 163, 184, 0.18);
    }
</style>
""", unsafe_allow_html=True)

# =================================================
# DATABASE
# =================================================
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

# Makes old database compatible with this version
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


# =================================================
# HELPERS
# =================================================
categories = [
    "Food", "Travel", "Shopping", "Bills",
    "Entertainment", "Health", "Education",
    "Rent", "Other"
]

category_icons = {
    "Food": "🍔",
    "Travel": "🚌",
    "Shopping": "🛍️",
    "Bills": "💡",
    "Entertainment": "🎬",
    "Health": "🏥",
    "Education": "📚",
    "Rent": "🏠",
    "Other": "📦"
}


def prepare_data():
    data = get_expenses()

    if not data.empty:
        data["expense_date"] = pd.to_datetime(data["expense_date"])
        data["month"] = data["expense_date"].dt.strftime("%B %Y")
        data["year_month"] = data["expense_date"].dt.to_period("M").astype(str)
        data["week"] = data["expense_date"].dt.isocalendar().week.astype(int)

    return data


def show_header(title, subtitle):
    st.markdown(f"""
    <div class="app-title">{title}</div>
    <div class="app-subtitle">{subtitle}</div>
    """, unsafe_allow_html=True)


def show_expense_table(data):
    if data.empty:
        st.info("No expenses found.")
        return

    table_df = data[
        ["id", "name", "category", "expense_date", "amount", "notes"]
    ].copy()

    table_df["category"] = table_df["category"].map(
        lambda x: f"{category_icons.get(x, '📦')} {x}"
    )

    table_df["expense_date"] = table_df["expense_date"].dt.strftime("%d-%m-%Y")
    table_df["amount"] = table_df["amount"].map(lambda x: f"₹{x:,.2f}")

    st.dataframe(
        table_df.rename(columns={"expense_date": "date"}),
        use_container_width=True,
        hide_index=True
    )


def show_ai_insights(data, budget):
    current_month = pd.Timestamp.today().strftime("%B %Y")
    current_df = data[data["month"] == current_month]

    if current_df.empty:
        st.info("Add an expense this month to unlock smart insights.")
        return

    current_total = current_df["amount"].sum()
    category_total = current_df.groupby("category")["amount"].sum()

    top_category = category_total.idxmax()
    top_amount = category_total.max()
    top_percent = (top_amount / current_total) * 100 if current_total else 0

    budget_left = budget - current_total
    suggested_save = top_amount * 0.10

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class="glass-card">
            <div class="insight-title">🔍 Spending Pattern</div>
            <p class="small-muted">
                <b>{top_category}</b> is your biggest category this month,
                using {top_percent:.0f}% of your spending.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        if budget_left >= 0:
            title = "💡 Budget Tip"
            text = f"You still have ₹{budget_left:,.2f} left in your monthly budget."
        else:
            title = "⚠️ Budget Alert"
            text = f"You are ₹{abs(budget_left):,.2f} above budget. Reduce optional spending."

        st.markdown(f"""
        <div class="glass-card">
            <div class="insight-title">{title}</div>
            <p class="small-muted">{text}</p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="glass-card">
            <div class="insight-title">🎯 Savings Suggestion</div>
            <p class="small-muted">
                Reducing <b>{top_category}</b> spending by 10% can save
                around ₹{suggested_save:,.2f}.
            </p>
        </div>
        """, unsafe_allow_html=True)


# =================================================
# SIDEBAR
# =================================================
with st.sidebar:
    st.markdown("## 💸 ExpenseFlow")
    st.caption("Personal finance, simplified")

    page = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "➕ Add Expense",
            "🧾 Expenses",
            "📈 Reports",
            "⚙️ Settings"
        ],
        label_visibility="collapsed"
    )

    st.divider()
    st.caption("Made by Rishi")

# =================================================
# LOAD DATA
# =================================================
df = prepare_data()
monthly_budget = get_budget()

# =================================================
# DASHBOARD
# =================================================
if page == "📊 Dashboard":
    show_header(
        "Good to see you 👋",
        "Your personal money command center."
    )

    if df.empty:
        st.markdown("""
        <div class="glass-card">
            <h3>Welcome to ExpenseFlow 💸</h3>
            <p class="small-muted">
                Add your first expense to unlock reports, insights,
                charts, and budget tracking.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("🚀 What you can do here")

        a1, a2, a3 = st.columns(3)

        with a1:
            st.markdown("""
            <div class="glass-card">
                <h3>➕ Add Expenses</h3>
                <p class="small-muted">Track food, travel, shopping, bills and more.</p>
            </div>
            """, unsafe_allow_html=True)

        with a2:
            st.markdown("""
            <div class="glass-card">
                <h3>📈 View Reports</h3>
                <p class="small-muted">Understand where your money is going.</p>
            </div>
            """, unsafe_allow_html=True)

        with a3:
            st.markdown("""
            <div class="glass-card">
                <h3>✨ Smart Insights</h3>
                <p class="small-muted">Get automatic savings suggestions.</p>
            </div>
            """, unsafe_allow_html=True)

    else:
        current_month = pd.Timestamp.today().strftime("%B %Y")
        current_df = df[df["month"] == current_month]

        current_total = current_df["amount"].sum()
        remaining = monthly_budget - current_total

        previous_month_period = (
            pd.Timestamp.today().to_period("M") - 1
        ).strftime("%Y-%m")

        previous_total = df[
            df["year_month"] == previous_month_period
        ]["amount"].sum()

        if previous_total > 0:
            change = ((current_total - previous_total) / previous_total) * 100
            change_text = f"{change:+.1f}% vs last month"
        else:
            change_text = "No previous data"

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("This Month", f"₹{current_total:,.2f}", change_text)
        m2.metric("Monthly Budget", f"₹{monthly_budget:,.2f}")
        m3.metric("Remaining", f"₹{remaining:,.2f}")
        m4.metric("Transactions", len(current_df))

        st.divider()

        left, right = st.columns([2, 1])

        with left:
            st.subheader("🎯 Monthly Budget Progress")

            if monthly_budget > 0:
                progress = min(current_total / monthly_budget, 1.0)
                st.progress(progress)

                if current_total >= monthly_budget:
                    st.error(f"Budget crossed by ₹{current_total - monthly_budget:,.2f}")
                elif current_total >= monthly_budget * 0.8:
                    st.warning(f"You used {progress * 100:.0f}% of your budget.")
                else:
                    st.success(f"Great! ₹{remaining:,.2f} is still available.")

        with right:
            average = current_total / len(current_df) if len(current_df) > 0 else 0
            highest = current_df["amount"].max() if not current_df.empty else 0

            st.subheader("⚡ Quick Summary")

            st.markdown(f"""
            <div class="glass-card">
                <b>Average expense</b><br>
                <span class="small-muted">₹{average:,.2f}</span>
            </div>
            <div class="glass-card">
                <b>Highest expense</b><br>
                <span class="small-muted">₹{highest:,.2f}</span>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        st.subheader("✨ AI Spending Insights")
        show_ai_insights(df, monthly_budget)

        st.divider()

        chart1, chart2 = st.columns(2)

        with chart1:
            st.subheader("📊 Spending by Category")

            if not current_df.empty:
                category_total = current_df.groupby(
                    "category"
                )["amount"].sum().sort_values(ascending=False)

                fig1, ax1 = plt.subplots()
                fig1.patch.set_facecolor("#111827")
                ax1.set_facecolor("#111827")

                ax1.bar(
                    [f"{category_icons.get(cat, '📦')} {cat}" for cat in category_total.index],
                    category_total.values
                )

                ax1.set_ylabel("Amount (₹)", color="white")
                ax1.tick_params(colors="white")
                plt.xticks(rotation=35)
                st.pyplot(fig1)

        with chart2:
            st.subheader("📅 Daily Spending Trend")

            if not current_df.empty:
                daily_total = current_df.groupby(
                    "expense_date"
                )["amount"].sum().sort_index()

                fig2, ax2 = plt.subplots()
                fig2.patch.set_facecolor("#111827")
                ax2.set_facecolor("#111827")

                ax2.plot(
                    daily_total.index,
                    daily_total.values,
                    marker="o"
                )

                ax2.set_ylabel("Amount (₹)", color="white")
                ax2.tick_params(colors="white")
                plt.xticks(rotation=35)
                st.pyplot(fig2)

        st.divider()

        bottom_left, bottom_right = st.columns(2)

        with bottom_left:
            st.subheader("🏆 Top Spending Categories")

            if not current_df.empty:
                top_categories = current_df.groupby(
                    "category"
                )["amount"].sum().sort_values(ascending=False).head(4)

                for category, value in top_categories.items():
                    percent = (value / current_total * 100) if current_total else 0

                    st.markdown(f"""
                    <div class="glass-card">
                        <b>{category_icons.get(category, '📦')} {category}</b><br>
                        <span class="small-muted">
                            ₹{value:,.2f} • {percent:.0f}% of this month
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

        with bottom_right:
            st.subheader("🕒 Recent Activity")

            for _, row in df.head(5).iterrows():
                icon = category_icons.get(row["category"], "📦")

                st.markdown(f"""
                <div class="glass-card">
                    <b>{icon} {row["name"]}</b><br>
                    <span class="small-muted">
                        {row["category"]} • {row["expense_date"].strftime("%d %b %Y")}
                    </span><br>
                    <b>₹{row["amount"]:,.2f}</b>
                </div>
                """, unsafe_allow_html=True)

        st.divider()
        st.subheader("💡 Financial Tip of the Day")

        tips = [
            "Try the 24-hour rule before buying non-essential things.",
            "Save at least 10% of your income before spending.",
            "Small daily expenses can become large monthly costs.",
            "Review your expenses every Sunday.",
            "Set separate limits for Food and Shopping."
        ]

        tip = tips[pd.Timestamp.today().day % len(tips)]

        st.markdown(f"""
        <div class="creator-card">
            <h3>✨ {tip}</h3>
            <p class="small-muted">
                Small money habits can create big savings over time.
            </p>
        </div>
        """, unsafe_allow_html=True)

# =================================================
# ADD EXPENSE
# =================================================
elif page == "➕ Add Expense":
    show_header("Add Expense", "Record your spending in a few seconds.")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    with st.form("add_expense_form", clear_on_submit=True):
        c1, c2 = st.columns(2)

        with c1:
            name = st.text_input("Expense name", placeholder="Example: Coffee")
            category = st.selectbox("Category", categories)

        with c2:
            expense_date = st.date_input("Expense date", value=date.today())
            amount = st.number_input("Amount (₹)", min_value=0.0, step=1.0)

        notes = st.text_area("Notes (optional)")

        submitted = st.form_submit_button("➕ Save Expense", use_container_width=True)

        if submitted:
            if name.strip() and amount > 0:
                add_expense(name.strip(), category, expense_date, amount, notes.strip())
                st.success("Expense saved successfully!")
            else:
                st.warning("Enter an expense name and valid amount.")

    st.markdown('</div>', unsafe_allow_html=True)

# =================================================
# EXPENSES
# =================================================
elif page == "🧾 Expenses":
    show_header("All Expenses", "Search, filter, edit, delete, and download transactions.")

    if df.empty:
        st.info("No expenses yet. Add an expense first.")

    else:
        f1, f2, f3 = st.columns(3)

        with f1:
            month_options = ["All months"] + sorted(df["month"].unique(), reverse=True)
            selected_month = st.selectbox("Month", month_options)

        with f2:
            category_options = ["All categories"] + sorted(df["category"].unique())
            selected_category = st.selectbox("Category", category_options)

        with f3:
            search_text = st.text_input("Search", placeholder="Search name or notes")

        filtered_df = df.copy()

        if selected_month != "All months":
            filtered_df = filtered_df[filtered_df["month"] == selected_month]

        if selected_category != "All categories":
            filtered_df = filtered_df[filtered_df["category"] == selected_category]

        if search_text.strip():
            filtered_df = filtered_df[
                filtered_df["name"].str.contains(search_text, case=False, na=False)
                |
                filtered_df["notes"].fillna("").str.contains(search_text, case=False, na=False)
            ]

        st.divider()
        show_expense_table(filtered_df)

        csv_data = filtered_df[
            ["name", "category", "expense_date", "amount", "notes"]
        ].to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇ Download filtered CSV",
            data=csv_data,
            file_name="expense_report.csv",
            mime="text/csv"
        )

        st.divider()
        st.subheader("✏️ Edit Expense")

        edit_options = {
            f"#{row['id']} | {row['name']} | ₹{row['amount']:,.2f}": row["id"]
            for _, row in df.iterrows()
        }

        edit_label = st.selectbox("Choose an expense to edit", list(edit_options.keys()))
        edit_id = edit_options[edit_label]
        row = df[df["id"] == edit_id].iloc[0]

        with st.form("edit_expense_form"):
            e1, e2, e3 = st.columns(3)

            with e1:
                edit_name = st.text_input("Expense name", value=row["name"])

            with e2:
                edit_category = st.selectbox(
                    "Category",
                    categories,
                    index=categories.index(row["category"])
                )

            with e3:
                edit_date = st.date_input("Date", value=row["expense_date"].date())

            e4, e5 = st.columns([1, 2])

            with e4:
                edit_amount = st.number_input(
                    "Amount",
                    min_value=0.0,
                    value=float(row["amount"]),
                    step=1.0
                )

            with e5:
                edit_notes = st.text_input(
                    "Notes",
                    value=row["notes"] if row["notes"] else ""
                )

            save_edit = st.form_submit_button("Save Changes", use_container_width=True)

            if save_edit:
                if edit_name.strip() and edit_amount > 0:
                    update_expense(
                        edit_id,
                        edit_name.strip(),
                        edit_category,
                        edit_date,
                        edit_amount,
                        edit_notes.strip()
                    )
                    st.success("Expense updated!")
                    st.rerun()
                else:
                    st.warning("Enter valid values.")

        st.divider()
        st.subheader("🗑 Delete Expense")

        delete_options = {
            f"#{row['id']} | {row['name']} | ₹{row['amount']:,.2f}": row["id"]
            for _, row in df.iterrows()
        }

        d1, d2 = st.columns(2)

        with d1:
            delete_label = st.selectbox(
                "Choose an expense to delete",
                list(delete_options.keys())
            )

            if st.button("Delete Selected Expense", use_container_width=True):
                delete_expense(delete_options[delete_label])
                st.success("Expense deleted.")
                st.rerun()

        with d2:
            st.write("")
            st.write("")

            if st.button("⚠️ Clear All Expenses", use_container_width=True):
                clear_all_expenses()
                st.success("All expenses cleared.")
                st.rerun()

# =================================================
# REPORTS
# =================================================
elif page == "📈 Reports":
    show_header("Reports & Analysis", "Understand where your money is going.")

    if df.empty:
        st.info("Add expenses first to view reports.")

    else:
        month_options = ["All months"] + sorted(df["month"].unique(), reverse=True)
        report_month = st.selectbox("Choose month for report", month_options)

        report_df = df.copy()

        if report_month != "All months":
            report_df = report_df[report_df["month"] == report_month]

        if report_df.empty:
            st.warning("No expenses found for this selection.")

        else:
            total = report_df["amount"].sum()
            highest = report_df["amount"].max()
            category_total = report_df.groupby("category")["amount"].sum()

            r1, r2, r3 = st.columns(3)
            r1.metric("Total Spending", f"₹{total:,.2f}")
            r2.metric("Highest Expense", f"₹{highest:,.2f}")
            r3.metric("Categories Used", len(category_total))

            st.divider()
            c1, c2 = st.columns(2)

            with c1:
                st.subheader("Category Distribution")

                fig1, ax1 = plt.subplots()
                fig1.patch.set_facecolor("#111827")
                ax1.set_facecolor("#111827")

                ax1.pie(
                    category_total,
                    labels=[
                        f"{category_icons.get(cat, '📦')} {cat}"
                        for cat in category_total.index
                    ],
                    autopct="%1.1f%%",
                    startangle=90,
                    textprops={"color": "white"}
                )

                ax1.axis("equal")
                st.pyplot(fig1)

            with c2:
                st.subheader("Category Spending")

                fig2, ax2 = plt.subplots()
                fig2.patch.set_facecolor("#111827")
                ax2.set_facecolor("#111827")

                ax2.bar(
                    [f"{category_icons.get(cat, '📦')} {cat}" for cat in category_total.index],
                    category_total.values
                )

                ax2.set_ylabel("Amount (₹)", color="white")
                ax2.tick_params(colors="white")
                plt.xticks(rotation=45)
                st.pyplot(fig2)

            st.divider()
            st.subheader("Spending Over Time")

            daily_total = report_df.groupby("expense_date")["amount"].sum().sort_index()

            fig3, ax3 = plt.subplots()
            fig3.patch.set_facecolor("#111827")
            ax3.set_facecolor("#111827")

            ax3.plot(daily_total.index, daily_total.values, marker="o")
            ax3.set_xlabel("Date", color="white")
            ax3.set_ylabel("Amount (₹)", color="white")
            ax3.tick_params(colors="white")
            plt.xticks(rotation=45)

            st.pyplot(fig3)

# =================================================
# SETTINGS
# =================================================
elif page == "⚙️ Settings":
    show_header("Settings", "Manage your budget and app information.")

    st.subheader("🎯 Monthly Budget")

    new_budget = st.number_input(
        "Set monthly budget (₹)",
        min_value=0.0,
        value=float(monthly_budget),
        step=500.0
    )

    if st.button("Save Monthly Budget", use_container_width=True):
        save_budget(new_budget)
        st.success("Monthly budget saved!")
        st.rerun()

    st.divider()
    st.subheader("👨‍💻 Creator")

    st.markdown("""
    <div class="creator-card">
        <h3>Made by Rishi</h3>
        <p class="small-muted">
            ExpenseFlow is a personal finance dashboard built with Python,
            Streamlit, SQLite, Pandas, and Matplotlib.
        </p>
        <p>
            🔗 GitHub:
            <a href="https://github.com/rishizz709" target="_blank"
            style="color:#93c5fd; font-weight:bold;">
            github.com/rishizz709
            </a>
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.subheader("ℹ️ App Information")

    st.markdown("""
    <div class="glass-card">
        <p class="small-muted">
            ExpenseFlow saves expenses using SQLite. It works best on your laptop.
            On free cloud hosting, SQLite data may reset after redeployment.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.divider()
st.caption("ExpenseFlow • Made by Rishi • Built with Python and Streamlit")
