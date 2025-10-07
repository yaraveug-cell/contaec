from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class AccountTypeViewSet(viewsets.ModelViewSet):
    """ViewSet para tipos de cuenta"""
    pass


class ChartOfAccountsViewSet(viewsets.ModelViewSet):
    """ViewSet para plan de cuentas"""
    pass


class JournalEntryViewSet(viewsets.ModelViewSet):
    """ViewSet para asientos contables"""
    pass


class FiscalYearViewSet(viewsets.ModelViewSet):
    """ViewSet para ejercicios fiscales"""
    pass


class BalanceSheetView(APIView):
    """Vista para balance general"""
    def get(self, request):
        return Response({"message": "Balance sheet endpoint"}, status=status.HTTP_200_OK)


class IncomeStatementView(APIView):
    """Vista para estado de resultados"""
    def get(self, request):
        return Response({"message": "Income statement endpoint"}, status=status.HTTP_200_OK)


class TrialBalanceView(APIView):
    """Vista para balance de comprobación"""
    def get(self, request):
        return Response({"message": "Trial balance endpoint"}, status=status.HTTP_200_OK)


class GeneralLedgerView(APIView):
    """Vista para libro mayor"""
    def get(self, request):
        return Response({"message": "General ledger endpoint"}, status=status.HTTP_200_OK)