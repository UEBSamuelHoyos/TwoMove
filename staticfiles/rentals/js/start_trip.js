console.log('1. Archivo start_trip.js cargado');

// Configuración de la API
const API_BASE = '/alquileres/api/rentals';

// Variables globales
let reservasData = [];
let selectedReserva = null;

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    console.log('2. DOM cargado - Inicializando página de inicio de viaje');
    
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

// ==================== EVENT LISTENERS ====================
function initEventListeners() {
    const startTripForm = document.getElementById('startTripForm');
    
    if (startTripForm) {
        startTripForm.addEventListener('submit', iniciarViaje);
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
    const listContainer = document.getElementById('reservasList');
    
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
        
        // Limpiar contenedor
        listContainer.innerHTML = '';
        
        // Mostrar mensaje si no hay reservas
        if (!reservas.length) {
            listContainer.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📭</div>
                    <p><strong>No tienes reservas activas</strong></p>
                    <p>Crea una reserva para poder iniciar un viaje</p>
                </div>
            `;
            return;
        }
        
        // Crear elementos de reserva
        reservas.forEach(reserva => {
            const reservaElement = crearReservaElement(reserva);
            listContainer.appendChild(reservaElement);
        });
        
        console.log('5. Lista de reservas renderizada');
        
    } catch (error) {
        console.error('Error al cargar reservas:', error);
        listContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">❌</div>
                <p><strong>Error al cargar reservas</strong></p>
                <p>Por favor, recarga la página</p>
            </div>
        `;
    }
}

// ==================== CREAR ELEMENTO DE RESERVA ====================
function crearReservaElement(reserva) {
    const div = document.createElement('div');
    div.className = 'reserva-item';
    div.dataset.reservaId = reserva.id;
    
    const fecha = reserva.fecha_reserva || 'Sin fecha';
    const hora = reserva.hora_reserva || '';
    const tipo = reserva.tipo_viaje === 'ultima_milla' ? 'Última Milla' : 'Recorrido Largo';
    const estado = reserva.estado || 'reservado';
    
    div.innerHTML = `
        <div class="reserva-header">
            <span class="reserva-id">Reserva #${reserva.id}</span>
            <span class="status-badge">${estado.charAt(0).toUpperCase() + estado.slice(1)}</span>
        </div>
        <div class="reserva-info">
            <span>📅 ${fecha} ${hora}</span>
            <span>📍 ${reserva.estacion_origen || 'N/A'}</span>
            <span>🚴 ${tipo}</span>
            <span>🚲 ${reserva.bike_serial_reservada || 'Por asignar'}</span>
        </div>
    `;
    
    // Event listener para seleccionar reserva
    div.addEventListener('click', function() {
        seleccionarReserva(reserva, div);
    });
    
    return div;
}

// ==================== SELECCIONAR RESERVA ====================
function seleccionarReserva(reserva, element) {
    console.log('6. Reserva seleccionada:', reserva);
    
    // Remover selección anterior
    document.querySelectorAll('.reserva-item').forEach(item => {
        item.classList.remove('selected');
    });
    
    // Seleccionar nueva
    element.classList.add('selected');
    selectedReserva = reserva;
    
    // Mostrar detalles
    mostrarDetallesReserva(reserva);
}

// ==================== MOSTRAR DETALLES DE RESERVA ====================
function mostrarDetallesReserva(reserva) {
    const detailsContainer = document.getElementById('reservaDetails');
    const codigoInput = document.getElementById('codigo');
    
    // Poblar detalles
    document.getElementById('detailOrigen').textContent = reserva.estacion_origen || 'N/A';
    document.getElementById('detailDestino').textContent = reserva.estacion_destino || 'N/A';
    document.getElementById('detailBici').textContent = reserva.bike_serial_reservada || 'Por asignar';
    document.getElementById('detailCodigo').textContent = '******'; // Por seguridad, no mostrar el código completo
    
    // Auto-rellenar el código en el input (opcional)
    // codigoInput.value = reserva.codigo_desbloqueo || '';
    
    // Mostrar contenedor
    detailsContainer.style.display = 'block';
    
    // Hacer scroll suave hacia el formulario
    document.getElementById('startTripForm').scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
    });
}

// ==================== INICIAR VIAJE ====================
async function iniciarViaje(e) {
    e.preventDefault();
    console.log('7. Iniciando viaje...');
    
    const codigoInput = document.getElementById('codigo');
    const btnStart = document.getElementById('btnStart');
    const codigo = codigoInput.value.trim().toUpperCase();
    
    // Validaciones
    if (!codigo) {
        mostrarAlerta('Por favor, ingresa el código de desbloqueo.', 'warning');
        codigoInput.focus();
        return;
    }
    
    if (codigo.length < 6) {
        mostrarAlerta('El código debe tener al menos 6 caracteres.', 'warning');
        codigoInput.focus();
        return;
    }
    
    // Deshabilitar botón
    btnStart.disabled = true;
    btnStart.innerHTML = '<span class="btn-icon">⏳</span>Iniciando viaje...';
    
    try {
        const response = await fetch(`${API_BASE}/start_by_user/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            credentials: 'include',
            body: JSON.stringify({ codigo })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            console.log('8. Viaje iniciado exitosamente:', data);
            mostrarAlerta('✅ ¡Viaje iniciado correctamente! Disfruta tu recorrido.', 'success');
            
            // Limpiar formulario
            codigoInput.value = '';
            
            // Ocultar detalles
            document.getElementById('reservaDetails').style.display = 'none';
            
            // Recargar reservas después de 2 segundos
            setTimeout(() => {
                cargarReservas();
            }, 2000);
            
        } else {
            console.error('Error al iniciar viaje:', data);
            mostrarAlerta(`❌ ${data.detail || 'No se pudo iniciar el viaje.'}`, 'danger');
        }
        
    } catch (error) {
        console.error('Error inesperado:', error);
        mostrarAlerta('Error inesperado al iniciar el viaje. Por favor, intenta de nuevo.', 'danger');
    } finally {
        // Rehabilitar botón
        btnStart.disabled = false;
        btnStart.innerHTML = '<span class="btn-icon">▶️</span>Iniciar Viaje';
    }
}

// ==================== MOSTRAR ALERTA ====================
function mostrarAlerta(mensaje, tipo = 'info') {
    const alertContainer = document.getElementById('alertMessage');
    
    alertContainer.className = 'alert-container';
    
    if (tipo === 'success') {
        alertContainer.classList.add('alert-success');
    } else if (tipo === 'danger') {
        alertContainer.classList.add('alert-danger');
    } else if (tipo === 'warning') {
        alertContainer.classList.add('alert-warning');
    }
    
    alertContainer.textContent = mensaje;
    alertContainer.style.display = 'block';
    
    setTimeout(() => {
        alertContainer.style.display = 'none';
    }, 5000);
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

console.log('9. Todas las funciones cargadas correctamente');