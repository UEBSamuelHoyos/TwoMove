console.log("1. Dashboard JS cargado");

document.addEventListener("DOMContentLoaded", function () {
  console.log("2. DOM cargado - Inicializando dashboard");

  // ==================== ANIMACIONES AL CARGAR ====================
  initAnimations();

  // ==================== ACTUALIZACIÓN AUTOMÁTICA ====================
  initAutoRefresh();

  // ==================== INTERACCIONES DE CARDS ====================
  initCardInteractions();

  // ==================== TOOLTIPS ====================
  initTooltips();

  console.log("3. Dashboard inicializado correctamente");
});

// ==================== ANIMACIONES AL CARGAR ====================
function initAnimations() {
  // Fade-in general
  document.body.style.opacity = 0;
  document.body.style.transition = "opacity 0.6s ease";
  setTimeout(() => {
    document.body.style.opacity = 1;
  }, 100);

  // Animación de métricas
  const metricCards = document.querySelectorAll(".metric-card");
  metricCards.forEach((card, index) => {
    card.style.opacity = 0;
    card.style.transform = "translateY(20px)";
    card.style.transition = "all 0.4s ease";

    setTimeout(() => {
      card.style.opacity = 1;
      card.style.transform = "translateY(0)";
    }, 100 + index * 100);
  });

  // Animación de números (contador)
  animateNumbers();
}

// ==================== CONTADOR DE NÚMEROS ====================
function animateNumbers() {
  const metricValues = document.querySelectorAll(".metric-value");

  metricValues.forEach((element) => {
    const text = element.textContent.trim();
    const number = parseFloat(text.replace(/[^0-9.-]/g, ""));

    if (!isNaN(number)) {
      let currentNumber = 0;
      const increment = number / 30;
      const prefix = text.match(/^\D*/)[0];
      const suffix = text.match(/\D*$/)[0];

      const timer = setInterval(() => {
        currentNumber += increment;
        if (currentNumber >= number) {
          currentNumber = number;
          clearInterval(timer);
        }

        element.textContent =
          prefix + Math.floor(currentNumber).toLocaleString("es-CO") + suffix;
      }, 30);
    }
  });
}

// ==================== AUTO REFRESH ====================
function initAutoRefresh() {
  // Actualizar la hora cada segundo
  const updateInfo = document.querySelector(".update-info span");
  if (updateInfo) {
    setInterval(() => {
      const now = new Date();
      const formatted = now.toLocaleString("es-CO", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
      updateInfo.textContent = `Última actualización: ${formatted}`;
    }, 1000);
  }

  // Notificación de auto-refresh cada 5 minutos
  setInterval(() => {
    mostrarNotificacion("Datos actualizados automáticamente", "success");
  }, 300000); // 5 minutos
}

// ==================== INTERACCIONES DE CARDS ====================
function initCardInteractions() {
  // Hover effect en metric cards
  const metricCards = document.querySelectorAll(".metric-card");
  metricCards.forEach((card) => {
    card.addEventListener("mouseenter", function () {
      this.style.transition = "all 0.3s ease";
      this.style.transform = "translateY(-8px)";
    });

    card.addEventListener("mouseleave", function () {
      this.style.transform = "translateY(0)";
    });
  });

  // Hover effect en action cards
  const actionCards = document.querySelectorAll(".action-card");
  actionCards.forEach((card) => {
    card.addEventListener("mouseenter", function () {
      const arrow = this.querySelector(".action-arrow");
      if (arrow) {
        arrow.style.transform = "translateX(8px)";
      }
    });

    card.addEventListener("mouseleave", function () {
      const arrow = this.querySelector(".action-arrow");
      if (arrow) {
        arrow.style.transform = "translateX(0)";
      }
    });
  });

  // Click en logout con confirmación
  const logoutBtn = document.querySelector(".logout-btn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", function (e) {
      if (!confirm("¿Estás seguro de que deseas cerrar sesión?")) {
        e.preventDefault();
      }
    });
  }
}

// ==================== TOOLTIPS ====================
function initTooltips() {
  const badges = document.querySelectorAll(".badge");
  badges.forEach((badge) => {
    badge.style.cursor = "help";
    badge.title = badge.textContent;
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
  notification.style.zIndex = "9999";
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

// ==================== DETECTAR INACTIVIDAD ====================
let inactivityTimer;
function resetInactivityTimer() {
  clearTimeout(inactivityTimer);
  inactivityTimer = setTimeout(() => {
    mostrarNotificacion("⚠️ Has estado inactivo. Considera refrescar los datos.", "warning");
  }, 600000); // 10 minutos
}

document.addEventListener("mousemove", resetInactivityTimer);
document.addEventListener("keypress", resetInactivityTimer);
resetInactivityTimer();

console.log("4. Todas las funciones del dashboard cargadas");