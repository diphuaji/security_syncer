from typing import Dict, Iterable, List
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy import ColumnElement, create_engine, MetaData, Table, INTEGER, REAL, Column, TEXT, DATE, Engine, select, \
    text, TIMESTAMP, DATETIME, BIGINT, BOOLEAN, UniqueConstraint
import datetime
from sqlalchemy import and_
from sqlalchemy.sql.expression import func
from dataclasses import dataclass
import dataclasses
from pandas import Timestamp
from app.interfaces import DataClassMixin


@dataclass
class DailyWeeklyTickerQuoteRow(DataClassMixin):
    symbol: str
    date: datetime.date
    open: float
    high: float
    low: float
    close: float
    volume: float


meta_metadata = MetaData()
security = Table(
    'security',
    meta_metadata,
    Column('id', INTEGER, primary_key=True, autoincrement=True),
    Column('symbol', TEXT, index=True),
    Column('name', TEXT, nullable=False),
    Column('exchange', TEXT, nullable=False),
    Column('asset_class', TEXT, nullable=False),
    Column('currency', TEXT, nullable=False, default='USD'),
    Column('country', TEXT, nullable=False),
    Column('sector', TEXT),
    Column('industry', TEXT),
    Column('isin', TEXT, unique=True),
    Column('cusip', TEXT, unique=True),
    Column('ipo_date', DATE),
    Column('is_active', BOOLEAN, default=True),
    Column('created_at', TIMESTAMP, default=text('CURRENT_TIMESTAMP')),
    Column('updated_at', TIMESTAMP, default=text('CURRENT_TIMESTAMP')),
    UniqueConstraint('symbol', 'exchange', name='uk-symbol-exchange')
)

sync_log = Table(
    'sync_log',
    meta_metadata,
    Column('for_date', DATE, primary_key=True),
    Column('run_time', DATETIME, primary_key=True),
    Column('status', TEXT),
)

def create_metadata_tables(engine: Engine):
    meta_metadata.create_all(engine, checkfirst=True)

daily_weekly_metadata = MetaData()

def create_daily_weekly_tables(engine: Engine):
    daily_weekly_metadata.create_all(engine)


adjusted_daily_price = Table(
    'adjusted_daily_price',
    daily_weekly_metadata,
    Column('symbol', TEXT, primary_key=True),
    Column('date', DATE, primary_key=True),
    Column('open', REAL),
    Column('high', REAL),
    Column('low', REAL),
    Column('close', REAL),
    Column('dividends', REAL),
    Column('splits', REAL),
    Column('volume', INTEGER),
)


adjusted_weekly_price = Table(
    'adjusted_weekly_price',
    daily_weekly_metadata,
    Column('symbol', TEXT, primary_key=True),
    Column('date', DATE, primary_key=True),
    Column('open', REAL),
    Column('high', REAL),
    Column('low', REAL),
    Column('close', REAL),
    Column('dividends', REAL),
    Column('splits', REAL),
    Column('volume', INTEGER),
)


ticker = Table(
    'ticker',
    daily_weekly_metadata,
    Column('symbol', TEXT, primary_key=True),
    Column('date', DATE, primary_key=True),
    Column('open', REAL),
    Column('high', REAL),
    Column('low', REAL),
    Column('close', REAL),
    Column('dividends', REAL),
    Column('splits', REAL),
    Column('volume', INTEGER),
)


intra_day_5m_metadata = MetaData()
adjusted_5m_price = Table(
    'adjusted_5m_price',
    intra_day_5m_metadata,
    Column('symbol', TEXT, primary_key=True),
    Column('timestamp', INTEGER, primary_key=True),
    Column('open', REAL),
    Column('high', REAL),
    Column('low', REAL),
    Column('close', REAL),
    Column('dividends', REAL),
    Column('splits', REAL),
    Column('volume', INTEGER),
)


intra_day_30m_metadata = MetaData()
adjusted_30m_price = Table(
    'adjusted_30m_price',
    intra_day_30m_metadata,
    Column('symbol', TEXT, primary_key=True),
    Column('timestamp', INTEGER, primary_key=True),
    Column('open', REAL),
    Column('high', REAL),
    Column('low', REAL),
    Column('close', REAL),
    Column('dividends', REAL),
    Column('splits', REAL),
    Column('volume', INTEGER),
)

