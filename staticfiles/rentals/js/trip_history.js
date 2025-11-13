console.log("1. Archivo trip_history.js cargado");

// Configuración de la API
const API_BASE = "/alquileres/api/rentals";

// Variables globales
let allTrips = [];
let filteredTrips = [];
let currentPage = 1;
const tripsPerPage = 10;

// Inicialización
document.addEventListener("DOMContentLoaded", function () {
  console.log("2. DOM cargado - Inicializando página de historial");

  // Inicializar sidebar móvil
  initMobileSidebar();

  // Inicializar scroll header
  initScrollHeader();

  // Cargar historial de viajes
  cargarHistorial();

  // Event Listeners
  initEventListeners();
});

// ==================== SIDEBAR MÓVIL ====================
function initMobileSidebar() {
  const menuToggle = document.getElementById("menuToggle");
  const closeSidebar = document.getElementById("closeSidebar");
  const sidebar = document.getElementById("sidebar");

  if (menuToggle) {
    menuToggle.addEventListener("click", function (e) {
      e.stopPropagation();
      sidebar.classList.add("active");
    });
  }

  if (closeSidebar) {
    closeSidebar.addEventListener("click", function (e) {
      e.stopPropagation();
      sidebar.classList.remove("active");
    });
  }

  document.addEventListener("click", function (e) {
    if (window.innerWidth <= 768) {
      const isLinkClick = e.target.closest(".sidebar-nav a, .logout-btn");
      if (isLinkClick) return;
      if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
        sidebar.classList.remove("active");
      }
    }
  });

  document.querySelectorAll(".sidebar-nav a, .logout-btn").forEach((link) => {
    link.addEventListener("click", function () {
      if (window.innerWidth <= 768) {
        setTimeout(() => sidebar.classList.remove("active"), 100);
      }
    });
  });
}

// ==================== SCROLL HEADER ====================
function initScrollHeader() {
  let lastScroll = 0;
  window.addEventListener("scroll", function () {
    const header = document.querySelector(".dashboard-header");
    const currentScroll = window.pageYOffset;

    if (currentScroll > lastScroll && currentScroll > 80) {
      header.style.transform = "translateY(-100%)";
    } else {
      header.style.transform = "translateY(0)";
    }

    lastScroll = currentScroll;
  });
}

// ==================== EVENT LISTENERS ====================
function initEventListeners() {
  const btnAplicarFiltros = document.getElementById("btnAplicarFiltros");
  const btnLimpiarFiltros = document.getElementById("btnLimpiarFiltros");
  const btnPrevPage = document.getElementById("btnPrevPage");
  const btnNextPage = document.getElementById("btnNextPage");
  const modalOverlay = document.getElementById("modalOverlay");
  const modalClose = document.getElementById("modalClose");

  if (btnAplicarFiltros) {
    btnAplicarFiltros.addEventListener("click", aplicarFiltros);
  }

  if (btnLimpiarFiltros) {
    btnLimpiarFiltros.addEventListener("click", limpiarFiltros);
  }

  if (btnPrevPage) {
    btnPrevPage.addEventListener("click", () => cambiarPagina(-1));
  }

  if (btnNextPage) {
    btnNextPage.addEventListener("click", () => cambiarPagina(1));
  }

  if (modalOverlay) {
    modalOverlay.addEventListener("click", cerrarModal);
  }

  if (modalClose) {
    modalClose.addEventListener("click", cerrarModal);
  }
}

