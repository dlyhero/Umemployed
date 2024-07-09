document.addEventListener("DOMContentLoaded", function () {
  const readMoreLinks = document.querySelectorAll(".read-more");

  readMoreLinks.forEach((link) => {
    link.addEventListener("click", function (event) {
      event.preventDefault();
      const hiddenText = this.previousElementSibling;
      const isCurrentlyOpen = hiddenText.classList.contains("extended");

      readMoreLinks.forEach((otherLink) => {
        const otherHiddenText = otherLink.previousElementSibling;
        if (
          otherLink !== link &&
          otherHiddenText.classList.contains("extended")
        ) {
          otherHiddenText.classList.remove("extended");
          otherLink.textContent = "Read more";
        }
      });

      if (isCurrentlyOpen) {
        hiddenText.classList.remove("extended");
        this.textContent = "Read more";
      } else {
        hiddenText.classList.add("extended");
        this.textContent = "Read less";
      }
    });
  });

  const hiddenTexts = document.querySelectorAll(".hidden-text");
  hiddenTexts.forEach((text) => {
    text.classList.remove("extended");
    const readMoreLink = text.nextElementSibling;
    readMoreLink.textContent = "Read more";
  });
});
document.addEventListener("DOMContentLoaded", function () {
  const readMoreLinks = document.querySelectorAll(".read-more");

  readMoreLinks.forEach((link) => {
    link.addEventListener("click", function (event) {
      event.preventDefault();
      const hiddenText = this.previousElementSibling;
      const isCurrentlyOpen = hiddenText.classList.contains("extended");

      readMoreLinks.forEach((otherLink) => {
        const otherHiddenText = otherLink.previousElementSibling;
        if (
          otherLink !== link &&
          otherHiddenText.classList.contains("extended")
        ) {
          otherHiddenText.classList.remove("extended");
          otherLink.textContent = "Read more";
        }
      });

      if (isCurrentlyOpen) {
        hiddenText.classList.remove("extended");
        this.textContent = "Read more";
      } else {
        hiddenText.classList.add("extended");
        this.textContent = "Read less";
      }
    });
  });

  const hiddenTexts = document.querySelectorAll(".hidden-text");
  hiddenTexts.forEach((text) => {
    text.classList.remove("extended");
    const readMoreLink = text.nextElementSibling;
    readMoreLink.textContent = "Read more";
  });

  async function downloadPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    const elementHTML = document.getElementById("Download").outerHTML;

    doc.html(elementHTML, {
      callback: function (doc) {
        doc.save("feedback_report.pdf");
      },
      x: 10,
      y: 10,
      width: 190,
      windowWidth: 650,
      autoPaging: "text",
      html2canvas: { scale: 0.3 },
    });
  }

  window.downloadPDF = downloadPDF;

  function retakeTest() {
    alert("Retake Test functionality is not implemented yet.");
  }

  window.retakeTest = retakeTest;
});
