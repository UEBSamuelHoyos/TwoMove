console.log("1. Reportes panel JS cargado");

document.addEventListener("DOMContentLoaded", function () {
  console.log("2. DOM cargado - Inicializando panel de reportes");

  // ==================== ANIMACIONES AL CARGAR ====================
  initAnimations();

  // ==================== AUTO-CERRAR ALERTAS ====================
  initAutoCloseAlerts();

  // ==================== LÓGICA DEL FORMULARIO ====================
  initFormLogic();

  // ==================== VALIDACIÓN DE FORMULARIO ====================
  initFormValidation();

  // ==================== INTERACCIONES ====================
  initInteractions();

  console.log("3. Panel de reportes inicializado");
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
  const formContainer = document.querySelector(".report-form-container");
  if (formContainer) {
    formContainer.style.opacity = 0;
    formContainer.style.transform = "translateY(20px)";
    formContainer.style.transition = "all 0.5s ease";

    setTimeout(() => {
      formContainer.style.opacity = 1;
      formContainer.style.transform = "translateY(0)";
    }, 200);
  }

  // Animación de las cards
  const reportCards = document.querySelectorAll(".report-card");
  reportCards.forEach((card, index) => {
    card.style.opacity = 0;
    card.style.transform = "translateY(20px)";
    card.style.transition = "all 0.4s ease";

    setTimeout(() => {
      card.style.opacity = 1;
      card.style.transform = "translateY(0)";
    }, 400 + index * 100);
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

// ==================== LÓGICA DEL FORMULARIO ====================
function initFormLogic() {
  const tipoSelect = document.getElementById("tipo_reporte");
  const wrapUsuario = document.getElementById("wrap_usuario");
  const usuarioSelect = document.getElementById("usuario_id");

  // Función para alternar visibilidad del selector de usuario
  window.toggleUsuario = function () {
    const esUsuario = tipoSelect.value === "usuario";

    if (esUsuario) {
      wrapUsuario.style.display = "block";
      usuarioSelect.required = true;

      // Animación de entrada
      wrapUsuario.style.opacity = 0;
      wrapUsuario.style.transform = "translateY(-10px)";
      setTimeout(() => {
        wrapUsuario.style.transition = "all 0.3s ease";
        wrapUsuario.style.opacity = 1;
        wrapUsuario.style.transform = "translateY(0)";
      }, 50);
    } else {
      wrapUsuario.style.display = "none";
      usuarioSelect.required = false;
      usuarioSelect.value = "";
    }
  };

  // Escuchar cambios en el tipo de reporte
  tipoSelect.addEventListener("change", toggleUsuario);

  // Ejecutar al cargar
  toggleUsuario();
}

// ==================== VALIDACIÓN DE FORMULARIO ====================
function initFormValidation() {
  const form = document.getElementById("form-reportes");
  if (!form) return;

  form.addEventListener("submit", function (e) {
    const tipoSelect = document.getElementById("tipo_reporte");
    const usuarioSelect = document.getElementById("usuario_id");
    const formatoSelect = document.getElementById("formato");

    // Validar tipo de reporte
    if (!tipoSelect.value) {
      e.preventDefault();
      mostrarNotificacion("⚠️ Por favor selecciona el tipo de reporte", "warning");
      tipoSelect.focus();
      return;
    }

    // Validar usuario si es reporte por usuario
    const esUsuario = tipoSelect.value === "usuario";
    const usuarioSeleccionado = usuarioSelect.value.trim();

    if (esUsuario && !usuarioSeleccionado) {
      e.preventDefault();
      mostrarNotificacion("⚠️ Por favor selecciona un usuario antes de continuar", "warning");
      usuarioSelect.focus();
      return;
    }

    // Validar formato
    if (!formatoSelect.value) {
      e.preventDefault();
      mostrarNotificacion("⚠️ Por favor selecciona el formato del reporte", "warning");
      formatoSelect.focus();
      return;
    }

    // Confirmación antes de generar
    const tipoTexto = tipoSelect.options[tipoSelect.selectedIndex].text;
    const formatoTexto = formatoSelect.options[formatoSelect.selectedIndex].text;
    let mensaje = `¿Deseas generar el siguiente reporte?\n\nTipo: ${tipoTexto}\nFormato: ${formatoTexto}`;

    if (esUsuario && usuarioSeleccionado) {
      const usuarioTexto = usuarioSelect.options[usuarioSelect.selectedIndex].text;
      mensaje += `\nUsuario: ${usuarioTexto}`;
    }

    const confirmacion = confirm(mensaje);

    if (!confirmacion) {
      e.preventDefault();
      return;
    }

    // Mostrar notificación de generación
    mostrarNotificacion("🔄 Generando reporte... Por favor espera", "info");

    console.log("Formulario validado - Generando reporte...");
  });
}

// ==================== INTERACCIONES ====================
function initInteractions() {
  // Hover en report cards
  const reportCards = document.querySelectorAll(".report-card");
  reportCards.forEach((card) => {
    card.addEventListener("mouseenter", function () {
      this.style.boxShadow = "0 12px 30px rgba(59, 130, 246, 0.2)";
    });

    card.addEventListener("mouseleave", function () {
      this.style.boxShadow = "";
    });
  });

  // Animación en botones
  const buttons = document.querySelectorAll(".btn-submit, .btn-reset, .btn-back");
  buttons.forEach((btn) => {
    btn.addEventListener("mouseenter", function () {
      this.style.transition = "all 0.3s ease";
    });
  });

  // Highlight del campo activo
  const selects = document.querySelectorAll("select");
  selects.forEach((select) => {
    select.addEventListener("focus", function () {
      this.parentElement.style.transform = "scale(1.01)";
      this.parentElement.style.transition = "transform 0.2s ease";
    });

    select.addEventListener("blur", function () {
      this.parentElement.style.transform = "scale(1)";
    });
  });

  // Info box interactiva
  const infoBox = document.querySelector(".info-box");
  if (infoBox) {
    infoBox.addEventListener("mouseenter", function () {
      this.style.transform = "translateX(5px)";
      this.style.transition = "transform 0.3s ease";
    });

    infoBox.addEventListener("mouseleave", function () {
      this.style.transform = "translateX(0)";
    });
  }
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
  notification.style.maxWidth = "400px";

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

// ==================== HELPERS ====================
function resetForm() {
  const form = document.getElementById("form-reportes");
  if (form) {
    form.reset();
    toggleUsuario();
    mostrarNotificacion("Formulario reiniciado", "success");
  }
}

// ==================== LOG FINAL ====================
console.log("4. Todas las funciones del panel de reportes cargadas correctamente");