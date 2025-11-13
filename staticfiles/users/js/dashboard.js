console.log('1. Archivo dashboard.js cargado');

// Configuración de la API
const API_BASE = '/alquileres/api/rentals';

document.addEventListener('DOMContentLoaded', function() {
    console.log('2. DOM cargado');
    
    // Inicializar sidebar móvil
    initMobileSidebar();
    
    // Inicializar scroll header
    initScrollHeader();
    
    // Convertir saldo a USD
    convertirSaldoUSD();
    
    // Cargar estadísticas del usuario
    cargarEstadisticas();
});

// ==================== CARGAR ESTADÍSTICAS ====================
async function cargarEstadisticas() {
    console.log('3. Cargando estadísticas del usuario...');
    
    try {
        const response = await fetch(`${API_BASE}/estadisticas/`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error(`Error HTTP ${response.status}`);
        }
        
        const stats = await response.json();
        console.log('4. Estadísticas obtenidas:', stats);
        
        // Actualizar el DOM con las estadísticas
        actualizarEstadisticas(stats);
        
    } catch (error) {
        console.error('Error al cargar estadísticas:', error);
        // Mantener valores por defecto si hay error
    }
}

// ==================== ACTUALIZAR ESTADÍSTICAS EN EL DOM ====================
function actualizarEstadisticas(stats) {
    // Actualizar viajes del mes
    const viajesMesElements = document.querySelectorAll('.stat-value');
    if (viajesMesElements[1]) {
        viajesMesElements[1].textContent = stats.viajes_mes || '0';
    }
    
    // Actualizar tiempo total
    if (viajesMesElements[2]) {
        viajesMesElements[2].textContent = stats.tiempo_total || '0h 0min';
    }
    
    // Actualizar nivel
    if (viajesMesElements[3]) {
        viajesMesElements[3].textContent = stats.nivel || 'Nuevo';
    }
    
    console.log('5. Estadísticas actualizadas en el dashboard');
}

// ==================== CONVERTIR SALDO A USD ====================
function convertirSaldoUSD() {
    const balanceCopElement = document.getElementById('balance-cop');
    const balanceUsdElement = document.getElementById('balance-usd');
    
    if (balanceCopElement && balanceUsdElement) {
        const balanceText = balanceCopElement.textContent;
        const balanceCOP = parseFloat(balanceText.replace(/[^0-9]/g, ''));
        
        if (balanceCOP > 0) {
            const balanceUSD = (balanceCOP * 0.00025).toFixed(2);
            balanceUsdElement.textContent = `≈ $${balanceUSD} USD`;
        }
    }
}

// ==================== SIDEBAR MÓVIL ====================
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
    
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            const isLinkClick = e.target.closest('.sidebar-nav a, .logout-btn');
            if (isLinkClick) return;
            if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
                sidebar.classList.remove('active');
            }
        }
    });
    
    document.querySelectorAll('.sidebar-nav a, .logout-btn').forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                setTimeout(() => sidebar.classList.remove('active'), 100);
            }
        });
    });
}

// ==================== SCROLL HEADER ====================
function initScrollHeader() {
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
}

console.log('6. Todas las funciones cargadas correctamente');