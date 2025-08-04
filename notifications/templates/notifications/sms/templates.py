# SMS Templates para Galletas Kati

# Confirmación de pedido
ORDER_CONFIRMATION = """
🍪 GALLETAS KATI
¡Pedido confirmado! #{order_id}
Total: ${total}
Estado: {status}
Ver detalles: http://127.0.0.1:8002/orders/detail/{order_id}/
"""

# Actualización de estado de pedido
ORDER_STATUS_UPDATE = """
🍪 GALLETAS KATI
Pedido #{order_id} - Actualización
Nuevo estado: {status}
{tracking_info}
Ver pedido: http://127.0.0.1:8002/orders/detail/{order_id}/
"""

# Promociones y ofertas
PROMOTION = """
🎉 GALLETAS KATI - OFERTA ESPECIAL
{message}
{discount_code}
{expiry_info}
Compra ya: http://127.0.0.1:8002/
"""

# Notificaciones generales
GENERAL = """
🍪 GALLETAS KATI
{message}
{action_info}
Más info: http://127.0.0.1:8002/
"""

# Soporte técnico
SUPPORT_TICKET = """
🎧 SOPORTE GALLETAS KATI
Ticket #{ticket_id}: {title}
Estado: {status}
{update_info}
Ver ticket: http://127.0.0.1:8002/support/tickets/{ticket_id}/
"""

# Bienvenida
WELCOME = """
🎊 ¡BIENVENIDO A GALLETAS KATI!
{message}
Explora nuestras galletas artesanales en: http://127.0.0.1:8002/
¡Disfruta de la experiencia más dulce!
"""

# Recordatorios
REMINDER = """
⏰ GALLETAS KATI - RECORDATORIO
{message}
{action_info}
No olvides visitarnos: http://127.0.0.1:8002/
"""

# Recuperación de contraseña
PASSWORD_RESET = """
🔒 GALLETAS KATI - Recuperar Contraseña
Recibimos una solicitud para restablecer tu contraseña.
Enlace: {reset_link}
El enlace expira en 1 hora.
Si no solicitaste esto, ignora este mensaje.
"""

# Verificación de cuenta
ACCOUNT_VERIFICATION = """
✅ GALLETAS KATI - Verificar Cuenta
¡Hola {username}!
Verifica tu cuenta aquí: {verification_link}
¡Bienvenido a la familia más dulce!
"""

# Carrito abandonado
CART_ABANDONMENT = """
🛒 GALLETAS KATI - ¡No olvides tus galletas!
Tienes productos esperándote en tu carrito.
Total: ${cart_total}
Finalizar compra: http://127.0.0.1:8002/cart/
¡No dejes escapar estas delicias!
"""
