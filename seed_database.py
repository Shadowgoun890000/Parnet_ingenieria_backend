import os
import sys
import random
from datetime import datetime, timedelta

# Agregar directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from DataBase.models.administrador import Administrador
from DataBase.models.producto import CategoriaProducto, Producto
from DataBase.models.servicio import Servicio, SolicitudServicio
from DataBase.models.cliente import Cliente
from DataBase.models.contacto import Contacto, Sugerencia
from DataBase.models.noticia import Noticia


def seed_administradores():
    """Insertar administradores iniciales"""
    try:
        # Verificar si ya existen administradores
        if Administrador.query.first():
            print("✅ Administradores ya existen en la base de datos")
            return True

        # Crear administrador principal
        admin = Administrador(
            username="admin",
            email="admin@parnet.com",
            nombre_completo="Administrador Principal",
            rol="admin"
        )
        admin.set_password("admin123")
        db.session.add(admin)

        # Crear editor
        editor = Administrador(
            username="editor",
            email="editor@parnet.com",
            nombre_completo="Editor de Contenidos",
            rol="editor"
        )
        editor.set_password("editor123")
        db.session.add(editor)

        db.session.commit()

        print("✅ Administradores creados:")
        print("   👤 admin / admin123 (Administrador)")
        print("   👤 editor / editor123 (Editor)")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando administradores: {e}")
        return False


def seed_categorias_productos():
    """Insertar categorías de productos iniciales"""
    try:
        categorias = [
            {
                'nombre': 'Fibra Óptica',
                'descripcion': 'Soluciones de conectividad con fibra óptica para redes de alta velocidad',
                'orden': 1
            },
            {
                'nombre': 'Equipos de Red',
                'descripcion': 'Routers, switches y equipos de networking empresarial',
                'orden': 2
            },
            {
                'nombre': 'Telecomunicaciones',
                'descripcion': 'Equipos y sistemas de telecomunicaciones avanzados',
                'orden': 3
            },
            {
                'nombre': 'Energía y UPS',
                'descripcion': 'Sistemas de energía ininterrumpida y estabilizadores',
                'orden': 4
            },
            {
                'nombre': 'Cableado Estructurado',
                'descripcion': 'Soluciones de cableado estructurado para edificios inteligentes',
                'orden': 5
            }
        ]

        for i, cat_data in enumerate(categorias):
            if not CategoriaProducto.query.filter_by(nombre=cat_data['nombre']).first():
                categoria = CategoriaProducto(
                    nombre=cat_data['nombre'],
                    descripcion=cat_data['descripcion'],
                    orden=cat_data.get('orden', i + 1)
                )
                db.session.add(categoria)

        db.session.commit()
        print("✅ Categorías de productos creadas")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando categorías: {e}")
        return False


