console.log('1. Archivo reserve_bike.js cargado');

// Configuración de la API
const API_BASE_STATIONS = '/estaciones/stations/';
const API_BASE_RENTALS = '/alquileres/api/rentals';

// Variables globales
let estacionesData = [];
let selectedOrigen = null;
let selectedDestino = null;

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    console.log('2. DOM cargado - Inicializando página de reserva');
    
    // Inicializar sidebar móvil
    initMobileSidebar();
    
    // Inicializar scroll header
    initScrollHeader();
    
    // Cargar estaciones
    cargarEstaciones();
    
    // Establecer fecha mínima (hoy)
    setMinDate();
    
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

// ==================== FECHA MÍNIMA ====================
function setMinDate() {
    const today = new Date().toISOString().split('T')[0];
    const fechaInput = document.getElementById('fechaReserva');
    if (fechaInput) {
        fechaInput.min = today;
        fechaInput.value = today;
    }
}

// ==================== EVENT LISTENERS ====================
function initEventListeners() {
    const estacionOrigen = document.getElementById('estacionOrigen');
    const estacionDestino = document.getElementById('estacionDestino');
    const fechaReserva = document.getElementById('fechaReserva');
    const horaReserva = document.getElementById('horaReserva');
    const tipoViaje = document.getElementById('tipoViaje');
    const btnReservar = document.getElementById('btnReservar');
    
    // Opciones de tipo de bicicleta
    const bikeOptions = document.querySelectorAll('.bike-option');
    bikeOptions.forEach(option => {
        option.addEventListener('click', function() {
            const radio = this.querySelector('input[type="radio"]');
            radio.checked = true;
            updateSummary();
        });
    });
    
    // Cambios en los selectores
    if (estacionOrigen) {
        estacionOrigen.addEventListener('change', function() {
            selectedOrigen = this.value;
            updateSummary();
        });
    }
    
    if (estacionDestino) {
        estacionDestino.addEventListener('change', function() {
            selectedDestino = this.value;
            updateSummary();
        });
    }
    
    // Cambios en fecha/hora
    if (fechaReserva) {
        fechaReserva.addEventListener('change', updateSummary);
    }
    
    if (horaReserva) {
        horaReserva.addEventListener('change', updateSummary);
    }
    
    if (tipoViaje) {
        tipoViaje.addEventListener('change', updateSummary);
    }
    
    // Botón de reservar
    if (btnReservar) {
        btnReservar.addEventListener('click', crearReserva);
    }
    
    // Modal
    const modalClose = document.getElementById('modalClose');
    const btnNuevaReserva = document.getElementById('btnNuevaReserva');
    const btnVerReservas = document.getElementById('btnVerReservas');
    
    if (modalClose) {
        modalClose.addEventListener('click', cerrarModal);
    }
    
    if (btnNuevaReserva) {
        btnNuevaReserva.addEventListener('click', function() {
            cerrarModal();
            limpiarFormulario();
        });
    }
    
    if (btnVerReservas) {
        btnVerReservas.addEventListener('click', function() {
            window.location.href = '/cancelar-reserva/'; // Ajusta la URL según tu proyecto
        });
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

// ==================== CARGAR ESTACIONES ====================
async function cargarEstaciones() {
    console.log('3. Cargando estaciones...');
    const selectOrigen = document.getElementById('estacionOrigen');
    const selectDestino = document.getElementById('estacionDestino');
    
    try {
        const response = await fetch(API_BASE_STATIONS);
        
        if (!response.ok) {
            throw new Error(`Error HTTP ${response.status}`);
        }
        
        const estaciones = await response.json();
        console.log('4. Estaciones obtenidas:', estaciones);
        
        estacionesData = estaciones;
        
        // Poblar selectores
        [selectOrigen, selectDestino].forEach(select => {
            select.innerHTML = '';
            
            // Opción por defecto
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = '-- Selecciona una estación --';
            select.appendChild(defaultOption);
            
            // Agregar estaciones
            estaciones.forEach(estacion => {
                const option = document.createElement('option');
                option.value = estacion.id;
                
                const electricas = estacion.disponibles_electricas || 0;
                const mecanicas = estacion.disponibles_mecanicas || 0;
                const total = estacion.total_disponibles || 0;
                
                option.textContent = `${estacion.nombre} — 🟢 ${electricas} eléctricas / ⚙️ ${mecanicas} mecánicas`;
                
                if (total === 0) {
                    option.disabled = true;
                    option.textContent += ' (Agotada)';
                }
                
                select.appendChild(option);
            });
        });
        
        console.log('5. Selectores de estaciones poblados');
        
    } catch (error) {
        console.error('Error al cargar estaciones:', error);
        mostrarAlerta('Error al cargar las estaciones. Por favor, recarga la página.', 'danger');
        
        [selectOrigen, selectDestino].forEach(select => {
            select.innerHTML = '<option value="">Error al cargar estaciones</option>';
        });
    }
}

// ==================== ACTUALIZAR RESUMEN ====================
function updateSummary() {
    const estacionOrigen = document.getElementById('estacionOrigen');
    const estacionDestino = document.getElementById('estacionDestino');
    const fechaReserva = document.getElementById('fechaReserva');
    const horaReserva = document.getElementById('horaReserva');
    const tipoBicicleta = document.querySelector('input[name="tipoBicicleta"]:checked');
    const tipoViaje = document.getElementById('tipoViaje');
    
    // Validar que todos los campos estén completos
    if (!estacionOrigen.value || !estacionDestino.value || !fechaReserva.value || !horaReserva.value) {
        document.getElementById('summaryCard').style.display = 'none';
        return;
    }
    
    // Mostrar card de resumen
    const summaryCard = document.getElementById('summaryCard');
    summaryCard.style.display = 'block';
    
    // Obtener nombres de estaciones
    const origenNombre = estacionOrigen.options[estacionOrigen.selectedIndex].text.split('—')[0].trim();
    const destinoNombre = estacionDestino.options[estacionDestino.selectedIndex].text.split('—')[0].trim();
    
    // Poblar resumen
    document.getElementById('summaryOrigen').textContent = origenNombre;
    document.getElementById('summaryDestino').textContent = destinoNombre;
    document.getElementById('summaryFechaHora').textContent = `${fechaReserva.value} a las ${horaReserva.value}`;
    document.getElementById('summaryBici').textContent = tipoBicicleta.value === 'electric' ? 'Eléctrica ⚡' : 'Convencional 🚴';
    document.getElementById('summaryTipoViaje').textContent = 
        tipoViaje.value === 'ultima_milla' ? 'Última Milla (45 min)' : 'Recorrido Largo (75 min)';
    
    // Calcular costo estimado (esto es un placeholder, ajusta según tu lógica)
    const costoBase = tipoViaje.value === 'ultima_milla' ? 3500 : 5000;
    const costoTipo = tipoBicicleta.value === 'electric' ? 1000 : 0;
    const costoTotal = costoBase + costoTipo;
    
    document.getElementById('summaryCosto').textContent = `$${formatearNumero(costoTotal)} COP`;
}

// ==================== CREAR RESERVA ====================
async function crearReserva() {
    console.log('6. Iniciando creación de reserva...');
    
    const estacionOrigen = document.getElementById('estacionOrigen');
    const estacionDestino = document.getElementById('estacionDestino');
    const fechaReserva = document.getElementById('fechaReserva');
    const horaReserva = document.getElementById('horaReserva');
    const tipoBicicleta = document.querySelector('input[name="tipoBicicleta"]:checked');
    const tipoViaje = document.getElementById('tipoViaje');
    const metodoPago = document.getElementById('metodoPago');
    const btnReservar = document.getElementById('btnReservar');
    
    // Validaciones
    if (!estacionOrigen.value) {
        mostrarAlerta('Por favor, selecciona una estación de origen.', 'warning');
        estacionOrigen.focus();
        return;
    }
    
    if (!estacionDestino.value) {
        mostrarAlerta('Por favor, selecciona una estación de destino.', 'warning');
        estacionDestino.focus();
        return;
    }
    
    if (estacionOrigen.value === estacionDestino.value) {
        mostrarAlerta('La estación de destino debe ser diferente a la de origen.', 'warning');
        estacionDestino.focus();
        return;
    }
    
    if (!fechaReserva.value) {
        mostrarAlerta('Por favor, selecciona una fecha.', 'warning');
        fechaReserva.focus();
        return;
    }
    
    if (!horaReserva.value) {
        mostrarAlerta('Por favor, selecciona una hora.', 'warning');
        horaReserva.focus();
        return;
    }
    
    // Preparar datos
    const body = {
        estacion_origen_id: estacionOrigen.value,
        estacion_destino_id: estacionDestino.value,
        tipo_bicicleta: tipoBicicleta.value,
        tipo_viaje: tipoViaje.value,
        metodo_pago: metodoPago.value,
        fecha_reserva: fechaReserva.value,
        hora_reserva: horaReserva.value
    };
    
    console.log('7. Datos de reserva:', body);
    
    // Deshabilitar botón
    btnReservar.disabled = true;
    btnReservar.innerHTML = '<span class="btn-icon">⏳</span>Procesando...';
    
    try {
        const response = await fetch(`${API_BASE_RENTALS}/reserve/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            credentials: 'include',
            body: JSON.stringify(body)
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('8. Reserva creada exitosamente:', data);
            
            // Mostrar modal de confirmación
            mostrarModalConfirmacion(data);
            
            // Recargar estaciones para actualizar disponibilidad
            await cargarEstaciones();
            
        } else {
            const error = await response.json();
            console.error('Error al crear reserva:', error);
            mostrarAlerta(`Error: ${error.detail || 'No se pudo completar la reserva.'}`, 'danger');
        }
        
    } catch (error) {
        console.error('Error inesperado:', error);
        mostrarAlerta('Error inesperado al crear la reserva. Por favor, intenta de nuevo.', 'danger');
    } finally {
        // Rehabilitar botón
        btnReservar.disabled = false;
        btnReservar.innerHTML = '<span class="btn-icon">✅</span>Confirmar Reserva';
    }
}

// ==================== MOSTRAR MODAL DE CONFIRMACIÓN ====================
function mostrarModalConfirmacion(data) {
    const modal = document.getElementById('confirmModal');
    const modalBody = document.getElementById('modalBody');
    
    modalBody.innerHTML = `
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🎉</div>
            <h3 style="color: #22543d; margin-bottom: 1.5rem;">¡Tu reserva está confirmada!</h3>
            
            <div style="background: #f7fafc; padding: 1.5rem; border-radius: 10px; text-align: left; margin-bottom: 1rem;">
                <p style="margin-bottom: 0.8rem;"><strong>🔵 Origen:</strong> ${data.estacion_origen || 'N/A'}</p>
                <p style="margin-bottom: 0.8rem;"><strong>🔴 Destino:</strong> ${data.estacion_destino || 'N/A'}</p>
                <p style="margin-bottom: 0.8rem;"><strong>🚴 Bicicleta:</strong> ${data.bike_serial_reservada || 'N/A'}</p>
                <p style="margin-bottom: 0.8rem;"><strong>🔑 Código de desbloqueo:</strong> <code style="background: #fff; padding: 0.3rem 0.6rem; border-radius: 5px; font-weight: bold; font-size: 1.1rem;">${data.codigo_desbloqueo || 'N/A'}</code></p>
                <p style="margin-bottom: 0.8rem;"><strong>💳 Método de pago:</strong> ${data.metodo_pago === 'wallet' ? 'Saldo en App' : 'Tarjeta de Crédito'}</p>
                <p style="margin-bottom: 0;"><strong>📅 Fecha:</strong> ${document.getElementById('fechaReserva').value} — ${document.getElementById('horaReserva').value}</p>
            </div>
            
            <p style="color: #718096; font-size: 0.9rem;">Guarda tu código de desbloqueo para acceder a la bicicleta.</p>
        </div>
    `;
    
    modal.style.display = 'flex';
}

// ==================== CERRAR MODAL ====================
function cerrarModal() {
    const modal = document.getElementById('confirmModal');
    modal.style.display = 'none';
}

// ==================== LIMPIAR FORMULARIO ====================
function limpiarFormulario() {
    document.getElementById('estacionOrigen').value = '';
    document.getElementById('estacionDestino').value = '';
    document.getElementById('horaReserva').value = '';
    document.querySelector('input[name="tipoBicicleta"][value="electric"]').checked = true;
    document.getElementById('tipoViaje').value = 'ultima_milla';
    document.getElementById('metodoPago').value = 'wallet';
    document.getElementById('summaryCard').style.display = 'none';
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

// ==================== UTILIDADES ====================
function formatearNumero(numero) {
    return new Intl.NumberFormat('es-CO').format(numero);
}

console.log('9. Todas las funciones cargadas correctamente');