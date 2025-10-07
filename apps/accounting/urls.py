from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .ajax_views import get_company_accounts
from .balance_views import balance_sheet_view, balance_sheet_data, export_balance_sheet_pdf
from .trial_balance_views import trial_balance_view, trial_balance_data, export_trial_balance_pdf
from .general_ledger_views import general_ledger_view, general_ledger_accounts, general_ledger_data, export_general_ledger_pdf
from .income_statement_views import income_statement_view, income_statement_data, export_income_statement_pdf
from .journal_book_views import journal_book_view, journal_book_data, export_journal_book_pdf
from .cash_flow_views import cash_flow_view, cash_flow_data, export_cash_flow_pdf

router = DefaultRouter()
router.register(r'account-types', views.AccountTypeViewSet, basename='accounttype')
router.register(r'chart-of-accounts', views.ChartOfAccountsViewSet, basename='chartofaccounts')
router.register(r'journal-entries', views.JournalEntryViewSet, basename='journalentry')
router.register(r'fiscal-years', views.FiscalYearViewSet, basename='fiscalyear')

urlpatterns = [
    path('', include(router.urls)),
    path('balance-sheet/', balance_sheet_view, name='balance_sheet'),
    path('balance-sheet/data/', balance_sheet_data, name='balance_sheet_data'),
    path('balance-sheet/export-pdf/', export_balance_sheet_pdf, name='export_balance_sheet_pdf'),
    path('trial-balance-report/', trial_balance_view, name='trial_balance_report'),
    path('trial-balance-data/', trial_balance_data, name='trial_balance_data'),
    path('trial-balance-pdf/', export_trial_balance_pdf, name='export_trial_balance_pdf'),
    path('general-ledger-report/', general_ledger_view, name='general_ledger_report'),
    path('general-ledger-accounts/', general_ledger_accounts, name='general_ledger_accounts'),
    path('general-ledger-data/', general_ledger_data, name='general_ledger_data'),
    path('general-ledger-pdf/', export_general_ledger_pdf, name='export_general_ledger_pdf'),
    path('income-statement-report/', income_statement_view, name='income_statement_report'),
    path('income-statement-data/', income_statement_data, name='income_statement_data'),
    path('export-income-statement-pdf/', export_income_statement_pdf, name='export_income_statement_pdf'),
    path('journal-book-report/', journal_book_view, name='journal_book_report'),
    path('journal-book-data/', journal_book_data, name='journal_book_data'),
    path('export-journal-book-pdf/', export_journal_book_pdf, name='export_journal_book_pdf'),
    path('cash-flow-report/', cash_flow_view, name='cash_flow_report'),
    path('cash-flow-data/', cash_flow_data, name='cash_flow_data'),
    path('export-cash-flow-pdf/', export_cash_flow_pdf, name='export_cash_flow_pdf'),
    path('income-statement/', views.IncomeStatementView.as_view(), name='income-statement'),
    path('trial-balance/', views.TrialBalanceView.as_view(), name='trial-balance'),
    path('general-ledger/', views.GeneralLedgerView.as_view(), name='general-ledger'),
    path('get_company_accounts/', get_company_accounts, name='get_company_accounts'),
]