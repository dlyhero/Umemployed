import { sideBar } from "./resume.js";
import { setupBackdropMenu } from "./resume.js";
import { skills } from "../data/data.js";
import user from "../data/user.js";


// DOM Elements
const cvBtn = document.getElementById("cv-btn");
const optionsBackdrop = document.getElementById("options-backdrop");
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
  optionsBackdrop.classList.remove('hidden');
});
optionsBackdrop.addEventListener("click", () => {
  optionsBackdrop.classList.add('hidden')
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

// Initialize event listeners for skill input
document.addEventListener("DOMContentLoaded", () => {
  skillInput.addEventListener("input", handleSkillInput);
  saveSkillBtn.addEventListener("click", handleSaveSkill);

  renderSkillList();
  attachDeleteButtonListeners();
  initializeSuggestedSkills();
  sideBar();
  setupBackdropMenu();
});

// Handle skill input for auto-suggestions
function handleSkillInput() {
  const query = skillInput.value.toLowerCase();
  suggestedSkillsContainer.innerHTML = "";

  if (query) {
    const filteredSkills = skills.filter((skill) =>
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

// Handle save skill button click
function handleSaveSkill() {
  selectedSkills = [];
  suggestedSkillsContainer.querySelectorAll('input[type="checkbox"]:checked').forEach((checkbox) => {
    const skillName = checkbox.value;
    const skillId = checkbox.dataset.id;
    selectedSkills.push({ name: skillName, id: skillId });
  });

  if (selectedSkills.length === 0 && skillInput.value === "") {
    displayMessage("Please input a skill or select from suggestions.", "error");
    return;
  }

  if (selectedSkills.length === 0 && skillInput.value !== "") {
    const skill = skills.find((s) => s.name === skillInput.value);
    if (skill) {
      selectedSkills.push({ name: skill.name, id: skill.id });
    } else {
      displayMessage("Skill not found.", "error");
      return;
    }
  }

  selectedSkills.forEach((newSkill) => {
    if (!user.skill.some((s) => s.name === newSkill.name)) {
      user.skill.push(newSkill);
      displayMessage(`Skill ${newSkill.name} added successfully.`, "success");
      // Redirect to dashboard using JavaScript
      window.location.href = '{% url "dashboard" %}';
    } else {
      displayMessage(`Skill ${newSkill.name} already exists.`, "error");
      // Redirect to dashboard using JavaScript
      window.location.href = '{% url "dashboard" %}';
    }
  });

  renderSkillList();
  attachDeleteButtonListeners();
  initializeSuggestedSkills()
  skillModal.style.display = "none"; // Hide the modal after saving
}

// Render skill list
function renderSkillList() {
  let skillHtml = "";
  user.skill.forEach((item) => {
    let htmlcode = `
      <div class="skill border p-5 mb-2 rounded-lg font-bold flex justify-between items-center" data-id="${item.id}">
        <p class="title">${item.name}</p>
        <div class="btn-wraps flex gap-4">
          <button class="w-6 delete-skill-btn" data-id="${item.id}"><img src="./build/img/delete-2-svgrepo-com.svg" alt="delete icon"></button>
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

// Initialize suggested skills
function initializeSuggestedSkills() {
  let suggestedSkillHtml = "";
  skills.slice(0, 15).forEach((skill) => {
    suggestedSkillHtml += `
      <li data-id='${skill.id}' class="hover:bg-blue-500 hover:text-white mb-2 text-nowrap px-2 py-1 w-fit rounded-full suggested-skill">
        <input type="checkbox" id="skill-${skill.id}" class="custom-checkbox" data-id="${skill.id}" value="${skill.name}">
        <label for="skill-${skill.id}" class="custom-label">${skill.name}</label>
      </li>`;
  });
  suggestedSkillsContainer.innerHTML = suggestedSkillHtml;
}
