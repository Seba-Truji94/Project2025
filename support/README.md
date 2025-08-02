# Sistema de Soporte con IA - Galletas Kati

## 📋 Descripción

Sistema completo de soporte al cliente con inteligencia artificial integrada, diseñado para Galletas Kati. Incluye gestión de tickets, chat en tiempo real, base de conocimiento y panel administrativo centralizado.

## ✨ Características Principales

### Para Clientes
- 🎫 **Creación y seguimiento de tickets**
- 💬 **Chat rápido con IA**
- ❓ **Base de conocimiento y FAQs**
- 📱 **Interfaz responsive y moderna**
- ⭐ **Sistema de calificación y feedback**

### Para Administradores (Solo Superusuarios)
- 🎛️ **Dashboard centralizado con estadísticas**
- 📊 **Métricas en tiempo real**
- 🔧 **Gestión completa de tickets**
- 👥 **Asignación de tickets al personal**
- 📈 **Análisis de rendimiento**
- 🤖 **Integración con IA para respuestas sugeridas**

## 🚀 Instalación y Configuración

### 1. Migrar la Base de Datos
```bash
python manage.py makemigrations support
python manage.py migrate
```

### 2. Crear Datos de Prueba
```bash
# Crear 25 tickets de prueba (default)
python manage.py create_support_data

# Crear número específico de tickets
python manage.py create_support_data --tickets 50

# Limpiar datos existentes y crear nuevos
python manage.py create_support_data --clean --tickets 30
```

### 3. Configurar Superusuario
```bash
python manage.py createsuperuser
```

## 📁 Estructura del Proyecto

```
support/
├── models.py              # Modelos de datos
├── views.py               # Vistas (usuario y admin)
├── forms.py               # Formularios
├── urls.py                # Rutas URL
├── admin.py               # Configuración Django Admin
├── ai_assistant.py        # Asistente de IA
├── decorators.py          # Decoradores de acceso
├── management/            # Comandos personalizados
│   └── commands/
│       └── create_support_data.py
└── templates/support/     # Templates
    ├── admin/             # Templates administrativos
    │   ├── dashboard.html
    │   ├── ticket_list.html
    │   └── ticket_detail.html
    └── [otros templates]
```

## 🔐 Control de Acceso

### Niveles de Usuario

1. **Clientes Regulares**
   - Crear y ver sus propios tickets
   - Usar chat rápido
   - Acceder a FAQs y base de conocimiento

2. **Staff/Personal**
   - Responder tickets asignados
   - Ver dashboard básico

3. **Superusuarios** 
   - Acceso completo al panel administrativo
   - Gestión de todos los tickets
   - Ver estadísticas y métricas
   - Asignar tickets al personal
   - Acciones en lote

## 🎯 Funcionalidades Principales

### Dashboard Administrativo
- **Estadísticas en tiempo real**: Total de tickets por estado
- **Alertas de prioridad**: Tickets urgentes y de alta prioridad
- **Tickets sin asignar**: Vista rápida de trabajo pendiente
- **Métricas de rendimiento**: Tiempo promedio de resolución
- **Acciones rápidas**: Botones de acceso directo

### Gestión de Tickets
- **Lista completa**: Todos los tickets con filtros avanzados
- **Vista detallada**: Historial completo de conversación
- **Asignación**: Asignar tickets al personal adecuado
- **Estados**: Abierto, En Progreso, Resuelto, Cerrado
- **Prioridades**: Baja, Normal, Alta, Urgente
- **Acciones en lote**: Cambiar estado de múltiples tickets

### Sistema de IA
- **Respuestas inteligentes**: Sugerencias basadas en contexto
- **Base de conocimiento**: Artículos de ayuda organizados
- **Chat en tiempo real**: Asistencia inmediata
- **Aprendizaje continuo**: Mejora con cada interacción

## 📊 Métricas y Reportes

