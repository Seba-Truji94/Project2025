try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

import json
import re
from django.conf import settings
from django.utils import timezone
from typing import List, Dict, Tuple
from .models import SupportKnowledgeBase, AIConversationHistory, SupportFAQ


class AIAssistant:
    """Asistente de AI para soporte técnico"""
    
    def __init__(self):
        # Configurar OpenAI (puedes usar cualquier proveedor de AI)
        self.client = None
        if OPENAI_AVAILABLE and hasattr(settings, 'OPENAI_API_KEY'):
            openai.api_key = settings.OPENAI_API_KEY
            self.client = openai
    
    def generate_response(self, user_message: str, user, conversation_history: List[Dict] = None) -> Dict:
        """
        Genera una respuesta de AI basada en el mensaje del usuario
        """
        try:
            # 1. Buscar en base de conocimiento
            knowledge_context = self._search_knowledge_base(user_message)
            
            # 2. Buscar en FAQs
            faq_context = self._search_faqs(user_message)
            
            # 3. Obtener contexto del usuario (pedidos, etc.)
            user_context = self._get_user_context(user)
            
            # 4. Preparar el prompt
            system_prompt = self._build_system_prompt(knowledge_context, faq_context, user_context)
            
            # 5. Generar respuesta (simulada por ahora, puedes integrar con OpenAI)
            response = self._generate_ai_response(user_message, system_prompt, conversation_history)
            
            # 6. Calcular confianza
            confidence = self._calculate_confidence(response, knowledge_context, faq_context)
            
            return {
                'response': response,
                'confidence': confidence,
                'sources': {
                    'knowledge_base': knowledge_context,
                    'faqs': faq_context,
                },
                'tokens_used': len(user_message.split()) + len(response.split()),
                'should_escalate': confidence < 0.7,
            }
            
        except Exception as e:
            return {
                'response': "Lo siento, hay un problema técnico. Un agente humano te ayudará pronto.",
                'confidence': 0.0,
                'error': str(e),
                'should_escalate': True,
                'tokens_used': 0,
            }
    
    def _search_knowledge_base(self, query: str) -> List[Dict]:
        """Busca en la base de conocimiento"""
        # Búsqueda simple por palabras clave (puedes mejorar con embeddings)
        keywords = self._extract_keywords(query)
        
        articles = SupportKnowledgeBase.objects.filter(
            is_active=True,
            keywords__icontains=keywords[0] if keywords else query
        )[:3]
        
        return [
            {
                'title': article.title,
                'content': article.content[:500] + '...' if len(article.content) > 500 else article.content,
                'category': article.category.name,
                'effectiveness': article.effectiveness_score,
            }
            for article in articles
        ]
    
    def _search_faqs(self, query: str) -> List[Dict]:
        """Busca en las FAQs"""
        keywords = self._extract_keywords(query)
        
        faqs = SupportFAQ.objects.filter(
            is_active=True,
            question__icontains=keywords[0] if keywords else query
        )[:2]
        
        return [
            {
                'question': faq.question,
                'answer': faq.answer,
                'category': faq.category.name,
                'helpfulness': faq.helpfulness_ratio,
            }
            for faq in faqs
        ]
    
    def _get_user_context(self, user) -> Dict:
        """Obtiene contexto del usuario"""
        try:
            from orders.models import Order
            recent_orders = Order.objects.filter(user=user).order_by('-created_at')[:3]
            
            return {
                'username': user.get_full_name() or user.username,
                'email': user.email,
                'recent_orders': [
                    {
                        'number': order.order_number,
                        'status': order.get_status_display(),
                        'payment_status': order.get_payment_status_display(),
                        'total': float(order.total),
                        'date': order.created_at.strftime('%d/%m/%Y'),
                    }
                    for order in recent_orders
                ],
                'total_orders': Order.objects.filter(user=user).count(),
            }
        except:
            return {
                'username': user.get_full_name() or user.username,
                'email': user.email,
            }
    
    def _build_system_prompt(self, knowledge_context: List[Dict], faq_context: List[Dict], user_context: Dict) -> str:
        """Construye el prompt del sistema"""
        return f"""
Eres un asistente de soporte de Dulce Bias, una tienda de galletas artesanales.

INFORMACIÓN DEL USUARIO:
- Nombre: {user_context.get('username', 'Cliente')}
- Email: {user_context.get('email', 'N/A')}
- Pedidos totales: {user_context.get('total_orders', 0)}

PEDIDOS RECIENTES:
{json.dumps(user_context.get('recent_orders', []), ensure_ascii=False, indent=2)}

BASE DE CONOCIMIENTO RELEVANTE:
{json.dumps(knowledge_context, ensure_ascii=False, indent=2)}

FAQS RELEVANTES:
{json.dumps(faq_context, ensure_ascii=False, indent=2)}

INSTRUCCIONES:
1. Responde de manera amigable y profesional
2. Usa la información proporcionada para dar respuestas precisas
3. Si no sabes algo, dilo honestamente
4. Ofrece escalación a soporte humano cuando sea necesario
5. Mantén las respuestas concisas pero completas
6. Usa emojis apropiados para hacer la conversación más cálida

CONTEXTO DE LA EMPRESA:
- Dulce Bias es una tienda de galletas artesanales
- Ofrecemos envíos a nivel nacional
- Aceptamos pagos por Webpay, transferencia y contra entrega
- Horario de atención: Lunes a Viernes 9:00-18:00
"""
    
    def _generate_ai_response(self, user_message: str, system_prompt: str, conversation_history: List[Dict] = None) -> str:
        """
        Genera respuesta de AI (versión simulada)
        Aquí puedes integrar con OpenAI, Claude, o cualquier otro modelo
        """
        
        # RESPUESTAS SIMULADAS INTELIGENTES
        message_lower = user_message.lower()
        
        # Detectar intención y generar respuesta apropiada
        if any(word in message_lower for word in ['pedido', 'orden', 'compra', 'estado']):
            return self._generate_order_response(user_message)
        
        elif any(word in message_lower for word in ['pago', 'transferencia', 'webpay', 'tarjeta']):
            return self._generate_payment_response(user_message)
        
        elif any(word in message_lower for word in ['envío', 'entrega', 'despacho', 'delivery']):
            return self._generate_shipping_response(user_message)
        
        elif any(word in message_lower for word in ['producto', 'galleta', 'ingredientes', 'alérgico']):
            return self._generate_product_response(user_message)
        
        elif any(word in message_lower for word in ['cuenta', 'perfil', 'contraseña', 'email']):
            return self._generate_account_response(user_message)
        
        elif any(word in message_lower for word in ['horario', 'contacto', 'teléfono', 'dirección']):
            return self._generate_contact_response(user_message)
        
        else:
            return self._generate_general_response(user_message)
    
    def _generate_order_response(self, message: str) -> str:
        return """¡Hola! 👋 Te ayudo con tu consulta sobre pedidos.

📦 **Estados de Pedido:**
- **Pendiente**: Tu pedido está confirmado y en cola de preparación
- **En Preparación**: Estamos horneando tus deliciosas galletas
- **Enviado**: Tu pedido está en camino
- **Entregado**: ¡Disfruta tus galletas!

💡 **¿Necesitas ayuda específica?**
- Puedes revisar el estado de tus pedidos en "Mis Pedidos"
- Si tienes el número de pedido, puedo ayudarte a verificar su estado
- Para cambios o cancelaciones, contáctanos lo antes posible

¿Hay algo específico sobre tu pedido que te gustaría saber? 🍪"""
    
    def _generate_payment_response(self, message: str) -> str:
        return """💳 **Métodos de Pago Disponibles:**

✅ **Webpay Plus** - Pago inmediato con tarjetas
✅ **Transferencia Bancaria** - Envía tu comprobante para verificación
✅ **Pago Contra Entrega** - Paga cuando recibas tu pedido

🔄 **Proceso de Transferencia:**
1. Realiza la transferencia a nuestra cuenta
2. Sube el comprobante en tu pedido
3. Verificamos el pago (máximo 24 horas)
4. ¡Preparamos tu pedido!

⚠️ **¿Problemas con el pago?**
- Verifica que el monto sea exacto
- Asegúrate de subir un comprobante claro
- Si pagaste y no se refleja, contáctanos

¿Necesitas ayuda con algún pago en particular? 💰"""
    
    def _generate_shipping_response(self, message: str) -> str:
        return """🚚 **Información de Envíos:**

📍 **Cobertura:**
- Región Metropolitana: 1-2 días hábiles
- V Región: 2-3 días hábiles  
- Otras regiones: 3-5 días hábiles

💰 **Costos de Envío:**
- RM: $3.000
- V Región: $4.000
- Nacional: $5.000

📦 **Seguimiento:**
- Recibirás un email con el código de seguimiento
- Puedes revisar el estado en "Mis Pedidos"

⏰ **Horarios de Entrega:**
- Lunes a Viernes: 9:00 - 18:00
- Sábados: 9:00 - 14:00

¿Tienes alguna consulta específica sobre tu envío? 📨"""
    
    def _generate_product_response(self, message: str) -> str:
        return """🍪 **Sobre Nuestros Productos:**

✨ **Galletas Artesanales:**
- Ingredientes 100% naturales
- Sin conservantes artificiales
- Recetas familiares tradicionales

🥜 **Información de Alérgenos:**
- Todos nuestros productos pueden contener trazas de frutos secos
- Especificamos ingredientes principales en cada producto
- Contáctanos para consultas específicas sobre alergias

🎯 **Variedades Populares:**
- Chips de chocolate
- Avena y miel
- Mantequilla clásica
- Especiales de temporada

¿Buscas información sobre algún producto específico? ¡Te ayudo a encontrar la galleta perfecta! 🎂"""
    
    def _generate_account_response(self, message: str) -> str:
        return """👤 **Gestión de Cuenta:**

🔑 **Problemas de Acceso:**
- ¿Olvidaste tu contraseña? Usa "Recuperar Contraseña"
- Verifica que tu email esté escrito correctamente
- Revisa tu carpeta de spam para emails de confirmación

📧 **Actualizar Información:**
- Puedes cambiar tus datos en "Mi Perfil"
- Actualiza tu dirección para envíos correctos
- Mantén tu email actualizado para notificaciones

🛡️ **Seguridad:**
- Usa contraseñas seguras
- No compartas tus credenciales
- Cierra sesión en dispositivos compartidos

¿Necesitas ayuda específica con tu cuenta? 🔒"""
    
    def _generate_contact_response(self, message: str) -> str:
        return """📞 **Información de Contacto:**

🏪 **Dulce Bias**
📧 Email: soporte@dulcesbias.com
📱 WhatsApp: +56 9 XXXX XXXX
📍 Dirección: [Tu dirección aquí]

⏰ **Horarios de Atención:**
- Lunes a Viernes: 9:00 - 18:00
- Sábados: 9:00 - 14:00
- Domingos: Cerrado

💬 **Canales de Soporte:**
- Chat AI: 24/7 (este chat)
- Email: Respuesta en 24 horas
- WhatsApp: Horario comercial

🚨 **Emergencias:**
Para problemas urgentes con pedidos, escríbenos directamente.

¿Hay algo más en lo que pueda ayudarte? 😊"""
    
    def _generate_general_response(self, message: str) -> str:
        return """¡Hola! 👋 Soy el asistente virtual de Dulce Bias.

Te puedo ayudar con:
📦 Estados de pedidos
💳 Información de pagos  
🚚 Consultas de envío
🍪 Productos y ingredientes
👤 Gestión de cuenta
📞 Información de contacto

Para ayudarte mejor, ¿podrías ser más específico sobre tu consulta?

Si necesitas atención personalizada, puedo conectarte con nuestro equipo humano. 

¿En qué puedo ayudarte hoy? 😊"""
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrae palabras clave del texto"""
        # Remover caracteres especiales y dividir
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filtrar palabras comunes
        stop_words = {'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'como', 'las', 'del', 'los', 'una', 'pero', 'sus', 'ese', 'está', 'han', 'hay', 'o', 'ser', 'al', 'me', 'mi', 'ti', 'tu', 'más', 'ya', 'si'}
        
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords[:5]  # Máximo 5 palabras clave
    
    def _calculate_confidence(self, response: str, knowledge_context: List[Dict], faq_context: List[Dict]) -> float:
        """Calcula la confianza de la respuesta"""
        confidence = 0.5  # Base
        
        # Aumentar confianza si hay contexto relevante
        if knowledge_context:
            confidence += 0.2
        
        if faq_context:
            confidence += 0.2
        
        # Aumentar confianza basada en la longitud y estructura de la respuesta
        if len(response) > 100:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def save_conversation(self, user, ticket, user_message: str, ai_response: Dict):
        """Guarda la conversación en el historial"""
        from .models import SupportMessage
        
        # Guardar mensaje del usuario
        user_msg = SupportMessage.objects.create(
            ticket=ticket,
            sender_type='user',
            sender=user,
            message=user_message
        )
        
        # Guardar respuesta de AI
        ai_msg = SupportMessage.objects.create(
            ticket=ticket,
            sender_type='ai',
            message=ai_response['response'],
            ai_context=ai_response.get('sources', {}),
            ai_tokens_used=ai_response.get('tokens_used', 0)
        )
        
        return user_msg, ai_msg
