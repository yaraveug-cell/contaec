#!/usr/bin/env python3
"""
Script para poblar datos de clientes y productos para la empresa GUEBER
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.companies.models import Company
from apps.invoicing.models import Customer
from apps.inventory.models import Product, Category, Warehouse, Stock, StockMovement
from django.contrib.auth import get_user_model
from decimal import Decimal

def main():
    print("=== Poblando datos para GUEBER ===")
    
    # Obtener empresa GUEBER
    try:
        gueber = Company.objects.get(trade_name='GUEBER')
        print(f"✅ Empresa encontrada: {gueber.trade_name} (ID: {gueber.id})")
    except Company.DoesNotExist:
        print("❌ Empresa GUEBER no encontrada")
        return
    
    # Obtener usuario admin para las operaciones
    User = get_user_model()
    admin_user = User.objects.get(username='admin')
    
    # Crear bodega principal
    print("\n--- Creando bodega principal ---")
    warehouse, created = Warehouse.objects.get_or_create(
        code='PRIN',
        company=gueber,
        defaults={
            'name': 'Bodega Principal',
            'address': 'Av. Principal 123, Quito',
            'responsible': admin_user,
            'is_active': True
        }
    )
    status = "✅ Creada" if created else "ℹ️ Ya existe"
    print(f"{status}: {warehouse.name} ({warehouse.code})")
    
    # Crear categorías de productos
    print("\n--- Creando categorías de productos ---")
    categories_data = [
        {"name": "Electrodomésticos", "description": "Electrodomésticos para el hogar"},
        {"name": "Electrónicos", "description": "Dispositivos electrónicos y tecnología"},
        {"name": "Muebles", "description": "Muebles para hogar y oficina"},
        {"name": "Herramientas", "description": "Herramientas de trabajo y construcción"},
        {"name": "Deportes", "description": "Artículos deportivos y recreativos"},
        {"name": "Hogar", "description": "Artículos para el hogar y decoración"}
    ]
    
    categories = {}
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data["name"],
            company=gueber,
            defaults={"description": cat_data["description"]}
        )
        categories[cat_data["name"]] = category
        status = "✅ Creada" if created else "ℹ️ Ya existe"
        print(f"{status}: {category.name}")
    
    # Crear productos
    print("\n--- Creando productos ---")
    products_data = [
        # Electrodomésticos
        {"name": "Refrigeradora LG 500L", "category": "Electrodomésticos", "code": "REF001", 
         "price": Decimal("1250.00"), "cost": Decimal("980.00"), "stock": 15},
        {"name": "Lavadora Samsung 18kg", "category": "Electrodomésticos", "code": "LAV001", 
         "price": Decimal("890.00"), "cost": Decimal("720.00"), "stock": 8},
        {"name": "Microondas Panasonic 1.2cu", "category": "Electrodomésticos", "code": "MIC001", 
         "price": Decimal("320.00"), "cost": Decimal("250.00"), "stock": 25},
        {"name": "Cocina Indurama 6 Hornillas", "category": "Electrodomésticos", "code": "COC001", 
         "price": Decimal("650.00"), "cost": Decimal("480.00"), "stock": 12},
        
        # Electrónicos
        {"name": "TV LED Samsung 55''", "category": "Electrónicos", "code": "TV001", 
         "price": Decimal("1450.00"), "cost": Decimal("1150.00"), "stock": 10},
        {"name": "Laptop HP Pavilion i7", "category": "Electrónicos", "code": "LAP001", 
         "price": Decimal("1890.00"), "cost": Decimal("1520.00"), "stock": 5},
        {"name": "Smartphone Samsung Galaxy", "category": "Electrónicos", "code": "CEL001", 
         "price": Decimal("680.00"), "cost": Decimal("520.00"), "stock": 20},
        {"name": "Tablet iPad 10.9''", "category": "Electrónicos", "code": "TAB001", 
         "price": Decimal("1120.00"), "cost": Decimal("890.00"), "stock": 8},
        
        # Muebles
        {"name": "Sala 3-2-1 Cuero Sintético", "category": "Muebles", "code": "SAL001", 
         "price": Decimal("2350.00"), "cost": Decimal("1800.00"), "stock": 3},
        {"name": "Comedor 6 Puestos Madera", "category": "Muebles", "code": "COM001", 
         "price": Decimal("1200.00"), "cost": Decimal("900.00"), "stock": 5},
        {"name": "Escritorio Ejecutivo", "category": "Muebles", "code": "ESC001", 
         "price": Decimal("450.00"), "cost": Decimal("320.00"), "stock": 12},
        {"name": "Cama Matrimonial + Colchón", "category": "Muebles", "code": "CAM001", 
         "price": Decimal("850.00"), "cost": Decimal("620.00"), "stock": 8},
        
        # Herramientas
        {"name": "Taladro Percutor Bosch", "category": "Herramientas", "code": "TAL001", 
         "price": Decimal("280.00"), "cost": Decimal("210.00"), "stock": 15},
        {"name": "Amoladora DeWalt 4.5''", "category": "Herramientas", "code": "AMO001", 
         "price": Decimal("180.00"), "cost": Decimal("135.00"), "stock": 20},
        {"name": "Soldadora Inverter 200A", "category": "Herramientas", "code": "SOL001", 
         "price": Decimal("420.00"), "cost": Decimal("310.00"), "stock": 6},
        
        # Deportes
        {"name": "Bicicleta MTB Specialized", "category": "Deportes", "code": "BIC001", 
         "price": Decimal("850.00"), "cost": Decimal("650.00"), "stock": 7},
        {"name": "Caminadora Eléctrica", "category": "Deportes", "code": "CAM002", 
         "price": Decimal("1200.00"), "cost": Decimal("950.00"), "stock": 4},
        {"name": "Juego Pesas Completo", "category": "Deportes", "code": "PES001", 
         "price": Decimal("320.00"), "cost": Decimal("240.00"), "stock": 10},
        
        # Hogar
        {"name": "Juego Ollas Acero Inoxidable", "category": "Hogar", "code": "OLL001", 
         "price": Decimal("120.00"), "cost": Decimal("85.00"), "stock": 30},
        {"name": "Aspiradora Robot iRobot", "category": "Hogar", "code": "ASP001", 
         "price": Decimal("650.00"), "cost": Decimal("480.00"), "stock": 8},
        {"name": "Ventilador de Techo Hunter", "category": "Hogar", "code": "VEN001", 
         "price": Decimal("180.00"), "cost": Decimal("130.00"), "stock": 18}
    ]
    
    products_created = 0
    for prod_data in products_data:
        category = categories[prod_data["category"]]
        product, created = Product.objects.get_or_create(
            code=prod_data["code"],
            company=gueber,
            defaults={
                "name": prod_data["name"],
                "category": category,
                "sale_price": prod_data["price"],
                "cost_price": prod_data["cost"],
                "minimum_stock": Decimal("5.00"),
                "maximum_stock": Decimal(str(prod_data["stock"] * 2)),
                "unit_of_measure": "UND",
                "is_active": True,
                "manages_inventory": True
            }
        )
        if created:
            products_created += 1
            print(f"✅ {product.name} - ${product.sale_price}")
            
            # Crear stock inicial
            if product.manages_inventory:
                initial_stock = Decimal(str(prod_data["stock"]))
                stock, stock_created = Stock.objects.get_or_create(
                    product=product,
                    warehouse=warehouse,
                    defaults={
                        'quantity': initial_stock,
                        'average_cost': prod_data["cost"]
                    }
                )
                
                # Crear movimiento inicial de stock
                if stock_created:
                    StockMovement.objects.create(
                        product=product,
                        warehouse=warehouse,
                        movement_type=StockMovement.IN,
                        quantity=initial_stock,
                        unit_cost=prod_data["cost"],
                        total_cost=initial_stock * prod_data["cost"],
                        description=f"Stock inicial - {product.name}",
                        reference="INICIAL",
                        created_by=admin_user
                    )
        else:
            print(f"ℹ️ {product.name} (ya existe)")
    
    # Crear clientes
    print("\n--- Creando clientes ---")
    customers_data = [
        {
            "trade_name": "María Elena Vásquez",
            "customer_type": "natural",
            "identification": "1712345678",
            "email": "maria.vasquez@email.com",
            "phone": "0987654321",
            "address": "Av. 6 de Diciembre N24-253, Quito"
        },
        {
            "trade_name": "Carlos Alberto Mendoza",
            "customer_type": "natural", 
            "identification": "1723456789",
            "email": "carlos.mendoza@email.com",
            "phone": "0976543210",
            "address": "Calle García Moreno 452, Cuenca"
        },
        {
            "trade_name": "Ana Patricia Ruiz",
            "customer_type": "natural",
            "identification": "0934567890",
            "email": "ana.ruiz@email.com", 
            "phone": "0965432109",
            "address": "Malecón Simón Bolívar 1234, Guayaquil"
        },
        {
            "trade_name": "Distribuidora El Sol S.A.",
            "customer_type": "juridical",
            "identification": "1890123456001",
            "email": "ventas@elsol.com.ec",
            "phone": "0987123456",
            "address": "Av. América N39-123, Quito"
        },
        {
            "trade_name": "Comercial Los Andes Cía. Ltda.",
            "customer_type": "juridical",
            "identification": "0190234567001", 
            "email": "info@losandes.ec",
            "phone": "0976234567",
            "address": "Av. José de Sucre 789, Cuenca"
        },
        {
            "trade_name": "Luis Fernando Castro",
            "customer_type": "natural",
            "identification": "1045678901",
            "email": "luis.castro@email.com",
            "phone": "0954321098",
            "address": "Cdla. Kennedy Norte Mz 15 Villa 8, Guayaquil"
        },
        {
            "trade_name": "Sofía Alejandra Torres",
            "customer_type": "natural", 
            "identification": "1756789012",
            "email": "sofia.torres@email.com",
            "phone": "0943210987",
            "address": "Av. Naciones Unidas E2-17, Quito"
        },
        {
            "trade_name": "Grupo Empresarial Costa S.A.",
            "customer_type": "juridical",
            "identification": "0990345678001",
            "email": "gerencia@grupocosta.ec", 
            "phone": "0932109876",
            "address": "Av. Francisco de Orellana, Edif. Torre Norte, Guayaquil"
        },
        {
            "trade_name": "Roberto Patricio Hidalgo",
            "customer_type": "natural",
            "identification": "1867890123",
            "email": "roberto.hidalgo@email.com",
            "phone": "0921098765",
            "address": "Av. Héroes de Verdeloma 567, Cuenca"
        },
        {
            "trade_name": "Corporación Andina de Comercio",
            "customer_type": "juridical", 
            "identification": "1790456789001",
            "email": "contacto@andina.com.ec",
            "phone": "0910987654",
            "address": "Av. República del Salvador N34-451, Quito"
        }
    ]
    
    customers_created = 0
    for cust_data in customers_data:
        customer, created = Customer.objects.get_or_create(
            identification=cust_data["identification"],
            company=gueber,
            defaults={
                "trade_name": cust_data["trade_name"],
                "customer_type": cust_data["customer_type"],
                "email": cust_data["email"],
                "phone": cust_data["phone"],
                "address": cust_data["address"],
                "is_active": True
            }
        )
        if created:
            customers_created += 1
            print(f"✅ {customer.trade_name} - {customer.identification}")
        else:
            print(f"ℹ️ {customer.trade_name} (ya existe)")
    
    # Resumen
    print(f"\n=== RESUMEN ===")
    print(f"✅ Empresa: {gueber.trade_name}")
    print(f"✅ Bodega: {warehouse.name}")
    print(f"✅ Categorías: {len(categories)} creadas")
    print(f"✅ Productos: {products_created} nuevos de {len(products_data)} total")
    print(f"✅ Clientes: {customers_created} nuevos de {len(customers_data)} total")
    print(f"✅ Base de datos poblada exitosamente!")
    print(f"✅ Puedes acceder al módulo de facturación en: http://127.0.0.1:8000/invoicing/")

if __name__ == "__main__":
    main()