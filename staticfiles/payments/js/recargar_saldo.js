// TwoMove - Recargar Saldo JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Recargar Saldo cargada correctamente');
    
    // Inicializar sidebar móvil
    initMobileSidebar();
    
    // Inicializar funcionalidades de recarga
    initRechargeForm();
    
    // Calcular y mostrar conversión a USD
    initCurrencyConversion();
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

// Inicializar formulario de recarga
function initRechargeForm() {
    const amountInput = document.getElementById('amount');
    const amountButtons = document.querySelectorAll('.amount-btn');
    const form = document.getElementById('recharge-form');
    const btnRecharge = document.getElementById('btn-recharge');
    
    // Manejar botones de monto rápido
    amountButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remover selección de todos los botones
            amountButtons.forEach(btn => btn.classList.remove('selected'));
            
            // Marcar este botón como seleccionado
            this.classList.add('selected');
            
            // Actualizar el valor del input (sin formato, solo número)
            const amount = this.getAttribute('data-amount');
            amountInput.value = amount;
        });
    });
    
    // Remover selección cuando se escribe manualmente
    amountInput.addEventListener('input', function() {
        amountButtons.forEach(btn => btn.classList.remove('selected'));
        updateAmountPreview(this.value);
    });
    
    // Validar formulario antes de enviar
    form.addEventListener('submit', function(e) {
        const amount = parseInt(amountInput.value);
        
        if (isNaN(amount) || amount < 1000) {
            e.preventDefault();
            showNotification('El monto mínimo de recarga es $1,000 COP', 'error');
            return;
        }
        
        // Cambiar estado del botón
        btnRecharge.disabled = true;
        btnRecharge.innerHTML = '<span class="btn-icon">⏳</span><span>Procesando...</span>';
    });
}

// Inicializar conversión de moneda
function initCurrencyConversion() {
    // Tasa de cambio COP a USD (aproximada, puedes ajustarla)
    const EXCHANGE_RATE = 0.00025; // 1 COP = 0.00025 USD (aprox 4000 COP = 1 USD)
    window.exchangeRate = EXCHANGE_RATE;
    
    // Convertir saldo actual en el balance card
    if (window.walletBalance) {
        const balanceUSD = (window.walletBalance * EXCHANGE_RATE).toFixed(2);
        const balanceUsdElement = document.getElementById('balance-usd');
        if (balanceUsdElement) {
            balanceUsdElement.textContent = `≈ ${balanceUSD} USD`;
        }
    }
}

// Actualizar preview de conversión
function updateAmountPreview(amount) {
    const preview = document.getElementById('amount-preview');
    
    if (!amount || amount <= 0) {
        preview.classList.remove('show');
        return;
    }
    
    const amountNum = parseInt(amount);
    if (isNaN(amountNum)) {
        preview.classList.remove('show');
        return;
    }
    
    // Calcular USD
    const amountUSD = (amountNum * window.exchangeRate).toFixed(2);
    
    // Formatear COP con separadores de miles
    const amountCOPFormatted = amountNum.toLocaleString('es-CO');
    
    // Actualizar preview
    const previewCOP = preview.querySelector('.preview-cop');
    const previewUSD = preview.querySelector('.preview-usd');
    
    if (previewCOP) previewCOP.textContent = `${amountCOPFormatted} COP`;
    if (previewUSD) previewUSD.textContent = `${amountUSD} USD`;
    
    preview.classList.add('show');
}

// Mostrar notificación
function showNotification(message, type) {
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.innerHTML = `
        <span class="alert-icon">${type === 'error' ? '❌' : '✅'}</span>
        <span>${message}</span>
    `;
    
    // Insertar antes del formulario
    const form = document.getElementById('recharge-form');
    form.parentElement.insertBefore(notification, form);
    
    // Remover después de 5 segundos
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Animación para remover notificaciones
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(-20px);
        }
    }
`;
document.head.appendChild(style);

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

// Auto-ocultar alertas después de 8 segundos
document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
        alert.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => alert.remove(), 300);
    }, 8000);
});