def seed_productos():
    """Insertar productos de ejemplo"""
    try:
        # Obtener categorías
        categorias = {
            'fibra': CategoriaProducto.query.filter_by(nombre='Fibra Óptica').first(),
            'red': CategoriaProducto.query.filter_by(nombre='Equipos de Red').first(),
            'telecom': CategoriaProducto.query.filter_by(nombre='Telecomunicaciones').first(),
            'energia': CategoriaProducto.query.filter_by(nombre='Energía y UPS').first(),
            'cableado': CategoriaProducto.query.filter_by(nombre='Cableado Estructurado').first()
        }

        productos = [
            {
                'nombre': 'Cable Fibra Óptica Monomodo 6 Hilos',
                'descripcion_corta': 'Cable de fibra óptica monomodo para exteriores',
                'descripcion_larga': 'Cable de fibra óptica monomodo de 6 hilos, ideal para instalaciones exteriores con alta resistencia a condiciones ambientales. Certificación OFNR.',
                'precio': 1250.50,
                'categoria_id': categorias['fibra'].id,
                'stock': 50,
                'estatus': 'disponible',
                'sku': 'FO-MONO-6H',
                'destacado': True,
                'caracteristicas': {
                    'tipo': 'Monomodo',
                    'hilos': 6,
                    'longitud': 'Por metro',
                    'aplicacion': 'Exteriores',
                    'atenuacion': '0.4 dB/km',
                    'diametro': '9/125 μm'
                }
            },
            {
                'nombre': 'Router Industrial Cisco Catalyst 1000',
                'descripcion_corta': 'Router industrial para redes empresariales',
                'descripcion_larga': 'Router industrial Cisco Catalyst serie 1000, diseñado para entornos empresariales con alta disponibilidad y seguridad. Soporte para VLAN, QoS y VPN.',
                'precio': 18500.00,
                'categoria_id': categorias['red'].id,
                'stock': 10,
                'estatus': 'disponible',
                'sku': 'ROUT-CISC-CAT1000',
                'destacado': True,
                'caracteristicas': {
                    'marca': 'Cisco',
                    'puertos': '8 x Gigabit Ethernet',
                    'velocidad': '1 Gbps',
                    'gestion': 'SNMP, Web, CLI',
                    'rack': '1U',
                    'garantia': '3 años'
                }
            },
            {
                'nombre': 'Switch Manageable HP 48 Puertos',
                'descripcion_corta': 'Switch manageable para centro de datos',
                'descripcion_larga': 'Switch manageable HP con 48 puertos Gigabit Ethernet, ideal para centros de datos y redes empresariales de mediano a gran tamaño.',
                'precio': 8900.00,
                'categoria_id': categorias['red'].id,
                'stock': 15,
                'estatus': 'disponible',
                'sku': 'SW-HP-48G',
                'caracteristicas': {
                    'marca': 'HP',
                    'puertos': '48 x Gigabit Ethernet',
                    'manageable': 'Sí',
                    'stackable': 'Sí',
                    'poe': 'No',
                    'garantia': 'Vitalicia'
                }
            },
            {
                'nombre': 'UPS Tripp Lite 3000VA',
                'descripcion_corta': 'Sistema de energía ininterrumpida 3000VA',
                'descripcion_larga': 'UPS Tripp Lite 3000VA con tecnología online de doble conversión, protección completa para equipos críticos y servidores.',
                'precio': 15200.00,
                'categoria_id': categorias['energia'].id,
                'stock': 8,
                'estatus': 'disponible',
                'sku': 'UPS-TRIP-3K',
                'destacado': False,
                'caracteristicas': {
                    'capacidad': '3000VA/2700W',
                    'tiempo_backup': '15-30 min',
                    'tipo': 'Online',
                    'baterias': 'Reemplazables',
                    'display': 'LCD',
                    'garantia': '2 años'
                }
            },
            {
                'nombre': 'Panel de Parcheo 24 Puertos Cat6',
                'descripcion_corta': 'Panel de parcheo categoría 6 para rack',
                'descripcion_larga': 'Panel de parcheo 24 puertos categoría 6, compatible con estándares TIA/EIA-568-B. Ideal para salas de telecomunicaciones.',
                'precio': 850.00,
                'categoria_id': categorias['cableado'].id,
                'stock': 25,
                'estatus': 'disponible',
                'sku': 'PAN-CAT6-24P',
                'caracteristicas': {
                    'categoria': 'Cat6',
                    'puertos': 24,
                    'montaje': 'Rack 1U',
                    'color': 'Blanco',
                    'blindaje': 'UTP'
                }
            }
        ]

        for prod_data in productos:
            if not Producto.query.filter_by(nombre=prod_data['nombre']).first():
                producto = Producto(**prod_data)
                db.session.add(producto)

        db.session.commit()
        print("✅ Productos de ejemplo creados")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando productos: {e}")
        return False


