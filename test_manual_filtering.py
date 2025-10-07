#!/usr/bin/env python3
"""
Script para probar directamente el filtrado en vivo
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

def test_manual_filtering():
    """Probar manualmente el escenario específico"""
    print("🎯 PRUEBA ESPECÍFICA: GUEBER + EFECTIVO → CAJA GENERAL")
    print("=" * 60)
    
    from apps.companies.models import Company, PaymentMethod
    from apps.accounting.models import ChartOfAccounts
    
    # Obtener datos específicos
    try:
        gueber = Company.objects.get(trade_name__icontains="GUEBER")
        efectivo = PaymentMethod.objects.get(name__icontains="efectivo")
        
        print(f"🏢 Empresa: {gueber.trade_name} (ID: {gueber.id})")
        print(f"💳 Forma de Pago: {efectivo.name} (ID: {efectivo.id})")
        print(f"📋 Cuenta Padre del Efectivo: {efectivo.parent_account}")
        
        # Buscar las cuentas hijas específicamente
        if efectivo.parent_account:
            parent = efectivo.parent_account
            children = ChartOfAccounts.objects.filter(
                company=gueber,
                code__startswith=parent.code,
                level=parent.level + 1,
                accepts_movement=True
            ).order_by('code')
            
            print(f"\n🎯 RESULTADO ESPERADO:")
            print(f"   Cuando selecciones:")
            print(f"   - Empresa: GUEBER")
            print(f"   - Forma de Pago: Efectivo")
            print(f"   El campo Cuenta debería mostrar:")
            
            for child in children:
                print(f"   ✅ {child.code} - {child.name}")
                
        # Simular configuración JavaScript
        print(f"\n🔧 CONFIGURACIÓN JAVASCRIPT:")
        print(f"   companyPaymentMethods['{gueber.id}'] = {{")
        print(f"     'id': {gueber.payment_method.id if gueber.payment_method else 'null'},")
        print(f"     'name': '{gueber.payment_method.name if gueber.payment_method else 'Sin configurar'}',")
        print(f"     'company_name': '{gueber.trade_name}'")
        print(f"   }}")
        
        print(f"\n   paymentMethodAccounts['{efectivo.id}'] = {{")
        print(f"     'method_name': '{efectivo.name}',")
        print(f"     'parent_account': {{")
        print(f"       'id': {efectivo.parent_account.id},")
        print(f"       'code': '{efectivo.parent_account.code}',")
        print(f"       'name': '{efectivo.parent_account.name}',")
        print(f"       'level': {efectivo.parent_account.level}")
        print(f"     }}")
        print(f"   }}")
        
        # Verificar lógica de filtrado
        print(f"\n🧪 LÓGICA DE FILTRADO:")
        print(f"   1. Usuario selecciona Empresa GUEBER (ID: {gueber.id})")
        print(f"   2. Sistema establece forma de pago por defecto: {gueber.payment_method.name if gueber.payment_method else 'Ninguna'}")
        print(f"   3. Usuario CAMBIA forma de pago a: Efectivo (ID: {efectivo.id})")
        print(f"   4. Sistema busca cuenta padre de Efectivo: {efectivo.parent_account.code}")
        print(f"   5. Sistema filtra cuentas que empiecen con: {efectivo.parent_account.code}")
        print(f"   6. RESULTADO: Muestra solo las cuentas hijas encontradas arriba")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def create_browser_test():
    """Crear un test que se puede ejecutar en el navegador"""
    test_js = """
// Test para ejecutar en la consola del navegador
console.log('🧪 INICIANDO TEST DE FILTRADO DINÁMICO');

// 1. Seleccionar GUEBER
const companyField = document.getElementById('id_company');
const gueberOption = Array.from(companyField.options).find(opt => opt.text.includes('GUEBER'));
if (gueberOption) {
    companyField.value = gueberOption.value;
    $(companyField).trigger('change');
    console.log('✅ Empresa GUEBER seleccionada');
} else {
    console.log('❌ Empresa GUEBER no encontrada');
}

// Esperar un momento para que se procesen los cambios
setTimeout(() => {
    // 2. Cambiar a Efectivo
    const paymentField = document.getElementById('id_payment_form');
    const efectivoOption = Array.from(paymentField.options).find(opt => opt.text.includes('Efectivo'));
    if (efectivoOption) {
        paymentField.value = efectivoOption.value;
        $(paymentField).trigger('change');
        console.log('✅ Forma de pago Efectivo seleccionada');
        
        // Verificar resultado después de un momento
        setTimeout(() => {
            const accountField = document.getElementById('id_account');
            const accounts = Array.from(accountField.options).filter(opt => opt.value !== '');
            console.log('📋 Cuentas disponibles después del filtrado:', accounts.map(opt => opt.text));
            
            const cajaGeneral = accounts.find(opt => opt.text.includes('CAJA GENERAL'));
            if (cajaGeneral) {
                console.log('✅ ¡ÉXITO! CAJA GENERAL está disponible:', cajaGeneral.text);
            } else {
                console.log('❌ CAJA GENERAL no encontrada en las opciones filtradas');
            }
        }, 1000);
    } else {
        console.log('❌ Forma de pago Efectivo no encontrada');
    }
}, 1000);
"""
    
    with open('browser_test.js', 'w', encoding='utf-8') as f:
        f.write(test_js)
    
    print(f"\n📝 TEST PARA NAVEGADOR CREADO:")
    print(f"   1. Abrir http://127.0.0.1:8000/admin/invoicing/invoice/add/")
    print(f"   2. Abrir herramientas de desarrollador (F12)")
    print(f"   3. Ir a la pestaña Console")
    print(f"   4. Copiar y pegar el contenido del archivo 'browser_test.js'")
    print(f"   5. Presionar Enter para ejecutar")

if __name__ == "__main__":
    test_manual_filtering()
    create_browser_test()
    
    print("\n" + "=" * 60)
    print("🔧 DIAGNÓSTICO PARA FILTRADO MANUAL COMPLETADO")
    print("=" * 60)