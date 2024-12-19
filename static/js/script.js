document.addEventListener("DOMContentLoaded", function () {
    // Initialize components based on their presence in the DOM
    if (document.querySelector('.hamburger')) {
        sideNav(); // Handles the mobile menu toggle
    }
  
    if (document.querySelector('select')) {
        selectForm();
    }
  
    if (document.querySelector('.datepicker')) {
        datepicker();
    }
  
    if (document.querySelector('.modal')) {
        initialiseModal();
    }
  
    if (document.querySelector('.carousel')) {
        initialiseCarousel();
    }
  
    if (document.querySelector('.manage-account-link')) {
        manageAccount();
    }
    if (document.querySelector('.dropdown-trigger')) {
        initialiseDropdown();
    }
  
    // New logic for checkbox-based menu toggle
    const checkbox = document.getElementById('mobile-menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');
  
    if (checkbox && mobileMenu) {
        checkbox.addEventListener('change', () => {
            if (checkbox.checked) {
                mobileMenu.classList.add('open');
            } else {
                mobileMenu.classList.remove('open');
            }
        });
    }
  });
  
  // Toggle mobile side navigation
  function sideNav() {
    document.querySelector('.hamburger').addEventListener('click', function () {
        document.querySelector('.mobile-menu').classList.toggle('open');
    });
  }  

// Initialize Materialize select elements with custom event handling
function selectForm() {
  const elems = document.querySelectorAll('select');
  M.FormSelect.init(elems);

  setTimeout(() => {
      document.querySelectorAll('.select-wrapper.input-field').forEach((parentDiv) => {
          const label = parentDiv.querySelector('label');
          const ul = parentDiv.querySelector('ul.select-dropdown');
          const caret = parentDiv.querySelector('svg.caret');
          const input = parentDiv.querySelector('input.select-dropdown');

          if (label && ul && label.nextElementSibling !== ul) {
              parentDiv.insertBefore(label, ul);
          }

          if (caret && input) {
              caret.addEventListener('click', () => input.click());
          }

          ul.querySelectorAll('li').forEach((li) => {
              li.addEventListener('click', () => input.click());
          });
      });
  }, 0);
}

// Initialize Materialize datepickers
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
      i18n: { done: "Select" }
  });
}

// Initialize Materialize modals
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

// Manage account hover effects
function manageAccount() {
  const accountLink = document.querySelector('.manage-account-link');
  const manageAccountElement = document.getElementById('manage-account');

  accountLink.addEventListener('mouseover', function () {
      manageAccountElement.classList.add('hovered');
  });

  accountLink.addEventListener('mouseout', function () {
      manageAccountElement.classList.remove('hovered');
  });
}

// Initialize Materialize carousels with autoplay
function initialiseCarousel() {
  const carousels = document.querySelectorAll('.carousel');
  M.Carousel.init(carousels, {
      fullWidth: true,
      indicators: true
  });

  const indicators = document.querySelectorAll('.carousel .indicator-item');
  const slideTime = 3000;
  const activeClass = "active";

  setInterval(() => {
      indicators.forEach(el => {
          if (el.classList.contains(activeClass)) {
              const sibling = el.nextElementSibling;
              if (!sibling) {
                  indicators[0].click();
              } else {
                  sibling.click();
              }
          }
      });
  }, slideTime);
}

// Toggle password visibility (JShint is saying this is unused but I need this to toggle visibility of the password entered hide/unhide)
function togglePasswordVisibility(inputId, toggleIconId) {
    const inputField = document.getElementById(inputId);
    const toggleIcon = document.getElementById(toggleIconId);
  
    if (inputField.type === "password") {
        inputField.type = "text";
        toggleIcon.classList.replace("visibility_off", "visibility");
    } else {
        inputField.type = "password";
        toggleIcon.classList.replace("visibility", "visibility_off");
    }
}

// Form validation function ()
function validateForm() {
  const formElements = document.forms[0].elements;
  const requiredFields = Array.from(formElements).filter(field => field.required);

  for (const field of requiredFields) {
      if (!field.value.trim()) {
          document.getElementById('error-message').innerText = "Please fill out all required fields.";
          return false;
      }
  }
  return true;
}

// Initialize Materialize dropdowns
function initialiseDropdown() {
  const elems = document.querySelectorAll('.dropdown-trigger');
  M.Dropdown.init(elems, {
      coverTrigger: false, // Dropdown appears below the trigger element
      constrainWidth: false // Dropdown width can vary
  });
}