

function renderSideBar() {
  document.getElementById("sidebar").style.display = "block";
}

function removeSideBar() {
  document.getElementById("sidebar").style.display = "none";
}



export function sideBar() {
  document.getElementById("menu-btn").addEventListener("click", renderSideBar);
  document.getElementById("remove-btn").addEventListener("click", removeSideBar);
  document.getElementById("sidebar").addEventListener("click", removeSideBar);
}

export function setupBackdropMenu() {
  document.getElementById("option-btn").addEventListener("click", () => {
    document.getElementById("backdrop-menu").classList.remove("hidden");
  });

  document.getElementById("backdrop-menu").addEventListener("click", () => {
    document.getElementById("backdrop-menu").classList.add("hidden");
  });
}



setupBackdropMenu();

// Initialize the sidebar and backdrop menu functionality
sideBar();
