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

sideBar();