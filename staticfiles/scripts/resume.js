const menuBtn = document.getElementById("menu-btn");
const removeBtn = document.getElementById("remove-btn");
const sidebar = document.getElementById("sidebar");

export function sideBar() {
  menuBtn.addEventListener("click", renderSideBar);
  removeBtn.addEventListener("click", removeSideBar);
  sidebar.addEventListener("click", removeSideBar);
}

sideBar();

 function renderSideBar() {
  sidebar.style.display = "block";
}

function removeSideBar() {
  sidebar.style.display = "none";
}
