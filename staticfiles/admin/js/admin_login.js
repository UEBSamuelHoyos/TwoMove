console.log("1. Admin login JS cargado");

document.addEventListener("DOMContentLoaded", () => {
  console.log("2. DOM cargado - Inicializando admin login");

  // --- Fade-in general ---
  document.body.style.opacity = 0;
  document.body.style.transition = "opacity 0.6s ease";
  setTimeout(() => {
    document.body.style.opacity = 1;
  }, 100);

  // --- Validación de formulario ---
  const form = document.getElementById("adminLoginForm");
  const emailInput = document.getElementById("email");
  const passwordInput = document.getElementById("password");

  if (form) {
    form.addEventListener("submit", (e) => {
      // Validación básica
      const email = emailInput.value.trim();
      const password = passwordInput.value.trim();

      if (!email || !password) {
        e.preventDefault();
        mostrarNotificacion(
          "Por favor completa todos los campos",
          "warning"
        );
        return;
      }

      // Validar formato de email
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        e.preventDefault();
        mostrarNotificacion("Por favor ingresa un email válido", "warning");
        return;
      }

      console.log("3. Formulario validado - Enviando...");
    });
  }

  // --- Hover suave en botones ---
  const buttons = document.querySelectorAll(".btn-submit, .back-link a");
  buttons.forEach((btn) => {
    btn.addEventListener("mouseenter", () => {
      btn.style.transition = "transform 0.2s ease";
      btn.style.transform = "translateY(-2px)";
    });
    btn.addEventListener("mouseleave", () => {
      btn.style.transform = "translateY(0)";
    });
  });

  // --- Auto-focus en el primer campo ---
  if (emailInput) {
    emailInput.focus();
  }

  // --- Animación de los campos al hacer focus ---
  const inputs = document.querySelectorAll(".form-group input");
  inputs.forEach((input) => {
    input.addEventListener("focus", function () {
      this.parentElement.style.transform = "scale(1.01)";
      this.parentElement.style.transition = "transform 0.2s ease";
    });

    input.addEventListener("blur", function () {
      this.parentElement.style.transform = "scale(1)";
    });
  });

  // --- Detectar Enter para submit ---
  inputs.forEach((input) => {
    input.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        if (input.id === "email") {
          passwordInput.focus();
        } else if (input.id === "password") {
          form.submit();
        }
      }
    });
  });

  console.log("4. Admin login inicializado correctamente");
});

// --- Función para mostrar notificaciones ---
function mostrarNotificacion(texto, tipo = "info") {
  // Crear notificación temporal
  const message = document.createElement("div");
  message.textContent = texto;
  message.style.position = "fixed";
  message.style.bottom = "30px";
  message.style.left = "50%";
  message.style.transform = "translateX(-50%)";
  message.style.padding = "0.8rem 1.5rem";
  message.style.borderRadius = "10px";
  message.style.boxShadow = "0 6px 15px rgba(0, 0, 0, 0.3)";
  message.style.fontSize = "0.95rem";
  message.style.opacity = "0";
  message.style.transition = "opacity 0.4s ease";
  message.style.zIndex = "9999";

  // Colores según tipo
  if (tipo === "success") {
    message.style.background = "#48bb78";
    message.style.color = "white";
  } else if (tipo === "error") {
    message.style.background = "#fc8181";
    message.style.color = "white";
  } else if (tipo === "warning") {
    message.style.background = "#f6ad55";
    message.style.color = "#744210";
  } else {
    message.style.background = "#4299e1";
    message.style.color = "white";
  }

  document.body.appendChild(message);
  setTimeout(() => {
    message.style.opacity = "1";
  }, 100);
  setTimeout(() => {
    message.style.opacity = "0";
    setTimeout(() => message.remove(), 500);
  }, 3000);
}

console.log("5. Funciones auxiliares cargadas");