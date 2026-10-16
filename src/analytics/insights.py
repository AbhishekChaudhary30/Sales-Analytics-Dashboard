"""Automated rule-based heuristic insights engine."""

import pandas as pd

from src.utils.formatting import format_currency, format_percentage


def generate_foundational_insights(df: pd.DataFrame) -> list[dict[str, str]]:
    """Generate meaningful business insights from mapped sales data.

    Returns a list of structured insight cards with status icons and explanations.
    """
    insights: list[dict[str, str]] = []

    if df.empty:
        return insights

    # 1. Total Revenue & Transactions
    if "sales" in df.columns:
        sales_sum = pd.to_numeric(df["sales"], errors="coerce").sum()
        total_rows = len(df)
        insights.append({
            "type": "summary",
            "icon": "💰",
            "title": "Revenue Overview",
            "description": f"Generated total revenue of {format_currency(sales_sum)} across {total_rows:,} transactions.",
            "status": "info",
        })

    # 2. Profitability check
    if "profit" in df.columns and "sales" in df.columns:
        profit_sum = pd.to_numeric(df["profit"], errors="coerce").sum()
        sales_sum = pd.to_numeric(df["sales"], errors="coerce").sum()
        if sales_sum > 0:
            margin = (profit_sum / sales_sum) * 100.0
            if margin > 15:
                insights.append({
                    "type": "profit",
                    "icon": "📈",
                    "title": "Healthy Profit Margin",
                    "description": f"Overall profit margin is robust at {format_percentage(margin)} ({format_currency(profit_sum)} total profit).",
                    "status": "success",
                })
            elif margin >= 0:
                insights.append({
                    "type": "profit",
                    "icon": "⚖️",
                    "title": "Moderate Profit Margin",
                    "description": f"Overall profit margin is currently {format_percentage(margin)}. Consider optimizing cost structures.",
                    "status": "warning",
                })
            else:
                insights.append({
                    "type": "profit",
                    "icon": "🚨",
                    "title": "Negative Profitability Alert",
                    "description": f"The business operates at a net loss of {format_currency(profit_sum)} ({format_percentage(margin)} margin). Urgent margin review advised.",
                    "status": "danger",
                })

    # 3. Top Category Contribution
    if "category" in df.columns and "sales" in df.columns:
        cat_sales = df.groupby("category")["sales"].sum().sort_values(ascending=False)
        if not cat_sales.empty:
            top_cat = cat_sales.index[0]
            top_cat_rev = cat_sales.iloc[0]
            total_rev = cat_sales.sum()
            share = (top_cat_rev / total_rev * 100.0) if total_rev > 0 else 0
            insights.append({
                "type": "category",
                "icon": "🏆",
                "title": f"Leading Category: {top_cat}",
                "description": f"'{top_cat}' accounts for {format_percentage(share)} of total sales revenue ({format_currency(top_cat_rev)}).",
                "status": "info",
            })

    # 4. Regional Market Concentration
    if "region" in df.columns and "sales" in df.columns:
        reg_sales = df.groupby("region")["sales"].sum().sort_values(ascending=False)
        if not reg_sales.empty:
            top_reg = reg_sales.index[0]
            reg_rev = reg_sales.iloc[0]
            insights.append({
                "type": "geography",
                "icon": "🗺️",
                "title": f"Top Regional Market: {top_reg}",
                "description": f"The {top_reg} region leads commercial performance with {format_currency(reg_rev)} in gross sales.",
                "status": "info",
            })

    # 5. Discount Impact Warning
    if "discount" in df.columns:
        mean_disc = pd.to_numeric(df["discount"], errors="coerce").mean()
        if pd.notna(mean_disc):
            if 0.0 < mean_disc <= 1.0:
                mean_disc *= 100.0
            if mean_disc >= 20.0:
                insights.append({
                    "type": "discount",
                    "icon": "⚠️",
                    "title": "High Average Discount Rate",
                    "description": f"Average discount is elevated at {format_percentage(mean_disc)}. Monitor for margin erosion.",
                    "status": "warning",
                })

    return insights
