from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class SupportCategory(models.Model):
    """Categorías de soporte"""
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    icon = models.CharField(max_length=50, default="fas fa-question", verbose_name="Icono")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    class Meta:
        verbose_name = "Categoría de Soporte"
        verbose_name_plural = "Categorías de Soporte"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class SupportTicket(models.Model):
    """Tickets de soporte con AI"""
    STATUS_CHOICES = [
        ('open', 'Abierto'),
        ('in_progress', 'En Progreso'),
        ('resolved', 'Resuelto'),
        ('closed', 'Cerrado'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('normal', 'Normal'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    # Identificación
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_number = models.CharField(max_length=20, unique=True, verbose_name="Número de Ticket")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets')
    category = models.ForeignKey(SupportCategory, on_delete=models.CASCADE)
    
    # Contenido
    subject = models.CharField(max_length=200, verbose_name="Asunto")
    description = models.TextField(verbose_name="Descripción del Problema")
    
    # Estado y Prioridad
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    is_resolved = models.BooleanField(default=False, verbose_name="Resuelto")
    
    # AI y Resolución
    ai_response = models.TextField(blank=True, verbose_name="Respuesta de AI")
    ai_confidence = models.FloatField(default=0.0, verbose_name="Confianza de AI (0-1)")
    is_resolved_by_ai = models.BooleanField(default=False, verbose_name="Resuelto por AI")
    
    # Calificación del usuario
    rating = models.PositiveIntegerField(null=True, blank=True, verbose_name="Calificación (1-5)")
    feedback = models.TextField(blank=True, verbose_name="Comentarios del Usuario")
    
    # Asignación Humana
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_tickets',
        verbose_name="Asignado a"
    )
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Ticket de Soporte"
        verbose_name_plural = "Tickets de Soporte"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"#{self.ticket_number} - {self.subject}"
    
    def save(self, *args, **kwargs):
        if not self.ticket_number:
            # Generar número de ticket único
            import random
            import string
            self.ticket_number = f"TK-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
        super().save(*args, **kwargs)
    
    def mark_resolved(self):
        self.status = 'resolved'
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.save()


class SupportMessage(models.Model):
    """Mensajes del chat de soporte"""
    MESSAGE_TYPES = [
        ('user', 'Usuario'),
        ('ai', 'AI Assistant'),
        ('human', 'Soporte Humano'),
        ('system', 'Sistema'),
        ('status_change', 'Cambio de Estado'),
        ('assignment_change', 'Cambio de Asignación'),
        ('notification', 'Notificación'),
        ('closure', 'Cierre de Ticket'),
    ]
    
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_ai_response = models.BooleanField(default=False, verbose_name="Respuesta de IA")
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='user')
    
    content = models.TextField(verbose_name="Contenido del Mensaje")
    
    # Campos para seguimiento de cambios
    previous_status = models.CharField(max_length=20, blank=True, null=True)
    new_status = models.CharField(max_length=20, blank=True, null=True)
    previous_assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, 
        related_name='previous_message_assignments'
    )
    new_assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='new_message_assignments'
    )
    
    # Metadata para AI
    ai_context = models.JSONField(default=dict, blank=True, verbose_name="Contexto de AI")
    ai_tokens_used = models.PositiveIntegerField(default=0, verbose_name="Tokens Utilizados")
    
    # Archivos adjuntos
    attachment = models.FileField(upload_to='support_attachments/%Y/%m/', blank=True, null=True)
    
    # Control de visibilidad
    is_internal = models.BooleanField(default=False, help_text="Solo visible para staff")
    is_notification_sent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Mensaje de Soporte"
        verbose_name_plural = "Mensajes de Soporte"
        ordering = ['created_at']
    
    def __str__(self):
        sender_type = "IA" if self.is_ai_response else "Usuario"
        return f"{sender_type}: {self.content[:50]}..."
    
    def is_status_change(self):
        """Verifica si el mensaje representa un cambio de estado"""
        return self.message_type == 'status_change' or (
            self.previous_status and self.new_status and 
            self.previous_status != self.new_status
        )
    
    def is_assignment_change(self):
        """Verifica si el mensaje representa un cambio de asignación"""
        return self.message_type == 'assignment_change' or (
            self.previous_assigned_to != self.new_assigned_to
        )
    
    def get_change_description(self):
        """Obtiene descripción del cambio realizado"""
        if self.is_status_change():
            old_status = dict(SupportTicket.STATUS_CHOICES).get(self.previous_status, self.previous_status)
            new_status = dict(SupportTicket.STATUS_CHOICES).get(self.new_status, self.new_status)
            return f"Estado cambiado de '{old_status}' a '{new_status}'"
        
        if self.is_assignment_change():
            old_user = self.previous_assigned_to.get_full_name() if self.previous_assigned_to else "Sin asignar"
            new_user = self.new_assigned_to.get_full_name() if self.new_assigned_to else "Sin asignar"
            return f"Asignación cambiada de '{old_user}' a '{new_user}'"
        
        return ""
    
    @classmethod
    def create_status_change_message(cls, ticket, user, old_status, new_status, extra_content=""):
        """Crear mensaje de cambio de estado"""
        status_names = dict(SupportTicket.STATUS_CHOICES)
        content = f"Estado del ticket cambiado de '{status_names.get(old_status, old_status)}' a '{status_names.get(new_status, new_status)}'"
        
        if extra_content:
            content += f"\n\n{extra_content}"
        
        return cls.objects.create(
            ticket=ticket,
            sender=user,
            content=content,
            message_type='status_change',
            previous_status=old_status,
            new_status=new_status
        )
    
    @classmethod
    def create_assignment_change_message(cls, ticket, user, old_assigned, new_assigned):
        """Crear mensaje de cambio de asignación"""
        old_name = old_assigned.get_full_name() if old_assigned else "Sin asignar"
        new_name = new_assigned.get_full_name() if new_assigned else "Sin asignar"
        
        content = f"Ticket reasignado de '{old_name}' a '{new_name}'"
        
        return cls.objects.create(
            ticket=ticket,
            sender=user,
            content=content,
            message_type='assignment_change',
            previous_assigned_to=old_assigned,
            new_assigned_to=new_assigned
        )
    
    @classmethod
    def create_closure_message(cls, ticket, user):
        """Crear mensaje automático de cierre de ticket"""
        content = """🎉 ¡Tu ticket ha sido marcado como resuelto!

Estimado/a cliente,

Nos complace informarte que tu ticket de soporte ha sido marcado como resuelto. Nuestro equipo ha trabajado para brindarte la mejor solución posible.

**Detalles del ticket:**
- Número de ticket: #{ticket_number}
- Fecha de creación: {created_date}
- Fecha de resolución: {resolved_date}

**¿Todo está resuelto?**
Si consideras que tu problema ha sido completamente solucionado, no necesitas realizar ninguna acción adicional. 

**¿Necesitas más ayuda?**
Si tu problema persiste o tienes nuevas consultas relacionadas, puedes:
- Responder a este ticket para reabrirlo
- Crear un nuevo ticket de soporte
- Contactarnos a través de nuestro chat rápido

**Tu opinión es importante**
Te invitamos a calificar nuestro servicio y dejar tus comentarios. Tu feedback nos ayuda a mejorar continuamente.

Gracias por confiar en Galletas Kati. ¡Esperamos seguir sirviéndote!

---
Equipo de Soporte Técnico
Galletas Kati""".format(
            ticket_number=ticket.ticket_number,
            created_date=ticket.created_at.strftime("%d/%m/%Y %H:%M"),
            resolved_date=ticket.resolved_at.strftime("%d/%m/%Y %H:%M") if ticket.resolved_at else "Ahora"
        )
        
        return cls.objects.create(
            ticket=ticket,
            sender=user,
            content=content,
            message_type='closure',
            is_ai_response=False
        )


