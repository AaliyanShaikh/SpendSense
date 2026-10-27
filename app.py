import json
from pathlib import Path
from datetime import date

import pandas as pd
import streamlit as st

from expense_manager import (
    load_expenses,
    add_expense,
    delete_expense,
    update_expense,
    CATEGORIES,
    PAYMENT_METHODS
)

from analytics import (
    calculate_summary,
    category_summary,
    category_chart,
    monthly_chart
)


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="SpendSense",
    page_icon="💰",
    layout="wide"
)


# ==========================================
# FILE CONFIGURATION
# ==========================================

DATA_FOLDER = Path("data")

BUDGET_FILE = DATA_FOLDER / "budget.json"


# ==========================================
# CUSTOM STYLING
# ==========================================

st.markdown(
    """
    <style>
    .main {
        background-color: #f8fafc;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    h1 {
        color: #0f172a;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def format_currency(amount):
    """Format an amount in Indian rupees."""

    return f"₹{amount:,.2f}"


def load_budget():
    """Load the saved monthly budget."""

    DATA_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    if not BUDGET_FILE.exists():
        return 5000.0

    try:
        with open(
            BUDGET_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        budget = float(
            data.get("monthly_budget", 5000)
        )

        if not pd.notna(budget) or budget <= 0:
            return 5000.0

        return budget

    except (
        OSError,
        ValueError,
        TypeError,
        json.JSONDecodeError
    ):

        return 5000.0


def save_budget(budget):
    """Save the monthly budget to a JSON file."""

    if not pd.notna(budget) or budget <= 0:
        raise ValueError(
            "Budget must be greater than zero."
        )

    DATA_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    try:
        with open(
            BUDGET_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                {
                    "monthly_budget": float(budget)
                },
                file,
                indent=4
            )

    except OSError as error:

        raise RuntimeError(
            f"Unable to save budget: {error}"
        ) from error


def get_monthly_expenses(df):
    """Return expenses recorded during the current month."""

    if df.empty:
        return df.copy()

    today = date.today()

    dates = pd.to_datetime(df["Date"])

    mask = (
        (dates.dt.year == today.year)
        & (dates.dt.month == today.month)
    )

    return df.loc[mask].copy()


def load_sample_data():
    """Add demonstration expenses if the file is empty."""

    df = load_expenses()

    if not df.empty:
        return False

    today = date.today()

    sample_expenses = [
        (
            "Lunch",
            "Food",
            150,
            "UPI"
        ),
        (
            "Bus Ticket",
            "Transport",
            40,
            "Cash"
        ),
        (
            "Notebook",
            "Education",
            100,
            "UPI"
        ),
        (
            "Movie Ticket",
            "Entertainment",
            250,
            "Debit Card"
        ),
        (
            "Groceries",
            "Food",
            450,
            "UPI"
        )
    ]

    for name, category, amount, payment in sample_expenses:

        add_expense(
            today,
            name,
            category,
            amount,
            payment,
            "Sample demonstration expense"
        )

    return True


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("💰 SpendSense")

st.sidebar.caption(
    "Personal Expense Analytics"
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Add Expense",
        "View Expenses",
        "Analytics",
        "Budget Manager"
    ]
)

st.sidebar.divider()

st.sidebar.write(
    "Track expenses. Understand habits. Manage money."
)

st.sidebar.caption(
    "Built using Python and Streamlit."
)


# ==========================================
# LOAD APPLICATION DATA
# ==========================================

try:

    expenses = load_expenses()

except RuntimeError as error:

    st.error(str(error))
    st.stop()


if "monthly_budget" not in st.session_state:

    st.session_state.monthly_budget = load_budget()


# ==========================================
# DASHBOARD
# ==========================================

if page == "Dashboard":

    st.title("💰 SpendSense")

    st.subheader(
        "Smart Expense Analyzer"
    )

    st.write(
        "Understand your spending patterns and "
        "take control of your monthly budget."
    )

    st.divider()

    monthly_expenses = get_monthly_expenses(
        expenses
    )

    summary = calculate_summary(
        monthly_expenses
    )

    budget = st.session_state.monthly_budget

    remaining = budget - summary["total"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Monthly Spending",
        format_currency(summary["total"])
    )

    col2.metric(
        "Monthly Budget",
        format_currency(budget)
    )

    col3.metric(
        "Budget Remaining",
        format_currency(remaining)
    )

    col4.metric(
        "Transactions",
        summary["count"]
    )

    st.divider()

    st.subheader(
        "Monthly Budget Progress"
    )

    budget_used = summary["total"] / budget

    st.progress(
        min(max(budget_used, 0.0), 1.0)
    )

    st.write(
        f"Budget utilized: {budget_used * 100:.1f}%"
    )

    if budget_used >= 1:

        st.error(
            "⚠️ You have exceeded your monthly budget!"
        )

    elif budget_used >= 0.8:

        st.warning(
            "⚠️ You have used at least 80% of your budget."
        )

    else:

        st.success(
            "You are within your monthly budget."
        )

    left, right = st.columns(2)

    with left:

        st.subheader(
            "Category-wise Spending"
        )

        st.pyplot(
            category_chart(monthly_expenses),
            clear_figure=True
        )

    with right:

        st.subheader(
            "Monthly Spending Trend"
        )

        st.pyplot(
            monthly_chart(expenses),
            clear_figure=True
        )

    st.divider()

    st.subheader(
        "Recent Transactions"
    )

    if expenses.empty:

        st.info(
            "No expenses recorded yet."
        )

        if st.button(
            "Load Sample Data"
        ):

            try:

                added = load_sample_data()

                if added:

                    st.success(
                        "Sample expenses added successfully."
                    )

                else:

                    st.info(
                        "Your expense file already contains records."
                    )

                st.rerun()

            except (RuntimeError, ValueError) as error:

                st.error(str(error))

    else:

        recent = expenses.sort_values(
            "Date",
            ascending=False
        ).head(5)

        st.dataframe(
            recent,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download All Expenses",
            data=expenses.to_csv(
                index=False
            ).encode("utf-8"),
            file_name="spendsense_expenses.csv",
            mime="text/csv"
        )


# ==========================================
# ADD EXPENSE
# ==========================================

elif page == "Add Expense":

    st.title("➕ Add Expense")

    st.write(
        "Record a new transaction."
    )

    with st.form("add_expense_form"):

        expense_date = st.date_input(
            "Expense Date",
            value=date.today(),
            max_value=date.today()
        )

        expense_name = st.text_input(
            "Expense Name",
            placeholder="e.g. Lunch, Travel, Books"
        )

        amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            value=100.0,
            step=10.0
        )

        category = st.selectbox(
            "Category",
            CATEGORIES
        )

        payment_method = st.selectbox(
            "Payment Method",
            PAYMENT_METHODS
        )

        notes = st.text_area(
            "Notes",
            placeholder="Optional description"
        )

        submitted = st.form_submit_button(
            "Save Expense",
            use_container_width=True
        )

    if submitted:

        try:

            add_expense(
                expense_date,
                expense_name,
                category,
                amount,
                payment_method,
                notes
            )

            st.success(
                "Expense saved successfully!"
            )

            st.rerun()

        except (ValueError, RuntimeError) as error:

            st.error(str(error))


# ==========================================
# VIEW, FILTER, EDIT AND DELETE EXPENSES
# ==========================================

elif page == "View Expenses":

    st.title("📋 Manage Expenses")

    if expenses.empty:

        st.info(
            "No expense records found. Add an expense first."
        )

    else:

        st.subheader(
            "Filter Expenses"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            selected_category = st.selectbox(
                "Category",
                ["All"] + CATEGORIES
            )

        with col2:

            minimum_amount = st.number_input(
                "Minimum Amount",
                min_value=0.0,
                value=0.0
            )

        with col3:

            maximum_amount = st.number_input(
                "Maximum Amount",
                min_value=0.0,
                value=float(
                    max(
                        expenses["Amount"].max(),
                        100.0
                    )
                )
            )

        filtered = expenses.copy()

        if selected_category != "All":

            filtered = filtered[
                filtered["Category"] == selected_category
            ]

        filtered = filtered[
            (filtered["Amount"] >= minimum_amount)
            & (filtered["Amount"] <= maximum_amount)
        ]

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )

        st.write(
            f"Records displayed: {len(filtered)}"
        )

        st.download_button(
            "Download Filtered Expenses",
            data=filtered.to_csv(
                index=False
            ).encode("utf-8"),
            file_name="filtered_expenses.csv",
            mime="text/csv"
        )

        st.divider()

        available_ids = filtered["ID"].tolist()

        if available_ids:

            selected_id = st.selectbox(
                "Select Expense ID",
                available_ids
            )

            selected_row = filtered[
                filtered["ID"] == selected_id
            ].iloc[0]

            tab1, tab2 = st.tabs(
                ["Edit Expense", "Delete Expense"]
            )

            with tab1:

                with st.form("edit_expense_form"):

                    old_date = selected_row["Date"]

                    edit_date = st.date_input(
                        "Expense Date",
                        value=old_date,
                        max_value=date.today()
                    )

                    edit_name = st.text_input(
                        "Expense Name",
                        value=str(selected_row["Expense"])
                    )

                    edit_amount = st.number_input(
                        "Amount (₹)",
                        min_value=0.0,
                        value=float(selected_row["Amount"]),
                        step=10.0
                    )

                    edit_category = st.selectbox(
                        "Category",
                        CATEGORIES,
                        index=CATEGORIES.index(
                            selected_row["Category"]
                        )
                    )

                    edit_payment = st.selectbox(
                        "Payment Method",
                        PAYMENT_METHODS,
                        index=PAYMENT_METHODS.index(
                            selected_row["Payment Method"]
                        )
                    )

                    edit_notes = st.text_area(
                        "Notes",
                        value=str(
                            selected_row["Notes"]
                            if pd.notna(selected_row["Notes"])
                            else ""
                        )
                    )

                    update_button = st.form_submit_button(
                        "Update Expense"
                    )

                if update_button:

                    try:

                        update_expense(
                            selected_id,
                            edit_date,
                            edit_name,
                            edit_category,
                            edit_amount,
                            edit_payment,
                            edit_notes
                        )

                        st.success(
                            "Expense updated successfully!"
                        )

                        st.rerun()

                    except (ValueError, RuntimeError) as error:

                        st.error(str(error))

            with tab2:

                st.warning(
                    "Deleting an expense permanently removes it "
                    "from the CSV file."
                )

                confirm_delete = st.checkbox(
                    f"Confirm deletion of expense ID {selected_id}"
                )

                if st.button(
                    "Delete Expense",
                    disabled=not confirm_delete
                ):

                    try:

                        delete_expense(
                            selected_id
                        )

                        st.success(
                            "Expense deleted successfully!"
                        )

                        st.rerun()

                    except (ValueError, RuntimeError) as error:

                        st.error(str(error))


# ==========================================
# ANALYTICS
# ==========================================

elif page == "Analytics":

    st.title("📊 Expense Analytics")

    if expenses.empty:

        st.info(
            "Add expenses to view analytics."
        )

    else:

        minimum_date = min(
            expenses["Date"]
        )

        maximum_date = max(
            expenses["Date"]
        )

        col1, col2 = st.columns(2)

        with col1:

            start_date = st.date_input(
                "Start Date",
                value=minimum_date,
                min_value=minimum_date,
                max_value=maximum_date
            )

        with col2:

            end_date = st.date_input(
                "End Date",
                value=maximum_date,
                min_value=minimum_date,
                max_value=maximum_date
            )

        if start_date > end_date:

            st.error(
                "Start date cannot be after end date."
            )

        else:

            dates = pd.to_datetime(
                expenses["Date"]
            )

            mask = (
                (dates.dt.date >= start_date)
                & (dates.dt.date <= end_date)
            )

            filtered = expenses.loc[
                mask
            ].copy()

            summary = calculate_summary(
                filtered
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Total Spending",
                format_currency(summary["total"])
            )

            col2.metric(
                "Average Expense",
                format_currency(summary["average"])
            )

            col3.metric(
                "Highest Expense",
                format_currency(summary["highest"])
            )

            st.divider()

            st.subheader(
                "Category Breakdown"
            )

            category_data = category_summary(
                filtered
            )

            if not category_data.empty:

                st.bar_chart(
                    category_data.set_index(
                        "Category"
                    )["Amount"]
                )

                st.dataframe(
                    category_data,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info(
                    "No expenses found in this date range."
                )

            st.subheader(
                "Spending Statistics"
            )

            st.write(
                f"Total transactions: {summary['count']}"
            )

            st.write(
                "Average daily spending: "
                f"{format_currency(summary['daily_average'])}"
            )


# ==========================================
# BUDGET MANAGER
# ==========================================

elif page == "Budget Manager":

    st.title("🎯 Budget Manager")

    st.write(
        "Set a monthly budget and monitor your spending."
    )

    with st.form("budget_form"):

        new_budget = st.number_input(
            "Monthly Budget (₹)",
            min_value=1.0,
            value=float(
                st.session_state.monthly_budget
            ),
            step=500.0
        )

        budget_submitted = st.form_submit_button(
            "Save Budget"
        )

    if budget_submitted:

        try:

            save_budget(
                new_budget
            )

            st.session_state.monthly_budget = new_budget

            st.success(
                "Budget saved successfully!"
            )

            st.rerun()

        except (ValueError, RuntimeError) as error:

            st.error(str(error))

    monthly_expenses = get_monthly_expenses(
        expenses
    )

    total_spent = calculate_summary(
        monthly_expenses
    )["total"]

    current_budget = st.session_state.monthly_budget

    remaining = current_budget - total_spent

    percentage = total_spent / current_budget

    st.divider()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Monthly Budget",
        format_currency(current_budget)
    )

    col2.metric(
        "Total Spent",
        format_currency(total_spent)
    )

    col3.metric(
        "Remaining Budget",
        format_currency(remaining)
    )

    st.subheader(
        "Budget Utilization"
    )

    st.progress(
        min(max(percentage, 0.0), 1.0)
    )

    st.write(
        f"You have used {percentage * 100:.1f}% of your budget."
    )

    if percentage >= 1:

        st.error(
            "You have exceeded your monthly budget."
        )

    elif percentage >= 0.8:

        st.warning(
            "You are approaching your monthly budget limit."
        )

    else:

        st.success(
            "Your spending is within the budget."
        )


# ==========================================
# FOOTER
# ==========================================

st.sidebar.divider()

st.sidebar.caption(
    "SpendSense | PPCA Mini Project"
)

st.sidebar.caption(
    "Python • Pandas • NumPy • Matplotlib • Streamlit"
)