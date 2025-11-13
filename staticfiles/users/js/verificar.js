// Limitar solo números en el campo de código
        const codigoInput = document.getElementById('codigo');
        codigoInput.addEventListener('input', function(e) {
            this.value = this.value.replace(/[^0-9]/g, '').slice(0, 6);
        });

        // Auto-focus en el campo de código
        codigoInput.focus();

        function handleSubmit(event) {
            event.preventDefault();
            alert('Formulario enviado - Aquí conectarías con tu backend');
        }

        function resendCode(event) {
            event.preventDefault();
            const link = event.target;
            link.style.pointerEvents = 'none';
            link.style.color = '#a0aec0';
            
            let seconds = 60;
            const originalText = link.textContent;
            
            const countdown = setInterval(() => {
                link.textContent = `Reenviar en ${seconds}s`;
                seconds--;
                
                if (seconds < 0) {
                    clearInterval(countdown);
                    link.textContent = originalText;
                    link.style.pointerEvents = 'auto';
                    link.style.color = '#48bb78';
                }
            }, 1000);
            
            alert('Código reenviado a tu correo');
        }