El sistema recopila automáticamente:
- ✅ Tickets resueltos por día/semana/mes
- ⏱️ Tiempo promedio de resolución
- 📈 Tendencias de categorías de problemas
- 👥 Carga de trabajo por agente
- ⭐ Satisfacción del cliente
- 🎯 Tickets por prioridad

## 🛣️ URLs Principales

### Para Clientes
- `/support/` - Página principal de soporte
- `/support/tickets/` - Lista de tickets del usuario
- `/support/tickets/create/` - Crear nuevo ticket
- `/support/faq/` - Preguntas frecuentes
- `/support/quick-chat/` - Chat rápido

### Para Administradores (Solo Superusuarios)
- `/support/admin/` - Dashboard administrativo
- `/support/admin/tickets/` - Lista completa de tickets
- `/support/admin/tickets/{id}/` - Detalle de ticket
- `/support/admin/tickets/bulk-actions/` - Acciones en lote

## 🎨 Personalización

### Categorías de Soporte
Configurables desde el admin de Django:
- Problemas Técnicos
- Pedidos y Envíos  
- Productos
- Facturación
- Cuenta de Usuario
- Sugerencias
- Quejas
- Información General

### Estados de Ticket
- **Abierto**: Recién creado, esperando atención
- **En Progreso**: Siendo trabajado por el personal
- **Resuelto**: Problema solucionado
- **Cerrado**: Ticket finalizado

### Niveles de Prioridad
- **Urgente**: Requiere atención inmediata
- **Alta**: Importante, resolver pronto
- **Normal**: Prioridad estándar
- **Baja**: No urgente

## 🔧 Configuración Avanzada

### Variables de Entorno
```python
# En settings.py
SUPPORT_SETTINGS = {
    'AUTO_ASSIGN_TICKETS': True,
    'AI_RESPONSES_ENABLED': True,
    'EMAIL_NOTIFICATIONS': True,
    'MAX_TICKET_ATTACHMENT_SIZE': 5 * 1024 * 1024,  # 5MB
}
```

### Personalización de IA
Editar `support/ai_assistant.py` para:
- Ajustar respuestas predeterminadas
- Modificar lógica de categorización
- Integrar con APIs externas
- Personalizar prompts de IA

## 📱 Responsive Design

Totalmente optimizado para:
- 📱 **Móviles**: iPhone, Android
- 📱 **Tablets**: iPad, tablets Android  
- 💻 **Desktop**: Navegadores modernos
- 🎨 **Tema**: Bootstrap 5 con diseño personalizado

## 🐛 Solución de Problemas

### Errores Comunes

1. **Error de permisos**: Verificar que el usuario sea superusuario
2. **Templates no encontrados**: Verificar estructura de carpetas
3. **Modelos no migrados**: Ejecutar `python manage.py migrate`
4. **Static files**: Ejecutar `python manage.py collectstatic`

### Logs y Debugging
```python
# Activar logging en settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'support_debug.log',
        },
    },
    'loggers': {
        'support': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    },
}
```

## 📈 Próximas Mejoras

- 🔔 **Notificaciones en tiempo real** con WebSockets
- 📧 **Notificaciones por email** automáticas
- 📊 **Dashboard de métricas** avanzado
- 🔍 **Búsqueda inteligente** en tickets
- 🤖 **IA más avanzada** con GPT-4
- 📱 **App móvil** nativa
- 🌐 **Soporte multiidioma**
- 📤 **Exportación de reportes** en PDF/Excel

## 👥 Contribución

Para contribuir al desarrollo:
1. Fork del repositorio
2. Crear rama de feature
3. Commit de cambios
4. Push a la rama
5. Crear Pull Request

## 📄 Licencia

Proyecto desarrollado para Galletas Kati. Todos los derechos reservados.

---

**¿Necesitas ayuda?** Contacta al equipo de desarrollo o crea un ticket en el sistema 😊
