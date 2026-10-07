/* ==========================================================================
   layout.js
   --------------------------------------------------------------------------
   Fills in the small bits of shared UI markup that every page repeats:
   sidebar navigation labels/icons, the hamburger button, the sidebar
   close button, and the dark-mode toggle label.

   Any element with a "data-icon" attribute is automatically filled with
   the matching inline SVG icon (see icons.js) — this keeps the HTML
   files free of repeated <svg> markup, and avoids duplicate-id issues
   since data attributes don't need to be unique.
   ========================================================================== */

const NAV_ITEMS = [
  { href: "index.html", label: "Predict Premium", icon: "calculator" },
];

/** Fills every <a class="nav-link" href="..."> with its icon + label. */
function renderNavLinks() {
  document.querySelectorAll(".nav-link").forEach((link) => {
    const href = link.getAttribute("href");
    const item = NAV_ITEMS.find((n) => n.href === href);
    if (!item) return;
    link.innerHTML = `${svgIcon(item.icon, 18)}<span>${item.label}</span>`;
  });
}

/** Fills every element with a "data-icon" attribute with its inline SVG icon. */
function renderStandaloneIcons() {
  document.querySelectorAll("[data-icon]").forEach((el) => {
    const iconName = el.getAttribute("data-icon");
    const size = Number(el.getAttribute("data-icon-size")) || 18;
    el.innerHTML = svgIcon(iconName, size);
  });
}

/** Fills the hamburger + sidebar-close buttons with their icons. */
function renderChromeIcons() {
  const hamburger = document.getElementById("hamburger-btn");
  if (hamburger) hamburger.innerHTML = svgIcon("menu", 20);

  const closeBtn = document.getElementById("sidebar-close-btn");
  if (closeBtn) closeBtn.innerHTML = svgIcon("close", 18);
}

/** Sets the dark-mode toggle's icon + label to match the current theme. */
function renderThemeToggleLabel() {
  const label = document.getElementById("theme-toggle-label");
  if (!label) return;
  const isDark = document.body.classList.contains("dark-mode");
  label.innerHTML = `${svgIcon(isDark ? "moon" : "sun", 16)}<span style="margin-left:8px;">${isDark ? "Dark Mode" : "Light Mode"}</span>`;
}

document.addEventListener("DOMContentLoaded", () => {
  renderNavLinks();
  renderStandaloneIcons();
  renderChromeIcons();
  renderThemeToggleLabel();

  // Keep the toggle label in sync whenever dark mode is switched.
  // theme.js's own click listener (registered first) flips the body
  // class; this one just re-renders the label/icon to match.
  const toggleBtn = document.getElementById("theme-toggle-btn");
  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      setTimeout(renderThemeToggleLabel, 0);
    });
  }
});