class SupportNotification(models.Model):
    """Notificaciones del sistema de soporte"""
    NOTIFICATION_TYPES = [
        ('ticket_created', 'Ticket Creado'),
        ('ticket_updated', 'Ticket Actualizado'),
        ('ticket_resolved', 'Ticket Resuelto'),
        ('ticket_closed', 'Ticket Cerrado'),
        ('new_message', 'Nuevo Mensaje'),
        ('status_changed', 'Estado Cambiado'),
        ('assigned', 'Ticket Asignado'),
        ('unassigned', 'Ticket Desasignado'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_notifications')
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Notificación de Soporte"
        verbose_name_plural = "Notificaciones de Soporte"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notificación para {self.user.username}: {self.title}"
    
    @classmethod
    def create_notification(cls, user, ticket, notification_type, title, message):
        """Crear una nueva notificación"""
        return cls.objects.create(
            user=user,
            ticket=ticket,
            notification_type=notification_type,
            title=title,
            message=message
        )


class SupportKnowledgeBase(models.Model):
    """Base de conocimiento para AI"""
    title = models.CharField(max_length=200, verbose_name="Título")
    content = models.TextField(verbose_name="Contenido")
    category = models.ForeignKey(SupportCategory, on_delete=models.CASCADE)
    
    # AI y Búsqueda
    keywords = models.TextField(verbose_name="Palabras Clave", help_text="Separadas por comas")
    embedding_vector = models.JSONField(default=list, blank=True, verbose_name="Vector de Embedding")
    
    # Estadísticas
    times_used = models.PositiveIntegerField(default=0, verbose_name="Veces Utilizado")
    effectiveness_score = models.FloatField(default=0.0, verbose_name="Puntuación de Efectividad")
    
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Artículo de Base de Conocimiento"
        verbose_name_plural = "Base de Conocimiento"
        ordering = ['-effectiveness_score', '-times_used']
    
    def __str__(self):
        return self.title


class AIConversationHistory(models.Model):
    """Historial de conversaciones con AI por usuario"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_conversations')
    session_id = models.UUIDField(default=uuid.uuid4, editable=False)
    
    # Contexto de la conversación
    conversation_data = models.JSONField(default=dict, verbose_name="Datos de la Conversación")
    total_messages = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)
    
    # Métricas
    user_satisfaction = models.PositiveIntegerField(null=True, blank=True, verbose_name="Satisfacción (1-5)")
    was_helpful = models.BooleanField(null=True, blank=True, verbose_name="Fue Útil")
    escalated_to_human = models.BooleanField(default=False, verbose_name="Escalado a Humano")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Historial de Conversación AI"
        verbose_name_plural = "Historial de Conversaciones AI"
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Conversación {self.session_id.hex[:8]} - {self.user.username}"


class SupportFAQ(models.Model):
    """Preguntas frecuentes"""
    question = models.CharField(max_length=300, verbose_name="Pregunta")
    answer = models.TextField(verbose_name="Respuesta")
    category = models.ForeignKey(SupportCategory, on_delete=models.CASCADE)
    
    # SEO y Búsqueda
    keywords = models.TextField(verbose_name="Palabras Clave", help_text="Separadas por comas")
    
    # Estadísticas
    view_count = models.PositiveIntegerField(default=0, verbose_name="Veces Vista")
    helpful_votes = models.PositiveIntegerField(default=0, verbose_name="Votos Útiles")
    not_helpful_votes = models.PositiveIntegerField(default=0, verbose_name="Votos No Útiles")
    
    is_featured = models.BooleanField(default=False, verbose_name="Destacada")
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Pregunta Frecuente"
        verbose_name_plural = "Preguntas Frecuentes"
        ordering = ['-is_featured', '-helpful_votes', '-view_count']
    
    def __str__(self):
        return self.question
    
    @property
    def upvotes(self):
        return self.helpful_votes
    
    @property
    def downvotes(self):
        return self.not_helpful_votes
    
    @property
    def helpfulness_ratio(self):
        total_votes = self.helpful_votes + self.not_helpful_votes
        if total_votes == 0:
            return 0
        return (self.helpful_votes / total_votes) * 100