fundamental_metadata = MetaData()
balance_sheet = Table(
    "balance_sheet", fundamental_metadata,
    Column("id", INTEGER, primary_key=True),  # Auto-increment primary key
    Column("security_id", INTEGER, nullable=False),  # security id as in metadata db
    Column("as_of_date", DATE, nullable=False),  # Reporting date of the balance sheet
    Column("period_type", TEXT),  # Quarterly or annual data
    Column("currency_code", TEXT),  # Currency used in reporting (e.g., USD)

    Column("accounts_payable", REAL),  # Amount owed to suppliers and vendors
    Column("accounts_receivable", REAL),  # Money owed to the company by customers
    Column("accum_depreciation", REAL),  # Total depreciation of assets to date
    Column("afs_securities", REAL),  # Investments classified as available for sale
    Column("capital_lease_oblig", REAL),  # Long-term lease obligations under capital leases
    Column("capital_stock", REAL),  # Par value of issued capital stock
    Column("cash_equiv", REAL),  # Highly liquid investments easily convertible to cash
    Column("cash_and_st_invest", REAL),  # Combined value of cash and short-term investments
    Column("cash_financial", REAL),  # Cash and equivalents from financial instruments
    Column("commercial_paper", REAL),  # Short-term unsecured promissory notes
    Column("common_stock", REAL),  # Value of common stock issued
    Column("common_equity", REAL),  # Total equity attributable to common shareholders
    Column("current_assets", REAL),  # Total assets expected to be used/sold within a year
    Column("current_lease_oblig", REAL),  # Lease obligations due within one year
    Column("current_debt", REAL),  # Short-term borrowings or current portion of long-term debt
    Column("current_debt_lease_oblig", REAL),  # Combined short-term debt and leases
    Column("current_deferred_liab", REAL),  # Short-term deferred liabilities
    Column("current_deferred_rev", REAL),  # Deferred revenue expected to be recognized within a year
    Column("current_liabilities", REAL),  # Obligations due within one year
    Column("gains_losses_ret_earnings", REAL),  # Unrealized gains/losses bypassing retained earnings
    Column("gross_ppe", REAL),  # Total value of property, plant, and equipment before depreciation
    Column("income_tax_payable", REAL),  # Taxes owed to tax authorities
    Column("inventory", REAL),  # Value of raw materials, work-in-progress, and finished goods
    Column("invested_capital", REAL),  # Total capital invested in the company
    Column("invest_fin_assets", REAL),  # Investments in financial instruments
    Column("investments_advances", REAL),  # Investments and loans to subsidiaries/affiliates
    Column("land_improvements", REAL),  # Value of land and land improvements
    Column("leases", REAL),  # Total lease obligations
    Column("lt_lease_oblig", REAL),  # Lease obligations due after one year
    Column("long_term_debt", REAL),  # Loans and financial obligations lasting over one year
    Column("lt_debt_lease_oblig", REAL),  # Combined long-term debt and lease obligations
    Column("machinery_equipment", REAL),  # Value of machinery, furniture, and equipment
    Column("net_debt", REAL),  # Total debt minus cash and cash equivalents
    Column("net_ppe", REAL),  # Property, plant, and equipment after depreciation
    Column("net_tangible_assets", REAL),  # Total tangible assets minus liabilities
    Column("nca_deferred_assets", REAL),  # Non-current deferred assets
    Column("nca_deferred_tax_assets", REAL),  # Deferred tax assets expected to be used in future years
    Column("ordinary_shares", REAL),  # Number of ordinary shares outstanding
    Column("other_curr_assets", REAL),  # Miscellaneous short-term assets
    Column("other_curr_borrowings", REAL),  # Other forms of current borrowing
    Column("other_curr_liab", REAL),  # Other miscellaneous current liabilities
    Column("other_equity_adj", REAL),  # Other adjustments to equity
    Column("other_investments", REAL),  # Miscellaneous investments not elsewhere classified
    Column("other_nca", REAL),  # Other non-current assets
    Column("other_non_curr_liab", REAL),  # Other long-term liabilities
    Column("other_properties", REAL),  # Properties not classified as PPE
    Column("other_receivables", REAL),  # Receivables not classified as accounts receivable
    Column("other_st_investments", REAL),  # Miscellaneous short-term investments
    Column("payables", REAL),  # Amounts owed, including trade and non-trade payables
    Column("payables_accrued_exp", REAL),  # Total of payables and accrued expenses
    Column("properties", REAL),  # Total value of real estate or property held
    Column("receivables", REAL),  # All money owed to the company (includes AR and others)
    Column("retained_earnings", REAL),  # Cumulative net income not paid as dividends
    Column("shares_issued", REAL),  # Total shares issued to shareholders
    Column("stockholders_equity", REAL),  # Total equity owned by shareholders
    Column("tangible_book_value", REAL),  # Book value excluding intangible assets
    Column("total_assets", REAL),  # Sum of all assets (current + non-current)
    Column("total_capitalization", REAL),  # Debt + shareholder equity
    Column("total_debt", REAL),  # All short-term and long-term debt
    Column("total_equity_with_minor", REAL),  # Total equity including minority interest
    Column("total_liab_no_minor", REAL),  # Total liabilities excluding minority interest
    Column("total_non_curr_assets", REAL),  # Assets not expected to convert within one year
    Column("total_non_curr_liab_no_minor", REAL),  # Long-term liabilities excluding minority interest
    Column("total_tax_payable", REAL),  # All current and deferred tax obligations
    Column("trade_payables_non_curr", REAL),  # Trade payables due beyond one year
    Column("treasury_shares", REAL),  # Shares repurchased and held by the company
    Column("working_capital", REAL),  # Current assets minus current liabilities
)

