# Commercial Analytics & Mathematical Methodology

This document details the rigorous formulas, accounting semantics, data validation standards, and statistical rules implemented in the **Sales Analytics Dashboard** engine.

---

## 1. Financial & Revenue Semantics

### 1.1 Gross Revenue, Returns, and Net Sales
A transaction dataset may record returns, refunds, credit notes, or adjustments as negative sales amounts. The metrics engine strictly differentiates between:

$$\text{Gross Revenue} = \sum_{i \in \text{Sales} > 0} \text{Sales}_i$$

$$\text{Returns \& Adjustments} = \sum_{i \in \text{Sales} < 0} \text{Sales}_i$$

$$\text{Net Revenue} = \sum_{\text{All } i} \text{Sales}_i = \text{Gross Revenue} + \text{Returns}$$

Negative records are **never silently deleted**; they are retained to compute commercial refund rates:

$$\text{Return / Refund Rate} = \frac{\text{Count of records with Sales} < 0}{\text{Total Transaction Count}} \times 100$$

### 1.2 Derived Revenue Rule
If `Sales` is unmapped, the engine only calculates revenue if both `Quantity` and `Unit Price` are mapped and verified:

$$\text{Derived Revenue} = \text{Quantity} \times \text{Unit Price}$$

If neither is available, revenue-dependent KPIs are disabled and flagged as unavailable.

---

## 2. Profitability and Margins

### 2.1 Net Profit
$$\text{Net Profit} = \sum \text{Profit}_i$$

If `Profit` is unmapped but `Sales` and `Cost` exist, the engine conservatively computes:

$$\text{Derived Profit} = \text{Sales} - \text{Cost}$$

*Note*: Cost must represent total transaction cost (COGS), not unadjusted unit cost.

### 2.2 Profit Margin %
$$\text{Profit Margin} = \left( \frac{\text{Net Profit}}{\text{Net Revenue}} \right) \times 100$$

- **Zero / Negative Denominator Handling**: If Net Revenue is $\le 0$, margin % is undefined and returned as `None` / `—`, avoiding misleading infinite or NaN values.

---

## 3. Orders and Average Order Value (AOV)

$$\text{Total Orders} = \text{Distinct Count of Valid } \text{Order ID}$$

If `Order ID` is absent, the engine reports total line-item records with an explicit label: `Transaction Rows (Order ID unmapped)`.

$$\text{Average Order Value (AOV)} = \frac{\text{Net Revenue}}{\text{Total Orders}}$$

Calculated only when the order count is positive.

---

## 4. Time Series & Period-over-Period (PoP) Comparison

### 4.1 Temporal Frequencies
Transactions are resampled into continuous time intervals:
- Daily (`D`), Weekly (`W`), Monthly (`ME`), Quarterly (`QE`), Yearly (`YE`).

### 4.2 Period Growth Formulation
$$\Delta_{\text{abs}} = V_{\text{current}} - V_{\text{previous}}$$

$$\text{Growth \%} = \left( \frac{V_{\text{current}} - V_{\text{previous}}}{|V_{\text{previous}}|} \right) \times 100 \quad \text{for } V_{\text{previous}} \neq 0$$

- **Zero-Base Rule**: If $V_{\text{previous}} = 0$, percentage growth is undefined. The dashboard reports $\Delta_{\text{abs}}$ and explains that percentage growth cannot be evaluated.

---

## 5. Assortment & Pareto 80/20 Analysis

Sorts items descending by revenue $S_1 \ge S_2 \ge \dots \ge S_N$:

$$\text{Cumulative Share}_k = \frac{\sum_{i=1}^k S_i}{\sum_{i=1}^N S_i} \times 100$$

The engine identifies the smallest index $k^*$ such that $\text{Cumulative Share}_{k^*} \ge 80\%$. It reports both the product count $k^*$ and the catalog percentage:

$$\text{Core Catalog \%} = \left( \frac{k^*}{N} \right) \times 100$$

---

## 6. Discount Tier Segmentation & Margin Erosion

Transactions are partitioned into 4 discrete commercial markdown tiers:
1. **No Discount**: $\text{Discount} = 0\%$
2. **Low Discount**: $0\% < \text{Discount} \le 10\%$
3. **Moderate Discount**: $10\% < \text{Discount} \le 20\%$
4. **High Discount**: $\text{Discount} > 20\%$

For each tier, the engine evaluates transaction volume, revenue, profit, and margin %, computing Pearson's correlation between discount rate and profit margin:

$$r = \frac{\sum (D_i - \bar{D})(P_i - \bar{P})}{\sqrt{\sum (D_i - \bar{D})^2 \sum (P_i - \bar{P})^2}}$$

---

## 7. Statistical Outlier Detection (IQR Method)

Identifies extreme non-normal transaction values without assuming normality:

$$\text{IQR} = Q_3 - Q_1$$

$$\text{Lower Fence} = Q_1 - 1.5 \times \text{IQR}$$

$$\text{Upper Fence} = Q_3 + 1.5 \times \text{IQR}$$

Records outside $[\text{Lower Fence}, \text{Upper Fence}]$ are flagged for inspection in the Data Explorer rather than discarded.
