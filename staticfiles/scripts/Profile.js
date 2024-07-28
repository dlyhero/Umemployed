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
  console.log("Fetching suggested skills...");
  fetch("/dashboard/api/suggested-skills/") // replace with your actual endpoint
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok " + response.statusText);
      }
      return response.json();
    })
    .then((data) => {
      console.log("Suggested skills fetched successfully:", data);
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



document.getElementById('skills-form').addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent the default form submission

    // Collect selected skills
    let selectedSkills = [];
    document.querySelectorAll('.skill-checkbox:checked').forEach(function (checkbox) {
        selectedSkills.push(checkbox.value);
    });

    console.log("Selected Skills:", selectedSkills); // Debug statement

    // Update the hidden input field with the selected skills
    document.getElementById('selected-skills').value = JSON.stringify(selectedSkills);

    console.log("Hidden Input Value:", document.getElementById('selected-skills').value); // Debug statement

    // Submit the form
    this.submit();
});




// Initialize suggested skills
function initializeSuggestedSkills() {
  suggestedSkillsContainer.innerHTML = "";
  suggestedSkills.forEach((skill) => {
    const skillElement = document.createElement("div");
    skillElement.innerHTML = `
      <li data-id="${skill.id}" class="hover:bg-blue-500 hover:text-white mb-2 text-nowrap px-2 py-1 w-fit rounded-full suggested-skill">
        <input type="checkbox" id="skill-${skill.id}" class="custom-checkbox" data-id="${skill.id}" value="${skill.name}">
        <label for="skill-${skill.id}" class="custom-label">${skill.name}</label>
      </li>`;
    suggestedSkillsContainer.appendChild(skillElement);
  });
}

function renderSkillList() {
  // Implement rendering skill list from the existing skills
}

function attachDeleteButtonListeners() {
  // Implement attaching listeners to delete buttons
}
