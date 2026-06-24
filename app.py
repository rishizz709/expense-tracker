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
# DARK PREMIUM STYLE
# =================================================
st.markdown("""
<style>
    .stApp {
        background:
            radial-gradient(circle at 12% 8%, rgba(37, 99, 235, 0.22), transparent 28%),
            radial-gradient(circle at 88% 12%, rgba(124, 58, 237, 0.20), transparent 30%),
            linear-gradient(135deg, #050816, #0b1020 55%, #111827);
        color: #f8fafc;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 1.8rem;
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
        margin-bottom: 4px;
        letter-spacing: -1px;
    }

    .app-subtitle {
        color: #aab7cf !important;
        font-size: 17px;
        margin-bottom: 24px;
    }

    .glass-card {
        background: rgba(19, 29, 52, 0.72);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 12px;
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.20);
    }

    .creator-card {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.18), rgba(124, 58, 237, 0.18));
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 18px;
        padding: 20px;
        margin-top: 12px;
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

    div[data-testid="stExpander"] {
        background: rgba(19, 29, 52, 0.65);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 16px;
    }

    hr {
        border-color: rgba(148, 163, 184, 0.18);
    }

    .small-muted {
        color: #aab7cf !important;
        font-size: 14px;
    }

    .insight-title {
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 6px;
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
    <div>
        <div class="app-title">{title}</div>
        <div class="app-subtitle">{subtitle}</div>
    </div>
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
    if data.empty:
        return

    current_month = pd.Timestamp.today().strftime("%B %Y")
    current_df = data[data["month"] == current_month]
    current_total = current_df["amount"].sum()

    category_total = current_df.groupby("category")["amount"].sum()

    st.subheader("✨ AI Spending Insights")

    if current_df.empty:
        st.info("Add expenses in the current month to get personalized insights.")
        return

    top_category = category_total.idxmax()
    top_amount = category_total.max()
    top_percentage = (top_amount / current_total) * 100 if current_total > 0 else 0

    budget_left = budget - current_total

    i1, i2, i3 = st.columns(3)

    with i1:
        st.markdown(f"""
        <div class="glass-card">
            <div class="insight-title">🔍 Spending Pattern</div>
            <p class="small-muted">
                <b>{top_category}</b> is your biggest category this month.
                It takes {top_percentage:.0f}% of your spending.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with i2:
        if budget_left >= 0:
            message = f"You still have ₹{budget_left:,.2f} left in your monthly budget."
            title = "💡 Budget Tip"
        else:
            message = f"You are ₹{abs(budget_left):,.2f} above your budget. Reduce optional spending."
            title = "⚠️ Budget Alert"

        st.markdown(f"""
        <div class="glass-card">
            <div class="insight-title">{title}</div>
            <p class="small-muted">{message}</p>
        </div>
        """, unsafe_allow_html=True)

    with i3:
        suggested_saving = top_amount * 0.10

        st.markdown(f"""
        <div class="glass-card">
            <div class="insight-title">🎯 Savings Suggestion</div>
            <p class="small-muted">
                Reducing <b>{top_category}</b> spending by just 10% could save about
                ₹{suggested_saving:,.2f} this month.
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
    st.caption("Built with Streamlit + SQLite")

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
        "A complete view of your money and spending habits."
    )

    if df.empty:
        st.markdown("""
        <div class="glass-card">
            <h3>Start tracking your money</h3>
            <p class="small-muted">
                Add your first expense from the sidebar to unlock your dashboard,
                reports, and smart insights.
            </p>
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
            month_change = (
                (current_total - previous_total) / previous_total
            ) * 100
            month_change_text = f"{month_change:+.1f}% vs last month"
        else:
            month_change_text = "No previous month data"

        total_all = df["amount"].sum()
        transaction_count = len(df)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("This Month", f"₹{current_total:,.2f}", month_change_text)
        c2.metric("Monthly Budget", f"₹{monthly_budget:,.2f}")
        c3.metric("Remaining", f"₹{remaining:,.2f}")
        c4.metric("Total Transactions", transaction_count)

        st.divider()
        st.subheader("🎯 Budget Status")

        if monthly_budget > 0:
            budget_progress = min(current_total / monthly_budget, 1.0)
            st.progress(budget_progress)

            if current_total >= monthly_budget:
                st.error("You have crossed your monthly budget.")
            elif current_total >= monthly_budget * 0.8:
                st.warning("You have used more than 80% of your budget.")
            else:
                st.success("Your spending is within budget.")

        st.divider()
        show_ai_insights(df, monthly_budget)

        st.divider()
        left, right = st.columns(2)

        with left:
            st.subheader("🏆 Top Categories")

            if not current_df.empty:
                top_categories = current_df.groupby(
                    "category"
                )["amount"].sum().sort_values(ascending=False).head(3)

                for category, value in top_categories.items():
                    st.markdown(f"""
                    <div class="glass-card">
                        <b>{category_icons.get(category, '📦')} {category}</b>
                        <br>
                        <span class="small-muted">₹{value:,.2f} spent this month</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No expenses added this month.")

        with right:
            st.subheader("📅 Weekly Spending")

            if not current_df.empty:
                weekly_total = current_df.groupby("week")["amount"].sum()

                fig, ax = plt.subplots()
                fig.patch.set_facecolor("#111827")
                ax.set_facecolor("#111827")

                ax.bar(
                    [f"Week {week}" for week in weekly_total.index],
                    weekly_total.values
                )

                ax.set_ylabel("Amount (₹)", color="white")
                ax.tick_params(colors="white")
                plt.xticks(rotation=25)

                st.pyplot(fig)
            else:
                st.info("No weekly spending data yet.")

        st.divider()
        st.subheader("🕒 Recent Transactions")
        show_expense_table(df.head(5))

# =================================================
# ADD EXPENSE
# =================================================
elif page == "➕ Add Expense":
    show_header(
        "Add Expense",
        "Record your spending in a few seconds."
    )

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    with st.form("add_expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Expense name", placeholder="Example: Coffee")
            category = st.selectbox("Category", categories)

        with col2:
            expense_date = st.date_input("Expense date", value=date.today())
            amount = st.number_input(
                "Amount (₹)",
                min_value=0.0,
                step=1.0,
                format="%.2f"
            )

        notes = st.text_area(
            "Notes (optional)",
            placeholder="Example: Coffee with friends"
        )

        submitted = st.form_submit_button(
            "➕ Save Expense",
            use_container_width=True
        )

        if submitted:
            if name.strip() and amount > 0:
                add_expense(
                    name.strip(),
                    category,
                    expense_date,
                    amount,
                    notes.strip()
                )
                st.success("Expense saved successfully!")
            else:
                st.warning("Enter an expense name and amount greater than 0.")

    st.markdown('</div>', unsafe_allow_html=True)

# =================================================
# EXPENSES
# =================================================
elif page == "🧾 Expenses":
    show_header(
        "All Expenses",
        "Search, filter, edit, delete, and download transactions."
    )

    if df.empty:
        st.info("No expenses yet. Add an expense first.")

    else:
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
            selected_category = st.selectbox("Category", category_options)

        with f3:
            search_text = st.text_input(
                "Search",
                placeholder="Search name or notes"
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

        selected_edit_label = st.selectbox(
            "Choose an expense to edit",
            list(edit_options.keys())
        )

        selected_edit_id = edit_options[selected_edit_label]
        selected_row = df[df["id"] == selected_edit_id].iloc[0]

        with st.form("edit_expense_form"):
            e1, e2, e3 = st.columns(3)

            with e1:
                edit_name = st.text_input(
                    "Expense name",
                    value=selected_row["name"],
                    key="edit_name"
                )

            with e2:
                edit_category = st.selectbox(
                    "Category",
                    categories,
                    index=categories.index(selected_row["category"]),
                    key="edit_category"
                )

            with e3:
                edit_date = st.date_input(
                    "Date",
                    value=selected_row["expense_date"].date(),
                    key="edit_date"
                )

            e4, e5 = st.columns([1, 2])

            with e4:
                edit_amount = st.number_input(
                    "Amount",
                    min_value=0.0,
                    value=float(selected_row["amount"]),
                    step=1.0,
                    key="edit_amount"
                )

            with e5:
                edit_notes = st.text_input(
                    "Notes",
                    value=selected_row["notes"] if selected_row["notes"] else "",
                    key="edit_notes"
                )

            save_edit = st.form_submit_button(
                "Save Changes",
                use_container_width=True
            )

            if save_edit:
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

        st.divider()
        st.subheader("🗑 Delete Expense")

        delete_options = {
            f"#{row['id']} | {row['name']} | ₹{row['amount']:,.2f}": row["id"]
            for _, row in df.iterrows()
        }

        d1, d2 = st.columns(2)

        with d1:
            selected_delete_label = st.selectbox(
                "Choose an expense to delete",
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

# =================================================
# REPORTS
# =================================================
elif page == "📈 Reports":
    show_header(
        "Reports & Analysis",
        "Understand where your money is going."
    )

    if df.empty:
        st.info("Add expenses first to view reports.")

    else:
        report_month_options = ["All months"] + sorted(
            df["month"].unique(),
            reverse=True
        )

        report_month = st.selectbox(
            "Choose month for report",
            report_month_options
        )

        report_df = df.copy()

        if report_month != "All months":
            report_df = report_df[
                report_df["month"] == report_month
            ]

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
                    [
                        category_icons.get(cat, "📦") + " " + cat
                        for cat in category_total.index
                    ],
                    category_total.values
                )

                ax2.set_ylabel("Amount (₹)", color="white")
                ax2.tick_params(colors="white")
                plt.xticks(rotation=45)

                st.pyplot(fig2)

            st.divider()
            st.subheader("Spending Over Time")

            daily_total = report_df.groupby(
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

# =================================================
# SETTINGS
# =================================================
elif page == "⚙️ Settings":
    show_header(
        "Settings",
        "Manage your budget and app information."
    )

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
            ExpenseFlow is a personal finance dashboard built using Python,
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
            ExpenseFlow stores expenses using SQLite.
            It works well locally. On free cloud hosting, SQLite files can reset
            after restart or redeployment.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.divider()
st.caption("ExpenseFlow • Made by Rishi • Built with Python and Streamlit")
