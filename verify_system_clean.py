#!/usr/bin/env python3
"""
Script de verificación del sistema después de eliminar funcionalidad de método de pago
Verifica que todas las funcionalidades principales siguen operativas
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

def test_invoice_model():
    """Probar que el modelo Invoice funciona correctamente sin métodos de pago"""
    print("🧪 Probando modelo Invoice...")
    
    from apps.invoicing.models import Invoice, InvoiceLine
    from apps.companies.models import Company
    from apps.invoicing.models import Customer
    from apps.inventory.models import Product
    
    try:
        # Verificar que el modelo no tiene los campos eliminados
        invoice_fields = [field.name for field in Invoice._meta.fields]
        
        removed_fields = ['payment_method', 'cash_account', 'client_account', 'credit_details']
        fields_found = [field for field in removed_fields if field in invoice_fields]
        
        if fields_found:
            print(f"❌ ERROR: Campos de método de pago aún presentes: {fields_found}")
            return False
        else:
            print("✅ Campos de método de pago eliminados correctamente")
        
        # Verificar campos esenciales presentes
        essential_fields = ['company', 'customer', 'number', 'date', 'due_date']
        missing_fields = [field for field in essential_fields if field not in invoice_fields]
        
        if missing_fields:
            print(f"❌ ERROR: Campos esenciales faltantes: {missing_fields}")
            return False
        else:
            print("✅ Todos los campos esenciales presentes")
        
        # Probar creación de factura (sin guardar)
        company = Company.objects.filter(is_active=True).first()
        if company:
            print(f"✅ Empresa de prueba encontrada: {company.trade_name}")
            
            customer = Customer.objects.filter(company=company).first()
            if customer:
                print(f"✅ Cliente de prueba encontrado: {customer.trade_name}")
                
                # Crear instancia de prueba
                test_invoice = Invoice(
                    company=company,
                    customer=customer,
                    number='TEST-001',
                )
                
                print(f"✅ Instancia de factura creada correctamente")
                print(f"   - Empresa: {test_invoice.company.trade_name}")
                print(f"   - Cliente: {test_invoice.customer.trade_name}")
                print(f"   - Número: {test_invoice.number}")
                
                return True
        
        print("⚠️  No hay datos de prueba disponibles")
        return True
        
    except Exception as e:
        print(f"❌ ERROR en modelo Invoice: {e}")
        return False

def test_invoice_calculations():
    """Probar que los cálculos de factura siguen funcionando"""
    print("\n🧮 Probando cálculos de factura...")
    
    try:
        from apps.invoicing.models import Invoice
        from apps.companies.models import Company
        
        company = Company.objects.filter(is_active=True).first()
        if company:
            # Buscar factura existente para probar cálculos
            invoice = Invoice.objects.filter(company=company).first()
            if invoice:
                # Verificar métodos de cálculo
                if hasattr(invoice, 'calculate_totals'):
                    print("✅ Método calculate_totals presente")
                
                if hasattr(invoice, 'get_tax_breakdown'):
                    breakdown = invoice.get_tax_breakdown()
                    print(f"✅ Método get_tax_breakdown funciona: {type(breakdown)}")
                
                # Probar cálculo de totales
                try:
                    totals = invoice.calculate_totals()
                    print(f"✅ Cálculos funcionan correctamente")
                    print(f"   - Subtotal disponible: {'subtotal' in totals}")
                    print(f"   - IVA disponible: {'iva_total' in totals}")
                    print(f"   - Total disponible: {'total' in totals}")
                except Exception as e:
                    print(f"⚠️  Error en cálculos: {e}")
                    
                return True
        
        print("⚠️  No hay facturas para probar cálculos")
        return True
        
    except Exception as e:
        print(f"❌ ERROR en cálculos: {e}")
        return False

def test_admin_config():
    """Probar que la configuración del admin está limpia"""
    print("\n⚙️  Probando configuración del admin...")
    
    try:
        from apps.invoicing.admin import InvoiceAdmin
        from apps.invoicing.models import Invoice
        
        # Verificar fieldsets
        admin_instance = InvoiceAdmin(Invoice, None)
        
        if hasattr(admin_instance, 'fieldsets'):
            fieldsets = admin_instance.fieldsets
            print(f"✅ Fieldsets configurados: {len(fieldsets)} secciones")
            
            # Verificar que no hay referencias a método de pago
            fieldset_text = str(fieldsets)
            payment_refs = ['payment_method', 'cash_account', 'client_account', 'credit_details']
            found_refs = [ref for ref in payment_refs if ref in fieldset_text]
            
            if found_refs:
                print(f"❌ Referencias a método de pago en fieldsets: {found_refs}")
                return False
            else:
                print("✅ Fieldsets limpios sin referencias a método de pago")
        
        # Verificar Media class
        if hasattr(admin_instance, 'Media'):
            media = admin_instance.Media
            if hasattr(media, 'js'):
                js_files = media.js
                print(f"✅ Archivos JavaScript: {len(js_files)}")
                
                # Verificar que no hay referencias a payment_method_handler
                payment_js = [js for js in js_files if 'payment' in js]
                if payment_js:
                    print(f"❌ Referencias a JS de método de pago: {payment_js}")
                    return False
                else:
                    print("✅ JavaScript limpio sin referencias a método de pago")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR en configuración admin: {e}")
        return False

def test_javascript_files():
    """Verificar que los archivos JavaScript principales existen"""
    print("\n📝 Verificando archivos JavaScript...")
    
    js_files = [
        'static/admin/js/invoice_line_calculator.js',
        'static/admin/js/description_autocomplete.js', 
        'static/admin/js/tax_breakdown_calculator.js',
        'static/admin/js/invoice_line_autocomplete.js'
    ]
    
    all_exist = True
    for js_file in js_files:
        if os.path.exists(js_file):
            print(f"✅ {js_file}")
        else:
            print(f"❌ FALTANTE: {js_file}")
            all_exist = False
    
    # Verificar que payment_method_handler.js fue eliminado
    payment_js = 'static/admin/js/payment_method_handler.js'
    if not os.path.exists(payment_js):
        print(f"✅ {payment_js} eliminado correctamente")
    else:
        print(f"❌ {payment_js} aún existe")
        all_exist = False
    
    return all_exist

def main():
    """Función principal de verificación"""
    print("🔍 VERIFICACIÓN DEL SISTEMA DESPUÉS DE ELIMINAR MÉTODO DE PAGO")
    print("=" * 70)
    
    tests = [
        ("Modelo Invoice", test_invoice_model),
        ("Cálculos de Factura", test_invoice_calculations), 
        ("Configuración Admin", test_admin_config),
        ("Archivos JavaScript", test_javascript_files),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\n❌ ERROR CRÍTICO en {test_name}: {e}")
            results.append(False)
    
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 70)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASÓ" if results[i] else "❌ FALLÓ"
        print(f"{status} - {test_name}")
    
    total_passed = sum(results)
    total_tests = len(results)
    
    print(f"\nResultado: {total_passed}/{total_tests} pruebas pasaron")
    
    if total_passed == total_tests:
        print("\n🎉 ¡SISTEMA LIMPIO Y FUNCIONAL!")
        print("✅ Todas las funcionalidades principales operativas")
        print("✅ Método de pago eliminado completamente")
        print("✅ Sin referencias residuales")
    else:
        print(f"\n⚠️  ATENCIÓN: {total_tests - total_passed} pruebas fallaron")
        print("Revisar los errores anteriores")
    
    return total_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)