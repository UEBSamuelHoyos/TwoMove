// TwoMove Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard cargado correctamente');
    
    initNavigation();
    initMobileSidebar();
    initTripTimer();
    initAmountButtons();
});

// --- Navegación entre secciones ---
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.content-section');
    
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            navItems.forEach(nav => nav.classList.remove('active'));
            sections.forEach(section => section.classList.remove('active'));
            
            this.classList.add('active');
            
            const sectionId = this.getAttribute('data-section');
            const targetSection = document.getElementById(sectionId);
            if (targetSection) {
                targetSection.classList.add('active');
            }
            
            if (window.innerWidth <= 768) {
                document.getElementById('sidebar').classList.remove('active');
            }
            
            window.scrollTo(0, 0);
        });
    });
}

// --- Navegación programática ---
function navigateTo(sectionId) {
    const targetNav = document.querySelector(`[data-section="${sectionId}"]`);
    if (targetNav) targetNav.click();
}

// --- Sidebar móvil ---
function initMobileSidebar() {
    const menuToggle = document.getElementById('menuToggle');
    const closeSidebar = document.getElementById('closeSidebar');
    const sidebar = document.getElementById('sidebar');
    
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function(e) {
            e.stopPropagation(); // evita cierre inmediato
            sidebar.classList.toggle('active');
        });
    }
    
    if (closeSidebar) {
        closeSidebar.addEventListener('click', function() {
            sidebar.classList.remove('active');
        });
    }
    
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768 && sidebar.classList.contains('active')) {
            if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
                sidebar.classList.remove('active');
            }
        }
    });
}

// --- Timer del viaje activo ---
function initTripTimer() {
    const timerElement = document.getElementById('tripTimer');
    if (timerElement) {
        let seconds = 0;
        let minutes = 45;
        let hours = 0;
        
        setInterval(function() {
            seconds++;
            if (seconds >= 60) {
                seconds = 0;
                minutes++;
            }
            if (minutes >= 60) {
                minutes = 0;
                hours++;
            }
            
            const formattedTime = 
                String(hours).padStart(2, '0') + ':' +
                String(minutes).padStart(2, '0') + ':' +
                String(seconds).padStart(2, '0');
            
            timerElement.textContent = formattedTime;
        }, 1000);
    }
}

// --- Botones de montos de recarga ---
function initAmountButtons() {
    const amountButtons = document.querySelectorAll('.amount-btn');
    
    amountButtons.forEach(button => {
        button.addEventListener('click', function() {
            const amount = this.getAttribute('data-amount');
            rechargeBalance(amount);
        });
    });
}

// --- Función para recargar saldo ---
function rechargeBalance(amount) {
    console.log('Recargando saldo:', amount);
    
    if (confirm(`¿Confirmas la recarga de $${Number(amount).toLocaleString()}?`)) {
        alert('Recarga exitosa! (Conectar con backend)');
    }
}

// --- Recarga personalizada ---
function rechargeCustom() {
    const customAmount = document.getElementById('customAmount').value;
    
    if (!customAmount || customAmount <= 0) {
        alert('Por favor ingresa un monto válido');
        return;
    }
    rechargeBalance(customAmount);
}

// --- Iniciar viaje ---
function startTrip() {
    if (confirm('¿Deseas iniciar un nuevo viaje?')) {
        alert('Iniciando viaje... (Conectar con backend)');
    }
}

// --- Obtener CSRF de Django ---
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// --- Formularios ---
const forms = document.querySelectorAll('form');
forms.forEach(form => {
    form.addEventListener('submit', function(e) {
        console.log('Formulario enviado:', this.action);
    });
});

// --- Smooth scroll UX ---
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        }
    });
});
