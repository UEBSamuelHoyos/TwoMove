console.log('1. Archivo cancel_reservation.js cargado');

// Configuración de la API
const API_BASE = '/alquileres/api/rentals';

// Variables globales
let reservasData = [];
let selectedReserva = null;

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    console.log('2. DOM cargado - Inicializando página de cancelación');
    
    // Inicializar sidebar móvil
    initMobileSidebar();
    
    // Inicializar scroll header
    initScrollHeader();
    
    // Cargar reservas
    cargarReservas();
    
    // Event Listeners
    initEventListeners();
});

// ==================== SIDEBAR MÓVIL ====================
function initMobileSidebar() {
    const menuToggle = document.getElementById('menuToggle');
    const closeSidebar = document.getElementById('closeSidebar');
    const sidebar = document.getElementById('sidebar');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            sidebar.classList.add('active');
            console.log('Sidebar abierto');
        });
    }
    
    if (closeSidebar) {
        closeSidebar.addEventListener('click', function(e) {
            e.stopPropagation();
            sidebar.classList.remove('active');
            console.log('Sidebar cerrado');
        });
    }
    
    // Cerrar sidebar al hacer clic fuera
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            const isLinkClick = e.target.closest('.sidebar-nav a, .logout-btn');
            if (isLinkClick) return;
            if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
                sidebar.classList.remove('active');
            }
        }
    });
    
    // Cerrar sidebar al navegar
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

// ==================== EVENT LISTENERS ====================
function initEventListeners() {
    const reservaSelect = document.getElementById('reservaSelect');
    const cancelBtn = document.getElementById('cancelBtn');
    
    // Cambio en el selector de reservas
    if (reservaSelect) {
        reservaSelect.addEventListener('change', function() {
            const reservaId = this.value;
            if (reservaId) {
                mostrarDetallesReserva(reservaId);
            } else {
                ocultarDetallesReserva();
            }
        });
    }
    
    // Botón de cancelar
    if (cancelBtn) {
        cancelBtn.addEventListener('click', cancelarReserva);
    }
}

// ==================== OBTENER TOKEN CSRF ====================
function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
            return decodeURIComponent(cookie.substring(name.length + 1));
        }
    }
    return '';
}

// ==================== CARGAR RESERVAS ====================
async function cargarReservas() {
    console.log('3. Cargando reservas del usuario...');
    const select = document.getElementById('reservaSelect');
    const cancelBtn = document.getElementById('cancelBtn');
    
    try {
        const response = await fetch(`${API_BASE}/mis_reservas/`, { 
            credentials: 'include' 
        });
        
        if (!response.ok) {
            throw new Error(`Error HTTP ${response.status}`);
        }
        
        const reservas = await response.json();
        console.log('4. Reservas obtenidas:', reservas);
        
        reservasData = reservas;
        select.innerHTML = '';
        
        if (!reservas.length) {
            select.innerHTML = '<option value="">No tienes reservas activas</option>';
            cancelBtn.disabled = true;
            mostrarAlerta('No tienes reservas activas para cancelar', 'warning');
            return;
        }
        
        // Opción por defecto
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'Selecciona una reserva...';
        select.appendChild(defaultOption);
        
        // Agregar reservas al selector
        reservas.forEach(reserva => {
            const option = document.createElement('option');
            option.value = reserva.id;
            
            const fecha = reserva.fecha_reserva || 'Sin fecha';
            const hora = reserva.hora_reserva || '';
            const origen = reserva.estacion_origen || 'Desconocida';
            const tipo = reserva.tipo_viaje === 'ultima_milla' ? 'Última Milla' : 'Recorrido Largo';
            const costo = reserva.costo_estimado ? ` - $${formatearNumero(reserva.costo_estimado)}` : '';
            
            option.textContent = `${fecha} ${hora} | ${tipo} (${origen})${costo}`;
            option.dataset.reserva = JSON.stringify(reserva);
            
            select.appendChild(option);
        });
        
        console.log('5. Selector de reservas poblado');
        
    } catch (error) {
        console.error('Error al cargar reservas:', error);
        select.innerHTML = '<option value="">Error al cargar reservas</option>';
        cancelBtn.disabled = true;
        mostrarAlerta('Error al obtener tus reservas. Por favor, recarga la página.', 'danger');
    }
}

