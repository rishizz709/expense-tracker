from components.navbar import show_navbar
from components.sidebar import show_sidebar
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime
from supabase import create_client, Client

# ---------------------------------------------------
# PAGE SETTINGS
# ---------------------------------------------------
st.set_page_config(
    page_title="ExpenseFlow",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------
# DESIGN
# ---------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #07111f 0%, #0d1b2a 50%, #102a43 100%);
        color: #f7fafc;
    }
    [data-testid="stSidebar"] {
        background: rgba(4, 14, 28, 0.96);
    }
    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .hero {
        padding: 1.6rem 1.8rem;
        border-radius: 22px;
        background: linear-gradient(120deg, #1d4ed8, #0f766e);
        margin-bottom: 1.2rem;
        box-shadow: 0 14px 40px rgba(0, 0, 0, 0.25);
    }
    .hero h1 {
        color: white;
        margin: 0;
        font-size: 2.2rem;
    }
    .hero p {
        color: #dbeafe;
        margin: 0.35rem 0 0 0;
    }
    .metric-card {
        padding: 1.15rem;
        border-radius: 18px;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.14);
        min-height: 125px;
    }
    .metric-label {
        color: #b9c8da;
        font-size: 0.9rem;
    }
    .metric-value {
        color: white;
        font-size: 1.75rem;
        font-weight: 700;
        margin-top: 0.4rem;
    }
    .small-note {
        color: #b9c8da;
        font-size: 0.88rem;
    }
    .footer {
        margin-top: 3rem;
        padding: 1.2rem;
        text-align: center;
        border-radius: 16px;
        background: rgba(255,255,255,0.06);
        color: #cbd5e1;
    }
    @media (max-width: 700px) {
        .block-container {
            padding: 1rem;
        }
        .hero h1 {
            font-size: 1.7rem;
        }
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------
# SUPABASE CONNECTION
# ---------------------------------------------------
@st.cache_resource
def get_supabase() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


try:
    supabase = get_supabase()
except Exception:
    st.error("Supabase is not connected yet. Add SUPABASE_URL and SUPABASE_KEY in Streamlit Secrets.")
    st.stop()


# ---------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------
def current_user():
    try:
        response = supabase.auth.get_user()
        return response.user
    except Exception:
        return None


def format_money(value):
    return f"₹{float(value):,.2f}"


def load_transactions(user_id):
    response = (
        supabase.table("transactions")
        .select("*")
        .eq("user_id", user_id)
        .order("transaction_date", desc=True)
        .execute()
    )
    return pd.DataFrame(response.data)


def load_budget(user_id, month):
    response = (
        supabase.table("budgets")
        .select("*")
        .eq("user_id", user_id)
        .eq("month", month)
        .execute()
    )

    if response.data:
        return response.data[0]

    return None


def load_goals(user_id):
    response = (
        supabase.table("goals")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )

    return pd.DataFrame(response.data)

def create_profile_if_missing(user):
    try:
        supabase.table("profiles").upsert({
            "id": user.id,
            "full_name": user.user_metadata.get("full_name", "")
        }).execute()
    except Exception:
        pass


# ---------------------------------------------------
# LOGIN / SIGNUP SCREEN
# ---------------------------------------------------
def login_screen():
    left, center, right = st.columns([1, 1.35, 1])

    with center:
        st.markdown("""
        <div class="hero">
            <h1>💰 ExpenseFlow</h1>
            <p>Your elegant personal finance dashboard.</p>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["Login", "Create account"])

        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Password", type="password", key="login_password")
                login_button = st.form_submit_button("Login", use_container_width=True)
                

            if login_button:
                try:
                    supabase.auth.sign_in_with_password({
                        "email": email,
                        "password": password
                    })
                    st.success("Login successful.")
                    st.rerun()
                except Exception as error:
                    st.error(f"Login failed: {error}")
                    st.markdown("---")
    st.subheader("Forgot Password")

    reset_email = st.text_input(
        "Enter your registered email",
        key="reset_email"
    )

    if st.button("Send Reset Link", use_container_width=True):
        try:
            supabase.auth.reset_password_email(
                reset_email,
                {
                    "redirect_to": "https://EXPENSE-FLOW-streamlit.app"
                }
            )

            st.success("Password reset email sent. Check your inbox.")

        except Exception as e:
            st.error(str(e))

        with tab_signup:
            with st.form("signup_form"):
                full_name = st.text_input("Your name")
                email = st.text_input("Email", key="signup_email")
                password = st.text_input(
                    "Password",
                    type="password",
                    help="Use at least 6 characters."
                )
                signup_button = st.form_submit_button("Create account", use_container_width=True)

            if signup_button:
                if len(password) < 6:
                    st.warning("Password must have at least 6 characters.")
                elif not email or not full_name:
                    st.warning("Enter your name and email.")
                else:
                    try:
                        supabase.auth.sign_up({
                            "email": email,
                            "password": password,
                            "options": {
                                "data": {
                                    "full_name": full_name
                                }
                            }
                        })
                        st.success("Account created. You can now log in.")
                    except Exception as error:
                        st.error(f"Could not create account: {error}")

        st.caption("Secure login • Your financial data is private to your account")

# ---------------------------------------------------
# MAIN APP
# ---------------------------------------------------
def main_app(user):
    user_name = user.user_metadata.get("full_name", "Rishi")
    show_navbar(user_name)

    create_profile_if_missing(user)

    full_name = user.user_metadata.get("full_name", "Friend")
    first_name = full_name.split()[0] if full_name else "Friend"

    page = show_sidebar(user.email)
    st.write("Current Page:", page)
    

    if page == "Logout":
        supabase.auth.sign_out()
        st.rerun()
    df = load_transactions(user.id)
    goals_df = load_goals(user.id)

    if df.empty:
        income_total = 0
        expense_total = 0
        balance = 0
    else:
        df["amount"] = pd.to_numeric(df["amount"])
        income_total = df.loc[df["transaction_type"] == "Income", "amount"].sum()
        expense_total = df.loc[df["transaction_type"] == "Expense", "amount"].sum()
        balance = income_total - expense_total

    if page == "Dashboard":
        st.markdown(f"""
        <div class="hero">
            <h1>Welcome back, {first_name} 👋</h1>
            <p>See where your money is going and make smarter decisions.</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total income</div>
                <div class="metric-value">{format_money(income_total)}</div>
                <div class="small-note">All recorded income</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total expenses</div>
                <div class="metric-value">{format_money(expense_total)}</div>
                <div class="small-note">All recorded spending</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Current balance</div>
                <div class="metric-value">{format_money(balance)}</div>
                <div class="small-note">Income minus expenses</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            savings_rate = (balance / income_total * 100) if income_total > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Savings rate</div>
                <div class="metric-value">{savings_rate:.1f}%</div>
                <div class="small-note">Based on recorded income</div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        left, right = st.columns([1.2, 1])

        with left:
            st.subheader("Spending by category")
            expense_df = df[df["transaction_type"] == "Expense"].copy() if not df.empty else pd.DataFrame()

            if expense_df.empty:
                st.info("Add expenses to see your category chart.")
            else:
                category_data = (
                    expense_df.groupby("category", as_index=False)["amount"]
                    .sum()
                    .sort_values("amount", ascending=False)
                )
                fig = px.pie(
                    category_data,
                    values="amount",
                    names="category",
                    hole=0.55
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    font_color="white",
                    margin=dict(t=20, b=20, l=20, r=20)
                )
                st.plotly_chart(fig, use_container_width=True)

        with right:
            st.subheader("Smart money check")

            if income_total == 0 and expense_total == 0:
                st.info("Start by adding an income or expense.")
            elif balance < 0:
                st.error("Your expenses are higher than your income. Try reducing non-essential categories.")
            elif savings_rate < 10:
                st.warning("You are saving less than 10% of income. Try setting a small weekly saving target.")
            elif savings_rate < 25:
                st.info("Good progress. Aim for a 25% savings rate if possible.")
            else:
                st.success("Excellent. Your savings rate is strong.")

            st.markdown("#### Quick actions")
            if st.button("➕ Add expense", use_container_width=True):
                st.session_state["quick_page"] = "Add transaction"
                st.info("Open **Add transaction** from the sidebar.")

            if not goals_df.empty:
                st.markdown("#### Your goals")
                for _, goal in goals_df.head(3).iterrows():
                    progress = min(float(goal["saved_amount"]) / float(goal["target_amount"]), 1.0)
                    st.write(f"**{goal['goal_name']}** — {progress * 100:.0f}%")
                    st.progress(progress)

        st.subheader("Recent activity")
        if df.empty:
            st.info("No transactions yet.")
        else:
            recent = df[[
                "transaction_date",
                "title",
                "category",
                "transaction_type",
                "amount"
            ]].head(8).copy()

            recent["amount"] = recent["amount"].apply(format_money)
            st.dataframe(recent, use_container_width=True, hide_index=True)

    elif page == "Add Transaction":
        st.markdown("""
        <div class="hero">
            <h1>Add a transaction</h1>
            <p>Record income or spending in a few seconds.</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("transaction_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                transaction_type = st.selectbox("Type", ["Expense", "Income"])
                title = st.text_input("Title", placeholder="Example: Groceries")
                amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0)

            with col2:
                category = st.selectbox(
                    "Category",
                    [
                        "Food", "Transport", "Shopping", "Bills",
                        "Entertainment", "Health", "Education",
                        "Salary", "Freelance", "Savings", "Other"
                    ]
                )
                transaction_date = st.date_input("Date", value=date.today())
                notes = st.text_area("Notes (optional)", placeholder="Any extra details")

            submitted = st.form_submit_button("Save transaction", use_container_width=True)

        if submitted:
            if not title.strip() or amount <= 0:
                st.warning("Enter a title and an amount greater than zero.")
            else:
                try:
                    supabase.table("transactions").insert({
                        "user_id": user.id,
                        "title": title.strip(),
                        "amount": float(amount),
                        "transaction_type": transaction_type,
                        "category": category,
                        "transaction_date": str(transaction_date),
                        "notes": notes.strip()
                    }).execute()
                    st.success("Transaction saved to your cloud account.")
                    st.rerun()
                except Exception as error:
                    st.error(f"Could not save transaction: {error}")

    elif page == "Transactions":
        st.markdown("""
        <div class="hero">
            <h1>Your transactions</h1>
            <p>Search, review, and manage your financial history.</p>
        </div>
        """, unsafe_allow_html=True)

        if df.empty:
            st.info("No transactions yet. Add your first one.")
        else:
            filter_col1, filter_col2, filter_col3 = st.columns(3)

            with filter_col1:
                type_filter = st.selectbox("Filter by type", ["All", "Expense", "Income"])

            with filter_col2:
                category_options = ["All"] + sorted(df["category"].dropna().unique().tolist())
                category_filter = st.selectbox("Filter by category", category_options)

            with filter_col3:
                search_text = st.text_input("Search title")

            filtered = df.copy()

            if type_filter != "All":
                filtered = filtered[filtered["transaction_type"] == type_filter]

            if category_filter != "All":
                filtered = filtered[filtered["category"] == category_filter]

            if search_text:
                filtered = filtered[
                    filtered["title"].str.contains(search_text, case=False, na=False)
                ]

            display_df = filtered[[
                "id", "transaction_date", "title", "category",
                "transaction_type", "amount", "notes"
            ]].copy()
            display_df["amount"] = display_df["amount"].apply(format_money)

            st.dataframe(display_df, use_container_width=True, hide_index=True)

            st.divider()
            st.subheader("Delete a transaction")

            transaction_options = {
                f"{row['title']} — {format_money(row['amount'])} ({row['transaction_date']})": row["id"]
                for _, row in filtered.iterrows()
            }

            if transaction_options:
                selected_transaction = st.selectbox(
                    "Choose a transaction to delete",
                    list(transaction_options.keys())
                )

                if st.button("Delete selected transaction"):
                    try:
                        supabase.table("transactions").delete().eq(
                            "id",
                            transaction_options[selected_transaction]
                        ).execute()
                        st.success("Transaction deleted.")
                        st.rerun()
                    except Exception as error:
                        st.error(f"Could not delete transaction: {error}")

    elif page == "Goals":
        st.markdown("""
        <div class="hero">
            <h1>Savings goals</h1>
            <p>Turn your plans into visible progress.</p>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("➕ Create a new goal", expanded=True):
            with st.form("goal_form", clear_on_submit=True):
                goal_name = st.text_input("Goal name", placeholder="Example: New laptop")
                target_amount = st.number_input("Target amount (₹)", min_value=1.0, step=100.0)
                saved_amount = st.number_input("Already saved (₹)", min_value=0.0, step=100.0)
                target_date = st.date_input("Target date", value=date.today())

                create_goal = st.form_submit_button("Create goal", use_container_width=True)

            if create_goal:
                if not goal_name.strip():
                    st.warning("Enter a goal name.")
                else:
                    try:
                        supabase.table("goals").insert({
                            "user_id": user.id,
                            "goal_name": goal_name.strip(),
                            "target_amount": float(target_amount),
                            "saved_amount": float(saved_amount),
                            "target_date": str(target_date)
                        }).execute()
                        st.success("Goal created.")
                        st.rerun()
                    except Exception as error:
                        st.error(f"Could not create goal: {error}")

        st.subheader("Your goal progress")

        if goals_df.empty:
            st.info("Create a goal to start tracking progress.")
        else:
            for _, goal in goals_df.iterrows():
                progress = min(float(goal["saved_amount"]) / float(goal["target_amount"]), 1.0)

                with st.container(border=True):
                    st.markdown(f"### {goal['goal_name']}")
                    st.write(
                        f"{format_money(goal['saved_amount'])} saved out of "
                        f"{format_money(goal['target_amount'])}"
                    )
                    st.progress(progress)
                    st.caption(
                        f"{progress * 100:.1f}% complete • "
                        f"Target: {goal['target_date']}"
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        add_to_goal = st.number_input(
                            f"Add savings to {goal['goal_name']}",
                            min_value=0.0,
                            step=100.0,
                            key=f"add_{goal['id']}"
                        )

                    with col2:
                        st.write("")
                        st.write("")
                        if st.button("Update goal", key=f"update_{goal['id']}"):
                            try:
                                new_saved = float(goal["saved_amount"]) + float(add_to_goal)
                                supabase.table("goals").update({
                                    "saved_amount": new_saved
                                }).eq("id", goal["id"]).execute()
                                st.success("Goal updated.")
                                st.rerun()
                            except Exception as error:
                                st.error(f"Could not update goal: {error}")

                    if st.button("Delete goal", key=f"delete_goal_{goal['id']}"):
                        try:
                            supabase.table("goals").delete().eq("id", goal["id"]).execute()
                            st.success("Goal deleted.")
                            st.rerun()
                        except Exception as error:
                            st.error(f"Could not delete goal: {error}")

    elif page == "Analytics":
        st.markdown("""
        <div class="hero">
            <h1>Money insights</h1>
            <p>Simple AI-style guidance based on your real spending.</p>
        </div>
        """, unsafe_allow_html=True)

        if df.empty:
            st.info("Add transactions first to unlock insights.")
        else:
            expense_df = df[df["transaction_type"] == "Expense"].copy()

            if expense_df.empty:
                st.info("Add expense records to see spending insights.")
            else:
                category_summary = (
                    expense_df.groupby("category", as_index=False)["amount"]
                    .sum()
                    .sort_values("amount", ascending=False)
                )

                top_category = category_summary.iloc[0]
                top_percentage = (top_category["amount"] / expense_total * 100) if expense_total else 0

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Highest spending category",
                        top_category["category"],
                        format_money(top_category["amount"])
                    )

                with col2:
                    st.metric(
                        "Largest category share",
                        f"{top_percentage:.1f}%",
                        "of total expenses"
                    )

                fig = px.bar(
                    category_summary,
                    x="category",
                    y="amount",
                    text_auto=".2s"
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="white",
                    margin=dict(t=30, b=20, l=20, r=20)
                )
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("Personalized suggestions")

                if top_percentage > 40:
                    st.warning(
                        f"**{top_category['category']}** is {top_percentage:.0f}% "
                        "of your expenses. Set a monthly limit for this category."
                    )
                else:
                    st.success(
                        "Your spending is reasonably spread across categories."
                    )

                if balance > 0:
                    suggested_saving = balance * 0.20
                    st.info(
                        f"Try moving **{format_money(suggested_saving)}** "
                        "toward a savings goal this month."
                    )
                else:
                    st.error(
                        "Your current recorded expenses are greater than income. "
                        "Focus on tracking essential versus optional spending."
                    )

                st.markdown("""
                ### Smart habit ideas
                - Review your top spending category once every week.
                - Record transactions on the same day you spend.
                - Create one small savings goal before creating a large one.
                - Keep a small emergency amount separate from daily spending.
                """)
    elif page == "AI Advisor":
         st.markdown("## 🤖 AI Advisor")
         st.info("AI Advisor coming soon!")

    elif page == "Settings":
         st.markdown("## ⚙️ Settings")
         st.write(f"Logged in as: {user.email}")

         st.markdown("---")
         st.markdown("""
### 👨‍💻 Developer

Made by **Rishi**

GitHub: https://github.com/rishizz709
""")

# ---------------------------------------------------
# RUN APP
# ---------------------------------------------------
user = current_user()

if user is None:
    login_screen()
else:
    main_app(user)