def seed_servicios():
    """Insertar servicios iniciales"""
    try:
        servicios = [
            {
                'nombre': 'Instalación de Redes Estructuradas',
                'descripcion': 'Diseño e implementación de redes estructuradas cableadas e inalámbricas para empresas. Incluye certificación de cableado y documentación completa.',
                'area': 'telecomunicaciones',
                'orden': 1,
                'caracteristicas': [
                    'Diseño personalizado según necesidades',
                    'Certificación de cableado garantizada',
                    'Documentación as-built completa',
                    'Soporte post-instalación 24/7'
                ]
            },
            {
                'nombre': 'Desarrollo de Software a Medida',
                'descripcion': 'Creación de aplicaciones web y móviles personalizadas según necesidades específicas de su empresa. Metodologías ágiles y tecnologías modernas.',
                'area': 'software',
                'orden': 2,
                'caracteristicas': [
                    'Análisis de requerimientos detallado',
                    'Desarrollo ágil con sprints',
                    'Pruebas de calidad exhaustivas',
                    'Mantenimiento continuo y soporte'
                ]
            },
            {
                'nombre': 'Sistemas de Energía Ininterrumpida',
                'descripcion': 'Instalación y mantenimiento de sistemas UPS para protección de equipos críticos. Análisis de carga y diseño de soluciones personalizadas.',
                'area': 'energia',
                'orden': 3,
                'caracteristicas': [
                    'Análisis de carga eléctrica',
                    'Instalación profesional certificada',
                    'Configuración y puesta en marcha',
                    'Mantenimiento preventivo programado'
                ]
            },
            {
                'nombre': 'Consultoría en Telecomunicaciones',
                'descripcion': 'Asesoría especializada en infraestructura de telecomunicaciones y conectividad. Optimización de redes existentes y planificación de expansión.',
                'area': 'consultoria',
                'orden': 4,
                'caracteristicas': [
                    'Auditoría completa de red',
                    'Plan de optimización detallado',
                    'Recomendaciones técnicas específicas',
                    'Análisis de ROI y costos'
                ]
            },
            {
                'nombre': 'Vigilancia y Seguridad Electrónica',
                'descripcion': 'Sistemas de videovigilancia IP, control de acceso y alarmas. Soluciones integradas para la seguridad de su empresa.',
                'area': 'telecomunicaciones',
                'orden': 5,
                'caracteristicas': [
                    'Cámaras IP de alta definición',
                    'Sistemas de grabación NVR',
                    'Control de acceso biométrico',
                    'Monitoreo remoto 24/7'
                ]
            }
        ]

        for serv_data in servicios:
            if not Servicio.query.filter_by(nombre=serv_data['nombre']).first():
                servicio = Servicio(**serv_data)
                db.session.add(servicio)

        db.session.commit()
        print("✅ Servicios creados")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando servicios: {e}")
        return False


def seed_clientes():
    """Insertar clientes iniciales"""
    try:
        clientes = [
            {
                'nombre_empresa': 'Telmex',
                'enlace_web': 'https://www.telmex.com',
                'testimonio': 'Excelente servicio en la implementación de nuestra red de fibra óptica. Profesionalismo y calidad en cada etapa del proyecto.',
                'orden': 1
            },
            {
                'nombre_empresa': 'Grupo Bimbo',
                'enlace_web': 'https://www.grupobimbo.com',
                'testimonio': 'Soporte técnico excepcional en nuestros sistemas de comunicación. Siempre disponibles cuando los necesitamos.',
                'orden': 2
            },
            {
                'nombre_empresa': 'Cemex',
                'enlace_web': 'https://www.cemex.com',
                'testimonio': 'Soluciones robustas y confiables para nuestra infraestructura TI. Cumplen con los más altos estándares de calidad.',
                'orden': 3
            },
            {
                'nombre_empresa': 'FEMSA',
                'enlace_web': 'https://www.femsa.com',
                'testimonio': 'Implementación exitosa de sistemas de videovigilancia IP en todas nuestras sucursales. Gran capacidad de respuesta.',
                'orden': 4
            },
            {
                'nombre_empresa': 'Banorte',
                'enlace_web': 'https://www.banorte.com',
                'testimonio': 'Consultoría invaluable para la modernización de nuestra infraestructura de telecomunicaciones.',
                'orden': 5
            },
            {
                'nombre_empresa': 'Alfa',
                'enlace_web': 'https://www.alfa.com.mx',
                'testimonio': 'Desarrollo de software a medida que optimizó nuestros procesos internos. Muy satisfechos con los resultados.',
                'orden': 6
            }
        ]

        for cliente_data in clientes:
            if not Cliente.query.filter_by(nombre_empresa=cliente_data['nombre_empresa']).first():
                cliente = Cliente(**cliente_data)
                db.session.add(cliente)

        db.session.commit()
        print("✅ Clientes de ejemplo creados")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando clientes: {e}")
        return False


