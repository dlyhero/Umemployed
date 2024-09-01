// JavaScript to toggle dropdowns on mobile
document.querySelectorAll(".mobile-toggle").forEach((toggle) => {
  toggle.addEventListener("click", function () {
    const content = this.nextElementSibling;
    const icon = this.querySelector(".toggle-icon");

    if (window.innerWidth < 640) {
      // Only allow toggle on mobile
      content.classList.toggle("hidden");
      icon.classList.toggle("fa-chevron-down");
      icon.classList.toggle("fa-chevron-up");
    }
  });
});
