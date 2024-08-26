/* jshint esversion: 11, jquery: true */
// Main Function 
$(document).ready(function () {
    sideNav();
    selectForm();
    datepicker();
    initialiseModal();
    initialiseToolTipped();
    initialiseDropdown();
});
    $('#message').on('input', function () {
        this.style.height = 'auto';

        this.style.height =
            (this.scrollHeight) + 'px';
    });
/** Initialisation of Materialize dropdown elements*/
function initialiseDropdown() {
    const elems = document.querySelectorAll('.dropdown-trigger');
    const instances = M.Dropdown.init(elems, {
        coverTrigger: false,
    });
}

function selectForm() {
    const elems = document.querySelectorAll('select');
    M.FormSelect.init(elems);
  
    // Credits to Tim Nelson for helping fix Materialize select bug
    // Wait for the Materialize initialization to complete
    setTimeout(() => {
      // Select each .select-wrapper.input-field and swap the label and ul if needed
      $('.select-wrapper.input-field').each(function () {
        const $parentDiv = $(this);
  
        // get the label and ul within the parent div
        const $label = $parentDiv.children('label');
        const $ul = $parentDiv.children('ul.select-dropdown');
        const $caret = $parentDiv.find('svg.caret');
        const $input = $parentDiv.find('input.select-dropdown');
  
        // move the label before the ul if it's not already
        if ($label.length && $ul.length && $label.next()[0] !== $ul[0]) {
          $label.insertBefore($ul);
        }
  
        // Ensure the caret triggers the dropdown
        if ($caret.length && $input.length) {
          $caret.on('click', function () {
            $input.trigger('click');
          });
        }
  
        // Close the dropdown when an option is clicked
        $ul.children('li').on('click', function () {
          $input.trigger('click');
        });
      });
    }, 0);
  }
  
/** Initialisation of Materialize datepicker elements*/
function datepicker() {
    const elems = document.querySelectorAll('.datepicker');
    const today = new Date();
    // Calculate the date 3 months from `today`
    // Credits to Tim Nelson for helping calculate the three months
    const threeMonthsFromToday = new Date(today);
    threeMonthsFromToday.setMonth(today.getMonth() + 3);
    const instances = M.Datepicker.init(elems, {
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
  
  /** Initialisation of Materialize Modal elements*/
function initialiseModal() {
  const elems = document.querySelectorAll('.modal');
  const instances = M.Modal.init(elems);
}


/** Initialisation of Materialize tooltipped elements*/
function initialiseToolTipped() {
  const elems = document.querySelectorAll('.tooltipped');
  const instances = M.Tooltip.init(elems);
}

document.addEventListener('DOMContentLoaded', () => {
  // initialize carousel
  const carousel = document.querySelectorAll('.carousel');
  M.Carousel.init(carousel, {
    fullWidth : true,
    indicators: true, // this option is require for autoplay functionnality
  });
  
  // custom function for autoplaying 
  let indicatorItems = document.querySelectorAll('.carousel .indicator-item'),
      slideTime = 3000,
      activeClass = "active";
      onCycleTo = 5

  setInterval(() => {
    indicatorItems.forEach(el => {
      if (el.classList.contains(activeClass)) {
        sib = el.nextElementSibling;
        if (sib == null) {
          indicatorItems[8].click();
        } else {
          sib.click()
        }
      }
    });
  }, slideTime);
});

