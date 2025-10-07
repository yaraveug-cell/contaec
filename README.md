# ContaEC - Sistema de Contabilidad para Empresas Ecuatorianas

## Descripción

ContaEC es un sistema integral de contabilidad diseñado específicamente para pequeñas y medianas empresas en Ecuador. El sistema cumple con la legislación ecuatoriana y se integra con los servicios del SRI (Servicio de Rentas Internas).

## Características Principales

### 🏢 Gestión Multiempresa
- Manejo de múltiples empresas desde una sola instalación
- Roles y permisos específicos por empresa
- Configuración independiente por empresa

### 📊 Contabilidad General
- Plan de cuentas configurable según NIIF
- Asientos contables automáticos y manuales
- Estados financieros (Balance General, Estado de Resultados)
- Libro Mayor y Balances de Comprobación
- Cierre de ejercicios fiscales

### 🧾 Facturación Electrónica
- Integración completa con SRI Ecuador
- Facturación electrónica, notas de crédito y débito
- Comprobantes de retención
- Firma digital de documentos
- Envío automático por email

### 📦 Inventarios
- Gestión de productos y servicios
- Control de stock en tiempo real
- Múltiples almacenes
- Costeo por PEPS, UEPS o promedio ponderado
- Reportes de inventario

### 💰 Cuentas por Cobrar/Pagar
- Gestión completa de clientes y proveedores
- Control de vencimientos
- Estados de cuenta
- Reportes de cartera
- Conciliación bancaria

### 📈 Reportes y Analytics
- Reportes financieros estándar
- Dashboard ejecutivo con métricas clave
- Exportación a PDF y Excel
- Gráficos interactivos

### 👥 Nómina (Planificado)
- Cálculo automático de nómina
- Décimo tercero y décimo cuarto sueldo
- Vacaciones y utilidades
- Reportes al IESS

### 🏭 Activos Fijos (Planificado)
- Registro y control de activos fijos
- Depreciación automática
- Revaluaciones
- Reportes de activos

## Tecnologías Utilizadas

### Backend
- **Python 3.10+**
- **Django 4.2** - Framework web
- **Django REST Framework** - API REST
- **PostgreSQL** - Base de datos principal
- **JWT** - Autenticación
- **Celery** - Tareas asíncronas (futuro)

### Frontend (Futuro)
- **React.js** - Interfaz de usuario
- **Material-UI** - Componentes UI
- **Chart.js** - Gráficos

### Integraciones
- **SRI Ecuador** - Facturación electrónica
- **Bancos ecuatorianos** - Conciliación bancaria (futuro)

## Instalación y Configuración

### Prerrequisitos

1. Python 3.10 o superior
2. PostgreSQL 12 o superior
3. Git

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/contaec.git
cd contaec
```

2. **Crear entorno virtual**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. **Configurar base de datos**
```sql
-- En PostgreSQL
CREATE DATABASE contaec_db;
CREATE USER contaec_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE contaec_db TO contaec_user;
```

6. **Ejecutar migraciones**
```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Crear superusuario**
```bash
python manage.py createsuperuser
```

8. **Cargar datos iniciales**
```bash
python manage.py loaddata fixtures/initial_data.json
```

9. **Ejecutar servidor de desarrollo**
```bash
python manage.py runserver
```

## Estructura del Proyecto

```
contaec/
├── apps/
│   ├── core/              # Modelos y utilidades base
│   ├── users/             # Gestión de usuarios
│   ├── companies/         # Gestión de empresas
│   ├── accounting/        # Contabilidad general
│   ├── invoicing/         # Facturación electrónica
│   ├── inventory/         # Inventarios
│   ├── reports/           # Reportes
│   ├── sri_integration/   # Integración con SRI
│   ├── payroll/           # Nómina (futuro)
│   └── fixed_assets/      # Activos fijos (futuro)
├── contaec/               # Configuración del proyecto
├── static/                # Archivos estáticos
├── media/                 # Archivos subidos
├── templates/             # Plantillas HTML
└── requirements.txt       # Dependencias Python
```

## API Documentation

Una vez ejecutando el servidor, puedes acceder a:
- **Swagger UI**: http://localhost:8000/api/docs/
- **API Schema**: http://localhost:8000/api/schema/

## Configuración SRI

Para la integración con el SRI de Ecuador:

1. Obtener certificado digital (.p12) del SRI
2. Configurar ambiente (pruebas/producción)
3. Establecer puntos de emisión
4. Configurar secuenciales

## Cumplimiento Legal Ecuador

El sistema cumple con:
- ✅ Ley Orgánica de Régimen Tributario Interno (LORTI)
- ✅ Reglamento para la aplicación de la LORTI
- ✅ Normas Internacionales de Información Financiera (NIIF)
- ✅ Resoluciones del SRI para facturación electrónica
- ✅ Catálogo único de cuentas (CUC) - Sector privado

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Soporte

Para soporte técnico:
- 📧 Email: soporte@contaec.com
- 📱 WhatsApp: +593 99 XXX XXXX
- 🌐 Web: https://www.contaec.com

## Roadmap

### Fase 1 (Actual) - MVP
- [x] Gestión de empresas y usuarios
- [x] Plan de cuentas básico
- [x] Asientos contables
- [ ] Facturación básica
- [ ] Reportes fundamentales

### Fase 2 - Funcionalidades Avanzadas
- [ ] Integración completa SRI
- [ ] Inventarios avanzados
- [ ] Conciliación bancaria
- [ ] Dashboard ejecutivo

### Fase 3 - Expansión
- [ ] Nómina completa
- [ ] Activos fijos
- [ ] App móvil
- [ ] Inteligencia artificial para categorización automática

---

**ContaEC** - Simplificando la contabilidad empresarial en Ecuador 🇪🇨