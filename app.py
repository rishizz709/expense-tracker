import streamlit as st

st.title("💰 Expense Tracker")

if "expenses" not in st.session_state:
    st.session_state.expenses = []

st.subheader("Add an expense")

name = st.text_input("Expense name")
amount = st.number_input("Amount (₹)", min_value=0.0, step=1.0)

if st.button("Add Expense"):
    if name != "" and amount > 0:
        st.session_state.expenses.append(
            {"name": name, "amount": amount}
        )
        st.success("Expense added successfully!")
    else:
        st.warning("Enter an expense name and amount.")

st.subheader("Your expenses")

if len(st.session_state.expenses) == 0:
    st.info("No expenses added yet.")
else:
    total = 0

    for i, expense in enumerate(st.session_state.expenses):
        st.write(
            f"{i + 1}. {expense['name']} — ₹{expense['amount']:.2f}"
        )
        total = total + expense["amount"]

    st.subheader(f"Total expense: ₹{total:.2f}")

    if st.button("Clear all expenses"):
        st.session_state.expenses = []
        st.rerun()
