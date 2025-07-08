  // Toggle the sidebar visibility on mobile

  document
  .getElementById("send-message")
  .addEventListener("click", sendMessage);
document
  .getElementById("message-input")
  .addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage();
  });

function sendMessage() {
  const input = document.getElementById("message-input");
  const message = input.value.trim();
  const time = new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
  if (message) {
    const messageContainer = document.createElement("div");
    messageContainer.classList.add(
      "message-container",
      "sent",
      "animate-slide-in-right",
      "flex",
      "mb-4",
      "gap-3"
    );
    messageContainer.innerHTML = `
    <img src="https://via.placeholder.com/40" alt="Profile Picture" class="w-10 h-10 rounded-full ml-3">
    <div>
      <div class="bg-blue-500 text-white p-3 rounded-lg">
        <p class="text-sm">${message}</p>
      </div>
      <span id='' class="text-xs text-gray-600 mt-1 block">${time}</span>
    </div>
  `;
    document
      .getElementById("chat-messages")
      .appendChild(messageContainer);
    input.value = "";
    document.getElementById("chat-messages").scrollTop =
      document.getElementById("chat-messages").scrollHeight;
  }

  document.getElementById("message-sidebar").classList.add("hidden");
  document.getElementById("chat-window").classList.remove("hidden");
}

const messageItems = document.querySelectorAll(".message-item");
const messageContent = document.getElementById("chat-window");
const messageSidebar = document.getElementById("message-sidebar");
messageItems.forEach((item) => {
  item.addEventListener("click", () => {
    const username = item.getAttribute("data-username");
    const message = item.getAttribute("data-message");
    const profile = item.getAttribute("data-profile");

    document.getElementById("chat-header-username").innerText = username;
    document.getElementById("chat-header-profile").src =
      "https://via.placeholder.com/40";

    // Here you can load the chat history for the selected user
    // For demo purposes, we'll just reset the chat messages
    const chatMessages = document.getElementById("chat-messages");
    chatMessages.innerHTML = `
    <div class="message-container received animate-slide-in-left flex mb-4">
      <img src="https://via.placeholder.com/40" alt="Profile Picture" class="w-10 h-10 rounded-full mr-3">
      <div>
        <div class="bg-gray-200 p-3 rounded-lg">
          <p class="text-sm text-gray-900">${message}</p>
        </div>
        <span class="text-xs text-gray-600 mt-1 block">Earlier</span>
      </div>
    </div>
  `;

    if (window.innerWidth < 768) {
      messageSidebar.classList.add("hidden");
      messageContent.classList.remove("hidden");
    }
  });
});

document
  .getElementById("add-message-btn")
  .addEventListener("click", () => {
    alert("Add message functionality to be implemented.");
  });

// Show the sidebar when navigating to the message page
window.addEventListener("load", () => {
  if (window.innerWidth < 768) {
    toggleSidebar(true); // Show sidebar
  }
});

function updateVhUnit() {
  document.documentElement.style.setProperty(
    "--vh",
    `${window.innerHeight * 0.01}px`
  );
}

window.addEventListener("resize", updateVhUnit);
window.addEventListener("orientationchange", updateVhUnit);

// Initial setting of vh unit
updateVhUnit();
// Update the height when the window is resized
window.addEventListener("resize", updateVhUnit);

document
  .getElementById("back-button")
  .addEventListener("click", function () {
    document.getElementById("chat-window").classList.add("hidden");
    document
      .getElementById("message-sidebar")
      .classList.remove("hidden");
  });
