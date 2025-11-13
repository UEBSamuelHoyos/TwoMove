console.log("1. Usuarios panel JS cargado");

document.addEventListener("DOMContentLoaded", function () {
  console.log("2. DOM cargado - Inicializando panel de usuarios");

  // ==================== ANIMACIONES AL CARGAR ====================
  initAnimations();

  // ==================== AUTO-CERRAR ALERTAS ====================
  initAutoCloseAlerts();

  // ==================== INTERACCIONES ====================
  initInteractions();

  console.log("3. Panel de usuarios inicializado");
});

// ==================== ANIMACIONES ====================
function initAnimations() {
  // Fade-in general
  document.body.style.opacity = 0;
  document.body.style.transition = "opacity 0.5s ease";
  setTimeout(() => {
    document.body.style.opacity = 1;
  }, 100);

  // Animación de filas de tabla
  const rows = document.querySelectorAll(".user-row");
  rows.forEach((row, index) => {
    row.style.opacity = 0;
    row.style.transform = "translateY(10px)";
    row.style.transition = "all 0.3s ease";

    setTimeout(() => {
      row.style.opacity = 1;
      row.style.transform = "translateY(0)";
    }, 50 + index * 30);
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

// ==================== INTERACCIONES ====================
function initInteractions() {
  // Focus automático en el input de búsqueda
  const searchInput = document.querySelector(".search-input");
  if (searchInput && !searchInput.value) {
    searchInput.focus();
  }

  // Animación en hover de botones de acción
  const actionButtons = document.querySelectorAll(".btn-action");
  actionButtons.forEach((btn) => {
    btn.addEventListener("mouseenter", function () {
      this.style.transition = "all 0.3s ease";
      this.style.transform = "translateY(-3px) scale(1.05)";
    });

    btn.addEventListener("mouseleave", function () {
      this.style.transform = "translateY(0) scale(1)";
    });
  });

  // Resaltar fila al hacer hover
  const rows = document.querySelectorAll(".user-row");
  rows.forEach((row) => {
    row.addEventListener("mouseenter", function () {
      this.style.boxShadow = "0 4px 15px rgba(0, 0, 0, 0.08)";
      this.style.transform = "scale(1.01)";
    });

    row.addEventListener("mouseleave", function () {
      this.style.boxShadow = "none";
      this.style.transform = "scale(1)";
    });
  });
}

// ==================== MODAL DE EDICIÓN ====================
function openEditModal(button) {
  const modal = document.getElementById("editModal");
  modal.classList.add("active");
  document.body.style.overflow = "hidden";

  // Llenar datos del formulario
  document.getElementById("editUsuarioId").value = button.dataset.id;
  document.getElementById("editNombre").value = button.dataset.nombre;
  document.getElementById("editApellido").value = button.dataset.apellido;
  document.getElementById("editEmail").value = button.dataset.email;
  document.getElementById("editCelular").value = button.dataset.celular || "";
  document.getElementById("editEstado").value = button.dataset.estado;

  console.log("Modal abierto para usuario ID:", button.dataset.id);
}

function closeEditModal() {
  const modal = document.getElementById("editModal");
  modal.classList.remove("active");
  document.body.style.overflow = "auto";

  console.log("Modal cerrado");
}

// Cerrar modal al hacer clic fuera
document.addEventListener("click", function (e) {
  const modal = document.getElementById("editModal");
  if (e.target === modal) {
    closeEditModal();
  }
});

// Cerrar modal con tecla ESC
document.addEventListener("keydown", function (e) {
  if (e.key === "Escape") {
    closeEditModal();
  }
});

// ==================== VALIDACIÓN DE FORMULARIO ====================
const editForm = document.getElementById("editForm");
if (editForm) {
  editForm.addEventListener("submit", function (e) {
    const nombre = document.getElementById("editNombre").value.trim();
    const apellido = document.getElementById("editApellido").value.trim();
    const email = document.getElementById("editEmail").value.trim();

    if (!nombre || !apellido || !email) {
      e.preventDefault();
      mostrarNotificacion("Por favor completa todos los campos obligatorios", "warning");
      return;
    }

    // Validar formato de email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      e.preventDefault();
      mostrarNotificacion("Por favor ingresa un email válido", "warning");
      return;
    }

    console.log("Formulario validado - Enviando...");
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

// ==================== BÚSQUEDA EN TIEMPO REAL (OPCIONAL) ====================
const searchInput = document.querySelector(".search-input");
if (searchInput) {
  let searchTimeout;
  searchInput.addEventListener("input", function () {
    clearTimeout(searchTimeout);
    const rows = document.querySelectorAll(".user-row");

    searchTimeout = setTimeout(() => {
      const query = this.value.toLowerCase();

      rows.forEach((row) => {
        const nombre = row.querySelector(".user-name").textContent.toLowerCase();
        const email = row.querySelector(".user-email").textContent.toLowerCase();
        const celular = row.querySelector(".user-phone").textContent.toLowerCase();

        if (nombre.includes(query) || email.includes(query) || celular.includes(query)) {
          row.style.display = "";
        } else {
          row.style.display = "none";
        }
      });
    }, 300);
  });
}

console.log("4. Todas las funciones cargadas correctamente");