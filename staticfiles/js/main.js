(function ($) {
    "use strict";

    // Spinner
    var spinner = function () {
        setTimeout(function () {
            if ($('#spinner').length > 0) {
                $('#spinner').removeClass('show');
            }
        }, 1);
    };
    spinner();
    
    
    // Initiate the wowjs
    new WOW().init();


    // Sticky Navbar
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            $('.sticky-top').css('top', '0px');
        } else {
            $('.sticky-top').css('top', '-100px');
        }
    });
    
    
    // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });
    $('.back-to-top').click(function () {
        $('html, body').animate({scrollTop: 0}, 1500, 'easeInOutExpo');
        return false;
    });


    // Header carousel
    $(".header-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1500,
        items: 1,
        dots: true,
        loop: true,
        nav : true,
        navText : [
            '<i class="bi bi-chevron-left"></i>',
            '<i class="bi bi-chevron-right"></i>'
        ]
    });


    // Testimonials carousel
    $(".testimonial-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        center: true,
        margin: 24,
        dots: true,
        loop: true,
        nav : false,
        responsive: {
            0:{
                items:1
            },
            768:{
                items:2
            },
            992:{
                items:3
            }
        }
    });
    
})(jQuery);



// see more and see less
document.addEventListener("DOMContentLoaded", function () {
  var allJobs = document.querySelectorAll(".job-item"); // Get all job items
  var showMoreButton = document.querySelector("#showMoreButton"); // Get the "See More Jobs" button

  var visibleJobs = 6; // Number of initially visible jobs
  var totalJobs = allJobs.length; // Total number of jobs

  // Function to toggle visibility of jobs
  function toggleJobsVisibility() {
    for (var i = 0; i < totalJobs; i++) {
      if (i < visibleJobs) {
        allJobs[i].style.display = "block";
      } else {
        allJobs[i].style.display = "none";
      }
    }

    // Update the button text based on visibility
    if (visibleJobs >= totalJobs) {
      showMoreButton.textContent = "See Less Jobs";
    } else {
      showMoreButton.textContent = "See More Jobs";
    }
  }

  // Show initial set of jobs
  toggleJobsVisibility();

  // Event listener for "See More Jobs" button
  showMoreButton.addEventListener("click", function (e) {
    e.preventDefault();

    // Toggle the number of visible jobs
    if (visibleJobs >= totalJobs) {
      visibleJobs = 6; // Reset to the initial number of visible jobs
    } else {
      visibleJobs += 6; // Increase the number of visible jobs by6
    }

    toggleJobsVisibility(); // Toggle visibility of jobs
  });
});
