// Desktop Menu Toggle
const menuButton = document.getElementById("menuButton");
const desktopMenu = document.getElementById("desktopMenu");

menuButton.addEventListener("click", () => {
  desktopMenu.classList.toggle("hidden");
});

// Hide the desktop menu when clicking outside
document.addEventListener("click", (event) => {
  if (
    !desktopMenu.contains(event.target) &&
    !menuButton.contains(event.target)
  ) {
    desktopMenu.classList.add("hidden");
  }
});

// Mobile Menu Toggle
const mobileMenu = document.getElementById("mobileMenu");
const mobileMenuButton = document.getElementById("mobileMenuButton");
const removeMobileMenu = document.getElementById("removeMobileMenu-btn");

mobileMenuButton.addEventListener("click", () => {
  mobileMenu.classList.add("show");
  document.body.classList.add("overflow-hidden"); // Prevent scrolling
});

removeMobileMenu.addEventListener("click", () => {
  mobileMenu.classList.remove("show");
  document.body.classList.remove("overflow-hidden"); // Re-enable scrolling
});
