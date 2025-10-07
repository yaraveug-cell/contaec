from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class CompanyViewSet(viewsets.ModelViewSet):
    """ViewSet para empresas"""
    pass


class CompanyTypeViewSet(viewsets.ModelViewSet):
    """ViewSet para tipos de empresa"""
    pass


class EconomicActivityViewSet(viewsets.ModelViewSet):
    """ViewSet para actividades económicas"""
    pass


class SwitchCompanyView(APIView):
    """Vista para cambiar de empresa"""
    def post(self, request, company_id):
        return Response({"message": f"Switched to company {company_id}"}, status=status.HTTP_200_OK)


class CurrentCompanyView(APIView):
    """Vista para obtener empresa actual"""
    def get(self, request):
        return Response({"message": "Current company endpoint"}, status=status.HTTP_200_OK)