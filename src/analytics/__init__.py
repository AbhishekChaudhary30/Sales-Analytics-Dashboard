"""Analytics module containing foundational business metrics, aggregations, and insights."""

from src.analytics.aggregations import (
    aggregate_by_category,
    aggregate_by_dimension,
    aggregate_by_time,
)
from src.analytics.insights import generate_foundational_insights
from src.analytics.metrics import SummaryKPIs, calculate_foundational_kpis

__all__ = [
    "SummaryKPIs",
    "aggregate_by_category",
    "aggregate_by_dimension",
    "aggregate_by_time",
    "calculate_foundational_kpis",
    "generate_foundational_insights",
]
