# WhatsApp Templates para Galletas Kati

# Confirmación de pedido
ORDER_CONFIRMATION = """
🍪 *GALLETAS KATI*

¡Hola {username}! ✨

Tu pedido ha sido *confirmado exitosamente*

📋 *Detalles del Pedido*
• Número: #{order_id}
• Total: *${total}*
• Estado: {status}
• Fecha: {order_date}

{items_list}

🚚 *Información de Entrega*
{delivery_info}

Ver pedido completo: http://127.0.0.1:8002/orders/detail/{order_id}/

¡Gracias por confiar en nosotros! 🙏
"""

# Actualización de estado
ORDER_STATUS_UPDATE = """
🍪 *GALLETAS KATI*

¡Hola {username}! 📦

Tu pedido #{order_id} tiene una *actualización importante*:

🔄 *Nuevo Estado:* {status}
{status_description}

{tracking_info}

{estimated_delivery}

Ver detalles: http://127.0.0.1:8002/orders/detail/{order_id}/

¿Preguntas? ¡Escríbenos! 💬
"""

# Promociones especiales
PROMOTION = """
🎉 *GALLETAS KATI - OFERTA ESPECIAL*

¡Hola {username}! ✨

{promotion_message}

🎁 *Tu descuento especial:*
Código: *{discount_code}*
Descuento: *{discount_percentage}%*
Válido hasta: {expiry_date}

🛒 *¿Cómo usar tu descuento?*
1. Agrega productos a tu carrito
2. Ingresa el código: *{discount_code}*
3. ¡Disfruta del descuento!

Comprar ahora: http://127.0.0.1:8002/

¡No dejes pasar esta oportunidad! ⏰
"""

# Soporte técnico
SUPPORT_TICKET = """
🎧 *SOPORTE GALLETAS KATI*

¡Hola {username}! 👋

{support_message}

🎫 *Información del Ticket*
• ID: #{ticket_id}
• Asunto: {title}
• Estado: *{status}*
• Prioridad: {priority}
• Asignado a: {assigned_to}

💬 *Última actualización:*
{last_response}

{next_steps}

Ver ticket completo: http://127.0.0.1:8002/support/tickets/{ticket_id}/

📞 *¿Necesitas ayuda inmediata?*
Llámanos: +56 9 1234 5678
Email: soporte@galletaskati.cl
"""

# Bienvenida
WELCOME = """
🎊 *¡BIENVENIDO A GALLETAS KATI!*

¡Hola {username}! ✨

{welcome_message}

🍪 *¿Qué puedes hacer ahora?*
• 🛒 Explora nuestras galletas artesanales
• 👤 Completa tu perfil
• 🔔 Configura tus notificaciones
• 🎯 Suscríbete a ofertas especiales

🎁 *Oferta de bienvenida:*
¡Obtén 10% de descuento en tu primera compra!
Código: *BIENVENIDO10*

Empezar a comprar: http://127.0.0.1:8002/

¡Bienvenido a la familia más dulce de Chile! 🇨🇱
"""

# Notificación general
GENERAL = """
🍪 *GALLETAS KATI*

¡Hola {username}! 👋

{message}

{additional_info}

{action_button}

Visítanos: http://127.0.0.1:8002/

¡Que tengas un día dulce! 🌟
"""

# Recordatorio de carrito abandonado
CART_ABANDONMENT = """
🛒 *GALLETAS KATI*

¡Hola {username}! 😊

*¡No olvides tus galletas favoritas!* 🍪

Tienes productos esperándote en tu carrito:
{cart_items}

💰 *Total: ${cart_total}*

🎁 *¡Oferta especial!*
Completa tu compra en las próximas 2 horas y obtén *envío gratis*

Finalizar compra: http://127.0.0.1:8002/cart/

¡No dejes escapar estas delicias artesanales! ⏰
"""

# Producto favorito en oferta
FAVORITE_PRODUCT_SALE = """
🍪 *GALLETAS KATI - ¡TU FAVORITA EN OFERTA!*

¡Hola {username}! ⭐

*{product_name}*, tu galleta favorita, está en *OFERTA ESPECIAL*

🏷️ *Descuento: {discount_percentage}%*
💰 Antes: ${original_price}
💰 Ahora: *${sale_price}*

⏰ *Oferta válida hasta: {expiry_date}*

{product_description}

Comprar ahora: {product_url}

¡No dejes pasar esta oportunidad! 🏃‍♀️💨
"""
