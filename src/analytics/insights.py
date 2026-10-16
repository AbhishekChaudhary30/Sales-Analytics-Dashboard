"""Deterministic, Evidence-Based Automated Business Insights Engine.

Generates quantified commercial observations, concentration signals, and risk warnings
derived directly from uploaded dataset calculations without external AI dependencies.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd

from src.analytics.customers import analyze_customer_concentration, analyze_repeat_customers
from src.analytics.products import calculate_pareto_analysis
from src.analytics.profitability import analyze_discount_tiers, analyze_loss_making_transactions
from src.analytics.statistics import detect_iqr_outliers
from src.utils.formatting import format_currency, format_percentage


@dataclass
class BusinessInsight:
    """Structured, evidence-backed analytical finding."""

    type: str  # 'revenue', 'profit', 'category', 'geography', 'customer', 'discount', 'outlier'
    icon: str
    title: str
    description: str
    observed_value: str
    status: str  # 'success', 'info', 'warning', 'danger'
    recommendation: Optional[str] = None


def generate_comprehensive_insights(
    df: pd.DataFrame,
    currency_label: str = "USD",
    use_indian_numbering: bool = False,
) -> List[BusinessInsight]:
    """Derive prioritized, factual business insights from the active analytical dataset.

    Prevents fabricated claims by verifying data thresholds before generating any insight.
    """
    insights: List[BusinessInsight] = []
    if df.empty:
        return insights

    # 1. Total Commercial Scale & Net Revenue
    if "sales" in df.columns:
        sales_clean = pd.to_numeric(df["sales"], errors="coerce").dropna()
        if not sales_clean.empty:
            net_rev = float(sales_clean.sum())
            gross_rev = float(sales_clean[sales_clean > 0].sum())
            return_rev = float(sales_clean[sales_clean < 0].sum())

            desc = (
                f"Achieved total net revenue of {format_currency(net_rev, currency_label, use_indian_numbering)} "
                f"(Gross: {format_currency(gross_rev, currency_label, use_indian_numbering)}) across {len(df):,} transactions."
            )
            if return_rev < 0:
                desc += f" (Includes {format_currency(abs(return_rev), currency_label, use_indian_numbering)} in product returns/adjustments)."

            insights.append(
                BusinessInsight(
                    type="revenue",
                    icon="💰",
                    title="Gross Sales Volume",
                    description=desc,
                    observed_value=format_currency(net_rev, currency_label, use_indian_numbering),
                    status="info",
                    recommendation="Monitor net-to-gross ratio to ensure revenue retention.",
                )
            )

    # 2. Profit Margin & Loss-Making Analysis
    if "profit" in df.columns and "sales" in df.columns:
        sales_clean = pd.to_numeric(df["sales"], errors="coerce").dropna()
        profit_clean = pd.to_numeric(df["profit"], errors="coerce").dropna()
        net_rev = float(sales_clean.sum())
        total_profit = float(profit_clean.sum())

        if net_rev > 0:
            margin_pct = (total_profit / net_rev) * 100.0
            if margin_pct >= 18.0:
                status = "success"
                title = "Strong Profit Margin"
                rec = "Continue prioritizing high-margin product categories to sustain strong profitability."
            elif margin_pct >= 5.0:
                status = "info"
                title = "Moderate Commercial Margin"
                rec = "Review product mix and fulfillment costs to elevate operating margins."
            elif margin_pct >= 0:
                status = "warning"
                title = "Thin Profit Margin Alert"
                rec = "Conduct margin review across low-margin items to guard against cost inflation."
            else:
                status = "danger"
                title = "Net Operational Loss Alert"
                rec = "Urgent commercial audit recommended: total transactions produce an overall net loss."

            insights.append(
                BusinessInsight(
                    type="profit",
                    icon="📈" if margin_pct >= 10 else "🚨",
                    title=title,
                    description=f"Overall business profit margin stands at {format_percentage(margin_pct)} ({format_currency(total_profit, currency_label, use_indian_numbering)} total net profit).",
                    observed_value=format_percentage(margin_pct),
                    status=status,
                    recommendation=rec,
                )
            )

        # Loss-making transactions check
        loss_analysis = analyze_loss_making_transactions(df)
        if loss_analysis and loss_analysis.total_loss_transactions > 0:
            insights.append(
                BusinessInsight(
                    type="profit",
                    icon="⚠️",
                    title="Unprofitable Transactions Detected",
                    description=f"{loss_analysis.total_loss_transactions:,} transactions ({format_percentage(loss_analysis.loss_transaction_rate_pct)}) recorded negative margins, creating {format_currency(loss_analysis.total_loss_amount, currency_label, use_indian_numbering)} in cumulative gross loss.",
                    observed_value=f"{loss_analysis.total_loss_transactions:,} orders",
                    status="warning",
                    recommendation="Examine heavily discounted or high-freight items that generate negative transaction-level margin.",
                )
            )

    # 3. Category Revenue Leader & Concentration
    if "category" in df.columns and "sales" in df.columns:
        valid_cat = df.dropna(subset=["category", "sales"]).copy()
        valid_cat["sales"] = pd.to_numeric(valid_cat["sales"], errors="coerce")
        cat_agg = valid_cat.groupby("category")["sales"].sum().sort_values(ascending=False)

        if not cat_agg.empty:
            top_cat = cat_agg.index[0]
            top_rev = cat_agg.iloc[0]
            tot_rev = cat_agg.sum()
            share = (top_rev / tot_rev * 100.0) if tot_rev > 0 else 0.0

            insights.append(
                BusinessInsight(
                    type="category",
                    icon="🏆",
                    title=f"Core Merchandise Category: {top_cat}",
                    description=f"The '{top_cat}' category generates {format_percentage(share)} of total sales revenue ({format_currency(top_rev, currency_label, use_indian_numbering)}).",
                    observed_value=f"{format_percentage(share)} share",
                    status="info",
                    recommendation="Ensure robust supplier relationships and inventory depth for top revenue drivers.",
                )
            )

    # 4. Regional Territory Concentration
    if "region" in df.columns and "sales" in df.columns:
        valid_reg = df.dropna(subset=["region", "sales"]).copy()
        valid_reg["sales"] = pd.to_numeric(valid_reg["sales"], errors="coerce")
        reg_agg = valid_reg.groupby("region")["sales"].sum().sort_values(ascending=False)

        if not reg_agg.empty:
            top_reg = reg_agg.index[0]
            top_reg_rev = reg_agg.iloc[0]
            tot_reg_rev = reg_agg.sum()
            share = (top_reg_rev / tot_reg_rev * 100.0) if tot_reg_rev > 0 else 0.0

            insights.append(
                BusinessInsight(
                    type="geography",
                    icon="🗺️",
                    title=f"Leading Sales Territory: {top_reg}",
                    description=f"The '{top_reg}' region produces {format_percentage(share)} of geographic sales ({format_currency(top_reg_rev, currency_label, use_indian_numbering)}).",
                    observed_value=f"{format_percentage(share)} share",
                    status="info",
                    recommendation="Investigate territory-specific marketing tactics for replication across lower-performing markets.",
                )
            )

    # 5. Product Pareto (80/20) Concentration
    pareto_res = calculate_pareto_analysis(df)
    if pareto_res:
        insights.append(
            BusinessInsight(
                type="category",
                icon="📊",
                title="Pareto 80/20 Revenue Concentration",
                description=f"Just {pareto_res.core_product_count} of {pareto_res.total_product_count} products ({format_percentage(pareto_res.core_product_percentage)}) generate 80% of total commercial revenue.",
                observed_value=f"{pareto_res.core_product_count} products ({format_percentage(pareto_res.core_product_percentage)})",
                status="info",
                recommendation="Protect supply chain availability and service levels for the critical 20% core catalog.",
            )
        )

    # 6. Customer Concentration Risk
    cust_conc = analyze_customer_concentration(df)
    if cust_conc and cust_conc.total_customers >= 5:
        status_c = "warning" if cust_conc.top5_share_pct > 35.0 else "info"
        insights.append(
            BusinessInsight(
                type="customer",
                icon="👥",
                title=f"Customer Revenue Concentration ({cust_conc.concentration_level})",
                description=f"The top 5 client accounts generate {format_percentage(cust_conc.top5_share_pct)} of overall sales revenue ({format_currency(cust_conc.top5_revenue, currency_label, use_indian_numbering)}).",
                observed_value=f"{format_percentage(cust_conc.top5_share_pct)} top 5 share",
                status=status_c,
                recommendation="Diversify customer acquisition pipeline if top-tier concentration exceeds 40%." if cust_conc.top5_share_pct > 35 else "Client revenue distribution shows healthy portfolio balance.",
            )
        )

    # 7. Repeat Customer Dynamics
    repeat_res = analyze_repeat_customers(df)
    if repeat_res and repeat_res.total_customers > 5:
        insights.append(
            BusinessInsight(
                type="customer",
                icon="🔄",
                title="Customer Retention & Repeat Orders",
                description=f"{repeat_res.repeat_customers:,} of {repeat_res.total_customers:,} customers ({format_percentage(repeat_res.repeat_rate_pct)}) have made 2 or more orders, accounting for {format_percentage(repeat_res.repeat_revenue_share_pct)} of revenue.",
                observed_value=format_percentage(repeat_res.repeat_rate_pct),
                status="success" if repeat_res.repeat_rate_pct >= 25 else "info",
                recommendation="Develop post-purchase loyalty programs to convert single-time buyers into recurring accounts.",
            )
        )

    # 8. Discount Tier Sensitivity
    disc_summary = analyze_discount_tiers(df)
    if disc_summary and disc_summary.high_discount_margin_pct is not None and disc_summary.no_discount_margin_pct is not None:
        margin_gap = disc_summary.no_discount_margin_pct - disc_summary.high_discount_margin_pct
        if margin_gap > 10.0:
            insights.append(
                BusinessInsight(
                    type="discount",
                    icon="🏷️",
                    title="Discount-Driven Margin Compression",
                    description=f"High discount orders (>20%) produce an average margin of {format_percentage(disc_summary.high_discount_margin_pct)}, compared to {format_percentage(disc_summary.no_discount_margin_pct)} for undiscounted items.",
                    observed_value=f"{format_percentage(margin_gap)} margin compression",
                    status="warning",
                    recommendation="Audit promotional guidelines to prevent aggressive discounts from eroding gross profitability.",
                )
            )

    # 9. Statistical Outlier Alert (IQR)
    if "sales" in df.columns:
        outlier_res = detect_iqr_outliers(df, column_name="sales")
        if outlier_res and outlier_res.outlier_count > 0:
            insights.append(
                BusinessInsight(
                    type="outlier",
                    icon="🔍",
                    title="Statistical Transaction Outliers",
                    description=f"Detected {outlier_res.outlier_count:,} statistical outlier transactions (> {format_currency(outlier_res.upper_bound, currency_label, use_indian_numbering)}) using the IQR method.",
                    observed_value=f"{outlier_res.outlier_count:,} records ({format_percentage(outlier_res.outlier_percentage)})",
                    status="info",
                    recommendation="Review individual outlier transactions in the Data Explorer to confirm whether they represent bulk orders.",
                )
            )

    return insights


# Maintain backward compatibility with Phase 1
def generate_foundational_insights(df: pd.DataFrame) -> List[Dict[str, str]]:
    """Backward compatibility wrapper returning dictionaries for Phase 1 legacy consumers."""
    rich_insights = generate_comprehensive_insights(df)
    return [
        {
            "type": "summary" if ins.type == "revenue" else ins.type,
            "icon": ins.icon,
            "title": ins.title,
            "description": ins.description,
            "status": ins.status,
        }
        for ins in rich_insights
    ]
