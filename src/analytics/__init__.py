"""Comprehensive Analytics Engine Package.

Exposes metrics, time series aggregations, product analytics, customer dynamics,
profitability breakdown, statistical distributions, filtering, and automated insights.
"""

from src.analytics.aggregations import (
    aggregate_by_category,
    aggregate_by_dimension,
    aggregate_by_time,
)
from src.analytics.customers import (
    CustomerConcentration,
    RepeatCustomerAnalysis,
    analyze_customer_concentration,
    analyze_repeat_customers,
    rank_customers,
)
from src.analytics.filters import (
    FilterResult,
    FilterState,
    apply_filters,
)
from src.analytics.geography import analyze_geography
from src.analytics.insights import (
    BusinessInsight,
    generate_comprehensive_insights,
    generate_foundational_insights,
)
from src.analytics.metrics import (
    ExecutiveKPISet,
    KPIMetadata,
    calculate_foundational_kpis,
    compute_all_kpis,
)
from src.analytics.products import (
    ParetoResult,
    analyze_categories,
    calculate_pareto_analysis,
    rank_products,
)
from src.analytics.profitability import (
    DiscountTierSummary,
    LossMakingAnalysis,
    analyze_discount_tiers,
    analyze_loss_making_transactions,
)
from src.analytics.statistics import (
    OutlierSummary,
    compute_correlation_matrix,
    compute_descriptive_stats,
    detect_iqr_outliers,
)
from src.analytics.time_series import (
    PeriodComparison,
    aggregate_time_series,
    calculate_year_over_year,
    compare_periods,
    parse_and_validate_dates,
)

__all__ = [
    "BusinessInsight",
    "CustomerConcentration",
    "DiscountTierSummary",
    "ExecutiveKPISet",
    "FilterResult",
    "FilterState",
    "KPIMetadata",
    "LossMakingAnalysis",
    "OutlierSummary",
    "ParetoResult",
    "PeriodComparison",
    "RepeatCustomerAnalysis",
    "aggregate_by_category",
    "aggregate_by_dimension",
    "aggregate_by_time",
    "aggregate_time_series",
    "analyze_categories",
    "analyze_customer_concentration",
    "analyze_discount_tiers",
    "analyze_geography",
    "analyze_loss_making_transactions",
    "analyze_repeat_customers",
    "apply_filters",
    "calculate_foundational_kpis",
    "calculate_pareto_analysis",
    "calculate_year_over_year",
    "compare_periods",
    "compute_all_kpis",
    "compute_correlation_matrix",
    "compute_descriptive_stats",
    "detect_iqr_outliers",
    "generate_comprehensive_insights",
    "generate_foundational_insights",
    "parse_and_validate_dates",
    "rank_customers",
    "rank_products",
]
