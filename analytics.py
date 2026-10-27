import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ==========================================
# SUMMARY STATISTICS
# ==========================================

def calculate_summary(df):
    """Calculate important expense statistics."""

    if df.empty:

        return {
            "total": 0.0,
            "average": 0.0,
            "highest": 0.0,
            "count": 0,
            "daily_average": 0.0
        }

    amounts = df["Amount"].to_numpy(
        dtype=float
    )

    total = float(np.sum(amounts))

    average = float(np.mean(amounts))

    highest = float(np.max(amounts))

    count = len(amounts)

    dates = pd.to_datetime(df["Date"])

    number_of_days = max(
        (dates.max() - dates.min()).days + 1,
        1
    )

    daily_average = total / number_of_days

    return {
        "total": total,
        "average": average,
        "highest": highest,
        "count": count,
        "daily_average": daily_average
    }


# ==========================================
# CATEGORY ANALYSIS
# ==========================================

def category_summary(df):
    """Calculate total spending per category."""

    if df.empty:

        return pd.DataFrame(
            columns=["Category", "Amount"]
        )

    result = (
        df.groupby("Category", as_index=False)["Amount"]
        .sum()
        .sort_values(
            "Amount",
            ascending=False
        )
    )

    return result


# ==========================================
# MONTHLY ANALYSIS
# ==========================================

def monthly_summary(df):
    """Calculate total spending for each month."""

    if df.empty:

        return pd.DataFrame(
            columns=["Month", "Amount"]
        )

    working_df = df.copy()

    working_df["Month"] = (
        pd.to_datetime(working_df["Date"])
        .dt.to_period("M")
        .astype(str)
    )

    result = (
        working_df.groupby(
            "Month",
            as_index=False
        )["Amount"]
        .sum()
        .sort_values("Month")
    )

    return result


# ==========================================
# PIE CHART
# ==========================================

def category_chart(df):
    """Generate a category-wise pie chart."""

    summary = category_summary(df)

    fig, ax = plt.subplots(
        figsize=(7, 5)
    )

    if summary.empty:

        ax.text(
            0.5,
            0.5,
            "No expense data available",
            ha="center",
            va="center"
        )

        ax.axis("off")

    else:

        ax.pie(
            summary["Amount"],
            labels=summary["Category"],
            autopct="%1.1f%%",
            startangle=90
        )

        ax.set_title(
            "Spending by Category"
        )

    fig.tight_layout()

    return fig


# ==========================================
# MONTHLY BAR CHART
# ==========================================

def monthly_chart(df):
    """Generate a monthly spending chart."""

    summary = monthly_summary(df)

    fig, ax = plt.subplots(
        figsize=(8, 4)
    )

    if summary.empty:

        ax.text(
            0.5,
            0.5,
            "No expense data available",
            ha="center",
            va="center"
        )

        ax.axis("off")

    else:

        ax.bar(
            summary["Month"],
            summary["Amount"]
        )

        ax.set_title(
            "Monthly Spending"
        )

        ax.set_xlabel(
            "Month"
        )

        ax.set_ylabel(
            "Amount (₹)"
        )

        plt.setp(
            ax.get_xticklabels(),
            rotation=45,
            ha="right"
        )

    fig.tight_layout()

    return fig