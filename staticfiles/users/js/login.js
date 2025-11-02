// verificar.js

document.addEventListener('DOMContentLoaded', () => {
    // --- Fade-in general ---
    document.body.style.opacity = 0;
    document.body.style.transition = 'opacity 0.6s ease';
    setTimeout(() => {
        document.body.style.opacity = 1;
    }, 100);

    // --- Hover suave en botones ---
    const buttons = document.querySelectorAll('.btn-submit, .resend-link, .back-link a');
    buttons.forEach(btn => {
        btn.addEventListener('mouseenter', () => {
            btn.style.transition = 'transform 0.2s ease';
            btn.style.transform = 'translateY(-2px)';
        });
        btn.addEventListener('mouseleave', () => {
            btn.style.transform = 'translateY(0)';
        });
    });

    // --- Simulación de reenviar correo ---
    const resendLink = document.querySelector('.resend-link');
    if (resendLink) {
        resendLink.addEventListener('click', (e) => {
            e.preventDefault();

            // Crear notificación temporal
            const message = document.createElement('div');
            message.textContent = 'Correo de verificación reenviado ✅';
            message.style.position = 'fixed';
            message.style.bottom = '30px';
            message.style.left = '50%';
            message.style.transform = 'translateX(-50%)';
            message.style.background = '#48bb78';
            message.style.color = 'white';
            message.style.padding = '0.8rem 1.5rem';
            message.style.borderRadius = '10px';
            message.style.boxShadow = '0 6px 15px rgba(72, 187, 120, 0.3)';
            message.style.fontSize = '0.95rem';
            message.style.opacity = '0';
            message.style.transition = 'opacity 0.4s ease';

            document.body.appendChild(message);
            setTimeout(() => { message.style.opacity = '1'; }, 100);
            setTimeout(() => {
                message.style.opacity = '0';
                setTimeout(() => message.remove(), 500);
            }, 2500);
        });
    }
});
