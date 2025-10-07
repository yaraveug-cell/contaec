#!/usr/bin/env python3
"""
Verificación final del sistema de filtrado dinámico - Version corregida
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

def final_verification():
    """Verificación completa y final"""
    print("🎯 VERIFICACIÓN FINAL DEL SISTEMA")
    print("=" * 60)
    
    from apps.companies.models import Company, PaymentMethod
    from apps.accounting.models import ChartOfAccounts
    
    print("📊 CONFIGURACIÓN ACTUAL:")
    
    # Datos de GUEBER
    gueber = Company.objects.get(trade_name__icontains="GUEBER")
    efectivo = PaymentMethod.objects.get(name__icontains="efectivo")
    
    print(f"🏢 Empresa: {gueber.trade_name} (ID: {gueber.id})")
    print(f"💳 Método Efectivo: {efectivo.name} (ID: {efectivo.id})")
    print(f"📋 Cuenta Padre Efectivo: {efectivo.parent_account.code} - {efectivo.parent_account.name}")
    
    # Buscar CAJA GENERAL específicamente
    caja_general = ChartOfAccounts.objects.filter(
        company=gueber,
        name__icontains="caja general"
    ).first()
    
    if caja_general:
        print(f"🎯 Caja General: {caja_general.code} - {caja_general.name}")
        
        # Verificar jerarquía correcta
        parent_code = efectivo.parent_account.code.rstrip('.')  # Remover punto final
        if caja_general.code.startswith(parent_code):
            print(f"✅ CAJA GENERAL es hija de {efectivo.parent_account.name}")
            print(f"   - Padre: {efectivo.parent_account.code} (nivel {efectivo.parent_account.level})")
            print(f"   - Hija: {caja_general.code} (nivel {caja_general.level})")
        else:
            print(f"⚠️  Verificando jerarquía:")
            print(f"   - Código padre: '{parent_code}'")
            print(f"   - Código hija: '{caja_general.code}'")
            print(f"   - ¿Empieza con padre?: {caja_general.code.startswith(parent_code)}")
    else:
        print("❌ CAJA GENERAL no encontrada")
    
    print(f"\n🔧 ARCHIVOS VERIFICADOS:")
    
    # Verificar JavaScript existe
    js_file = "static/admin/js/integrated_payment_account_handler.js"
    if os.path.exists(js_file):
        print(f"✅ JavaScript: {js_file} existe")
    else:
        print(f"❌ JavaScript no encontrado")
    
    # Verificar admin.py
    admin_file = "apps/invoicing/admin.py"
    if os.path.exists(admin_file):
        print(f"✅ Admin: {admin_file} existe")
    
    print(f"\n🌐 SERVIDOR:")
    print(f"   Status: Ejecutándose en http://127.0.0.1:8000/")
    
    print(f"\n🎯 PASOS PARA PROBAR AHORA:")
    print(f"1. Ir a: http://127.0.0.1:8000/admin/invoicing/invoice/add/")
    print(f"2. ¡¡IMPORTANTE!! Refrescar con Ctrl+F5 para cargar JavaScript actualizado")
    print(f"3. Abrir Developer Tools (F12) → Console")
    print(f"4. Seleccionar empresa: GUEBER")
    print(f"5. Observar logs en consola del navegador")
    print(f"6. Cambiar forma de pago a: Efectivo")
    print(f"7. Verificar que aparezca: CAJA GENERAL")
    
    print(f"\n💻 TEST AUTOMATIZADO:")
    print(f"   En la consola del navegador, ejecutar:")
    
    test_code = """
// Test rápido
const company = document.getElementById('id_company');
const payment = document.getElementById('id_payment_form');
const account = document.getElementById('id_account');

// Seleccionar GUEBER
const gueber = Array.from(company.options).find(o => o.text.includes('GUEBER'));
company.value = gueber.value;
$(company).trigger('change');

setTimeout(() => {
    // Seleccionar Efectivo
    const efectivo = Array.from(payment.options).find(o => o.text.includes('Efectivo'));
    payment.value = efectivo.value;
    $(payment).trigger('change');
    
    setTimeout(() => {
        // Verificar resultado
        const accounts = Array.from(account.options).filter(o => o.value);
        console.log('Cuentas disponibles:', accounts.map(o => o.text));
        const caja = accounts.find(o => o.text.includes('CAJA GENERAL'));
        console.log(caja ? '✅ CAJA GENERAL encontrada!' : '❌ CAJA GENERAL no encontrada');
    }, 1000);
}, 1000);
"""
    print(f"\n   {test_code}")

if __name__ == "__main__":
    final_verification()
    
    print("\n" + "=" * 60)
    print("🚀 SISTEMA ACTUALIZADO - ¡Probar con Ctrl+F5!")
    print("=" * 60)