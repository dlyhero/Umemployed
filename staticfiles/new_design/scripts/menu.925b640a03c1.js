const menuButton = document.getElementById("menuButton");
const desktopMenu = document.getElementById("desktopMenu");

menuButton.addEventListener("click", () => {
  desktopMenu.classList.toggle("hidden");
});

// Optionally, you can add a click event listener to the document to hide the menu when clicking outside
document.addEventListener("click", (event) => {
  if (
    !desktopMenu.contains(event.target) &&
    !menuButton.contains(event.target)
  ) {
    desktopMenu.classList.add("hidden");
  }
});

const mobileMenu = document.getElementById("mobileMenu");
const mobileMenuButton = document.getElementById("mobileMenuButton");
const removeMobileMenu = document.getElementById("removeMobileMenu-btn");

mobileMenuButton.addEventListener("click", () => {
  mobileMenu.classList.add("show");
});

removeMobileMenu.addEventListener("click", () => {
  mobileMenu.classList.remove("show");
});
