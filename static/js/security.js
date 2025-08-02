/**
 * Validador de seguridad de contraseñas en tiempo real
 * Galletas Kati - Sistema de Seguridad
 */

class PasswordValidator {
    constructor(passwordInput, strengthIndicator) {
        this.passwordInput = document.getElementById(passwordInput);
        this.strengthIndicator = document.getElementById(strengthIndicator);
        this.init();
    }

    init() {
        if (this.passwordInput) {
            this.passwordInput.addEventListener('input', () => {
                this.validatePassword();
            });
            this.createStrengthIndicator();
        }
    }

    createStrengthIndicator() {
        if (!this.strengthIndicator) {
            // Crear indicador si no existe
            const indicator = document.createElement('div');
            indicator.id = 'password-strength';
            indicator.className = 'password-strength mt-2';
            this.passwordInput.parentNode.appendChild(indicator);
            this.strengthIndicator = indicator;
        }
    }

    validatePassword() {
        const password = this.passwordInput.value;
        const strength = this.calculateStrength(password);
        this.updateIndicator(strength);
        
        // Validación en servidor (opcional)
        if (password.length > 8) {
            this.checkPasswordAPI(password);
        }
    }

    calculateStrength(password) {
        let score = 0;
        const feedback = [];

        // Longitud
        if (password.length >= 12) {
            score += 25;
        } else if (password.length >= 8) {
            score += 15;
            feedback.push('Usa al menos 12 caracteres');
        } else {
            feedback.push('Muy corta - mínimo 8 caracteres');
        }

        // Minúsculas
        if (/[a-z]/.test(password)) {
            score += 15;
        } else {
            feedback.push('Incluye letras minúsculas');
        }

        // Mayúsculas
        if (/[A-Z]/.test(password)) {
            score += 15;
        } else {
            feedback.push('Incluye letras mayúsculas');
        }

        // Números
        if (/\d/.test(password)) {
            score += 15;
        } else {
            feedback.push('Incluye números');
        }

        // Caracteres especiales
        if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
            score += 20;
        } else {
            feedback.push('Incluye símbolos (!@#$%^&*)');
        }

        // Bonificaciones
        if (password.length >= 16) score += 10;
        if (/[!@#$%^&*(),.?":{}|<>].*[!@#$%^&*(),.?":{}|<>]/.test(password)) score += 5;

        return {
            score: Math.min(score, 100),
            feedback: feedback,
            level: this.getStrengthLevel(score)
        };
    }

    getStrengthLevel(score) {
        if (score < 30) return 'very-weak';
        if (score < 50) return 'weak';
        if (score < 70) return 'fair';
        if (score < 90) return 'good';
        return 'strong';
    }

    updateIndicator(strength) {
        const colors = {
            'very-weak': '#dc3545',
            'weak': '#fd7e14',
            'fair': '#ffc107',
            'good': '#20c997',
            'strong': '#28a745'
        };

        const labels = {
            'very-weak': 'Muy débil',
            'weak': 'Débil',
            'fair': 'Regular',
            'good': 'Buena',
            'strong': 'Muy fuerte'
        };

        const color = colors[strength.level];
        const label = labels[strength.level];

        this.strengthIndicator.innerHTML = `
            <div class="password-strength-bar mb-2">
                <div class="progress" style="height: 6px;">
                    <div class="progress-bar" 
                         style="width: ${strength.score}%; background-color: ${color};" 
                         role="progressbar">
                    </div>
                </div>
            </div>
            <div class="password-strength-label">
                <small class="fw-bold" style="color: ${color};">
                    Seguridad: ${label} (${strength.score}/100)
                </small>
            </div>
            ${strength.feedback.length > 0 ? `
                <div class="password-feedback mt-1">
                    <small class="text-muted">
                        Mejoras sugeridas:
                        <ul class="mb-0 ps-3">
                            ${strength.feedback.map(tip => `<li>${tip}</li>`).join('')}
                        </ul>
                    </small>
                </div>
            ` : ''}
        `;
    }

    async checkPasswordAPI(password) {
        try {
            const response = await fetch('/security/api/check-password/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ password: password })
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    // Usar resultado del servidor si está disponible
                    console.log('Password strength from server:', data.strength);
                }
            }
        } catch (error) {
            console.log('Password validation offline mode');
        }
    }
}

// Validador de formularios de seguridad
class SecurityFormValidator {
    constructor() {
        this.init();
    }

    init() {
        // Prevenir envío múltiple de formularios
        this.preventDoubleSubmit();
        
        // Validar campos en tiempo real
        this.setupRealtimeValidation();
        
        // Detectar honeypots
        this.setupHoneypotProtection();
    }

    preventDoubleSubmit() {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function() {
                const submitBtn = this.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Procesando...';
                    
                    // Re-habilitar después de 10 segundos por si falla
                    setTimeout(() => {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = submitBtn.getAttribute('data-original-text') || 'Enviar';
                    }, 10000);
                }
            });
        });
    }

    setupRealtimeValidation() {
        // Username validation
        const usernameInput = document.getElementById('id_username');
        if (usernameInput) {
            usernameInput.addEventListener('input', this.validateUsername.bind(this));
        }

        // Email validation
        const emailInput = document.getElementById('id_email');
        if (emailInput) {
            emailInput.addEventListener('input', this.validateEmail.bind(this));
        }
    }

    validateUsername(event) {
        const username = event.target.value;
        const feedback = document.getElementById('username-feedback');
        
        if (username.length < 3) {
            this.showFieldFeedback(event.target, 'Mínimo 3 caracteres', 'warning');
        } else if (!/^[a-zA-Z0-9_]+$/.test(username)) {
            this.showFieldFeedback(event.target, 'Solo letras, números y guiones bajos', 'error');
        } else {
            this.showFieldFeedback(event.target, 'Nombre de usuario válido', 'success');
        }
    }

    validateEmail(event) {
        const email = event.target.value;
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (email && !emailRegex.test(email)) {
            this.showFieldFeedback(event.target, 'Formato de email inválido', 'error');
        } else if (email) {
            this.showFieldFeedback(event.target, 'Email válido', 'success');
        }
    }

    showFieldFeedback(field, message, type) {
        // Remover feedback anterior
        const existingFeedback = field.parentNode.querySelector('.field-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }

        // Crear nuevo feedback
        const feedback = document.createElement('div');
        feedback.className = `field-feedback small mt-1`;
        
        const colors = {
            'success': 'text-success',
            'warning': 'text-warning', 
            'error': 'text-danger'
        };

        const icons = {
            'success': 'fas fa-check',
            'warning': 'fas fa-exclamation-triangle',
            'error': 'fas fa-times'
        };

        feedback.className += ` ${colors[type]}`;
        feedback.innerHTML = `<i class="${icons[type]} me-1"></i>${message}`;
        
        field.parentNode.appendChild(feedback);
    }

    setupHoneypotProtection() {
        // Ocultar campos honeypot
        const honeypots = document.querySelectorAll('input[name="website"]');
        honeypots.forEach(input => {
            input.style.display = 'none';
            input.setAttribute('tabindex', '-1');
            input.setAttribute('autocomplete', 'off');
        });
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar validador de contraseñas
    new PasswordValidator('id_password1', 'password-strength');
    new PasswordValidator('password-input', 'password-strength');
    
    // Inicializar validador de formularios
    new SecurityFormValidator();
    
    // Mostrar avisos de seguridad
    if (window.location.protocol !== 'https:' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        console.warn('⚠️ Conexión no segura. Se recomienda usar HTTPS en producción.');
    }
});
