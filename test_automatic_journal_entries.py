"""
Tests para el servicio de asientos contables automáticos
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from apps.invoicing.models import Invoice, InvoiceLine, Customer
from apps.companies.models import Company, PaymentMethod
from apps.accounting.models import ChartOfAccounts, AccountType, JournalEntry, JournalEntryLine
from apps.accounting.services import AutomaticJournalEntryService

User = get_user_model()


class AutomaticJournalEntryServiceTest(TestCase):
    """Tests para el servicio de asientos contables automáticos"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        # Usuario
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        # Empresa
        self.company = Company.objects.create(
            identification='1234567890001',
            legal_name='Test Company S.A.',
            trade_name='Test Company'
        )
        
        # Cliente
        self.customer = Customer.objects.create(
            company=self.company,
            customer_type='natural',
            identification='1234567890',
            trade_name='Cliente Test',
            legal_name='Cliente Test Nombre Legal',
            address='Dirección Test 123'
        )
        
        # Tipos de cuenta
        self.asset_type = AccountType.objects.create(
            code='ASSET',
            name='Activo'
        )
        
        self.income_type = AccountType.objects.create(
            code='INCOME',
            name='Ingresos'
        )
        
        self.liability_type = AccountType.objects.create(
            code='LIABILITY',
            name='Pasivo'
        )
        
        # Cuentas contables
        self.caja_account = ChartOfAccounts.objects.create(
            company=self.company,
            code='1.1.01.01',
            name='CAJA GENERAL',
            account_type=self.asset_type,
            level=4,
            accepts_movement=True,
            is_detail=True
        )
        
        self.sales_account = ChartOfAccounts.objects.create(
            company=self.company,
            code='4.1.01',
            name='VENTAS',
            account_type=self.income_type,
            level=3,
            accepts_movement=True,
            is_detail=True
        )
        
        self.iva_15_account = ChartOfAccounts.objects.create(
            company=self.company,
            code='2.1.01.01.03.01',
            name='IVA COBRADO EN VENTAS 15%',
            account_type=self.liability_type,
            level=6,
            accepts_movement=True,
            is_detail=True
        )
        
        # Forma de pago
        self.payment_method = PaymentMethod.objects.create(
            name='EFECTIVO',
            is_active=True
        )
    
    def test_create_journal_entry_success(self):
        """Test creación exitosa de asiento contable"""
        # Crear factura
        invoice = Invoice.objects.create(
            company=self.company,
            customer=self.customer,
            account=self.caja_account,
            payment_form=self.payment_method,
            date='2025-01-01',
            subtotal=Decimal('100.00'),
            tax_amount=Decimal('15.00'),
            total=Decimal('115.00'),
            status='sent',
            created_by=self.user
        )
        
        # Crear línea de factura
        invoice_line = InvoiceLine.objects.create(
            invoice=invoice,
            description='Producto Test',
            quantity=Decimal('1.00'),
            unit_price=Decimal('100.00'),
            discount=Decimal('0.00'),
            iva_rate=Decimal('15.00'),
            line_total=Decimal('115.00')
        )
        
        # Crear asiento
        journal_entry, created = AutomaticJournalEntryService.create_journal_entry_from_invoice(invoice)
        
        # Verificaciones
        self.assertTrue(created, "El asiento debería haberse creado")
        self.assertIsNotNone(journal_entry, "El asiento no debería ser None")
        self.assertEqual(journal_entry.company, self.company)
        self.assertEqual(journal_entry.reference, f'FAC-{invoice.id}')
        self.assertEqual(journal_entry.total_debit, Decimal('115.00'))
        self.assertEqual(journal_entry.total_credit, Decimal('115.00'))
        self.assertTrue(journal_entry.is_balanced, "El asiento debería estar balanceado")
        
        # Verificar líneas del asiento
        lines = journal_entry.lines.all()
        self.assertEqual(lines.count(), 3, "Debería tener 3 líneas (DEBE + 2 HABER)")
        
        # Línea DEBE (Caja)
        debit_line = lines.filter(debit__gt=0).first()
        self.assertIsNotNone(debit_line)
        self.assertEqual(debit_line.account, self.caja_account)
        self.assertEqual(debit_line.debit, Decimal('115.00'))
        self.assertEqual(debit_line.credit, Decimal('0.00'))
        
        # Línea HABER (Ventas)
        sales_line = lines.filter(account=self.sales_account).first()
        self.assertIsNotNone(sales_line)
        self.assertEqual(sales_line.debit, Decimal('0.00'))
        self.assertEqual(sales_line.credit, Decimal('100.00'))
        
        # Línea HABER (IVA)
        iva_line = lines.filter(account=self.iva_15_account).first()
        self.assertIsNotNone(iva_line)
        self.assertEqual(iva_line.debit, Decimal('0.00'))
        self.assertEqual(iva_line.credit, Decimal('15.00'))
    
    def test_duplicate_journal_entry_prevention(self):
        """Test prevención de asientos duplicados"""
        # Crear factura
        invoice = Invoice.objects.create(
            company=self.company,
            customer=self.customer,
            account=self.caja_account,
            payment_form=self.payment_method,
            date='2025-01-01',
            subtotal=Decimal('100.00'),
            tax_amount=Decimal('15.00'),
            total=Decimal('115.00'),
            status='sent',
            created_by=self.user
        )
        
        # Crear línea de factura
        InvoiceLine.objects.create(
            invoice=invoice,
            description='Producto Test',
            quantity=Decimal('1.00'),
            unit_price=Decimal('100.00'),
            iva_rate=Decimal('15.00'),
            line_total=Decimal('115.00')
        )
        
        # Primer intento - debería crear
        journal_entry1, created1 = AutomaticJournalEntryService.create_journal_entry_from_invoice(invoice)
        self.assertTrue(created1)
        self.assertIsNotNone(journal_entry1)
        
        # Segundo intento - NO debería crear
        journal_entry2, created2 = AutomaticJournalEntryService.create_journal_entry_from_invoice(invoice)
        self.assertFalse(created2)
        self.assertEqual(journal_entry1.id, journal_entry2.id)
        
        # Verificar que solo existe un asiento
        count = JournalEntry.objects.filter(reference=f'FAC-{invoice.id}').count()
        self.assertEqual(count, 1)
    
    def test_reverse_journal_entry(self):
        """Test creación de asiento de reversión"""
        # Crear factura con asiento
        invoice = Invoice.objects.create(
            company=self.company,
            customer=self.customer,
            account=self.caja_account,
            payment_form=self.payment_method,
            date='2025-01-01',
            subtotal=Decimal('100.00'),
            tax_amount=Decimal('15.00'),
            total=Decimal('115.00'),
            status='sent',
            created_by=self.user
        )
        
        InvoiceLine.objects.create(
            invoice=invoice,
            description='Producto Test',
            quantity=Decimal('1.00'),
            unit_price=Decimal('100.00'),
            iva_rate=Decimal('15.00'),
            line_total=Decimal('115.00')
        )
        
        # Crear asiento original
        original_entry, _ = AutomaticJournalEntryService.create_journal_entry_from_invoice(invoice)
        
        # Crear reversión
        reverse_entry, created = AutomaticJournalEntryService.reverse_journal_entry(invoice)
        
        # Verificaciones
        self.assertTrue(created)
        self.assertIsNotNone(reverse_entry)
        self.assertEqual(reverse_entry.reference, f'REV-FAC-{invoice.id}')
        self.assertEqual(reverse_entry.total_debit, original_entry.total_debit)
        self.assertEqual(reverse_entry.total_credit, original_entry.total_credit)
        
        # Verificar que las líneas están invertidas
        original_lines = original_entry.lines.all()
        reverse_lines = reverse_entry.lines.all()
        
        self.assertEqual(original_lines.count(), reverse_lines.count())
        
        for orig_line in original_lines:
            # Buscar línea correspondiente en reversión
            rev_line = reverse_lines.filter(account=orig_line.account).first()
            self.assertIsNotNone(rev_line)
            
            # Verificar que débito y crédito están intercambiados
            self.assertEqual(orig_line.debit, rev_line.credit)
            self.assertEqual(orig_line.credit, rev_line.debit)
    
    def test_validation_missing_data(self):
        """Test validación con datos faltantes"""
        # Factura sin cuenta
        invoice = Invoice.objects.create(
            company=self.company,
            customer=self.customer,
            account=None,  # Sin cuenta
            payment_form=self.payment_method,
            date='2025-01-01',
            subtotal=Decimal('100.00'),
            total=Decimal('115.00'),
            status='sent',
            created_by=self.user
        )
        
        # No debería crear asiento
        journal_entry, created = AutomaticJournalEntryService.create_journal_entry_from_invoice(invoice)
        
        self.assertFalse(created)
        self.assertIsNone(journal_entry)
    
    def test_iva_breakdown_calculation(self):
        """Test cálculo correcto del desglose de IVA"""
        invoice = Invoice.objects.create(
            company=self.company,
            customer=self.customer,
            account=self.caja_account,
            payment_form=self.payment_method,
            date='2025-01-01',
            subtotal=Decimal('200.00'),
            tax_amount=Decimal('25.00'),
            total=Decimal('225.00'),
            status='sent',
            created_by=self.user
        )
        
        # Línea con IVA 15%
        InvoiceLine.objects.create(
            invoice=invoice,
            description='Producto 15% IVA',
            quantity=Decimal('1.00'),
            unit_price=Decimal('100.00'),
            iva_rate=Decimal('15.00'),
            line_total=Decimal('115.00')
        )
        
        # Línea con IVA 5%
        InvoiceLine.objects.create(
            invoice=invoice,
            description='Producto 5% IVA',
            quantity=Decimal('1.00'),
            unit_price=Decimal('100.00'),
            iva_rate=Decimal('5.00'),
            line_total=Decimal('105.00')
        )
        
        # Crear cuenta IVA 5%
        iva_5_account = ChartOfAccounts.objects.create(
            company=self.company,
            code='2.1.01.01.03.02',
            name='IVA COBRADO EN VENTAS 5%',
            account_type=self.liability_type,
            level=6,
            accepts_movement=True,
            is_detail=True
        )
        
        # Calcular desglose
        iva_breakdown = AutomaticJournalEntryService._calculate_iva_breakdown(invoice)
        
        # Verificaciones
        self.assertEqual(iva_breakdown[Decimal('15.00')], Decimal('15.00'))
        self.assertEqual(iva_breakdown[Decimal('5.00')], Decimal('5.00'))
        
        print("✅ Tests de asientos contables automáticos completados")