// ==================== CARGAR HISTORIAL ====================
async function cargarHistorial() {
  console.log("3. Cargando historial de viajes...");
  const listContainer = document.getElementById("tripsList");

  try {
    // ✅ URL correcta de la API
    const response = await fetch(`${API_BASE}/historial/`, {
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error(`Error HTTP ${response.status}`);
    }

    const data = await response.json();
    console.log("4. Datos obtenidos del servidor:", data);

    // ✅ Usar la estructura correcta de la respuesta
    allTrips = data.viajes || [];
    filteredTrips = [...allTrips];

    console.log(`5. Total de viajes cargados: ${allTrips.length}`);

    // Actualizar estadísticas con los datos reales de la API
    if (data.estadisticas) {
      document.getElementById("totalViajes").textContent = data.estadisticas.total_viajes;
      document.getElementById("totalGastado").textContent = 
        `$${data.estadisticas.total_gastado.toLocaleString("es-CO")}`;
    }

    // Mostrar viajes
    mostrarViajes();
  } catch (error) {
    console.error("❌ Error al cargar historial:", error);
    listContainer.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">❌</div>
        <h3>Error al cargar el historial</h3>
        <p>Por favor, recarga la página</p>
      </div>
    `;
  }
}

// ==================== MOSTRAR VIAJES ====================
function mostrarViajes() {
  const listContainer = document.getElementById("tripsList");
  const tripsCount = document.getElementById("tripsCount");

  // Actualizar contador
  tripsCount.textContent = `${filteredTrips.length} viaje${filteredTrips.length !== 1 ? "s" : ""}`;

  console.log(`6. Mostrando ${filteredTrips.length} viajes`);

  // Si no hay viajes
  if (filteredTrips.length === 0) {
    listContainer.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">📭</div>
        <h3>No hay viajes en el historial</h3>
        <p>Tus viajes aparecerán aquí</p>
      </div>
    `;
    document.getElementById("pagination").style.display = "none";
    return;
  }

  // Calcular paginación
  const startIndex = (currentPage - 1) * tripsPerPage;
  const endIndex = startIndex + tripsPerPage;
  const tripsToShow = filteredTrips.slice(startIndex, endIndex);

  console.log(`7. Mostrando viajes ${startIndex + 1} a ${Math.min(endIndex, filteredTrips.length)}`);

  // Limpiar contenedor
  listContainer.innerHTML = "";

  // Crear cards de viajes
  tripsToShow.forEach((trip) => {
    const tripCard = crearTripCard(trip);
    listContainer.appendChild(tripCard);
  });

  // Actualizar paginación
  actualizarPaginacion();
}

// ==================== CREAR TRIP CARD ====================
function crearTripCard(trip) {
  const card = document.createElement("div");
  card.className = "trip-card";
  card.dataset.tripId = trip.id;

  const fecha = trip.hora_fin
    ? new Date(trip.hora_fin).toLocaleDateString("es-CO", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    : new Date(trip.hora_inicio).toLocaleDateString("es-CO", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });

  const tipo =
    trip.tipo_viaje === "ultima_milla" ? "Última Milla" : "Recorrido Largo";
  const duracion = trip.duracion_minutos || "N/A";
  const costo = trip.costo_total
    ? `$${parseFloat(trip.costo_total).toLocaleString("es-CO")}`
    : "$0";

  card.innerHTML = `
    <div class="trip-card-header">
      <span class="trip-id">Viaje #${trip.id}</span>
      <span class="trip-status status-${trip.estado}">${trip.estado.charAt(0).toUpperCase() + trip.estado.slice(1)}</span>
    </div>
    <div class="trip-card-body">
      <div class="trip-detail">
        <span class="emoji">📍</span>
        <span><strong>Origen:</strong> ${trip.estacion_origen || "N/A"}</span>
      </div>
      <div class="trip-detail">
        <span class="emoji">🎯</span>
        <span><strong>Destino:</strong> ${trip.estacion_destino || "N/A"}</span>
      </div>
      <div class="trip-detail">
        <span class="emoji">🕓</span>
        <span><strong>Tipo:</strong> ${tipo}</span>
      </div>
      <div class="trip-detail">
        <span class="emoji">⏱️</span>
        <span><strong>Duración:</strong> ${duracion} min</span>
      </div>
    </div>
    <div class="trip-card-footer">
      <span class="trip-cost">${costo} COP</span>
      <span class="trip-date">${fecha}</span>
    </div>
  `;

  // Event listener para abrir modal
  card.addEventListener("click", () => abrirModal(trip));

  return card;
}

// ==================== APLICAR FILTROS ====================
function aplicarFiltros() {
  console.log("8. Aplicando filtros...");

  const filterEstado = document.getElementById("filterEstado").value;
  const filterTipo = document.getElementById("filterTipo").value;
  const filterFecha = document.getElementById("filterFecha").value;

  filteredTrips = allTrips.filter((trip) => {
    // Filtro por estado
    if (filterEstado && trip.estado !== filterEstado) {
      return false;
    }

    // Filtro por tipo
    if (filterTipo && trip.tipo_viaje !== filterTipo) {
      return false;
    }

    // Filtro por fecha
    if (filterFecha) {
      const tripDate = trip.hora_fin 
        ? new Date(trip.hora_fin).toISOString().split("T")[0]
        : new Date(trip.hora_inicio).toISOString().split("T")[0];
      
      if (tripDate !== filterFecha) {
        return false;
      }
    }

    return true;
  });

  currentPage = 1;
  mostrarViajes();
  mostrarAlerta(
    `Filtros aplicados: ${filteredTrips.length} viaje${filteredTrips.length !== 1 ? "s" : ""} encontrado${filteredTrips.length !== 1 ? "s" : ""}`,
    "success"
  );
}

// ==================== LIMPIAR FILTROS ====================
function limpiarFiltros() {
  document.getElementById("filterEstado").value = "";
  document.getElementById("filterTipo").value = "";
  document.getElementById("filterFecha").value = "";

  filteredTrips = [...allTrips];
  currentPage = 1;
  mostrarViajes();
  mostrarAlerta("Filtros limpiados", "success");
}

// ==================== PAGINACIÓN ====================
function actualizarPaginacion() {
  const pagination = document.getElementById("pagination");
  const paginationInfo = document.getElementById("paginationInfo");
  const btnPrevPage = document.getElementById("btnPrevPage");
  const btnNextPage = document.getElementById("btnNextPage");

  const totalPages = Math.ceil(filteredTrips.length / tripsPerPage);

  if (totalPages <= 1) {
    pagination.style.display = "none";
    return;
  }

  pagination.style.display = "flex";
  paginationInfo.textContent = `Página ${currentPage} de ${totalPages}`;

  btnPrevPage.disabled = currentPage === 1;
  btnNextPage.disabled = currentPage === totalPages;
}

function cambiarPagina(direction) {
  currentPage += direction;
  mostrarViajes();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// ==================== MODAL ====================
function abrirModal(trip) {
  console.log("9. Abriendo modal para viaje:", trip);

  const modal = document.getElementById("tripModal");
  const modalBody = document.getElementById("modalBody");

  const fecha = trip.hora_fin
    ? new Date(trip.hora_fin).toLocaleDateString("es-CO", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    : new Date(trip.hora_inicio).toLocaleDateString("es-CO", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });

  const tipo =
    trip.tipo_viaje === "ultima_milla" ? "Última Milla" : "Recorrido Largo";

  modalBody.innerHTML = `
    <div style="display: flex; flex-direction: column; gap: 20px;">
      <div style="background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%); border-radius: 12px; padding: 20px; border: 2px solid #48bb78;">
        <h4 style="margin-bottom: 16px; color: #22543d;">📋 Información del Viaje</h4>
        <div style="display: grid; gap: 12px;">
          <p><strong>ID de Viaje:</strong> #${trip.id}</p>
          <p><strong>Estado:</strong> ${trip.estado.charAt(0).toUpperCase() + trip.estado.slice(1)}</p>
          <p><strong>Tipo de viaje:</strong> ${tipo}</p>
          <p><strong>Duración:</strong> ${trip.duracion_minutos || "N/A"} minutos</p>
        </div>
      </div>

      <div style="background: #f7fafc; border-radius: 12px; padding: 20px;">
        <h4 style="margin-bottom: 16px; color: #2d3748;">🚴 Detalles del Recorrido</h4>
        <div style="display: grid; gap: 12px;">
          <p><strong>📍 Origen:</strong> ${trip.estacion_origen || "N/A"}</p>
          <p><strong>🎯 Destino:</strong> ${trip.estacion_destino || "N/A"}</p>
          <p><strong>🚲 Bicicleta:</strong> ${trip.bike_serial_reservada || "N/A"}</p>
          <p><strong>💳 Método de pago:</strong> ${trip.metodo_pago || "N/A"}</p>
        </div>
      </div>

      <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-radius: 12px; padding: 20px; text-align: center;">
        <p style="font-size: 0.9rem; color: #92400e; margin-bottom: 8px;"><strong>💰 Costo Total</strong></p>
        <p style="font-size: 2rem; font-weight: 700; color: #78350f;">$${parseFloat(trip.costo_total || 0).toLocaleString("es-CO")} COP</p>
      </div>

      <div style="text-align: center; color: #718096; font-size: 0.9rem;">
        <p>📅 ${fecha}</p>
      </div>
    </div>
  `;

  modal.style.display = "flex";
  document.body.style.overflow = "hidden";
}

function cerrarModal() {
  const modal = document.getElementById("tripModal");
  modal.style.display = "none";
  document.body.style.overflow = "auto";
}

// ==================== MOSTRAR ALERTA ====================
function mostrarAlerta(mensaje, tipo = "info") {
  const alertContainer = document.getElementById("alertMessage");

  alertContainer.className = "alert-container";

  if (tipo === "success") {
    alertContainer.classList.add("alert-success");
  } else if (tipo === "danger") {
    alertContainer.classList.add("alert-danger");
  } else if (tipo === "warning") {
    alertContainer.classList.add("alert-warning");
  }

  alertContainer.textContent = mensaje;
  alertContainer.style.display = "block";

  setTimeout(() => {
    alertContainer.style.display = "none";
  }, 5000);

  window.scrollTo({ top: 0, behavior: "smooth" });
}

console.log("10. Todas las funciones cargadas correctamente");