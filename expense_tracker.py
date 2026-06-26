expenses = []

while True:
    print("\n--- EXPENSE TRACKER ---")
    print("1. Add expense")
    print("2. View expenses")
    print("3. Show total")
    print("4. Exit")

    choice = input("Enter your choice (1-4): ")

    if choice == "1":
        name = input("Enter expense name: ")

        try:
            amount = float(input("Enter amount: "))
            expenses.append([name, amount])
            print("Expense added successfully!")
        except ValueError:
            print("Please enter a valid number for the amount.")

    elif choice == "2":
        if len(expenses) == 0:
            print("No expenses added yet.")
        else:
            print("\n--- YOUR EXPENSES ---")
            for i in range(len(expenses)):
                print(f"{i + 1}. {expenses[i][0]} - ₹{expenses[i][1]:.2f}")

    elif choice == "3":
        total = 0

        for expense in expenses:
            total = total + expense[1]

        print(f"\nTotal expense = ₹{total:.2f}")

    elif choice == "4":
        print("Thank you for using Expense Tracker!")
        break

    else:
        print("Invalid choice. Please enter a number from 1 to 4.")