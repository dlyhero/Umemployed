function setupBackdropMenu() {
    document.getElementById("option-btn").addEventListener("click", () => {
      document.getElementById("backdrop-menu").classList.remove("hidden");
    });

    document.getElementById("backdrop-menu").addEventListener("click", () => {
      document.getElementById("backdrop-menu").classList.add("hidden");
    });
  }



  setupBackdropMenu();
