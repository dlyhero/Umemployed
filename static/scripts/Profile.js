import { sideBar } from "./resume.js";
import user from "../data/user.js";
console.log("Profile.js loaded successfully");
// DOM Elements
const cvBtn = document.getElementById("option-btn");
const options = document.getElementById("options");
const addSkillBtn = document.getElementById("add-skill-btn");
const skillModal = document.getElementById("skill-modal");
const skillModalBtn = document.getElementById("skill-modal-btn");
const skillInput = document.getElementById("input-skill");
const suggestedSkillsContainer = document.getElementById("suggested-skills");
const saveSkillBtn = document.getElementById("save-skill-btn");
const backdrop = document.querySelector("#backdrop");
const feedbackMessage = document.querySelector("#feedback-message");

// Toggle options display
cvBtn.addEventListener("click", () => {
  options.style.display = "block";
});
options.addEventListener("click", () => {
  options.style.display = "none";
});

// Show/hide skill modal
addSkillBtn.addEventListener("click", () => {
  skillModal.style.display = "flex";
});
skillModalBtn.addEventListener("click", () => {
  skillModal.style.display = "none";
});
backdrop.addEventListener("click", () => {
  skillModal.style.display = "none";
});

// Initialize variables for skill input
let selectedSkills = [];
let suggestedSkills = []; // to hold the skills from the backend
let Skills = []
// Fetch suggested skills from the backend
document.addEventListener("DOMContentLoaded", () => {
  skillInput.addEventListener("input", handleSkillInput);

  fetchSuggestedSkills();
  renderSkillList();
  attachDeleteButtonListeners();
  sideBar();
});

// Fetch suggested skills from backend and initialize them
function fetchSuggestedSkills() {
  fetch("/dashboard/api/suggested-skills/") // replace with your actual endpoint
    .then((response) => response.json())
    .then((data) => {
      suggestedSkills = data;
      initializeSuggestedSkills();
    })
    .catch((error) => console.error("Error fetching suggested skills:", error));
}

// Handle skill input for auto-suggestions
function handleSkillInput() {
  const query = skillInput.value.toLowerCase();
  suggestedSkillsContainer.innerHTML = "";

  if (query) {
    const filteredSkills = suggestedSkills.filter((skill) =>
      skill.name.toLowerCase().includes(query)
    );
    if (filteredSkills.length === 0) {
      const notFoundElement = document.createElement("div");
      notFoundElement.textContent = "No skills found";
      notFoundElement.className = "not-found";
      suggestedSkillsContainer.appendChild(notFoundElement);
    } else {
      filteredSkills.forEach((skill) => {
        const skillElement = document.createElement("div");
        skillElement.innerHTML = `
          <li data-id="${skill.id}" class="hover:bg-blue-500 hover:text-white mb-2 text-nowrap px-2 py-1 w-fit rounded-full suggested-skill">
            <input type="checkbox" id="skill-${skill.id}" class="custom-checkbox" data-id="${skill.id}" value="${skill.name}">
            <label for="skill-${skill.id}" class="custom-label">${skill.name}</label>
          </li>`;
        suggestedSkillsContainer.appendChild(skillElement);
      });
    }
  }
}

// Initialize suggested skills
function initializeSuggestedSkills() {
  let suggestedSkillHtml = "";
  suggestedSkills.slice(0, 15).forEach((skill) => {
    suggestedSkillHtml += `
      <li data-id='${skill.id}' class="hover:bg-blue-500 hover:text-white mb-2 text-nowrap px-2 py-1 w-fit rounded-full suggested-skill">
        <input type="checkbox" id="skill-${skill.id}" class="custom-checkbox" data-id="${skill.id}" value="${skill.name}">
        <label for="skill-${skill.id}" class="custom-label">${skill.name}</label>
      </li>`;
  });
  suggestedSkillsContainer.innerHTML = suggestedSkillHtml;
}

// Handle save skill button click
// Get the CSRF token from the cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrfToken = getCookie('csrftoken');

saveSkillBtn.addEventListener("click", handleSaveSkill);

// Handle save skill button click
function handleSaveSkill() {
  console.log("handleSaveSkill function called"); // Add this line for debugging

  // Get the IDs of selected skills
  const selectedSkillIds = [];
  document.querySelectorAll('#suggested-skills input[type="checkbox"]:checked').forEach((checkbox) => {
    selectedSkillIds.push(checkbox.dataset.id);
  });

  console.log("Selected Skill IDs:", selectedSkillIds); // Print selected skill IDs to the console

  // Send a POST request to update user skills
  fetch("/dashboard/update-user-skills/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken, // Assuming you have a CSRF token available
    },
    body: JSON.stringify({ selected_skills: selectedSkillIds }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Failed to update skills");
      }
      return response.json();
    })
    .then((data) => {
      // Handle success response
      console.log(data.message); // Log success message
      renderSkillList();
      attachDeleteButtonListeners();
      initializeSuggestedSkills();
      skillModal.style.display = "none"; // Hide the modal after saving
    })
    .catch((error) => {
      // Handle error
      console.error(error);
      displayMessage("Failed to update skills", "error");
    });
}

// Render skill list
function renderSkillList() {
  let skillHtml = "";
  skills.forEach((item) => {
    let htmlcode = `
      <div class="skill border p-5 mb-2 rounded-lg font-bold flex justify-between items-center" data-id="${item.id}">
        <p class="title">${item.name}</p>
        <div class="btn-wraps flex gap-4">
          <button class="w-6 delete-skill-btn" data-id="${item.id}"><img src="../build/img/delete-2-svgrepo-com.svg" alt="delete icon"></button>
        </div>
      </div>
    `;
    skillHtml += htmlcode;
  });
  document.getElementById("skill-wrap").innerHTML = skillHtml;
  attachDeleteButtonListeners();
}


// Display feedback message
function displayMessage(message, type) {
  feedbackMessage.textContent = message;
  feedbackMessage.classList.remove("hidden", "success", "error");
  feedbackMessage.classList.add(type);

  setTimeout(() => {
    feedbackMessage.classList.add("hidden");
  }, 3000);
}

// Attach delete button listeners
function attachDeleteButtonListeners() {
  document.querySelectorAll(".delete-skill-btn").forEach((button) => {
    button.addEventListener("click", () => {
      const skillId = button.dataset.id;
      user.skill = user.skill.filter((skill) => skill.id !== skillId);
      renderSkillList();
    });
  });
}
