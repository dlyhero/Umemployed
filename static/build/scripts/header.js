function activateLink(linkId) {
  // Remove 'active' class from all links
  document.querySelectorAll(".header-link").forEach((link) => {
    link.classList.remove("active-link");
    const icon = link.querySelector(".icon");
    if (icon) {
      icon.classList.remove("active-icon");
    }
  });

  // Add 'active' class to the clicked link
  const link = document.getElementById(linkId);
  if (link) {
    link.classList.add("active-link");
    const icon = link.querySelector(".icon");
    if (icon) {
      icon.classList.add("active-icon");
    }
  }
}

// Initialize the active link on page load
document.addEventListener("DOMContentLoaded", () => {
  const currentUrl = window.location.href;
  document.querySelectorAll(".header-link").forEach((link) => {
    if (link.href === currentUrl) {
      activateLink(link.id);
    }
  });
});

// Attach click event listeners to links
document.querySelectorAll(".header-link").forEach((link) => {
  link.addEventListener("click", function () {
    activateLink(this.id);
  });
});
