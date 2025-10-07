"""
Helper para manejo de timezone en Ecuador
"""
from django.utils import timezone

def get_ecuador_time():
    """Obtener hora actual de Ecuador"""
    return timezone.localtime()

def format_for_pdf():
    """Formatear hora para PDFs (Ecuador)"""
    ecuador_time = timezone.localtime()
    return ecuador_time.strftime('%d/%m/%Y a las %H:%M')

def format_for_display():
    """Formatear hora para mostrar al usuario"""
    ecuador_time = timezone.localtime()
    return ecuador_time.strftime('%d/%m/%Y %H:%M:%S')
