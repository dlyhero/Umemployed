document.addEventListener("DOMContentLoaded", function () {
  let currentSkill = "python"; // Default skill
  let questionSetIndex = 0;
  let timer;
  let timeRemaining = 300; // 5 minutes in seconds
  let timerExpired = false; // Flag to handle timer expiration

  const skillButtons = document.querySelectorAll(".skill-btn");
  const questionSection = document.getElementById("question-section");
  const questionForm = document.getElementById("question-form");
  const nextBtn = document.getElementById("next-btn");
  const submitBtn = document.getElementById("submit-btn");
  const timerDisplay = document.getElementById("timer");

  nextBtn.classList.remove("hidden");
  submitBtn.classList.add("hidden");

  skillButtons.forEach((button) => {
    button.addEventListener("click", () => {
      currentSkill = button.getAttribute("data-skill");
      questionSetIndex = 0;
      displayQuestions();
      nextBtn.classList.remove("hidden");
      submitBtn.classList.add("hidden");
      resetTimer();
    });
  });

  submitBtn.addEventListener("click", () => {
    timerExpired = true; // Stop timer-based submission
    clearInterval(timer); // Stop the timer immediately
    submitForm(false); // Direct manual submission without alert
  });

  function displayQuestions() {
    if (!currentSkill) return;
    const questions = skills[currentSkill][questionSetIndex];
    questionForm.innerHTML = "";

    questions.forEach((question, index) => {
      const fieldset = document.createElement("fieldset");
      fieldset.classList.add("mb-2");
      fieldset.innerHTML = `
                <legend class="font-semibold mb-2">${question.question}</legend>
                ${question.options
                  .map(
                    (option) => `
                    <label class="block mb-0">
                        <input type="radio" name="question${index}" value="${option}" class="mr-2">
                        ${option}
                    </label>
                `
                  )
                  .join("")}
            `;
      questionForm.appendChild(fieldset);
    });
  }

  function resetTimer() {
    clearInterval(timer);
    timeRemaining = 300; // 5 minutes in seconds
    timerExpired = false; // Reset expiration flag for new skill
    updateTimerDisplay();
    timer = setInterval(() => {
      timeRemaining--;
      updateTimerDisplay();
      if (timeRemaining <= 0 && !timerExpired) {
        // Only submit if timer runs out without manual submission
        clearInterval(timer);
        submitForm(true); // Timer-based submission
      }
    }, 1000);
  }

  function updateTimerDisplay() {
    const minutes = Math.floor(timeRemaining / 60);
    const seconds = timeRemaining % 60;
    timerDisplay.textContent = `Timer: ${minutes}:${
      seconds < 10 ? "0" : ""
    }${seconds}`;
  }

  function submitForm(isTimerTriggered = false) {
    if (isTimerTriggered) {
      alert("Time's up! Submitting the responses.");
    }
    questionForm.submit();
  }

  resetTimer(); // Start timer on page load
});
