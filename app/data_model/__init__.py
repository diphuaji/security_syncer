import typing
from typing import Optional

from datetime import date

from app.interfaces import DataClassMixin


class Security(DataClassMixin):
    symbol: str
    name: str
    exchange: str = 'UNKNOWN'
    country: str = 'US'
    currency: str = "USD"
    asset_class: str = 'EQUITY'
    sector: Optional[str] = None
    industry: Optional[str] = None
    isin: Optional[str] = None
    cusip: Optional[str] = None
    ipo_date: Optional[date] = None
    is_active: bool = True


class BalanceSheet(DataClassMixin):
    id: int  # Auto-increment primary key
    security_id: int  # Security ID as in metadata db
    as_of_date: date  # Reporting date of the balance sheet
    period_type: Optional[str] = None  # Quarterly or annual data
    currency_code: Optional[str] = None  # Currency used in reporting (e.g., USD)

    accounts_payable: Optional[float] = None  # Amount owed to suppliers and vendors
    accounts_receivable: Optional[float] = None  # Money owed to the company by customers
    accum_depreciation: Optional[float] = None  # Total depreciation of assets to date
    afs_securities: Optional[float] = None  # Available-for-sale securities
    capital_lease_oblig: Optional[float] = None  # Long-term capital lease obligations
    capital_stock: Optional[float] = None  # Par value of issued capital stock
    cash_equiv: Optional[float] = None  # Cash equivalents
    cash_and_st_invest: Optional[float] = None  # Cash and short-term investments
    cash_financial: Optional[float] = None  # Cash from financial instruments
    commercial_paper: Optional[float] = None  # Short-term promissory notes
    common_stock: Optional[float] = None  # Value of common stock issued
    common_equity: Optional[float] = None  # Equity attributable to common shareholders
    current_assets: Optional[float] = None  # Assets expected to be used/sold within a year
    current_lease_oblig: Optional[float] = None  # Lease obligations due within one year
    current_debt: Optional[float] = None  # Short-term borrowings
    current_debt_lease_oblig: Optional[float] = None  # Short-term debt + leases
    current_deferred_liab: Optional[float] = None  # Short-term deferred liabilities
    current_deferred_rev: Optional[float] = None  # Deferred revenue < 1 year
    current_liabilities: Optional[float] = None  # Obligations due within a year
    gains_losses_ret_earnings: Optional[float] = None  # Gains/losses bypassing retained earnings
    gross_ppe: Optional[float] = None  # PPE before depreciation
    income_tax_payable: Optional[float] = None  # Taxes owed
    inventory: Optional[float] = None  # Inventory value
    invested_capital: Optional[float] = None  # Total capital invested
    invest_fin_assets: Optional[float] = None  # Financial asset investments
    investments_advances: Optional[float] = None  # Loans/investments in subsidiaries
    land_improvements: Optional[float] = None  # Land and improvements value
    leases: Optional[float] = None  # Total lease obligations
    lt_lease_oblig: Optional[float] = None  # Long-term lease obligations
    long_term_debt: Optional[float] = None  # Debt > 1 year
    lt_debt_lease_oblig: Optional[float] = None  # Long-term debt + leases
    machinery_equipment: Optional[float] = None  # Machinery, furniture, equipment
    net_debt: Optional[float] = None  # Debt - cash equivalents
    net_ppe: Optional[float] = None  # PPE after depreciation
    net_tangible_assets: Optional[float] = None  # Tangible assets - liabilities
    nca_deferred_assets: Optional[float] = None  # Non-current deferred assets
    nca_deferred_tax_assets: Optional[float] = None  # Long-term deferred tax assets
    ordinary_shares: Optional[float] = None  # Ordinary shares outstanding
    other_curr_assets: Optional[float] = None  # Other current assets
    other_curr_borrowings: Optional[float] = None  # Other short-term borrowings
    other_curr_liab: Optional[float] = None  # Other short-term liabilities
    other_equity_adj: Optional[float] = None  # Other equity adjustments
    other_investments: Optional[float] = None  # Other investments
    other_nca: Optional[float] = None  # Other long-term assets
    other_non_curr_liab: Optional[float] = None  # Other long-term liabilities
    other_properties: Optional[float] = None  # Non-PPE properties
    other_receivables: Optional[float] = None  # Non-AR receivables
    other_st_investments: Optional[float] = None  # Other short-term investments
    payables: Optional[float] = None  # Trade and non-trade payables
    payables_accrued_exp: Optional[float] = None  # Payables + accrued expenses
    properties: Optional[float] = None  # Real estate/property
    receivables: Optional[float] = None  # All company receivables
    retained_earnings: Optional[float] = None  # Retained net income
    shares_issued: Optional[float] = None  # Issued shares
    stockholders_equity: Optional[float] = None  # Total shareholder equity
    tangible_book_value: Optional[float] = None  # Book value excluding intangibles
    total_assets: Optional[float] = None  # All assets (current + non-current)
    total_capitalization: Optional[float] = None  # Debt + shareholder equity
    total_debt: Optional[float] = None  # All debt (short + long term)
    total_equity_with_minor: Optional[float] = None  # Equity incl. minority interest
    total_liab_no_minor: Optional[float] = None  # Liabilities excl. minority interest
    total_non_curr_assets: Optional[float] = None  # Long-term assets
    total_non_curr_liab_no_minor: Optional[float] = None  # Long-term liabilities excl. minority
    total_tax_payable: Optional[float] = None  # Total tax obligations
    trade_payables_non_curr: Optional[float] = None  # Trade payables > 1 year
    treasury_shares: Optional[float] = None  # Repurchased shares held
    working_capital: Optional[float] = None  # Current assets - current liabilities


