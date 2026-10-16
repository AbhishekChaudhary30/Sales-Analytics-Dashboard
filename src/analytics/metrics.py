"""Comprehensive Business Metrics Engine.

Calculates core financial, operational, and customer KPIs with strict schema verification,
conservative derivation, and explicit availability metadata.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import pandas as pd

from src.utils.formatting import format_currency, format_number, format_percentage


@dataclass
class KPIMetadata:
    """Rich metadata describing a computed KPI, its validity, and required schema."""

    key: str
    display_name: str
    value: Optional[float]
    formatted_value: str
    sublabel: str
    definition: str
    required_fields: List[str]
    is_available: bool
    status_note: str
    is_derived: bool = False


@dataclass
class ExecutiveKPISet:
    """Consolidated collection of high-level business indicators."""

    kpi_dict: Dict[str, KPIMetadata] = field(default_factory=dict)

    @property
    def net_revenue(self) -> Optional[float]:
        kpi = self.kpi_dict.get("net_sales")
        return kpi.value if kpi and kpi.is_available else None

    @property
    def total_profit(self) -> Optional[float]:
        kpi = self.kpi_dict.get("total_profit")
        return kpi.value if kpi and kpi.is_available else None

    @property
    def profit_margin(self) -> Optional[float]:
        kpi = self.kpi_dict.get("profit_margin")
        return kpi.value if kpi and kpi.is_available else None

    @property
    def total_orders(self) -> Optional[int]:
        kpi = self.kpi_dict.get("total_orders")
        return int(kpi.value) if kpi and kpi.is_available and kpi.value is not None else None

    @property
    def aov(self) -> Optional[float]:
        kpi = self.kpi_dict.get("avg_order_value")
        return kpi.value if kpi and kpi.is_available else None


def compute_all_kpis(
    df: pd.DataFrame,
    currency_label: str = "USD",
    use_indian_numbering: bool = False,
) -> ExecutiveKPISet:
    """Calculate the complete suite of canonical sales KPIs from a working DataFrame.

    Handles partial schemas, negative transactions (returns), zero denominators,
    and returns rich KPIMetadata for every indicator.
    """
    kpis: Dict[str, KPIMetadata] = {}

    if df.empty:
        return ExecutiveKPISet()

    # 1. Net Sales / Revenue
    if "sales" in df.columns:
        sales_series = pd.to_numeric(df["sales"], errors="coerce").dropna()
        if not sales_series.empty:
            gross_val = float(sales_series[sales_series > 0].sum())
            return_val = float(sales_series[sales_series < 0].sum())
            net_val = float(sales_series.sum())

            sub_note = f"Gross: {format_currency(gross_val, currency_label, use_indian_numbering)}"
            if return_val < 0:
                sub_note += f" | Returns: {format_currency(return_val, currency_label, use_indian_numbering)}"

            kpis["net_sales"] = KPIMetadata(
                key="net_sales",
                display_name="Total Net Revenue",
                value=net_val,
                formatted_value=format_currency(net_val, currency_label, use_indian_numbering),
                sublabel=sub_note,
                definition="Net monetary sales revenue (gross transactions minus returns/refunds).",
                required_fields=["sales"],
                is_available=True,
                status_note="Computed from validated sales column.",
            )
        else:
            kpis["net_sales"] = KPIMetadata(
                key="net_sales",
                display_name="Total Net Revenue",
                value=None,
                formatted_value="—",
                sublabel="All sales values missing",
                definition="Net monetary sales revenue.",
                required_fields=["sales"],
                is_available=False,
                status_note="Sales column exists but contains only null or invalid values.",
            )
    else:
        kpis["net_sales"] = KPIMetadata(
            key="net_sales",
            display_name="Total Net Revenue",
            value=None,
            formatted_value="—",
            sublabel="Sales field not mapped",
            definition="Net monetary sales revenue.",
            required_fields=["sales"],
            is_available=False,
            status_note="Sales field unmapped. Map 'Sales / Revenue' or 'Quantity' and 'Unit Price'.",
        )

    # 2. Total Orders / Transactions
    if "order_id" in df.columns:
        order_series = df["order_id"].dropna().astype(str).str.strip()
        order_count = int(order_series.nunique())
        kpis["total_orders"] = KPIMetadata(
            key="total_orders",
            display_name="Distinct Orders",
            value=float(order_count),
            formatted_value=format_number(order_count),
            sublabel=f"{len(df):,} line items",
            definition="Count of distinct commercial order or invoice identifiers.",
            required_fields=["order_id"],
            is_available=True,
            status_note="Computed from distinct Order IDs.",
        )
    else:
        # Fallback to transaction row count with explicit qualification
        kpis["total_orders"] = KPIMetadata(
            key="total_orders",
            display_name="Transaction Rows",
            value=float(len(df)),
            formatted_value=format_number(len(df)),
            sublabel="Order ID unmapped (row count)",
            definition="Total transaction records (distinct order ID not available).",
            required_fields=["order_id"],
            is_available=True,
            status_note="Order ID unmapped; reporting raw record rows instead.",
        )

    # 3. Total Quantity
    if "quantity" in df.columns:
        qty_series = pd.to_numeric(df["quantity"], errors="coerce").dropna()
        if not qty_series.empty:
            total_qty = float(qty_series.sum())
            kpis["total_quantity"] = KPIMetadata(
                key="total_quantity",
                display_name="Units Sold",
                value=total_qty,
                formatted_value=f"{format_number(total_qty)} units",
                sublabel=f"Avg {qty_series.mean():.1f} per item",
                definition="Total product units sold across all transactions.",
                required_fields=["quantity"],
                is_available=True,
                status_note="Computed from validated quantity column.",
            )
        else:
            kpis["total_quantity"] = KPIMetadata(
                key="total_quantity",
                display_name="Units Sold",
                value=None,
                formatted_value="—",
                sublabel="Quantity data invalid",
                definition="Total product units sold.",
                required_fields=["quantity"],
                is_available=False,
                status_note="Quantity column contains no valid numeric values.",
            )
    else:
        kpis["total_quantity"] = KPIMetadata(
            key="total_quantity",
            display_name="Units Sold",
            value=None,
            formatted_value="—",
            sublabel="Quantity field unmapped",
            definition="Total product units sold.",
            required_fields=["quantity"],
            is_available=False,
            status_note="Map 'Quantity' in Step 4 to track volume metrics.",
        )

    # 4. Average Order Value (AOV)
    net_sales_kpi = kpis.get("net_sales")
    orders_kpi = kpis.get("total_orders")

    if (
        net_sales_kpi
        and net_sales_kpi.is_available
        and net_sales_kpi.value is not None
        and orders_kpi
        and orders_kpi.value is not None
        and orders_kpi.value > 0
    ):
        aov_val = net_sales_kpi.value / orders_kpi.value
        kpis["avg_order_value"] = KPIMetadata(
            key="avg_order_value",
            display_name="Average Order Value (AOV)",
            value=aov_val,
            formatted_value=format_currency(aov_val, currency_label, use_indian_numbering),
            sublabel=f"Revenue per {'order' if 'order_id' in df.columns else 'transaction'}",
            definition="Total net revenue divided by total distinct orders or transactions.",
            required_fields=["sales", "order_id"],
            is_available=True,
            status_note="Computed as Net Sales / Order Count.",
        )
    else:
        kpis["avg_order_value"] = KPIMetadata(
            key="avg_order_value",
            display_name="Average Order Value (AOV)",
            value=None,
            formatted_value="—",
            sublabel="Requires Sales & Order Count",
            definition="Total net revenue divided by total distinct orders.",
            required_fields=["sales", "order_id"],
            is_available=False,
            status_note="Cannot calculate AOV without valid revenue and order denominator.",
        )

    # 5. Total Profit & Margin
    if "profit" in df.columns:
        profit_series = pd.to_numeric(df["profit"], errors="coerce").dropna()
        if not profit_series.empty:
            total_profit = float(profit_series.sum())
            kpis["total_profit"] = KPIMetadata(
                key="total_profit",
                display_name="Net Profit",
                value=total_profit,
                formatted_value=format_currency(total_profit, currency_label, use_indian_numbering),
                sublabel="Earnings after costs",
                definition="Total net profit generated across transactions.",
                required_fields=["profit"],
                is_available=True,
                status_note="Computed from profit column.",
            )

            # Profit Margin %
            if net_sales_kpi and net_sales_kpi.is_available and net_sales_kpi.value and net_sales_kpi.value > 0:
                margin_pct = (total_profit / net_sales_kpi.value) * 100.0
                kpis["profit_margin"] = KPIMetadata(
                    key="profit_margin",
                    display_name="Profit Margin",
                    value=margin_pct,
                    formatted_value=format_percentage(margin_pct),
                    sublabel=f"{format_currency(total_profit, currency_label, use_indian_numbering)} net",
                    definition="Net profit expressed as a percentage of total net revenue.",
                    required_fields=["profit", "sales"],
                    is_available=True,
                    status_note="Computed as (Total Profit / Net Revenue) * 100.",
                )
            else:
                kpis["profit_margin"] = KPIMetadata(
                    key="profit_margin",
                    display_name="Profit Margin",
                    value=None,
                    formatted_value="—",
                    sublabel="Revenue is zero or missing",
                    definition="Net profit as a percentage of net revenue.",
                    required_fields=["profit", "sales"],
                    is_available=False,
                    status_note="Profit margin requires non-zero positive revenue denominator.",
                )
        else:
            kpis["total_profit"] = KPIMetadata(
                key="total_profit",
                display_name="Net Profit",
                value=None,
                formatted_value="—",
                sublabel="Profit values missing",
                definition="Total net profit.",
                required_fields=["profit"],
                is_available=False,
                status_note="Profit column contains no valid numeric values.",
            )
            kpis["profit_margin"] = KPIMetadata(
                key="profit_margin",
                display_name="Profit Margin",
                value=None,
                formatted_value="—",
                sublabel="Profit data missing",
                definition="Profit margin percentage.",
                required_fields=["profit", "sales"],
                is_available=False,
                status_note="Profit data missing.",
            )
    else:
        kpis["total_profit"] = KPIMetadata(
            key="total_profit",
            display_name="Net Profit",
            value=None,
            formatted_value="—",
            sublabel="Profit field unmapped",
            definition="Total net profit.",
            required_fields=["profit"],
            is_available=False,
            status_note="Map 'Profit' or 'Sales' and 'Cost' in Step 4.",
        )
        kpis["profit_margin"] = KPIMetadata(
            key="profit_margin",
            display_name="Profit Margin",
            value=None,
            formatted_value="—",
            sublabel="Profit field unmapped",
            definition="Profit margin percentage.",
            required_fields=["profit", "sales"],
            is_available=False,
            status_note="Profit margin requires mapped profit field.",
        )

    # 6. Unique Customers
    cust_col = "customer_id" if "customer_id" in df.columns else ("customer_name" if "customer_name" in df.columns else None)
    if cust_col:
        cust_series = df[cust_col].dropna().astype(str).str.strip()
        cust_count = int(cust_series.nunique())
        kpis["unique_customers"] = KPIMetadata(
            key="unique_customers",
            display_name="Active Customers",
            value=float(cust_count),
            formatted_value=format_number(cust_count),
            sublabel=f"Based on {cust_col.replace('_', ' ').title()}",
            definition="Count of distinct purchasing customer accounts or names.",
            required_fields=[cust_col],
            is_available=True,
            status_note=f"Calculated from distinct {cust_col}.",
        )
    else:
        kpis["unique_customers"] = KPIMetadata(
            key="unique_customers",
            display_name="Active Customers",
            value=None,
            formatted_value="—",
            sublabel="Customer fields unmapped",
            definition="Distinct purchasing customer accounts.",
            required_fields=["customer_id", "customer_name"],
            is_available=False,
            status_note="Customer ID and Customer Name are unmapped.",
        )

    # 7. Average Discount
    if "discount" in df.columns:
        disc_series = pd.to_numeric(df["discount"], errors="coerce").dropna()
        if not disc_series.empty:
            mean_disc = float(disc_series.mean())
            if 0.0 < mean_disc <= 1.0:
                mean_disc *= 100.0
            kpis["avg_discount"] = KPIMetadata(
                key="avg_discount",
                display_name="Average Discount",
                value=mean_disc,
                formatted_value=format_percentage(mean_disc),
                sublabel=f"Max {disc_series.max() * (100 if disc_series.max() <= 1.0 else 1):.0f}%",
                definition="Average markdown applied per transaction line item.",
                required_fields=["discount"],
                is_available=True,
                status_note="Computed from discount values.",
            )
        else:
            kpis["avg_discount"] = KPIMetadata(
                key="avg_discount",
                display_name="Average Discount",
                value=None,
                formatted_value="—",
                sublabel="Discount data invalid",
                definition="Average markdown applied.",
                required_fields=["discount"],
                is_available=False,
                status_note="Discount column contains no numeric values.",
            )
    else:
        kpis["avg_discount"] = KPIMetadata(
            key="avg_discount",
            display_name="Average Discount",
            value=None,
            formatted_value="—",
            sublabel="Discount field unmapped",
            definition="Average markdown applied.",
            required_fields=["discount"],
            is_available=False,
            status_note="Discount field is unmapped.",
        )

    # 8. Average Selling Price (ASP)
    if "unit_price" in df.columns:
        price_series = pd.to_numeric(df["unit_price"], errors="coerce").dropna()
        if not price_series.empty:
            asp_val = float(price_series.mean())
            kpis["avg_selling_price"] = KPIMetadata(
                key="avg_selling_price",
                display_name="Average Unit Price",
                value=asp_val,
                formatted_value=format_currency(asp_val, currency_label, use_indian_numbering),
                sublabel="Mean catalogue price",
                definition="Arithmetic mean of item unit prices.",
                required_fields=["unit_price"],
                is_available=True,
                status_note="Computed from unit price column.",
            )
    elif (
        net_sales_kpi
        and net_sales_kpi.is_available
        and net_sales_kpi.value
        and "total_quantity" in kpis
        and kpis["total_quantity"].is_available
        and kpis["total_quantity"].value
        and kpis["total_quantity"].value > 0
    ):
        implied_asp = net_sales_kpi.value / kpis["total_quantity"].value
        kpis["avg_selling_price"] = KPIMetadata(
            key="avg_selling_price",
            display_name="Implied Price / Unit",
            value=implied_asp,
            formatted_value=format_currency(implied_asp, currency_label, use_indian_numbering),
            sublabel="Derived: Revenue / Total Units",
            definition="Revenue divided by total quantity sold.",
            required_fields=["sales", "quantity"],
            is_available=True,
            status_note="Derived from net sales divided by total units.",
            is_derived=True,
        )
    else:
        kpis["avg_selling_price"] = KPIMetadata(
            key="avg_selling_price",
            display_name="Average Selling Price",
            value=None,
            formatted_value="—",
            sublabel="Price & Quantity unmapped",
            definition="Average price per unit sold.",
            required_fields=["unit_price"],
            is_available=False,
            status_note="Requires Unit Price or Sales and Quantity.",
        )

    # 9. Return / Refund Rate
    if "sales" in df.columns:
        valid_sales = pd.to_numeric(df["sales"], errors="coerce").dropna()
        if not valid_sales.empty:
            neg_count = int((valid_sales < 0).sum())
            return_rate = (neg_count / len(valid_sales)) * 100.0
            kpis["return_rate"] = KPIMetadata(
                key="return_rate",
                display_name="Return / Refund Rate",
                value=return_rate,
                formatted_value=format_percentage(return_rate),
                sublabel=f"{neg_count:,} negative transactions",
                definition="Percentage of transactions recorded with negative sales value.",
                required_fields=["sales"],
                is_available=True,
                status_note="Computed from negative sales entries.",
            )

    return ExecutiveKPISet(kpi_dict=kpis)


# Backward compatibility wrapper for Phase 1
def calculate_foundational_kpis(df: pd.DataFrame) -> Any:
    """Wrapper ensuring existing Phase 1 imports continue to function smoothly."""
    from dataclasses import make_dataclass
    kpi_set = compute_all_kpis(df)

    LegacyKPIs = make_dataclass(
        "LegacyKPIs",
        [
            ("total_revenue", Optional[float]),
            ("total_orders", Optional[int]),
            ("total_units", Optional[float]),
            ("avg_order_value", Optional[float]),
            ("total_profit", Optional[float]),
            ("profit_margin_pct", Optional[float]),
            ("avg_discount_pct", Optional[float]),
            ("unique_customers", Optional[int]),
            ("unique_products", Optional[int]),
        ],
    )

    cust_kpi = kpi_set.kpi_dict.get("unique_customers")
    cust_val = int(cust_kpi.value) if cust_kpi and cust_kpi.is_available and cust_kpi.value else None

    disc_kpi = kpi_set.kpi_dict.get("avg_discount")
    disc_val = disc_kpi.value if disc_kpi and disc_kpi.is_available else None

    units_kpi = kpi_set.kpi_dict.get("total_quantity")
    units_val = units_kpi.value if units_kpi and units_kpi.is_available else None

    prod_count = None
    if "product_name" in df.columns:
        prod_count = int(df["product_name"].dropna().nunique())
    elif "product_id" in df.columns:
        prod_count = int(df["product_id"].dropna().nunique())

    return LegacyKPIs(
        total_revenue=kpi_set.net_revenue,
        total_orders=kpi_set.total_orders,
        total_units=units_val,
        avg_order_value=kpi_set.aov,
        total_profit=kpi_set.total_profit,
        profit_margin_pct=kpi_set.profit_margin,
        avg_discount_pct=disc_val,
        unique_customers=cust_val,
        unique_products=prod_count,
    )
