from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.core.models import BaseModel, DocumentType


class User(AbstractUser):
    """Usuario personalizado del sistema"""
    email = models.EmailField(unique=True, verbose_name='Correo electrónico')
    document_type = models.ForeignKey(
        DocumentType, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Tipo de documento'
    )
    document_number = models.CharField(
        max_length=20, 
        unique=True, 
        null=True, 
        blank=True,
        verbose_name='Número de documento'
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    address = models.TextField(blank=True, verbose_name='Dirección')
    is_verified = models.BooleanField(default=False, verbose_name='Verificado')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class UserProfile(BaseModel):
    """Perfil extendido del usuario"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario')
    avatar = models.ImageField(
        upload_to='avatars/', 
        null=True, 
        blank=True, 
        verbose_name='Avatar'
    )
    bio = models.TextField(blank=True, verbose_name='Biografía')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Fecha de nacimiento')
    timezone = models.CharField(
        max_length=50, 
        default='America/Guayaquil', 
        verbose_name='Zona horaria'
    )
    language = models.CharField(
        max_length=10, 
        default='es', 
        verbose_name='Idioma'
    )
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
    
    def __str__(self):
        return f"Perfil de {self.user.full_name}"