// ==================== MOSTRAR DETALLES DE RESERVA ====================
function mostrarDetallesReserva(reservaId) {
    const reserva = reservasData.find(r => r.id == reservaId);
    const cancelBtn = document.getElementById('cancelBtn');
    
    if (!reserva) {
        console.error('Reserva no encontrada:', reservaId);
        return;
    }
    
    console.log('6. Mostrando detalles de reserva:', reserva);
    selectedReserva = reserva;
    
    // Mostrar contenedor de detalles
    const detailsContainer = document.getElementById('reservaDetails');
    detailsContainer.style.display = 'block';
    
    // Poblar detalles
    document.getElementById('detailFecha').textContent = reserva.fecha_reserva || 'Sin fecha';
    document.getElementById('detailHora').textContent = reserva.hora_reserva || 'Sin hora';
    document.getElementById('detailEstacion').textContent = reserva.estacion_origen || 'Desconocida';
    document.getElementById('detailTipo').textContent = 
        reserva.tipo_viaje === 'ultima_milla' ? 'Última Milla' : 'Recorrido Largo';
    document.getElementById('detailCosto').textContent = 
        reserva.costo_estimado ? `$${formatearNumero(reserva.costo_estimado)} COP` : 'Por calcular';
    
    // Estado
    const estadoBadge = document.getElementById('detailEstado');
    estadoBadge.textContent = reserva.estado || 'Pendiente';
    estadoBadge.className = 'status-badge ' + (reserva.estado === 'activa' ? 'activa' : 'pendiente');
    
    // Habilitar botón de cancelar
    cancelBtn.disabled = false;
}

// ==================== OCULTAR DETALLES ====================
function ocultarDetallesReserva() {
    const detailsContainer = document.getElementById('reservaDetails');
    const cancelBtn = document.getElementById('cancelBtn');
    
    detailsContainer.style.display = 'none';
    cancelBtn.disabled = true;
    selectedReserva = null;
}

// ==================== CANCELAR RESERVA ====================
async function cancelarReserva() {
    console.log('7. Iniciando cancelación de reserva...');
    
    const select = document.getElementById('reservaSelect');
    const reasonInput = document.getElementById('reasonInput');
    const cancelBtn = document.getElementById('cancelBtn');
    
    const reservaId = select.value;
    const reason = reasonInput.value.trim();
    
    // Validaciones
    if (!reservaId || reservaId === "No tienes reservas activas") {
        mostrarAlerta('Por favor, selecciona una reserva válida.', 'warning');
        return;
    }
    
    if (!reason) {
        mostrarAlerta('Por favor, indica el motivo de la cancelación.', 'warning');
        reasonInput.focus();
        return;
    }
    
    // Confirmar cancelación
    if (!confirm('¿Estás seguro de que deseas cancelar esta reserva?')) {
        return;
    }
    
    // Deshabilitar botón
    cancelBtn.disabled = true;
    cancelBtn.innerHTML = '<span class="btn-icon">⏳</span>Cancelando...';
    
    try {
        const response = await fetch(`${API_BASE}/cancel_general/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            credentials: 'include',
            body: JSON.stringify({ 
                rental_id: reservaId, 
                reason: reason 
            })
        });
        
        if (response.ok) {
            console.log('8. Reserva cancelada exitosamente');
            mostrarAlerta('✅ Reserva cancelada correctamente. El saldo ha sido devuelto a tu billetera.', 'success');
            
            // Limpiar formulario
            reasonInput.value = '';
            ocultarDetallesReserva();
            
            // Recargar reservas
            await cargarReservas();
            
        } else {
            const error = await response.json();
            console.error('Error al cancelar:', error);
            mostrarAlerta(`Error: ${error.detail || 'No se pudo cancelar la reserva.'}`, 'danger');
            cancelBtn.disabled = false;
            cancelBtn.innerHTML = '<span class="btn-icon">❌</span>Cancelar Reserva';
        }
        
    } catch (error) {
        console.error('Error inesperado:', error);
        mostrarAlerta('Error inesperado al cancelar la reserva. Por favor, intenta de nuevo.', 'danger');
        cancelBtn.disabled = false;
        cancelBtn.innerHTML = '<span class="btn-icon">❌</span>Cancelar Reserva';
    }
}

// ==================== MOSTRAR ALERTA ====================
function mostrarAlerta(mensaje, tipo = 'info') {
    const alertContainer = document.getElementById('alertMessage');
    
    // Limpiar clases anteriores
    alertContainer.className = 'alert-container';
    
    // Agregar clase según el tipo
    if (tipo === 'success') {
        alertContainer.classList.add('alert-success');
    } else if (tipo === 'danger') {
        alertContainer.classList.add('alert-danger');
    } else if (tipo === 'warning') {
        alertContainer.classList.add('alert-warning');
    }
    
    alertContainer.textContent = mensaje;
    alertContainer.style.display = 'block';
    
    // Auto-ocultar después de 5 segundos
    setTimeout(() => {
        alertContainer.style.display = 'none';
    }, 5000);
    
    // Scroll hacia arriba para ver la alerta
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ==================== UTILIDADES ====================
function formatearNumero(numero) {
    return new Intl.NumberFormat('es-CO').format(numero);
}

console.log('9. Todas las funciones cargadas correctamente');