def seed_noticias():
    """Insertar noticias iniciales"""
    try:
        noticias = [
            {
                'titulo': 'PARNET Ingeniería celebra 15 años de innovación en telecomunicaciones',
                'contenido': '''
                <p>Este año celebramos 15 años de proporcionar soluciones integrales en telecomunicaciones a empresas de todos los tamaños. Desde nuestra fundación en 2009, hemos crecido hasta convertirnos en un referente en el sector.</p>

                <p>Durante estos 15 años, hemos completado más de 500 proyectos exitosos, implementado soluciones en más de 200 empresas y mantenido una tasa de satisfacción del cliente del 98%.</p>

                <p>"Estamos orgullosos del camino recorrido y agradecidos con nuestros clientes por su confianza continuada", comentó el Director General.</p>

                <p>Para celebrar este hito, estamos lanzando nuevas soluciones en fibra óptica y expandiendo nuestro equipo de consultoría.</p>
                ''',
                'resumen': 'Aniversario de 15 años de PARNET Ingeniería en el mercado de telecomunicaciones, con más de 500 proyectos completados.',
                'autor': 'Departamento de Comunicación',
                'etiquetas': ['aniversario', 'telecomunicaciones', 'innovación', '15 años']
            },
            {
                'titulo': 'Nuevas soluciones en fibra óptica para 2024',
                'contenido': '''
                <p>Presentamos nuestras nuevas soluciones en fibra óptica que permiten velocidades de hasta 10 Gbps para empresas y centros de datos.</p>

                <p>Las nuevas tecnologías incluyen:</p>
                <ul>
                    <li>Fibra monomodo de baja atenuación</li>
                    <li>Sistemas de empalme por fusión</li>
                    <li>Soluciones para FTTH (Fiber to the Home)</li>
                    <li>Equipos de prueba y certificación</li>
                </ul>

                <p>Estas soluciones están diseñadas para satisfacer la creciente demanda de ancho de banda en la era digital.</p>

                <p>Nuestro equipo de ingenieros está disponible para realizar evaluaciones gratuitas de infraestructura.</p>
                ''',
                'resumen': 'Lanzamiento de nuevas soluciones de fibra óptica de alta velocidad para empresas y centros de datos.',
                'autor': 'Ing. Carlos Martínez',
                'etiquetas': ['fibra optica', 'tecnologia', 'velocidad', 'innovacion']
            },
            {
                'titulo': 'Expansión de servicios de ciberseguridad',
                'contenido': '''
                <p>Respondiendo a las crecientes amenazas digitales, expandimos nuestros servicios de ciberseguridad con nuevas soluciones:</p>

                <ul>
                    <li>Auditorías de seguridad perimetral</li>
                    <li>Implementación de firewalls de última generación</li>
                    <li>Monitoreo continuo de redes</li>
                    <li>Capacitación en conciencia de seguridad</li>
                </ul>

                <p>Las empresas mexicanas enfrentan un promedio de 1,200 intentos de ciberataques por mes, según datos recientes.</p>

                <p>Nuestro enfoque proactivo ayuda a las organizaciones a prevenir incidentes antes de que ocurran.</p>
                ''',
                'resumen': 'Ampliación de servicios de ciberseguridad para proteger a las empresas de amenazas digitales crecientes.',
                'autor': 'Lic. Ana Rodríguez',
                'etiquetas': ['ciberseguridad', 'proteccion', 'firewall', 'auditoria']
            }
        ]

        # Crear fechas de publicación variadas
        base_date = datetime.utcnow()

        for i, noticia_data in enumerate(noticias):
            if not Noticia.query.filter_by(titulo=noticia_data['titulo']).first():
                noticia = Noticia(
                    titulo=noticia_data['titulo'],
                    contenido=noticia_data['contenido'],
                    resumen=noticia_data['resumen'],
                    autor=noticia_data['autor'],
                    etiquetas=noticia_data['etiquetas'],
                    fecha_publicacion=base_date - timedelta(days=i * 10),  # Publicaciones espaciadas
                    visitas=random.randint(50, 500)
                )
                db.session.add(noticia)

        db.session.commit()
        print("✅ Noticias de ejemplo creadas")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando noticias: {e}")
        return False


