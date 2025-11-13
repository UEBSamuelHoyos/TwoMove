// TwoMove - Agregar Tarjeta JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Agregar Tarjeta cargada correctamente');
    
    // Inicializar sidebar móvil
    initMobileSidebar();
    
    // Inicializar Stripe
    initStripe();
});

// Sidebar móvil
function initMobileSidebar() {
    const menuToggle = document.getElementById('menuToggle');
    const closeSidebar = document.getElementById('closeSidebar');
    const sidebar = document.getElementById('sidebar');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            sidebar.classList.add('active');
        });
    }
    
    if (closeSidebar) {
        closeSidebar.addEventListener('click', function(e) {
            e.stopPropagation();
            sidebar.classList.remove('active');
        });
    }
    
    // Cerrar sidebar al hacer click fuera
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            const isLinkClick = e.target.closest('.sidebar-nav a, .logout-btn');
            
            if (isLinkClick) {
                return;
            }
            
            if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
                sidebar.classList.remove('active');
            }
        }
    });
    
    // Permitir navegación en enlaces del sidebar
    document.querySelectorAll('.sidebar-nav a, .logout-btn').forEach(link => {
        link.addEventListener('click', function (e) {
            if (window.innerWidth <= 768) {
                setTimeout(() => {
                    sidebar.classList.remove('active');
                }, 100);
            }
        });
    });
}

// Inicializar Stripe
function initStripe() {
    // Verificar que las variables estén disponibles
    if (!window.stripePublicKey || !window.clientSecret) {
        console.error('Error: No se encontraron las claves de Stripe');
        showMessage('Error al inicializar el sistema de pagos', 'error');
        return;
    }

    // Inicializar Stripe
    const stripe = Stripe(window.stripePublicKey);
    const elements = stripe.elements();
    
    // Crear elemento de tarjeta con estilos personalizados
    const cardElement = elements.create('card', {
        hidePostalCode: true,
        style: {
            base: {
                fontSize: '16px',
                color: '#2d3748',
                fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                '::placeholder': {
                    color: '#a0aec0',
                },
                iconColor: '#48bb78',
            },
            invalid: {
                color: '#e53e3e',
                iconColor: '#e53e3e',
            },
        },
    });
    
    // Montar el elemento en el DOM
    cardElement.mount('#card-element');
    
    // Manejar errores en tiempo real
    const cardErrors = document.getElementById('card-errors');
    cardElement.on('change', function(event) {
        if (event.error) {
            cardErrors.textContent = event.error.message;
        } else {
            cardErrors.textContent = '';
        }
    });
    
    // Manejar el envío del formulario
    const form = document.getElementById('form-tarjeta');
    const btnGuardar = document.getElementById('btn-guardar');
    const mensaje = document.getElementById('mensaje');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Deshabilitar botón y mostrar estado de carga
        btnGuardar.disabled = true;
        btnGuardar.innerHTML = '<span class="btn-icon">⏳</span><span>Procesando...</span>';
        mensaje.innerHTML = '';
        
        try {
            // Confirmar SetupIntent con Stripe
            const { setupIntent, error } = await stripe.confirmCardSetup(
                window.clientSecret,
                {
                    payment_method: {
                        card: cardElement,
                        billing_details: {
                            name: window.userName
                        }
                    }
                }
            );
            
            if (error) {
                // Error de Stripe
                showMessage(`❌ ${error.message}`, 'error');
                resetButton(btnGuardar);
                return;
            }
            
            // Enviar payment_method_id al backend
            const response = await fetch(window.guardarTarjetaUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.csrfToken
                },
                body: JSON.stringify({
                    payment_method_id: setupIntent.payment_method
                })
            });
            
            const data = await response.json();
            
            if (response.ok && data.mensaje) {
                // Éxito
                showMessage(`✅ ${data.mensaje}`, 'success');
                
                // Limpiar el formulario
                cardElement.clear();
                
                // Redireccionar después de 2 segundos
                setTimeout(() => {
                    window.location.href = '/payment/';
                }, 2000);
            } else {
                // Error del backend
                showMessage(`❌ ${data.error || 'Error al guardar la tarjeta'}`, 'error');
                resetButton(btnGuardar);
            }
            
        } catch (error) {
            console.error('Error:', error);
            showMessage('❌ Error de conexión con el servidor', 'error');
            resetButton(btnGuardar);
        }
    });
}

// Mostrar mensajes
function showMessage(text, type) {
    const mensaje = document.getElementById('mensaje');
    mensaje.textContent = text;
    mensaje.className = `mensaje ${type}`;
}

// Resetear botón
function resetButton(button) {
    button.disabled = false;
    button.innerHTML = '<span class="btn-icon">💾</span><span>Guardar Tarjeta</span>';
}

// Animación al hacer scroll en header
let lastScroll = 0;
window.addEventListener('scroll', function() {
    const header = document.querySelector('.dashboard-header');
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > lastScroll && currentScroll > 80) {
        header.style.transform = 'translateY(-100%)';
    } else {
        header.style.transform = 'translateY(0)';
    }
    
    lastScroll = currentScroll;
});