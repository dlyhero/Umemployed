document.addEventListener("DOMContentLoaded", () => {
  const userBtn = document.getElementById("user-btn");
  const menuBtn = document.getElementById("menu-btn");
  const sidebar = document.getElementById("sidebar");
  const removeBtn = document.getElementById("remove-btn");
  const backdropMenu = document.getElementById("backdrop-menu");

  // Show sidebar when menu button is clicked
  menuBtn.addEventListener("click", () => {
    sidebar.classList.remove("hidden");
    sidebar
      .querySelector(".sidebar-content")
      .classList.remove("-translate-x-full");
  });

  // Hide sidebar when remove button or backdrop is clicked
  removeBtn.addEventListener("click", () => {
    sidebar
      .querySelector(".sidebar-content")
      .classList.add("-translate-x-full");
    sidebar.classList.add("hidden");
  });

  sidebar.addEventListener("click", (e) => {
    if (e.target === sidebar) {
      sidebar
        .querySelector(".sidebar-content")
        .classList.add("-translate-x-full");
      sidebar.classList.add("hidden");
    }
  });

  // Show backdrop menu when user button is clicked
  userBtn.addEventListener("click", () => {
    backdropMenu.classList.remove("hidden");
  });

  // Hide backdrop menu when it is clicked
  backdropMenu.addEventListener("click", () => {
    backdropMenu.classList.add("hidden");
  });
});
