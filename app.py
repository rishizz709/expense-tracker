import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date

st.title("💰 Expense Tracker")

# Create an empty list when the app starts
if "expenses" not in st.session_state:
    st.session_state.expenses = []

# ---------------- ADD EXPENSE ----------------
st.subheader("Add an expense")

name = st.text_input("Expense name")

category = st.selectbox(
    "Category",
    ["Food", "Travel", "Shopping", "Bills", "Entertainment", "Other"]
)

expense_date = st.date_input("Expense date", value=date.today())

amount = st.number_input("Amount (₹)", min_value=0.0, step=1.0)

if st.button("Add Expense"):
    if name != "" and amount > 0:
        st.session_state.expenses.append(
            {
                "name": name,
                "category": category,
                "date": expense_date,
                "amount": amount
            }
        )
        st.success("Expense added successfully!")
    else:
        st.warning("Enter an expense name and amount.")

# ---------------- VIEW EXPENSES ----------------
st.subheader("Your expenses")

if len(st.session_state.expenses) == 0:
    st.info("No expenses added yet.")

else:
    df = pd.DataFrame(st.session_state.expenses)

    # Show expense table
    st.dataframe(df, use_container_width=True)

    # Total expense
    total = df["amount"].sum()
    st.subheader(f"Total expense: ₹{total:.2f}")

    # Download CSV button
    st.download_button(
        label="Download expenses as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="my_expenses.csv",
        mime="text/csv"
    )

    # ---------------- DELETE ONE EXPENSE ----------------
    st.subheader("Delete an expense")

    expense_options = [
        f"{i + 1}. {expense['name']} | {expense['category']} | ₹{expense['amount']:.2f}"
        for i, expense in enumerate(st.session_state.expenses)
    ]

    selected_expense = st.selectbox(
        "Select an expense to delete",
        expense_options
    )

    if st.button("Delete selected expense"):
        selected_index = expense_options.index(selected_expense)
        deleted_item = st.session_state.expenses.pop(selected_index)
        st.success(f"Deleted: {deleted_item['name']}")
        st.rerun()

    # ---------------- PIE CHART ----------------
    st.subheader("Expenses by category")

    category_total = df.groupby("category")["amount"].sum()

    fig, ax = plt.subplots()

    ax.pie(
        category_total,
        labels=category_total.index,
        autopct="%1.1f%%",
        startangle=90
    )

    ax.axis("equal")
    st.pyplot(fig)

    # ---------------- CLEAR ALL ----------------
    if st.button("Clear all expenses"):
        st.session_state.expenses = []
        st.rerun()
