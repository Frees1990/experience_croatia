/* jshint esversion: 11, jquery: true */

// Main Function
$(document).ready(function () {
  sideNav();
  selectForm();
  datepicker();
  initialiseModal();
  initialiseToolTipped();
  initialiseDropdown();
  manageAccount();
  initialiseCarousel();
});

// Side Navigation Function
function sideNav() {
  $('.hamburger').on("click", function () {
    $(".mobile-menu").toggleClass("open");
  });
}

// Form Select Initialization with Materialize Fix
function selectForm() {
  const elems = document.querySelectorAll('select');
  M.FormSelect.init(elems);

  setTimeout(() => {
    $('.select-wrapper.input-field').each(function () {
      const $parentDiv = $(this);
      const $label = $parentDiv.children('label');
      const $ul = $parentDiv.children('ul.select-dropdown');
      const $caret = $parentDiv.find('svg.caret');
      const $input = $parentDiv.find('input.select-dropdown');

      if ($label.length && $ul.length && $label.next()[0] !== $ul[0]) {
        $label.insertBefore($ul);
      }

      if ($caret.length && $input.length) {
        $caret.on('click', function () {
          $input.trigger('click');
        });
      }

      $ul.children('li').on('click', function () {
        $input.trigger('click');
      });
    });
  }, 0);
}

// Dropdown Initialization Function
function initialiseDropdown() {
  const elems = document.querySelectorAll('.dropdown-trigger');
  M.Dropdown.init(elems, {
    coverTrigger: false,
  });
}

// Datepicker Initialization
function datepicker() {
  const elems = document.querySelectorAll('.datepicker');
  const today = new Date();
  const threeMonthsFromToday = new Date(today);
  threeMonthsFromToday.setMonth(today.getMonth() + 3);

  M.Datepicker.init(elems, {
    format: "dd mmmm, yyyy",
    minDate: today,
    maxDate: threeMonthsFromToday,
    yearRange: 1,
    showClearBtn: true,
    i18n: {
      done: "Select"
    }
  });
}

// Modal Initialization Function
function initialiseModal() {
  const elems = document.querySelectorAll('.modal');
  M.Modal.init(elems, {
    opacity: 0.5,
    inDuration: 250,
    outDuration: 200,
    dismissible: true,
    startingTop: '4%',
    endingTop: '10%'
  });
}

// Tooltip Initialization Function
function initialiseToolTipped() {
  const elems = document.querySelectorAll('.tooltipped');
  M.Tooltip.init(elems);
}

// Manage Account Hover Effect
function manageAccount() {
  $(".manage-account-link").hover(
    function () {
      $("#manage-account").addClass("hovered");
    },
    function () {
      $("#manage-account").removeClass("hovered");
    }
  );
}

// Carousel Initialization and Autoplay
function initialiseCarousel() {
  const carousel = document.querySelectorAll('.carousel');
  M.Carousel.init(carousel, {
    fullWidth: true,
    indicators: true,
  });

  let indicatorItems = document.querySelectorAll('.carousel .indicator-item'),
      slideTime = 3000,
      activeClass = "active";

  setInterval(() => {
    indicatorItems.forEach(el => {
      if (el.classList.contains(activeClass)) {
        let sib = el.nextElementSibling;
        if (sib == null) {
          indicatorItems[0].click();
        } else {
          sib.click();
        }
      }
    });
  }, slideTime);
}

// Auto-resizing Text Area for Messages
$('#message').on('input', function () {
  this.style.height = 'auto';
  this.style.height = (this.scrollHeight) + 'px';
});
