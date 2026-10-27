import os
import pandas as pd
from datetime import date


# ==========================================
# CONFIGURATION
# ==========================================

DATA_FOLDER = "data"
FILE_PATH = os.path.join(DATA_FOLDER, "expenses.csv")

CATEGORIES = [
    "Food",
    "Transport",
    "Education",
    "Shopping",
    "Entertainment",
    "Bills",
    "Health",
    "Other"
]

PAYMENT_METHODS = [
    "Cash",
    "UPI",
    "Debit Card",
    "Credit Card",
    "Net Banking"
]

COLUMNS = [
    "ID",
    "Date",
    "Expense",
    "Category",
    "Amount",
    "Payment Method",
    "Notes"
]


# ==========================================
# OOP: EXPENSE CLASS
# ==========================================

class Expense:
    """Represent an individual expense."""

    def __init__(
        self,
        expense_id,
        expense_date,
        expense_name,
        category,
        amount,
        payment_method,
        notes=""
    ):
        self.expense_id = expense_id
        self.expense_date = expense_date
        self.expense_name = expense_name
        self.category = category
        self.amount = amount
        self.payment_method = payment_method
        self.notes = notes

    def to_dict(self):
        """Convert expense object into a dictionary."""

        return {
            "ID": self.expense_id,
            "Date": self.expense_date.isoformat(),
            "Expense": self.expense_name,
            "Category": self.category,
            "Amount": self.amount,
            "Payment Method": self.payment_method,
            "Notes": self.notes
        }


# ==========================================
# FILE INITIALIZATION
# ==========================================

def initialize_file():
    """Create the data directory and CSV file."""

    try:
        os.makedirs(DATA_FOLDER, exist_ok=True)

        if not os.path.exists(FILE_PATH):
            df = pd.DataFrame(columns=COLUMNS)
            df.to_csv(FILE_PATH, index=False)

    except OSError as error:
        raise RuntimeError(
            f"Unable to initialize storage: {error}"
        ) from error


# ==========================================
# LOAD EXPENSES
# ==========================================

def load_expenses():
    """Read expense records from the CSV file."""

    initialize_file()

    try:
        df = pd.read_csv(FILE_PATH)

        if list(df.columns) != COLUMNS:
            raise ValueError(
                "The CSV file does not have the expected columns."
            )

        if not df.empty:

            df["Date"] = pd.to_datetime(
                df["Date"],
                errors="raise"
            ).dt.date

            df["Amount"] = pd.to_numeric(
                df["Amount"],
                errors="raise"
            )

            df["ID"] = pd.to_numeric(
                df["ID"],
                errors="raise"
            )

            if (
                not df["Amount"].map(
                    lambda value: pd.notna(value)
                    and value > 0
                ).all()
            ):
                raise ValueError(
                    "Expense amounts must be positive numbers."
                )

            if df["ID"].duplicated().any():
                raise ValueError(
                    "Duplicate expense IDs were found."
                )

            if df["Expense"].isna().any():
                raise ValueError(
                    "An expense name is missing."
                )

        return df

    except (
        OSError,
        ValueError,
        pd.errors.ParserError
    ) as error:

        raise RuntimeError(
            f"Unable to load expenses: {error}"
        ) from error


# ==========================================
# VALIDATION
# ==========================================

def validate_expense(
    expense_date,
    expense_name,
    category,
    amount,
    payment_method
):
    """Validate expense information."""

    expense_name = expense_name.strip()

    if not expense_name:
        raise ValueError(
            "Expense name cannot be empty."
        )

    if not isinstance(expense_date, date):
        raise ValueError(
            "Please select a valid date."
        )

    if expense_date > date.today():
        raise ValueError(
            "Expense date cannot be in the future."
        )

    if category not in CATEGORIES:
        raise ValueError(
            "Please select a valid category."
        )

    if payment_method not in PAYMENT_METHODS:
        raise ValueError(
            "Please select a valid payment method."
        )

    try:
        amount = float(amount)

    except (ValueError, TypeError) as error:
        raise ValueError(
            "Amount must be a valid number."
        ) from error

    if not pd.notna(amount) or amount <= 0:
        raise ValueError(
            "Amount must be greater than zero."
        )

    return expense_name, amount


# ==========================================
# ADD EXPENSE
# ==========================================

def add_expense(
    expense_date,
    expense_name,
    category,
    amount,
    payment_method,
    notes=""
):
    """Add a new expense to the CSV file."""

    expense_name, amount = validate_expense(
        expense_date,
        expense_name,
        category,
        amount,
        payment_method
    )

    df = load_expenses()

    if df.empty:
        new_id = 1

    else:
        new_id = int(df["ID"].max()) + 1

    expense = Expense(
        new_id,
        expense_date,
        expense_name,
        category,
        amount,
        payment_method,
        notes.strip()
    )

    new_record = pd.DataFrame([
        expense.to_dict()
    ])

    updated_df = pd.concat(
        [df, new_record],
        ignore_index=True
    )

    try:
        updated_df.to_csv(
            FILE_PATH,
            index=False
        )

    except OSError as error:
        raise RuntimeError(
            f"Unable to save expense: {error}"
        ) from error


# ==========================================
# DELETE EXPENSE
# ==========================================

def delete_expense(expense_id):
    """Delete an expense using its ID."""

    df = load_expenses()

    if df.empty:
        raise ValueError(
            "There are no expenses to delete."
        )

    matching_rows = (
        df["ID"].astype(int) == int(expense_id)
    )

    if not matching_rows.any():
        raise ValueError(
            "Expense ID was not found."
        )

    updated_df = df.loc[
        ~matching_rows
    ].copy()

    try:
        updated_df.to_csv(
            FILE_PATH,
            index=False
        )

    except OSError as error:
        raise RuntimeError(
            f"Unable to delete expense: {error}"
        ) from error


# ==========================================
# EDIT EXPENSE
# ==========================================

def update_expense(
    expense_id,
    expense_date,
    expense_name,
    category,
    amount,
    payment_method,
    notes=""
):
    """Update an existing expense."""

    expense_name, amount = validate_expense(
        expense_date,
        expense_name,
        category,
        amount,
        payment_method
    )

    df = load_expenses()

    matching_rows = (
        df["ID"].astype(int) == int(expense_id)
    )

    if not matching_rows.any():
        raise ValueError(
            "Expense ID was not found."
        )

    index = df.index[matching_rows][0]

    updated_expense = Expense(
        int(expense_id),
        expense_date,
        expense_name,
        category,
        amount,
        payment_method,
        notes.strip()
    )

    for column, value in updated_expense.to_dict().items():
        df.at[index, column] = value

    try:
        df.to_csv(
            FILE_PATH,
            index=False
        )

    except OSError as error:
        raise RuntimeError(
            f"Unable to update expense: {error}"
        ) from error