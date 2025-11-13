console.log("1. Sanciones panel JS cargado");

document.addEventListener("DOMContentLoaded", function () {
  console.log("2. DOM cargado - Inicializando panel de sanciones");

  // ==================== ANIMACIONES AL CARGAR ====================
  initAnimations();

  // ==================== AUTO-CERRAR ALERTAS ====================
  initAutoCloseAlerts();

  // ==================== VALIDACIÓN DE FORMULARIO ====================
  initFormValidation();

  // ==================== INTERACCIONES ====================
  initInteractions();

  console.log("3. Panel de sanciones inicializado");
});

// ==================== ANIMACIONES ====================
function initAnimations() {
  // Fade-in general
  document.body.style.opacity = 0;
  document.body.style.transition = "opacity 0.5s ease";
  setTimeout(() => {
    document.body.style.opacity = 1;
  }, 100);

  // Animación del formulario
  const formContainer = document.querySelector(".sanction-form-container");
  if (formContainer) {
    formContainer.style.opacity = 0;
    formContainer.style.transform = "translateY(20px)";
    formContainer.style.transition = "all 0.5s ease";

    setTimeout(() => {
      formContainer.style.opacity = 1;
      formContainer.style.transform = "translateY(0)";
    }, 200);
  }

  // Animación de filas de tabla
  const rows = document.querySelectorAll(".sanction-row");
  rows.forEach((row, index) => {
    row.style.opacity = 0;
    row.style.transform = "translateY(10px)";
    row.style.transition = "all 0.3s ease";

    setTimeout(() => {
      row.style.opacity = 1;
      row.style.transform = "translateY(0)";
    }, 300 + index * 50);
  });
}

// ==================== AUTO-CERRAR ALERTAS ====================
function initAutoCloseAlerts() {
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach((alert) => {
    setTimeout(() => {
      alert.style.opacity = "0";
      alert.style.transform = "translateX(-20px)";
      setTimeout(() => alert.remove(), 300);
    }, 5000);
  });
}

// ==================== VALIDACIÓN DE FORMULARIO ====================
function initFormValidation() {
  const form = document.getElementById("sanctionForm");
  if (!form) return;

  form.addEventListener("submit", function (e) {
    const usuarioId = document.getElementById("usuario_id").value;
    const motivo = document.getElementById("motivo").value;
    const dias = document.getElementById("dias").value;

    // Validar que se seleccionó un usuario
    if (!usuarioId) {
      e.preventDefault();
      mostrarNotificacion("Por favor selecciona un usuario", "warning");
      document.getElementById("usuario_id").focus();
      return;
    }

    // Validar motivo
    if (!motivo) {
      e.preventDefault();
      mostrarNotificacion("Por favor selecciona un motivo", "warning");
      document.getElementById("motivo").focus();
      return;
    }

    // Validar duración
    if (!dias || dias < 1 || dias > 365) {
      e.preventDefault();
      mostrarNotificacion("La duración debe estar entre 1 y 365 días", "warning");
      document.getElementById("dias").focus();
      return;
    }

    // Confirmación antes de aplicar sanción
    const confirmacion = confirm(
      `¿Estás seguro de aplicar esta sanción?\n\n` +
      `Usuario: ${document.getElementById("usuario_id").selectedOptions[0].text}\n` +
      `Motivo: ${document.getElementById("motivo").selectedOptions[0].text}\n` +
      `Duración: ${dias} días`
    );

    if (!confirmacion) {
      e.preventDefault();
      return;
    }

    console.log("Formulario validado - Enviando sanción...");
  });

  // Reset form con confirmación
  form.addEventListener("reset", function (e) {
    if (!confirm("¿Deseas limpiar todos los campos del formulario?")) {
      e.preventDefault();
    }
  });
}

