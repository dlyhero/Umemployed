
        const modal = document.getElementById("applyModal");
        const closeModalBtn = document.getElementsByClassName("close")[0];
        const applyButtons = document.querySelectorAll(".apply-button");


        applyButtons.forEach(button => {
            button.addEventListener("click", () => {
                modal.style.display = "block";
            });
        });


        closeModalBtn.onclick = function() {
            modal.style.display = "none";
        }


        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = "none";
            }
        }
