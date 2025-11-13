console.log("1. Archivo end_trip.js cargado");

// Configuración de la API
const API_BASE = "/alquileres/api/rentals";

// Variable global para el rental activo
let activeRental = null;

// Inicialización
document.addEventListener("DOMContentLoaded", function () {
  console.log("2. DOM cargado - Inicializando página de finalizar viaje");

  // Inicializar sidebar móvil
  initMobileSidebar();

  // Inicializar scroll header
  initScrollHeader();

  // Cargar viaje activo
  cargarViajeActivo();

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
  const finalizarBtn = document.getElementById("finalizarBtn");

  if (finalizarBtn) {
    finalizarBtn.addEventListener("click", finalizarViaje);
  }
}

// ==================== OBTENER TOKEN CSRF ====================
function getCSRFToken() {
  const name = "csrftoken";
  const cookies = document.cookie.split(";");
  for (let cookie of cookies) {
    cookie = cookie.trim();
    if (cookie.startsWith(name + "=")) {
      return decodeURIComponent(cookie.substring(name.length + 1));
    }
  }
  // Fallback: intentar obtener del meta tag
  const metaToken = document.querySelector('meta[name="csrf-token"]');
  return metaToken ? metaToken.content : "";
}

// ==================== CARGAR VIAJE ACTIVO ====================
async function cargarViajeActivo() {
  console.log("3. Cargando viaje activo del usuario...");

  const loadingCard = document.getElementById("loadingCard");
  const viajeActivoCard = document.getElementById("viajeActivoCard");
  const emptyCard = document.getElementById("emptyCard");

  try {
    const response = await fetch(`${API_BASE}/mis_reservas/`, {
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error(`Error HTTP ${response.status}`);
    }

    const reservas = await response.json();
    console.log("4. Reservas obtenidas:", reservas);

    // Buscar reserva activa
    const activa = reservas.find((r) => r.estado === "activo");

    // Ocultar loading
    loadingCard.style.display = "none";

    if (!activa) {
      console.log("5. No hay viajes activos");
      emptyCard.style.display = "block";
      return;
    }

    console.log("6. Viaje activo encontrado:", activa);
    activeRental = activa;

    // Mostrar información del viaje activo
    mostrarViajeActivo(activa);
    viajeActivoCard.style.display = "block";
  } catch (error) {
    console.error("Error al cargar viaje activo:", error);
    loadingCard.style.display = "none";
    mostrarAlerta(
      "Error al cargar la información del viaje. Por favor, recarga la página.",
      "danger"
    );
  }
}

// ==================== MOSTRAR VIAJE ACTIVO ====================
function mostrarViajeActivo(viaje) {
  document.getElementById("origenValue").textContent =
    viaje.estacion_origen || "N/A";
  document.getElementById("destinoValue").textContent =
    viaje.estacion_destino || "No especificada";
  document.getElementById("biciValue").textContent =
    viaje.bike_serial_reservada || "N/A";

  const tipo =
    viaje.tipo_viaje === "ultima_milla" ? "Última Milla" : "Recorrido Largo";
  document.getElementById("tipoValue").textContent = tipo;
}

// ==================== FINALIZAR VIAJE ====================
async function finalizarViaje() {
  console.log("7. Iniciando finalización de viaje...");

  if (!activeRental) {
    mostrarAlerta("No hay un viaje activo para finalizar.", "warning");
    return;
  }

  const finalizarBtn = document.getElementById("finalizarBtn");

  // Confirmar acción
  if (
    !confirm(
      "¿Estás seguro de que deseas finalizar tu viaje? Se calculará el costo total."
    )
  ) {
    return;
  }

  // Deshabilitar botón
  finalizarBtn.disabled = true;
  finalizarBtn.innerHTML =
    '<span class="btn-icon">⏳</span>Finalizando viaje...';

  try {
    const response = await fetch(`${API_BASE}/end_trip/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
      },
      credentials: "include",
      body: JSON.stringify({ rental_id: activeRental.id }),
    });

    const data = await response.json();

    if (response.ok) {
      console.log("8. Viaje finalizado exitosamente:", data);
      mostrarAlerta(
        data.mensaje || "✅ ¡Viaje finalizado correctamente!",
        "success"
      );

      // Ocultar card de viaje activo
      document.getElementById("viajeActivoCard").style.display = "none";

      // Mostrar resultados
      mostrarResultados(data);
    } else {
      console.error("Error al finalizar viaje:", data);
      mostrarAlerta(
        `❌ ${data.detail || data.error || "No se pudo finalizar el viaje."}`,
        "danger"
      );

      // Rehabilitar botón
      finalizarBtn.disabled = false;
      finalizarBtn.innerHTML =
        '<span class="btn-icon">✅</span>Finalizar Viaje';
    }
  } catch (error) {
    console.error("Error inesperado:", error);
    mostrarAlerta(
      "Error inesperado al finalizar el viaje. Por favor, intenta de nuevo.",
      "danger"
    );

    // Rehabilitar botón
    finalizarBtn.disabled = false;
    finalizarBtn.innerHTML = '<span class="btn-icon">✅</span>Finalizar Viaje';
  }
}
// ==================== MOSTRAR RESULTADOS ====================
function mostrarResultados(data) {
  const resultsCard = document.getElementById("resultsCard");

  // Poblar datos
  const costoFormateado = data.costo_total
    ? `$${Number(data.costo_total).toLocaleString("es-CO")} COP`
    : "N/A";

  document.getElementById("resCosto").textContent = costoFormateado;
  document.getElementById("resDuracion").textContent =
    `${data.duracion_minutos || 0} minutos`;
  document.getElementById("resDestino").textContent =
    data.estacion_destino || "N/A";

  // Fecha actual formateada
  const ahora = new Date();
  const fechaFormateada = ahora.toLocaleDateString("es-CO", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
  document.getElementById("resFecha").textContent = fechaFormateada;

  // Mostrar card de resultados
  resultsCard.style.display = "block";

  // Scroll suave hacia resultados
  resultsCard.scrollIntoView({ behavior: "smooth", block: "center" });
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

console.log("9. Todas las funciones cargadas correctamente");