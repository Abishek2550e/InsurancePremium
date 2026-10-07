/* ==========================================================================
   theme.js
   --------------------------------------------------------------------------
   Handles the two small pieces of UI state shared by every page:
     1. Dark mode (persisted in localStorage, applied via a body class)
     2. The mobile sidebar (hamburger menu open/close)
   Also highlights the current page's link in the sidebar navigation.
   ========================================================================== */

/** Applies the saved dark-mode preference as early as possible. */
function applySavedTheme() {
  const isDark = localStorage.getItem("darkMode") === "true";
  document.body.classList.toggle("dark-mode", isDark);
}

/** Wires up the dark-mode toggle button in the sidebar. */
function initThemeToggle() {
  const toggleBtn = document.getElementById("theme-toggle-btn");
  if (!toggleBtn) return;

  toggleBtn.addEventListener("click", () => {
    const isDark = document.body.classList.toggle("dark-mode");
    localStorage.setItem("darkMode", String(isDark));
  });
}

/** Wires up the hamburger button + overlay for the mobile sidebar. */
function initMobileSidebar() {
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebar-overlay");
  const openBtn = document.getElementById("hamburger-btn");
  const closeBtn = document.getElementById("sidebar-close-btn");

  if (!sidebar || !overlay || !openBtn || !closeBtn) return;

  function openSidebar() {
    sidebar.classList.add("open");
    overlay.classList.add("open");
  }

  function closeSidebar() {
    sidebar.classList.remove("open");
    overlay.classList.remove("open");
  }

  openBtn.addEventListener("click", openSidebar);
  closeBtn.addEventListener("click", closeSidebar);
  overlay.addEventListener("click", closeSidebar);
}

/** Adds the "active" class to the sidebar link matching the current page. */
function highlightActiveNavLink() {
  const currentPage = window.location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".nav-link").forEach((link) => {
    const linkPage = link.getAttribute("href");
    if (linkPage === currentPage) {
      link.classList.add("active");
    }
  });
}

// Apply the theme immediately (before DOMContentLoaded) to avoid a flash
// of the wrong theme while the page loads.
applySavedTheme();

document.addEventListener("DOMContentLoaded", () => {
  initThemeToggle();
  initMobileSidebar();
  highlightActiveNavLink();
});
