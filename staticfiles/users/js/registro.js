// registro.js - TwoMove

document.addEventListener('DOMContentLoaded', () => {
    // --- Fade-in suave de toda la página ---
    document.body.style.opacity = 0;
    document.body.style.transition = 'opacity 0.7s ease';
    setTimeout(() => {
        document.body.style.opacity = 1;
    }, 50);

    // --- Validación en tiempo real ---
    const form = document.querySelector('.registro-form');
    const inputs = form.querySelectorAll('input');
    
    inputs.forEach(input => {
        // Animación al hacer focus
        input.addEventListener('focus', () => {
            input.parentElement.style.transition = 'all 0.3s ease';
        });

        // Validación mientras escribe
        input.addEventListener('input', () => {
            validateField(input);
        });

        // Validación al perder el foco
        input.addEventListener('blur', () => {
            validateField(input);
        });
    });

    // --- Función de validación ---
    function validateField(input) {
        const value = input.value.trim();
        const fieldName = input.name || input.id;

        // Email
        if (fieldName.includes('email')) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (value && !emailRegex.test(value)) {
                setFieldError(input, 'Email inválido');
            } else {
                clearFieldError(input);
            }
        }

        // Celular
        if (fieldName.includes('celular')) {
            const phoneRegex = /^[0-9]{10,}$/;
            if (value && !phoneRegex.test(value)) {
                setFieldError(input, 'Número de celular inválido');
            } else {
                clearFieldError(input);
            }
        }

        // Contraseña
        if (fieldName.includes('contrasena') && !fieldName.includes('confirmar')) {
            if (value && value.length < 8) {
                setFieldError(input, 'Mínimo 8 caracteres');
            } else {
                clearFieldError(input);
            }
        }

        // Confirmar contraseña
        if (fieldName.includes('confirmar')) {
            const passwordInput = document.querySelector('[name*="contrasena"]:not([name*="confirmar"])');
            if (passwordInput && value !== passwordInput.value) {
                setFieldError(input, 'Las contraseñas no coinciden');
            } else {
                clearFieldError(input);
            }
        }
    }

    function setFieldError(input, message) {
        input.style.borderColor = '#ef4444';
        input.style.background = '#fef2f2';
        
        // Remover error anterior si existe
        const existingError = input.parentElement.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }

        // Agregar mensaje de error
        const errorSpan = document.createElement('small');
        errorSpan.className = 'error-message';
        errorSpan.style.color = '#dc2626';
        errorSpan.style.fontSize = '0.8rem';
        errorSpan.style.marginTop = '0.3rem';
        errorSpan.textContent = message;
        input.parentElement.appendChild(errorSpan);
    }

    function clearFieldError(input) {
        input.style.borderColor = '#e5e7eb';
        input.style.background = '#fafafa';
        
        const errorMessage = input.parentElement.querySelector('.error-message');
        if (errorMessage) {
            errorMessage.remove();
        }
    }

    // --- Animación del botón de submit ---
    const submitBtn = document.querySelector('.btn-registro');
    if (submitBtn) {
        submitBtn.addEventListener('mouseenter', () => {
            submitBtn.style.transition = 'all 0.3s ease';
        });
    }

    // --- Efecto en los enlaces ---
    const links = document.querySelectorAll('.link-login, .back-link a');
    links.forEach(link => {
        link.addEventListener('mouseenter', () => {
            link.style.transition = 'color 0.2s ease, transform 0.2s ease';
        });
    });

    // --- Prevenir envío si hay errores ---
    form.addEventListener('submit', (e) => {
        const errors = form.querySelectorAll('.error-message');
        
        if (errors.length > 0) {
            e.preventDefault();
            
            // Mostrar notificación
            showNotification('Por favor corrige los errores antes de continuar', 'error');
            
            // Scroll al primer error
            const firstError = errors[0];
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
            // Deshabilitar botón y mostrar loading
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span>Creando cuenta...</span>';
            submitBtn.style.opacity = '0.7';
            submitBtn.style.cursor = 'not-allowed';
        }
    });

    // --- Sistema de notificaciones ---
    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Estilos
        Object.assign(notification.style, {
            position: 'fixed',
            bottom: '30px',
            left: '50%',
            transform: 'translateX(-50%)',
            background: type === 'success' ? '#22c55e' : '#ef4444',
            color: 'white',
            padding: '1rem 1.5rem',
            borderRadius: '12px',
            boxShadow: '0 8px 20px rgba(0, 0, 0, 0.15)',
            fontSize: '0.95rem',
            fontWeight: '600',
            opacity: '0',
            transition: 'opacity 0.4s ease, transform 0.4s ease',
            zIndex: '9999'
        });

        document.body.appendChild(notification);

        // Animación de entrada
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(-50%) translateY(-10px)';
        }, 100);

        // Animación de salida
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(-50%) translateY(0)';
            setTimeout(() => notification.remove(), 400);
        }, 3500);
    }

    // --- Animación de carga para inputs ---
    inputs.forEach((input, index) => {
        input.style.opacity = '0';
        input.style.transform = 'translateY(10px)';
        
        setTimeout(() => {
            input.style.transition = 'all 0.4s ease';
            input.style.opacity = '1';
            input.style.transform = 'translateY(0)';
        }, 100 + (index * 50));
    });

    // --- Efecto parallax suave en scroll ---
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const registroCard = document.querySelector('.registro-card');
        
        if (registroCard) {
            registroCard.style.transform = `translateY(${scrolled * 0.05}px)`;
        }
    });
});