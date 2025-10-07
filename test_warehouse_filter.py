#!/usr/bin/env python3
"""
Script para verificar que el filtro de bodegas funciona correctamente
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.companies.models import Company, CompanyUser
from apps.inventory.models import Warehouse, Stock
from apps.core.filters import UserCompanyWarehouseFilter
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
import sys

User = get_user_model()

def create_mock_request(user):
    """Crear un request mock con sesión"""
    factory = RequestFactory()
    request = factory.get('/admin/inventory/stock/')
    
    # Agregar middleware de sesión
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session.save()
    
    # Asignar usuario
    request.user = user
    
    # Simular datos de sesión (esto normalmente se hace en el middleware)
    if not user.is_superuser:
        user_companies = CompanyUser.objects.filter(
            user=user, 
            is_active=True
        ).values_list('company_id', flat=True)
        request.session['user_companies'] = list(user_companies)
    else:
        request.session['user_companies'] = 'all'
    
    return request

def test_warehouse_filter():
    print("=== PRUEBA DEL FILTRO DE BODEGAS POR EMPRESA ===\n")
    
    # Obtener usuarios
    try:
        admin_user = User.objects.get(email='admin@contaec.com')
        contador_user = User.objects.get(email='contador@comecuador.com')
    except User.DoesNotExist as e:
        print(f"❌ Error: Usuario no encontrado - {e}")
        return
    
    print("📋 ESTADO ACTUAL DEL SISTEMA")
    print("-" * 40)
    
    # Mostrar todas las empresas y bodegas
    companies = Company.objects.all()
    for company in companies:
        warehouses = Warehouse.objects.filter(company=company)
        print(f"🏢 {company.trade_name}:")
        for warehouse in warehouses:
            stock_count = Stock.objects.filter(warehouse=warehouse).count()
            print(f"   📦 {warehouse.name} ({warehouse.code}) - {stock_count} stocks")
    
    print(f"\n{'='*50}")
    print("🔐 PRUEBA DE FILTROS POR USUARIO")
    print("=" * 50)
    
    # Probar filtro para ADMIN (superuser)
    print(f"\n👨‍💼 USUARIO ADMIN (Superuser)")
    print("-" * 30)
    
    admin_request = create_mock_request(admin_user)
    filter_instance = UserCompanyWarehouseFilter(
        admin_request, 
        {}, 
        Stock, 
        None  # model_admin
    )
    
    admin_lookups = filter_instance.lookups(admin_request, None)
    print(f"Bodegas visibles para admin: {len(admin_lookups)}")
    for warehouse_id, warehouse_name in admin_lookups:
        print(f"   ✅ {warehouse_name}")
    
    # Probar filtro para CONTADOR
    print(f"\n👨‍💻 USUARIO CONTADOR (Usuario regular)")
    print("-" * 35)
    
    contador_request = create_mock_request(contador_user)
    
    # Verificar asignaciones del contador
    contador_companies = CompanyUser.objects.filter(user=contador_user, is_active=True)
    print("Empresas asignadas al contador:")
    for cu in contador_companies:
        print(f"   🏢 {cu.company.trade_name} (como {cu.get_role_display()})")
    
    filter_instance = UserCompanyWarehouseFilter(
        contador_request, 
        {}, 
        Stock, 
        None  # model_admin
    )
    
    contador_lookups = filter_instance.lookups(contador_request, None)
    print(f"\nBodegas visibles para contador: {len(contador_lookups)}")
    for warehouse_id, warehouse_name in contador_lookups:
        print(f"   ✅ {warehouse_name}")
    
    # Verificar que la restricción funciona
    print(f"\n{'='*50}")
    print("🎯 VERIFICACIÓN DE SEGURIDAD")
    print("=" * 50)
    
    total_warehouses = Warehouse.objects.count()
    admin_visible = len(admin_lookups)
    contador_visible = len(contador_lookups)
    
    print(f"📊 RESUMEN:")
    print(f"   Total de bodegas en sistema: {total_warehouses}")
    print(f"   Bodegas visibles para admin: {admin_visible}")
    print(f"   Bodegas visibles para contador: {contador_visible}")
    
    if admin_visible == total_warehouses:
        print(f"   ✅ Admin ve todas las bodegas (correcto)")
    else:
        print(f"   ❌ Admin no ve todas las bodegas (error)")
    
    if contador_visible < total_warehouses and contador_visible > 0:
        print(f"   ✅ Contador ve solo sus bodegas (correcto)")
    elif contador_visible == 0:
        print(f"   ⚠️ Contador no ve ninguna bodega")
    else:
        print(f"   ❌ Contador ve todas las bodegas (error de seguridad)")
    
    print(f"\n✅ PRUEBA COMPLETADA")

if __name__ == "__main__":
    test_warehouse_filter()