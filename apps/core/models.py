from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """Modelo base con campos de auditoría"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    
    class Meta:
        abstract = True


class Country(BaseModel):
    """Países"""
    code = models.CharField(max_length=3, unique=True, verbose_name='Código')
    name = models.CharField(max_length=100, verbose_name='Nombre')
    
    class Meta:
        verbose_name = 'País'
        verbose_name_plural = 'Países'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Province(BaseModel):
    """Provincias del Ecuador"""
    country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name='País')
    code = models.CharField(max_length=2, verbose_name='Código')
    name = models.CharField(max_length=100, verbose_name='Nombre')
    
    class Meta:
        verbose_name = 'Provincia'
        verbose_name_plural = 'Provincias'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class City(BaseModel):
    """Ciudades"""
    province = models.ForeignKey(Province, on_delete=models.CASCADE, verbose_name='Provincia')
    code = models.CharField(max_length=4, verbose_name='Código')
    name = models.CharField(max_length=100, verbose_name='Nombre')
    
    class Meta:
        verbose_name = 'Ciudad'
        verbose_name_plural = 'Ciudades'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.province.name}"


class Currency(BaseModel):
    """Monedas"""
    code = models.CharField(max_length=3, unique=True, verbose_name='Código ISO')
    name = models.CharField(max_length=100, verbose_name='Nombre')
    symbol = models.CharField(max_length=5, verbose_name='Símbolo')
    
    class Meta:
        verbose_name = 'Moneda'
        verbose_name_plural = 'Monedas'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class DocumentType(BaseModel):
    """Tipos de documento para personas"""
    CEDULA = 'CI'
    RUC = 'RUC'
    PASAPORTE = 'PA'
    
    TYPE_CHOICES = [
        (CEDULA, 'Cédula de Identidad'),
        (RUC, 'RUC'),
        (PASAPORTE, 'Pasaporte'),
    ]
    
    code = models.CharField(max_length=3, choices=TYPE_CHOICES, unique=True, verbose_name='Código')
    name = models.CharField(max_length=50, verbose_name='Nombre')
    mask = models.CharField(max_length=20, blank=True, verbose_name='Máscara de formato')
    
    class Meta:
        verbose_name = 'Tipo de Documento'
        verbose_name_plural = 'Tipos de Documento'
        ordering = ['name']
    
    def __str__(self):
        return self.name