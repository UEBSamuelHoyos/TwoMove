document.addEventListener('DOMContentLoaded', () => {
    // --- Fade-in con efecto de escala ---
    document.body.style.opacity = 0;
    document.body.style.transform = 'scale(0.98)';
    document.body.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    
    setTimeout(() => {
        document.body.style.opacity = 1;
        document.body.style.transform = 'scale(1)';
    }, 50);

    // --- Referencias ---
    const form = document.querySelector('.recuperar-form');
    const emailInput = document.querySelector('#email');
    const submitBtn = document.querySelector('.btn-recuperar');

    // Verificar que los elementos existen antes de continuar
    if (!form || !emailInput || !submitBtn) {
        console.warn('Algunos elementos del formulario no se encontraron');
        return;
    }

    // --- Validación de email en tiempo real ---
    emailInput.addEventListener('input', () => {
        validateEmail(emailInput);
    });

    emailInput.addEventListener('blur', () => {
        validateEmail(emailInput);
    });

    // Animación al hacer focus
    emailInput.addEventListener('focus', () => {
        emailInput.style.transition = 'all 0.3s ease';
    });

    // --- Función de validación de email ---
    function validateEmail(input) {
        const value = input.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (value === '') {
            clearFieldError(input);
            return;
        }

        if (!emailRegex.test(value)) {
            setFieldError(input, 'Por favor ingresa un correo válido');
        } else {
            setFieldSuccess(input);
        }
    }

    function setFieldError(input, message) {
        input.style.borderColor = '#ef4444';
        input.style.background = '#fef2f2';
        
        const existingError = input.parentElement.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }

        const errorSpan = document.createElement('small');
        errorSpan.className = 'error-message';
        errorSpan.style.color = '#dc2626';
        errorSpan.style.fontSize = '0.82rem';
        errorSpan.style.marginTop = '0.4rem';
        errorSpan.style.display = 'flex';
        errorSpan.style.alignItems = 'center';
        errorSpan.style.gap = '0.3rem';
        errorSpan.innerHTML = `
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="15" y1="9" x2="9" y2="15"></line>
                <line x1="9" y1="9" x2="15" y2="15"></line>
            </svg>
            ${message}
        `;
        
        input.parentElement.appendChild(errorSpan);
    }

    function setFieldSuccess(input) {
        input.style.borderColor = '#10b981';
        input.style.background = '#f0fdf4';
        
        const existingError = input.parentElement.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }

        const successSpan = document.createElement('small');
        successSpan.className = 'error-message';
        successSpan.style.color = '#059669';
        successSpan.style.fontSize = '0.82rem';
        successSpan.style.marginTop = '0.4rem';
        successSpan.style.display = 'flex';
        successSpan.style.alignItems = 'center';
        successSpan.style.gap = '0.3rem';
        successSpan.innerHTML = `
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
            Correo válido
        `;
        
        input.parentElement.appendChild(successSpan);
    }

    function clearFieldError(input) {
        input.style.borderColor = '#e2e8f0';
        input.style.background = '#f8fafc';
        
        const errorMessage = input.parentElement.querySelector('.error-message');
        if (errorMessage) {
            errorMessage.remove();
        }
    }

    // --- Prevenir envío con errores ---
    form.addEventListener('submit', (e) => {
        const emailValue = emailInput.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailValue || !emailRegex.test(emailValue)) {
            e.preventDefault();
            showNotification('Por favor ingresa un correo válido', 'error');
            emailInput.focus();
            return;
        }

        // Efecto de loading en el botón
        submitBtn.disabled = true;
        submitBtn.style.opacity = '0.7';
        submitBtn.style.cursor = 'not-allowed';
        
        submitBtn.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="animation: spin 1s linear infinite;">
                <circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle>
                <path d="M12 2a10 10 0 0 1 10 10" stroke-opacity="1"></path>
            </svg>
            <span>Enviando...</span>
        `;

        // Agregar animación de spin
        const style = document.createElement('style');
        style.textContent = `
            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    });

    // --- Sistema de notificaciones mejorado ---
    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        const icon = type === 'success' 
            ? '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>'
            : '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>';
        
        notification.innerHTML = `${icon}<span>${message}</span>`;
        
        Object.assign(notification.style, {
            position: 'fixed',
            bottom: '30px',
            left: '50%',
            transform: 'translateX(-50%)',
            background: type === 'success' ? '#3b82f6' : '#ef4444',
            color: 'white',
            padding: '1rem 1.5rem',
            borderRadius: '14px',
            boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
            fontSize: '0.95rem',
            fontWeight: '600',
            opacity: '0',
            transition: 'opacity 0.4s ease, transform 0.4s ease',
            zIndex: '9999',
            display: 'flex',
            alignItems: 'center',
            gap: '0.8rem',
            minWidth: '300px',
            maxWidth: '90%'
        });

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(-50%) translateY(-10px)';
        }, 100);

        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(-50%) translateY(0)';
            setTimeout(() => notification.remove(), 400);
        }, 4000);
    }

    // --- Animación de entrada del formulario ---
    const formElements = [emailInput, submitBtn];
    formElements.forEach((element, index) => {
        if (element) {
            element.style.opacity = '0';
            element.style.transform = 'translateX(-20px)';
            
            setTimeout(() => {
                element.style.transition = 'all 0.5s ease';
                element.style.opacity = '1';
                element.style.transform = 'translateX(0)';
            }, 200 + (index * 100));
        }
    });

    // --- Efecto hover en enlaces ---
    const links = document.querySelectorAll('.link-login, .link-registro, .back-link a');
    links.forEach(link => {
        link.addEventListener('mouseenter', () => {
            link.style.transition = 'all 0.2s ease';
        });
    });

    // --- Auto-focus en el input de email ---
    setTimeout(() => {
        if (emailInput) {
            emailInput.focus();
        }
    }, 600);

    // --- Efecto de partículas en el icono ---
    const icon = document.querySelector('.recuperar-icon');
    if (icon) {
        icon.addEventListener('mouseenter', () => {
            icon.style.transform = 'rotate(-5deg) scale(1.1)';
        });
        
        icon.addEventListener('mouseleave', () => {
            icon.style.transform = 'rotate(-5deg) scale(1)';
        });
    }

    // --- Detección de pegado de email ---
    emailInput.addEventListener('paste', (e) => {
        setTimeout(() => {
            validateEmail(emailInput);
        }, 100);
    });
});