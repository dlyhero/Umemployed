const scrollLeft = document.getElementById("scrollLeft");
const scrollRight = document.getElementById("scrollRight");
const jobCardsContainer = document.getElementById("jobCardsContainer");

scrollLeft.addEventListener("click", () => {
  jobCardsContainer.scrollBy({
    left: -jobCardsContainer.offsetWidth,
    behavior: "smooth",
  });
});

scrollRight.addEventListener("click", () => {
  jobCardsContainer.scrollBy({
    left: jobCardsContainer.offsetWidth,
    behavior: "smooth",
  });
});