class IncomeStatement(DataClassMixin):
    id: int  # Auto-increment primary key
    security_id: int  # Security ID as in metadata DB
    as_of_date: date  # Reporting date of the income statement
    period_type: Optional[str] = None  # Reporting period type: annual or quarterly
    currency_code: Optional[str] = None  # Currency of the financial report

    basic_average_shares: Optional[float] = None  # Weighted average of basic shares outstanding
    basic_eps: Optional[float] = None  # Earnings per share using basic shares
    cost_of_revenue: Optional[float] = None  # Direct costs attributable to goods/services sold
    diluted_average_shares: Optional[float] = None  # Weighted average of diluted shares outstanding
    diluted_eps: Optional[float] = None  # Earnings per share using diluted shares
    diluted_net_income_to_common_stockholders: Optional[float] = None  # Net income available to common shareholders, diluted

    ebit: Optional[float] = None  # Earnings Before Interest and Taxes
    ebitda: Optional[float] = None  # Earnings Before Interest, Taxes, Depreciation, and Amortization
    gross_profit: Optional[float] = None  # Revenue minus cost of revenue

    interest_expense: Optional[float] = None  # Total interest expenses incurred
    interest_expense_non_operating: Optional[float] = None  # Interest expense not related to core business
    interest_income: Optional[float] = None  # Total interest income earned
    interest_income_non_operating: Optional[float] = None  # Interest income not related to core operations

    net_income: Optional[float] = None  # Final profit after all expenses and taxes
    net_income_common_stockholders: Optional[float] = None  # Net income attributable to common shareholders
    net_income_continuous_operations: Optional[float] = None  # Net income from ongoing business operations

    net_income_from_cont_and_discontinued_operation: Optional[float] = None  # Income from continuing + discontinued operations
    net_income_cont_operation_net_minority_interest: Optional[float] = None  # Net income from continuing operations after minority interest
    net_income_incl_noncontrolling_interests: Optional[float] = None  # Net income including minority interests

    net_interest_income: Optional[float] = None  # Interest income minus interest expense
    net_non_operating_interest_income_expense: Optional[float] = None  # Net interest from non-operating activities

    normalized_ebitda: Optional[float] = None  # Adjusted EBITDA excluding irregular items
    normalized_income: Optional[float] = None  # Adjusted net income excluding irregular items

    operating_expense: Optional[float] = None  # Total operating expenses
    operating_income: Optional[float] = None  # Earnings from core operations
    operating_revenue: Optional[float] = None  # Revenue from primary business activities

    other_income_expense: Optional[float] = None  # Miscellaneous income and expenses
    other_non_operating_income_expenses: Optional[float] = None  # Non-operating miscellaneous income/expenses

    pretax_income: Optional[float] = None  # Earnings before tax
    reconciled_cost_of_revenue: Optional[float] = None  # Adjusted cost of revenue
    reconciled_depreciation: Optional[float] = None  # Adjusted depreciation and amortization

    research_and_development: Optional[float] = None  # R&D expenses
    selling_general_and_administration: Optional[float] = None  # SG&A expenses

    tax_effect_of_unusual_items: Optional[float] = None  # Tax effects of one-time items
    tax_provision: Optional[float] = None  # Total taxes provided for
    tax_rate_for_calcs: Optional[float] = None  # Effective tax rate used in calculations

    total_expenses: Optional[float] = None  # Total costs and expenses
    total_operating_income_as_reported: Optional[float] = None  # Operating income before adjustments
    total_revenue: Optional[float] = None  # Total revenue from all sources


class FundamentalAnalytics(DataClassMixin):
    p_e_ratio: float
    earning_growth: float
    revenue_growth: float
    profit_margin: float
    return_on_equity: float
    debt_to_equity_ratio: float
    quick_ratio: float



# todo
class Quote(typing.NamedTuple):
    ticker: str
    exchange: str

