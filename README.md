🚀 Parnet Ingeniería - Sistema Completo API
📋 Descripción General

Sistema backend completo para Parnet Ingeniería S.A. de C.V. desarrollado en Flask, que gestiona productos, servicios, clientes, noticias y contactos con autenticación JWT, generación de PDFs, envío de emails y dashboard administrativo.

🎯 Funcionalidades Principales
🔐 Sistema de Autenticación

    Login/Logout con JWT

    Roles de usuario: Admin y Editor

    Protección de rutas con decoradores

    Cambio de contraseñas seguro

📦 Gestión de Productos

    CRUD completo de productos

    Categorización de productos

    Control de inventario y stock

    Fichas técnicas en PDF

    Productos destacados

    Búsqueda y filtros avanzados

🔧 Gestión de Servicios

    Catálogo de servicios por áreas

    Solicitudes de servicio desde frontend

    Seguimiento de estados (pendiente, en proceso, atendido)

    Notificaciones por email

👥 Gestión de Clientes

    Portafolio de clientes

    Testimonios y casos de éxito

    Logos y enlaces web

📰 Sistema de Noticias

    Blog corporativo

    Contador de visitas

    Etiquetas y categorización

    Fechas de publicación

📞 Sistema de Contacto

    Formulario de contacto público

    Sistema de sugerencias

    Notificaciones automáticas por email

    Gestión de consultas

🛠️ Utilidades Integradas
📧 Sistema de Emails (email_sender.py)

    Envío asíncrono de emails

    Plantillas HTML profesionales

    Notificaciones automáticas para:

        Nuevos contactos

        Solicitudes de servicio

        Sugerencias

        Emails de prueba

📄 Generador de PDFs (pdf_generator.py)

    Fichas técnicas de productos

    Reportes de productos en PDF

    Reportes de sugerencias

    Diseño profesional con logo

📊 Sistema de Estadísticas (singleton.py)

    Tracking de visitas en tiempo real

    Sesiones de usuario

    Páginas más visitadas

    Estadísticas diarias

    Patrón Singleton para una única instancia

🚀 Configuración e Instalación
1. Requisitos Previos
bash

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno en .env
MYSQL_HOST=localhost
MYSQL_USER=tu_usuario
MYSQL_PASSWORD=tu_contraseña
MYSQL_DATABASE=parnet_ingenieria
JWT_SECRET_KEY=tu_clave_secreta
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_contraseña_app

2. Inicialización Paso a Paso
bash

# 1. Verificar estructura de archivos
python check_structure.py

# 2. Inicializar base de datos
python init_database.py

# 3. Poblar con datos de ejemplo
python seed_database.py

# 4. Verificar estado de la BD
python check_database.py

# 5. Crear administrador (opcional)
python crear_admin.py

# 6. Ejecutar la aplicación
python run.py

3. Scripts de Configuración
📄 init_database.py

    ✅ Crea la base de datos MySQL

    ✅ Configura migraciones con Flask-Migrate

    ✅ Verifica tablas creadas

    ✅ Genera estructura inicial

🌱 seed_database.py

    👥 Crea administradores (admin/editor)

    📦 Categorías y productos de ejemplo

    🔧 Servicios predefinidos

    🏢 Clientes reconocidos

    📰 Noticias de ejemplo

    📞 Solicitudes de servicio

🔍 check_database.py

    🔌 Verifica conexión MySQL

    📊 Estadísticas de tablas

    🔗 Verifica relaciones

    📈 Resumen del estado

🌐 Endpoints de la API
Públicos (Sin Autenticación)
text

GET  /api/public/productos           # Lista productos
GET  /api/public/productos/{id}      # Producto específico
GET  /api/public/servicios           # Lista servicios
GET  /api/public/clientes            # Lista clientes
GET  /api/public/noticias            # Lista noticias
POST /api/contactos/contactos        # Enviar contacto
POST /api/contactos/sugerencias      # Enviar sugerencia
POST /api/servicios/solicitudes      # Solicitar servicio

Autenticados (Con JWT)
text

POST /api/auth/login                 # Iniciar sesión
GET  /api/auth/me                    # Perfil usuario
POST /api/auth/change-password       # Cambiar contraseña

GET  /api/dashboard/estadisticas     # Estadísticas dashboard
GET  /api/dashboard/actividad-reciente # Actividad reciente

GET  /api/utils/productos/reporte-pdf    # Reporte productos PDF
GET  /api/utils/sugerencias/reporte-pdf  # Reporte sugerencias PDF
POST /api/utils/test-email              # Probar email
GET  /api/utils/config-info             # Info configuración

Utilidades
text

GET  /api/stats                      # Estadísticas del sitio
POST /api/stats/cleanup              # Limpiar sesiones
GET  /api/utils/productos/{id}/ficha-pdf  # Ficha técnica PDF

🔧 Modelos de Base de Datos
👥 Administradores

    Usuario, email, contraseña hasheada

    Roles: admin/editor

    Último acceso y actividad

📦 Productos

    SKU, nombre, descripciones

    Precio, stock, estado

    Categorías, características técnicas

    Destacados y activos

🔧 Servicios

    Nombre, descripción, área

    Orden y características

    Solicitudes asociadas

🏢 Clientes

    Nombre empresa, logo, enlace web

    Testimonios y orden de visualización

📞 Contactos y Sugerencias

    Información de contacto

    Mensajes y asuntos

    Fechas de creación

📰 Noticias

    Título, contenido, resumen

    Autor, etiquetas, visitas

    Fechas de publicación

✨ Características Técnicas
🛡️ Seguridad

    JWT Tokens para autenticación

    Contraseñas hasheadas con werkzeug

    CORS configurado para frontend

    Validación de datos en modelos

📊 Rendimiento

    Sesiones en memoria para estadísticas

    Emails asíncronos en hilos separados

    PDFs temporales para descargas

    Consultas optimizadas con SQLAlchemy

🔌 Integraciones

    MySQL para base de datos

    JWT para autenticación

    SMTP para envío de emails

    CORS para frontend

    FPDF para generación de PDFs

🎨 Frontend Preparado

La API está diseñada para conectar con un frontend que incluya:

    🏠 Página principal con productos destacados

    📦 Catálogo de productos con filtros

    🔧 Página de servicios con solicitudes

    📰 Blog de noticias

    👥 Portafolio de clientes

    📞 Formularios de contacto

    🔐 Panel administrativo

🚦 Flujo de Trabajo Recomendado

    🔧 Configuración inicial con los scripts proporcionados

    👤 Crear administradores con crear_admin.py

    🌱 Poblar datos con seed_database.py

    🚀 Ejecutar con python run.py

    🔍 Verificar con check_database.py

    📧 Probar emails con endpoint /api/utils/test-email

    📄 Probar PDFs con endpoints de generación

🐛 Solución de Problemas
Problemas Comunes:

    Error de conexión MySQL: Verificar variables de entorno

    Email no enviado: Revisar configuración SMTP

    PDF no generado: Verificar permisos de escritura

    JWT no funciona: Revisar secret key

Herramientas de Diagnóstico:

    check_database.py - Estado de la BD

    check_structure.py - Estructura de archivos

    Endpoint /api/utils/config-info - Info configuración

    Endpoint /api/utils/test-email - Probar emails

📞 Soporte y Mantenimiento

El sistema incluye:

    ✅ Logs detallados de errores

    📊 Estadísticas de uso

    🔄 Backups automáticos (configurar)

    📧 Notificaciones de errores críticos
