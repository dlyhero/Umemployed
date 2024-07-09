const menu = document.getElementById("aside-menu");
const menuBtn = document.getElementById("aside-menu-btn");
const asideCancelBtn = document.getElementById('cancel-aside-btn');

const asideItems = document.querySelectorAll(".aside-item");

asideItems.forEach(item => {
  item.addEventListener("click", (event) => {
    // Prevent default link behavior if necessary
    event.preventDefault();
    
    // Remove 'active' class from all items
    asideItems.forEach(i => i.classList.remove("active"));
    
    // Add 'active' class to the clicked item
    item.classList.add("active");
    
    // Optionally navigate to the link
    const link = item.getAttribute('href');
    if (link) {
      window.location.href = link;
    }
  });
});

// Mark the appropriate link as active based on current URL
const currentPath = window.location.pathname;
asideItems.forEach(item => {
  const link = item.getAttribute('href');
  if (link === currentPath) {
    item.classList.add('active');
  }
});

function displayMenu() {
  menuBtn.addEventListener("click", () => {
    if (window.innerWidth <= 765) {
      menu.classList.remove('hidden');
      menu.classList.add('block');
    }
  });
}

displayMenu();

function removeMenu(){
  asideCancelBtn.addEventListener('click', ()=> {
    if (window.innerWidth <= 765) {
      menu.classList.add('hidden');
      menu.classList.remove('block');
    }
  });
}

removeMenu();

function setupBackdropMenu() {
  document.getElementById("option-btn").addEventListener("click", () => {
    document.getElementById("backdrop-menu").classList.remove("hidden");
  });

  document.getElementById("backdrop-menu").addEventListener("click", () => {
    document.getElementById("backdrop-menu").classList.add("hidden");
  });
}



setupBackdropMenu();