def seed_solicitudes_servicios():
    """Crear algunas solicitudes de servicio de ejemplo"""
    try:
        servicios = Servicio.query.all()

        if not servicios:
            print("⚠️  No hay servicios para crear solicitudes")
            return True

        solicitudes = [
            {
                'servicio_id': servicios[0].id,  # Instalación de redes
                'nombre_cliente': 'Juan Pérez',
                'email': 'juan.perez@empresa.com',
                'telefono': '555-123-4567',
                'empresa': 'Distribuidora Comercial SA',
                'mensaje': 'Necesitamos instalar una red estructurada en nuestras nuevas oficinas de 3 pisos. Requerimos cotización para 150 puntos de red.',
                'estado': 'pendiente'
            },
            {
                'servicio_id': servicios[1].id,  # Desarrollo de software
                'nombre_cliente': 'María García',
                'email': 'mgarcia@consultora.com',
                'telefono': '555-987-6543',
                'empresa': 'Consultora Estratégica',
                'mensaje': 'Buscamos desarrollar un sistema de gestión de proyectos para nuestro equipo de 25 consultores. Preferimos tecnologías web modernas.',
                'estado': 'en_proceso'
            },
            {
                'servicio_id': servicios[3].id,  # Consultoría
                'nombre_cliente': 'Roberto López',
                'email': 'rlopez@manufactura.com',
                'telefono': '555-456-7890',
                'empresa': 'Manufactura Avanzada MX',
                'mensaje': 'Requiero una auditoría de nuestra red actual y recomendaciones para mejorar la conectividad entre nuestras 4 plantas.',
                'estado': 'atendido'
            }
        ]

        for sol_data in solicitudes:
            solicitud = SolicitudServicio(**sol_data)
            db.session.add(solicitud)

        db.session.commit()
        print("✅ Solicitudes de servicio de ejemplo creadas")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando solicitudes: {e}")
        return False


def main():
    """Función principal para poblar la base de datos"""
    print("🌱 Iniciando población de base de datos con datos iniciales...")
    print("=" * 60)

    with app.app_context():
        steps = [
            ("Administradores", seed_administradores),
            ("Categorías de Productos", seed_categorias_productos),
            ("Productos", seed_productos),
            ("Servicios", seed_servicios),
            ("Clientes", seed_clientes),
            ("Noticias", seed_noticias),
            ("Solicitudes de Servicio", seed_solicitudes_servicios)
        ]

        success_count = 0
        total_steps = len(steps)

        for step_name, step_function in steps:
            print(f"\n🔄 Ejecutando: {step_name}")
            if step_function():
                success_count += 1
                print(f"✅ {step_name} completado")
            else:
                print(f"❌ {step_name} falló")

        print(f"\n📊 Resumen: {success_count}/{total_steps} pasos completados exitosamente")
        print("=" * 60)

        if success_count == total_steps:
            print("🎉 Base de datos poblada exitosamente!")
            print("\n🔑 Credenciales de acceso:")
            print("   👤 Administrador: admin / admin123")
            print("   👤 Editor: editor / editor123")
            print("\n📦 Datos creados:")
            print("   • 2 administradores")
            print("   • 5 categorías de productos")
            print("   • 5 productos de ejemplo")
            print("   • 5 servicios")
            print("   • 6 clientes")
            print("   • 3 noticias")
            print("   • 3 solicitudes de servicio")
            print("\n🚀 Próximo paso: Ejecutar 'python run.py'")
        else:
            print("⚠️  Algunos pasos fallaron. Revisa los errores anteriores.")


if __name__ == '__main__':
    main()