"""
Datos iniciales de bancos ecuatorianos
Población del catálogo básico sin afectar sistema existente
"""

#!/usr/bin/env python
import os
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.banking.models import Bank


def populate_ecuadorian_banks():
    """Poblar catálogo de bancos ecuatorianos"""
    
    print("🏦 POBLANDO CATÁLOGO DE BANCOS ECUATORIANOS")
    print("=" * 60)
    
    # Datos de bancos principales de Ecuador
    banks_data = [
        {
            'sbs_code': '001',
            'name': 'Banco Pichincha C.A.',
            'short_name': 'PICHINCHA',
            'swift_code': 'PICHECEG',
            'website': 'https://www.pichincha.com',
            'phone': '1700-742-742'
        },
        {
            'sbs_code': '002',
            'name': 'Banco del Pacífico S.A.',
            'short_name': 'PACIFICO',
            'swift_code': 'PACIECEG',
            'website': 'https://www.bancodelpacifico.com',
            'phone': '1700-275-275'
        },
        {
            'sbs_code': '003',
            'name': 'Banco Internacional S.A.',
            'short_name': 'INTERNACIONAL',
            'swift_code': 'BINIECEG',
            'website': 'https://www.bancointernacional.com.ec',
            'phone': '1700-468-372'
        },
        {
            'sbs_code': '005',
            'name': 'Banco de Guayaquil S.A.',
            'short_name': 'GUAYAQUIL',
            'swift_code': 'BGUAECEG',
            'website': 'https://www.bancoguayaquil.com',
            'phone': '1700-426-824'
        },
        {
            'sbs_code': '007',
            'name': 'Banco Bolivariano C.A.',
            'short_name': 'BOLIVARIANO',
            'swift_code': 'BBOLECEG',
            'website': 'https://www.bolivariano.com',
            'phone': '1700-265-482'
        },
        {
            'sbs_code': '009',
            'name': 'Banco ProCredit S.A.',
            'short_name': 'PROCREDIT',
            'swift_code': 'MFIIECEG',
            'website': 'https://www.procredit-bg.ec',
            'phone': '1700-776-273'
        },
        {
            'sbs_code': '011',
            'name': 'Banco Solidario S.A.',
            'short_name': 'SOLIDARIO',
            'swift_code': 'BSOLECEG',
            'website': 'https://www.banco-solidario.com',
            'phone': '1700-765-432'
        },
        {
            'sbs_code': '012',
            'name': 'Banco Machala S.A.',
            'short_name': 'MACHALA',
            'swift_code': 'BMACECEG',
            'website': 'https://www.bancomachala.com',
            'phone': '1700-622-425'
        },
        {
            'sbs_code': '013',
            'name': 'Banco de Loja S.A.',
            'short_name': 'LOJA',
            'swift_code': 'BLOJECEG',
            'website': 'https://www.bancodeloja.fin.ec',
            'phone': '1700-256-563'
        },
        {
            'sbs_code': '017',
            'name': 'Banco Diners Club del Ecuador S.A.',
            'short_name': 'DINERS',
            'swift_code': 'DINCECEG',
            'website': 'https://www.dinersclub.com.ec',
            'phone': '1700-346-377'
        },
        {
            'sbs_code': '020',
            'name': 'Banco General Rumiñahui S.A.',
            'short_name': 'RUMIÑAHUI',
            'swift_code': 'BGRUECEG',
            'website': 'https://www.bancogrn.com',
            'phone': '1700-786-463'
        }
    ]
    
    created_count = 0
    updated_count = 0
    
    for bank_data in banks_data:
        try:
            bank, created = Bank.objects.get_or_create(
                sbs_code=bank_data['sbs_code'],
                defaults=bank_data
            )
            
            if created:
                created_count += 1
                print(f"✅ Creado: {bank.name}")
            else:
                # Actualizar datos si ya existe
                for key, value in bank_data.items():
                    if key != 'sbs_code':
                        setattr(bank, key, value)
                bank.save()
                updated_count += 1
                print(f"🔄 Actualizado: {bank.name}")
                
        except Exception as e:
            print(f"❌ Error procesando {bank_data['name']}: {e}")
    
    print(f"\n📊 RESUMEN:")
    print(f"   ✅ Bancos creados: {created_count}")
    print(f"   🔄 Bancos actualizados: {updated_count}")
    print(f"   📋 Total en catálogo: {Bank.objects.count()}")
    
    return created_count, updated_count


if __name__ == '__main__':
    populate_ecuadorian_banks()