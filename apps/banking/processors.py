"""
Procesadores automáticos de extractos bancarios por banco
"""
import csv
from datetime import datetime
from decimal import Decimal
from django.utils import timezone


class ExtractoBancarioProcessor:
    """Procesador base para extractos bancarios"""
    
    @classmethod
    def detect_bank_format(cls, file_path):
        """Detectar formato del banco basado en contenido del archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(500).lower()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read(500).lower()
            except Exception:
                return 'unknown'
        
        # Detectar PICHINCHA
        if 'pichincha' in content or 'movimientos' in content:
            return 'pichincha'
        
        # Detectar PACIFICO (o formato genérico CSV)
        if any(keyword in content for keyword in ['pacifico', 'fecha', 'descripcion']):
            return 'pacifico'
        
        return 'generic'
    
    @classmethod
    def process_extracto(cls, extracto):
        """Procesar extracto según el banco detectado"""
        file_path = extracto.file.path
        bank_format = cls.detect_bank_format(file_path)
        
        if bank_format == 'pichincha':
            return PichinchaProcessor.process(extracto)
        elif bank_format == 'pacifico':
            return PacificoProcessor.process(extracto)
        else:
            return GenericProcessor.process(extracto)


class PichinchaProcessor:
    """Procesador específico para extractos de PICHINCHA"""
    
    @classmethod
    def process(cls, extracto):
        """Procesar extracto de PICHINCHA"""
        from apps.banking.models import ExtractoBancarioDetalle
        
        try:
            # Detectar encoding
            encoding = 'utf-8'
            try:
                with open(extracto.file.path, 'r', encoding='utf-8') as f:
                    f.read(100)
            except UnicodeDecodeError:
                encoding = 'latin-1'
            
            # Leer archivo
            with open(extracto.file.path, 'r', encoding=encoding) as f:
                reader = csv.reader(f, delimiter=';')
                rows = list(reader)
            
            # Buscar headers (dos formatos posibles)
            headers_row = None
            datos_inicio = None
            
            # Formato 1: Buscar "Movimientos" seguido de headers
            for i, row in enumerate(rows):
                if any('Movimientos' in str(cell) for cell in row):
                    # Buscar headers en las siguientes filas
                    for j in range(i + 1, min(i + 5, len(rows))):
                        next_row = [cell.strip() for cell in rows[j] if cell.strip()]
                        if next_row and 'Fecha' in next_row:
                            headers_row = j
                            datos_inicio = j + 1
                            break
                    break
            
            # Formato 2: Buscar directamente headers con "Fecha"
            if not datos_inicio:
                for i, row in enumerate(rows):
                    row_clean = [cell.strip() for cell in row if cell.strip()]
                    if row_clean and len(row_clean) > 2 and 'Fecha' in row_clean:
                        headers_row = i
                        datos_inicio = i + 1
                        break
            
            if not datos_inicio or datos_inicio >= len(rows):
                return False, "No se encontró sección de headers/movimientos en el archivo"
            
            # Verificar headers detectados
            if headers_row is not None:
                headers = [cell.strip() for cell in rows[headers_row] if cell.strip()]
            else:
                headers = ['Fecha', 'Concepto', 'Monto', 'Detalle']  # Headers por defecto
            
            # Limpiar detalles existentes
            ExtractoBancarioDetalle.objects.filter(extracto=extracto).delete()
            
            # Procesar datos
            datos_filas = rows[datos_inicio:]
            detalles_creados = 0
            errores = []
            
            for i, row in enumerate(datos_filas):
                try:
                    row_clean = [cell.strip() for cell in row]
                    
                    # Filtrar filas vacías o con muy pocos datos
                    if len(row_clean) < 3 or not any(row_clean):
                        continue
                    
                    # Extraer campos de manera flexible
                    fecha_str = ''
                    concepto = ''
                    tipo = ''
                    monto_str = ''
                    saldo_str = ''
                    
                    for j, cell in enumerate(row_clean):
                        if not fecha_str and cell and any(char in cell for char in ['/', '-']) and len(cell) >= 8:
                            fecha_str = cell
                        elif not concepto and cell and len(cell) > 3 and not any(char in cell for char in ['$']):
                            # Excluir números y montos para descripción
                            if not (cell.replace(',', '').replace('.', '').replace('-', '').isdigit()):
                                concepto = cell
                        elif ('$' in cell or 
                              (cell.replace(',', '').replace('.', '').replace('-', '').isdigit() and len(cell) > 1)):
                            if not monto_str:
                                monto_str = cell
                            else:
                                saldo_str = cell
                        elif cell.lower() in ['credito', 'debito', 'crédito', 'débito']:
                            tipo = cell.lower()
                    
                    if not fecha_str or not monto_str:
                        continue
                    
                    # Parsear fecha
                    fecha = cls._parse_fecha_pichincha(fecha_str)
                    if not fecha:
                        continue
                    
                    # Parsear monto (corregir problema de decimales)
                    monto_clean = monto_str.replace('$', '').strip()
                    if not monto_clean:
                        continue
                    
                    # Manejar formato decimal de PICHINCHA (5,00 = 5.00, no 500)
                    if ',' in monto_clean and '.' not in monto_clean:
                        # Formato: "5,00" -> "5.00" (coma como separador decimal)
                        monto_clean = monto_clean.replace(',', '.')
                    else:
                        # Formato: "5.000,50" -> "5000.50" (coma decimal, punto miles)
                        if ',' in monto_clean and '.' in monto_clean:
                            monto_clean = monto_clean.replace('.', '').replace(',', '.')
                        elif ',' in monto_clean:
                            # Solo coma, asumir decimal: "5,00" -> "5.00"
                            monto_clean = monto_clean.replace(',', '.')
                    
                    monto = Decimal(monto_clean)
                    
                    # Determinar débito/crédito basado en tipo o valor
                    if tipo in ['credito', 'crédito'] or (tipo == '' and monto > 0):
                        debito = None
                        credito = abs(monto)
                    else:
                        debito = abs(monto) 
                        credito = None
                    
                    # Parsear saldo si existe (aplicar misma lógica decimal)
                    saldo = Decimal('0.00')
                    if saldo_str:
                        try:
                            saldo_clean = saldo_str.replace('$', '').strip()
                            
                            # Aplicar misma lógica de decimales que al monto
                            if ',' in saldo_clean and '.' not in saldo_clean:
                                saldo_clean = saldo_clean.replace(',', '.')
                            elif ',' in saldo_clean and '.' in saldo_clean:
                                saldo_clean = saldo_clean.replace('.', '').replace(',', '.')
                            elif ',' in saldo_clean:
                                saldo_clean = saldo_clean.replace(',', '.')
                            
                            if saldo_clean:
                                saldo = Decimal(saldo_clean)
                        except:
                            pass
                    
                    # Crear detalle
                    ExtractoBancarioDetalle.objects.create(
                        extracto=extracto,
                        fecha=fecha,
                        descripcion=concepto or f'Movimiento {fecha}',
                        referencia='',
                        debito=debito,
                        credito=credito,
                        saldo=saldo,
                        is_reconciled=False
                    )
                    
                    detalles_creados += 1
                
                except Exception as e:
                    errores.append(f"Fila {i+1}: {str(e)}")
                    if len(errores) > 10:  # Limitar errores
                        break
            
            if detalles_creados > 0:
                # Actualizar status
                extracto.status = 'processed'
                extracto.processed_at = timezone.now()
                extracto.save()
                
                return True, f"Procesado exitosamente: {detalles_creados} movimientos"
            else:
                error_msg = f"No se procesaron movimientos. Errores: {'; '.join(errores[:5])}"
                return False, error_msg
        
        except Exception as e:
            return False, f"Error procesando archivo: {str(e)}"
    
    @classmethod
    def _parse_fecha_pichincha(cls, fecha_str):
        """Parsear fecha en formatos de PICHINCHA"""
        if not fecha_str or not fecha_str.strip():
            return None
        
        fecha_clean = fecha_str.strip()
        
        # Formato: "2025-10-3, 9:34 PM" -> extraer solo fecha
        if ',' in fecha_clean:
            fecha_clean = fecha_clean.split(',')[0].strip()
        
        # Formatos posibles
        formats = [
            '%Y-%m-%d',     # 2025-10-03
            '%Y-%m-%#d',    # 2025-10-3 (Windows)
            '%d/%m/%Y',     # 03/10/2025
            '%d-%m-%Y',     # 03-10-2025
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(fecha_clean, fmt).date()
            except ValueError:
                continue
        
        return None


class PacificoProcessor:
    """Procesador para extractos de PACÍFICO"""
    
    @classmethod
    def process(cls, extracto):
        """Procesar extracto de PACÍFICO (formato CSV genérico)"""
        from apps.banking.models import ExtractoBancarioDetalle
        
        try:
            # Detectar encoding
            encoding = 'utf-8'
            try:
                with open(extracto.file.path, 'r', encoding='utf-8') as f:
                    f.read(100)
            except UnicodeDecodeError:
                encoding = 'latin-1'
            
            # Leer CSV
            with open(extracto.file.path, 'r', encoding=encoding) as f:
                # Detectar delimitador
                first_line = f.readline()
                delimiter = ',' if ',' in first_line else ';'
                
                f.seek(0)
                reader = csv.DictReader(f, delimiter=delimiter)
                
                # Limpiar detalles existentes
                ExtractoBancarioDetalle.objects.filter(extracto=extracto).delete()
                
                detalles_creados = 0
                errores = []
                
                for i, row in enumerate(reader):
                    try:
                        # Mapeo flexible de campos
                        fecha_field = cls._find_field(row, ['fecha', 'date'])
                        desc_field = cls._find_field(row, ['descripcion', 'detalle', 'description'])
                        ref_field = cls._find_field(row, ['referencia', 'reference', 'ref'])
                        debito_field = cls._find_field(row, ['debito', 'debe', 'debit'])
                        credito_field = cls._find_field(row, ['credito', 'haber', 'credit'])
                        saldo_field = cls._find_field(row, ['saldo', 'balance'])
                        
                        if not fecha_field:
                            continue
                        
                        # Parsear fecha
                        fecha = cls._parse_date(row[fecha_field])
                        if not fecha:
                            continue
                        
                        # Extraer montos
                        debito = cls._parse_decimal(row.get(debito_field, '')) if debito_field else None
                        credito = cls._parse_decimal(row.get(credito_field, '')) if credito_field else None
                        saldo = cls._parse_decimal(row.get(saldo_field, '')) if saldo_field else Decimal('0.00')
                        
                        # Crear detalle
                        ExtractoBancarioDetalle.objects.create(
                            extracto=extracto,
                            fecha=fecha,
                            descripcion=row.get(desc_field, ''),
                            referencia=row.get(ref_field, ''),
                            debito=debito,
                            credito=credito,
                            saldo=saldo,
                            is_reconciled=False
                        )
                        
                        detalles_creados += 1
                    
                    except Exception as e:
                        errores.append(f"Fila {i+1}: {str(e)}")
                        if len(errores) > 10:
                            break
                
                if detalles_creados > 0:
                    extracto.status = 'processed'
                    extracto.processed_at = timezone.now()
                    extracto.save()
                    
                    return True, f"Procesado exitosamente: {detalles_creados} movimientos"
                else:
                    error_msg = f"No se procesaron movimientos. Errores: {'; '.join(errores[:5])}"
                    return False, error_msg
        
        except Exception as e:
            return False, f"Error procesando archivo: {str(e)}"
    
    @classmethod
    def _find_field(cls, row, possible_names):
        """Encontrar campo en el row por nombres posibles"""
        for name in possible_names:
            for key in row.keys():
                if name.lower() in key.lower():
                    return key
        return None
    
    @classmethod
    def _parse_date(cls, date_str):
        """Parsear fecha en varios formatos"""
        if not date_str or not date_str.strip():
            return None
        
        date_str = date_str.strip()
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None
    
    @classmethod 
    def _parse_decimal(cls, value_str):
        """Parsear decimal limpiando formato"""
        if not value_str or not str(value_str).strip():
            return None
        
        try:
            clean_str = str(value_str).replace(',', '').replace('$', '').strip()
            return Decimal(clean_str) if clean_str else None
        except:
            return None


class GenericProcessor:
    """Procesador genérico para otros formatos"""
    
    @classmethod
    def process(cls, extracto):
        """Procesamiento genérico"""
        return False, "Formato de archivo no reconocido. Use formato PICHINCHA o PACÍFICO."