income_statement = Table(
    "income_statement", fundamental_metadata,
    Column("id", INTEGER, primary_key=True),  # Auto-increment primary key
    Column("security_id", INTEGER, nullable=False),  # security id as in metadata db
    Column("as_of_date", DATE, nullable=False),  # Reporting date of the income statement
    Column("period_type", TEXT),  # Reporting period type: annual or quarterly
    Column("currency_code", TEXT),  # Currency of the financial report

    Column("basic_average_shares", REAL),  # Weighted average of basic shares outstanding
    Column("basic_eps", REAL),  # Earnings per share using basic shares
    Column("cost_of_revenue", REAL),  # Direct costs attributable to goods/services sold
    Column("diluted_average_shares", REAL),  # Weighted average of diluted shares outstanding
    Column("diluted_eps", REAL),  # Earnings per share using diluted shares
    Column("diluted_net_income_to_common_stockholders", REAL),  # Net income available to common shareholders, diluted

    Column("ebit", REAL),  # Earnings Before Interest and Taxes
    Column("ebitda", REAL),  # Earnings Before Interest, Taxes, Depreciation, and Amortization
    Column("gross_profit", REAL),  # Revenue minus cost of revenue

    Column("interest_expense", REAL),  # Total interest expenses incurred
    Column("interest_expense_non_operating", REAL),  # Interest expense not related to core business
    Column("interest_income", REAL),  # Total interest income earned
    Column("interest_income_non_operating", REAL),  # Interest income not related to core operations

    Column("net_income", REAL),  # Final profit after all expenses and taxes
    Column("net_income_common_stockholders", REAL),  # Net income attributable to common shareholders
    Column("net_income_continuous_operations", REAL),  # Net income from ongoing business operations

    Column("net_income_from_cont_and_discontinued_operation", REAL),  # Combined income from continuing and discontinued operations
    Column("net_income_cont_operation_net_minority_interest", REAL),  # Net income from continuing operations after minority interest
    Column("net_income_incl_noncontrolling_interests", REAL),  # Net income including minority interests

    Column("net_interest_income", REAL),  # Interest income minus interest expense
    Column("net_non_operating_interest_income_expense", REAL),  # Net interest from non-operating activities

    Column("normalized_ebitda", REAL),  # Adjusted EBITDA excluding irregular items
    Column("normalized_income", REAL),  # Adjusted net income excluding irregular items

    Column("operating_expense", REAL),  # Total operating expenses
    Column("operating_income", REAL),  # Earnings from core operations
    Column("operating_revenue", REAL),  # Revenue from primary business activities

    Column("other_income_expense", REAL),  # Miscellaneous income and expenses
    Column("other_non_operating_income_expenses", REAL),  # Non-operating miscellaneous income/expenses

    Column("pretax_income", REAL),  # Earnings before tax
    Column("reconciled_cost_of_revenue", REAL),  # Adjusted cost of revenue
    Column("reconciled_depreciation", REAL),  # Adjusted depreciation and amortization

    Column("research_and_development", REAL),  # R&D expenses
    Column("selling_general_and_administration", REAL),  # SG&A expenses

    Column("tax_effect_of_unusual_items", REAL),  # Tax effects of one-time items
    Column("tax_provision", REAL),  # Total taxes provided for
    Column("tax_rate_for_calcs", REAL),  # Effective tax rate used in calculations

    Column("total_expenses", REAL),  # Total costs and expenses
    Column("total_operating_income_as_reported", REAL),  # Operating income before adjustments
    Column("total_revenue", REAL),  # Total revenue from all sources
)


def create_intra_day_5m_tables(engine: Engine):
    intra_day_5m_metadata.create_all(engine)

def create_intra_day_30m_tables(engine: Engine):
    intra_day_30m_metadata.create_all(engine)