// ==================== INTERACCIONES ====================
function initInteractions() {
  // Hover en filas de tabla
  const rows = document.querySelectorAll(".sanction-row");
  rows.forEach((row) => {
    row.addEventListener("mouseenter", function () {
      if (this.classList.contains("active-sanction")) {
        this.style.boxShadow = "0 4px 15px rgba(239, 68, 68, 0.15)";
      } else {
        this.style.boxShadow = "0 4px 15px rgba(0, 0, 0, 0.08)";
      }
    });

    row.addEventListener("mouseleave", function () {
      this.style.boxShadow = "none";
    });
  });

  // Contador de caracteres en descripción
  const descripcion = document.getElementById("descripcion");
  if (descripcion) {
    const maxLength = 500;
    const counterDiv = document.createElement("div");
    counterDiv.style.cssText = "text-align: right; font-size: 0.85rem; color: #94a3b8; margin-top: 0.5rem;";
    counterDiv.textContent = `0 / ${maxLength} caracteres`;
    descripcion.parentElement.appendChild(counterDiv);

    descripcion.addEventListener("input", function () {
      const length = this.value.length;
      counterDiv.textContent = `${length} / ${maxLength} caracteres`;

      if (length > maxLength) {
        counterDiv.style.color = "#ef4444";
        this.value = this.value.substring(0, maxLength);
      } else if (length > maxLength * 0.9) {
        counterDiv.style.color = "#f59e0b";
      } else {
        counterDiv.style.color = "#94a3b8";
      }
    });
  }

  // Validación en tiempo real de días
  const diasInput = document.getElementById("dias");
  if (diasInput) {
    diasInput.addEventListener("input", function () {
      const value = parseInt(this.value);
      if (value < 1) {
        this.value = 1;
      } else if (value > 365) {
        this.value = 365;
      }
    });
  }

  // Animación en botones
  const buttons = document.querySelectorAll(".btn-lift, .btn-submit, .btn-reset, .btn-back");
  buttons.forEach((btn) => {
    btn.addEventListener("mouseenter", function () {
      this.style.transition = "all 0.3s ease";
    });
  });
}

// ==================== NOTIFICACIONES ====================
function mostrarNotificacion(mensaje, tipo = "info") {
  const notification = document.createElement("div");
  notification.className = `notification notification-${tipo}`;
  notification.textContent = mensaje;

  notification.style.position = "fixed";
  notification.style.top = "20px";
  notification.style.right = "20px";
  notification.style.padding = "1rem 1.5rem";
  notification.style.borderRadius = "10px";
  notification.style.boxShadow = "0 4px 15px rgba(0, 0, 0, 0.2)";
  notification.style.fontSize = "0.9rem";
  notification.style.fontWeight = "500";
  notification.style.zIndex = "99999";
  notification.style.opacity = "0";
  notification.style.transform = "translateY(-10px)";
  notification.style.transition = "all 0.3s ease";

  // Colores según tipo
  if (tipo === "success") {
    notification.style.background = "linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)";
    notification.style.color = "#065f46";
    notification.style.border = "2px solid #10b981";
  } else if (tipo === "error") {
    notification.style.background = "linear-gradient(135deg, #fee2e2 0%, #fecaca 100%)";
    notification.style.color = "#991b1b";
    notification.style.border = "2px solid #ef4444";
  } else if (tipo === "warning") {
    notification.style.background = "linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)";
    notification.style.color = "#92400e";
    notification.style.border = "2px solid #f59e0b";
  } else {
    notification.style.background = "linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)";
    notification.style.color = "#1e40af";
    notification.style.border = "2px solid #3b82f6";
  }

  document.body.appendChild(notification);

  // Animar entrada
  setTimeout(() => {
    notification.style.opacity = "1";
    notification.style.transform = "translateY(0)";
  }, 100);

  // Animar salida
  setTimeout(() => {
    notification.style.opacity = "0";
    notification.style.transform = "translateY(-10px)";
    setTimeout(() => {
      notification.remove();
    }, 300);
  }, 4000);
}

// ==================== FILTRO DE TABLA ====================
function filtrarTabla(termino) {
  const rows = document.querySelectorAll(".sanction-row");
  const terminoLower = termino.toLowerCase();

  rows.forEach((row) => {
    const email = row.querySelector(".user-email").textContent.toLowerCase();
    const nombre = row.querySelector(".user-name").textContent.toLowerCase();
    const motivo = row.querySelector(".reason-badge").textContent.toLowerCase();

    if (email.includes(terminoLower) || nombre.includes(terminoLower) || motivo.includes(terminoLower)) {
      row.style.display = "";
    } else {
      row.style.display = "none";
    }
  });
}

// ==================== ESTADÍSTICAS ====================
function actualizarEstadisticas() {
  const totalSanciones = document.querySelectorAll(".sanction-row").length;
  const sancionesActivas = document.querySelectorAll(".active-sanction").length;
  
  console.log(`📊 Estadísticas:`);
  console.log(`Total sanciones: ${totalSanciones}`);
  console.log(`Sanciones activas: ${sancionesActivas}`);
  console.log(`Sanciones levantadas: ${totalSanciones - sancionesActivas}`);
}

// Ejecutar al cargar
setTimeout(actualizarEstadisticas, 1000);

console.log("4. Todas las funciones cargadas correctamente");