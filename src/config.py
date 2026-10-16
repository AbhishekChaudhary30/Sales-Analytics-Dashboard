"""Configuration constants and standard business field definitions.

This module provides centralized settings for application metadata, UI themes,
supported file types, and internal business field mapping schemas.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AppConfig:
    """Core application metadata and operational constraints."""

    APP_NAME: str = "Sales Analytics Dashboard"
    TAGLINE: str = "Understand Sales. Discover Trends. Make Better Decisions."
    DESCRIPTION: str = (
        "An interactive sales intelligence workspace that transforms raw sales data "
        "into understandable business insights and visual reports."
    )
    VERSION: str = "1.0.0"

    # Ingestion constraints
    MAX_FILE_SIZE_MB: int = 50
    MAX_FILE_SIZE_BYTES: int = 50 * 1024 * 1024
    SUPPORTED_EXTENSIONS: tuple = (".csv", ".xlsx", ".xls")

    # Sample data
    DEFAULT_SAMPLE_PATH: str = "data/samples/superstore_sample.csv"


@dataclass(frozen=True)
class UIThemeConfig:
    """Design system color palette tokens and styling parameters."""

    # Backgrounds
    BG_DARK: str = "#0B0F19"  # Deep graphite base
    BG_CARD: str = "#111827"  # Deep navy card surface
    BG_CARD_ELEVATED: str = "#1F2937"  # Elevated card surface
    BG_INPUT: str = "#1A2234"  # Input field background

    # Accents
    PRIMARY_VIOLET: str = "#8B5CF6"  # Electric violet
    PRIMARY_VIOLET_HOVER: str = "#7C3AED"
    PRIMARY_VIOLET_GLOW: str = "rgba(139, 92, 246, 0.25)"

    SECONDARY_CYAN: str = "#06B6D4"  # Electric cyan
    SECONDARY_CYAN_HOVER: str = "#22D3EE"
    SECONDARY_CYAN_GLOW: str = "rgba(6, 182, 212, 0.25)"

    # Status / Indicators
    COLOR_SUCCESS: str = "#10B981"  # Emerald
    COLOR_WARNING: str = "#F59E0B"  # Amber
    COLOR_DANGER: str = "#EF4444"  # Rose
    COLOR_INFO: str = "#3B82F6"  # Blue

    # Text hierarchy
    TEXT_PRIMARY: str = "#F9FAFB"
    TEXT_SECONDARY: str = "#D1D5DB"
    TEXT_MUTED: str = "#9CA3AF"
    TEXT_SUBTLE: str = "#6B7280"

    # Borders & Dividers
    BORDER_DEFAULT: str = "#1F2937"
    BORDER_LIGHT: str = "#374151"
    BORDER_ACCENT: str = "rgba(139, 92, 246, 0.4)"

    # Plotly sequential and categorical palette
    PLOTLY_PALETTE: tuple = (
        "#8B5CF6",  # Violet
        "#06B6D4",  # Cyan
        "#10B981",  # Emerald
        "#F59E0B",  # Amber
        "#EC4899",  # Pink
        "#6366F1",  # Indigo
        "#14B8A6",  # Teal
        "#F97316",  # Orange
    )


@dataclass
class BusinessField:
    """Definition of a standard internal business field."""

    key: str
    display_name: str
    category: str  # 'transaction', 'customer', 'product', 'geography', 'financial', 'logistics'
    data_type: str  # 'numeric', 'datetime', 'categorical', 'text', 'id'
    description: str
    is_essential: bool
    aliases: list[str] = field(default_factory=list)


# Comprehensive standard field registry
STANDARD_BUSINESS_FIELDS: dict[str, BusinessField] = {
    "order_id": BusinessField(
        key="order_id",
        display_name="Order ID",
        category="transaction",
        data_type="id",
        description="Unique identifier for sales orders or invoices.",
        is_essential=False,
        aliases=[
            "order_id", "order id", "orderid", "invoice_no", "invoiceno",
            "invoice number", "transaction_id", "transaction id", "trans_id",
            "sales_order", "document_no", "order_number", "order no"
        ],
    ),
    "order_date": BusinessField(
        key="order_date",
        display_name="Order Date",
        category="transaction",
        data_type="datetime",
        description="Date when the transaction or order occurred.",
        is_essential=True,
        aliases=[
            "order_date", "order date", "orderdate", "invoice_date",
            "invoicedate", "transaction_date", "date", "purchase_date",
            "sale_date", "trans_date", "created_at", "order timestamp"
        ],
    ),
    "ship_date": BusinessField(
        key="ship_date",
        display_name="Ship Date",
        category="logistics",
        data_type="datetime",
        description="Date when the order was shipped or fulfilled.",
        is_essential=False,
        aliases=[
            "ship_date", "ship date", "shipdate", "shipping_date",
            "dispatch_date", "delivery_date", "shipped_at"
        ],
    ),
    "customer_id": BusinessField(
        key="customer_id",
        display_name="Customer ID",
        category="customer",
        data_type="id",
        description="Unique customer identifier or account number.",
        is_essential=False,
        aliases=[
            "customer_id", "customer id", "customerid", "client_id",
            "clientid", "account_id", "user_id", "buyer_id", "cust_id"
        ],
    ),
    "customer_name": BusinessField(
        key="customer_name",
        display_name="Customer Name",
        category="customer",
        data_type="categorical",
        description="Name of the customer or purchasing company.",
        is_essential=False,
        aliases=[
            "customer_name", "customer name", "customername", "client_name",
            "client", "buyer_name", "customer", "contact_name", "company_name"
        ],
    ),
    "product_id": BusinessField(
        key="product_id",
        display_name="Product ID",
        category="product",
        data_type="id",
        description="Unique identifier or SKU for the product.",
        is_essential=False,
        aliases=[
            "product_id", "product id", "productid", "item_id", "item id",
            "sku", "stock_code", "stockcode", "part_number", "item_code"
        ],
    ),
    "product_name": BusinessField(
        key="product_name",
        display_name="Product Name",
        category="product",
        data_type="categorical",
        description="Name or title of the product item sold.",
        is_essential=False,
        aliases=[
            "product_name", "product name", "productname", "product",
            "item_name", "item", "description", "item_description",
            "product_description", "title"
        ],
    ),
    "category": BusinessField(
        key="category",
        display_name="Category",
        category="product",
        data_type="categorical",
        description="Broad merchandise grouping or product category.",
        is_essential=False,
        aliases=[
            "category", "product_category", "item_category", "department",
            "product_line", "category_name", "group"
        ],
    ),
    "subcategory": BusinessField(
        key="subcategory",
        display_name="Subcategory",
        category="product",
        data_type="categorical",
        description="Specific granular category within a primary category.",
        is_essential=False,
        aliases=[
            "subcategory", "sub_category", "sub-category", "sub category",
            "product_subcategory", "item_subcategory", "class", "sub_class"
        ],
    ),
    "quantity": BusinessField(
        key="quantity",
        display_name="Quantity",
        category="financial",
        data_type="numeric",
        description="Number of units sold per transaction item.",
        is_essential=False,
        aliases=[
            "quantity", "qty", "units", "units_sold", "volume",
            "order_quantity", "quantity_ordered", "item_count", "count"
        ],
    ),
    "unit_price": BusinessField(
        key="unit_price",
        display_name="Unit Price",
        category="financial",
        data_type="numeric",
        description="Selling price for a single unit.",
        is_essential=False,
        aliases=[
            "unit_price", "unit price", "unitprice", "price", "rate",
            "item_price", "price_per_unit", "each_price"
        ],
    ),
    "sales": BusinessField(
        key="sales",
        display_name="Sales / Revenue",
        category="financial",
        data_type="numeric",
        description="Total monetary transaction revenue or gross sales value.",
        is_essential=True,
        aliases=[
            "sales", "revenue", "sales_amount", "sale_amount", "total_sales",
            "total_revenue", "net_sales", "turnover", "gross_sales",
            "line_total", "total_amount", "order_value"
        ],
    ),
    "cost": BusinessField(
        key="cost",
        display_name="Cost",
        category="financial",
        data_type="numeric",
        description="Cost of goods sold (COGS) or production cost.",
        is_essential=False,
        aliases=[
            "cost", "cogs", "cost_of_goods_sold", "total_cost",
            "unit_cost", "purchase_cost", "product_cost", "manufacturing_cost"
        ],
    ),
    "profit": BusinessField(
        key="profit",
        display_name="Profit",
        category="financial",
        data_type="numeric",
        description="Net profit or margin generated by the transaction.",
        is_essential=False,
        aliases=[
            "profit", "net_profit", "profit_amount", "gross_profit",
            "earnings", "net_income", "profit_loss"
        ],
    ),
    "discount": BusinessField(
        key="discount",
        display_name="Discount",
        category="financial",
        data_type="numeric",
        description="Discount percentage or monetary markdown applied.",
        is_essential=False,
        aliases=[
            "discount", "discount_amount", "discount_rate", "discount_pct",
            "discount_percentage", "rebate", "markdown", "disc"
        ],
    ),
    "region": BusinessField(
        key="region",
        display_name="Region",
        category="geography",
        data_type="categorical",
        description="Sales territory, region, or continental market.",
        is_essential=False,
        aliases=[
            "region", "territory", "sales_region", "sales_territory", "geographic_region"
        ],
    ),
    "country": BusinessField(
        key="country",
        display_name="Country",
        category="geography",
        data_type="categorical",
        description="Country where the sale occurred.",
        is_essential=False,
        aliases=[
            "country", "nation", "country_code", "billing_country",
            "ship_country"
        ],
    ),
    "state": BusinessField(
        key="state",
        display_name="State / Province",
        category="geography",
        data_type="categorical",
        description="State, province, or administrative division.",
        is_essential=False,
        aliases=[
            "state", "province", "region_state", "state_province",
            "state_code"
        ],
    ),
    "city": BusinessField(
        key="city",
        display_name="City",
        category="geography",
        data_type="categorical",
        description="City or municipality of the customer or branch.",
        is_essential=False,
        aliases=[
            "city", "town", "municipality", "billing_city", "ship_city"
        ],
    ),
    "sales_channel": BusinessField(
        key="sales_channel",
        display_name="Sales Channel",
        category="transaction",
        data_type="categorical",
        description="Channel through which the sale occurred (e.g. Online, Retail).",
        is_essential=False,
        aliases=[
            "sales_channel", "channel", "distribution_channel",
            "channel_name", "platform", "store_type", "order_channel"
        ],
    ),
    "payment_method": BusinessField(
        key="payment_method",
        display_name="Payment Method",
        category="transaction",
        data_type="categorical",
        description="Payment mechanism used (e.g., Credit Card, PayPal, Cash).",
        is_essential=False,
        aliases=[
            "payment_method", "payment_type", "payment_mode",
            "pay_method", "tender_type", "payment_channel"
        ],
    ),
    "shipping_mode": BusinessField(
        key="shipping_mode",
        display_name="Shipping Mode",
        category="logistics",
        data_type="categorical",
        description="Delivery speed or carrier tier (e.g., Standard Class, Express).",
        is_essential=False,
        aliases=[
            "shipping_mode", "ship_mode", "delivery_mode", "ship_method",
            "shipping_method", "carrier", "fulfillment_method"
        ],
    ),
}

# Supported Pages in navigation order
PAGE_ROUTES = {
    "overview": {"title": "Welcome & Overview", "icon": "🏠", "step": 1},
    "upload": {"title": "Upload Dataset", "icon": "📤", "step": 2},
    "inspection": {"title": "Data Inspection", "icon": "🔍", "step": 3},
    "mapping": {"title": "Column Mapping", "icon": "🧭", "step": 4},
    "workspace": {"title": "Analysis Workspace", "icon": "📊", "step": 5},
    "reports": {"title": "Reports & Export", "icon": "📑", "step": 6},
}
