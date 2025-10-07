"""
URL configuration for ContaEC project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from . import views

urlpatterns = [
    # Home page
    path('', views.home_view, name='home'),
    
    # Authentication
    path('login/', views.login_view, name='web_login'),
    path('logout/', views.logout_view, name='web_logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('perfil/', views.profile_view, name='profile'),
    
    # Modules
    path('modulos/', include('apps.core.module_urls')),
    
    # Web modules
    path('accounting/', include('apps.accounting.urls')),
    path('suppliers/', include('apps.suppliers.urls')),
    path('banking/', include('apps.banking.urls')),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API Info
    path('api/v1/', views.api_info, name='api-info'),
    
    # API URLs
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/companies/', include('apps.companies.urls')),
    path('api/v1/accounting/', include('apps.accounting.urls')),
    path('api/v1/invoicing/', include('apps.invoicing.urls')),
    path('api/v1/inventory/', include('apps.inventory.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
    path('api/v1/sri/', include('apps.sri_integration.urls')),
    path('api/v1/payroll/', include('apps.payroll.urls')),
    path('api/v1/assets/', include('apps.fixed_assets.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/guide/', views.api_docs_view, name='api-guide'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)