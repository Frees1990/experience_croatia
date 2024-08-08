/* jshint esversion: 11, jquery: true */
// Main Function 
$(document).ready(function () {
    sideNav();
    initialiseDropdown();

});
  
/** Initialisation of sidenav*/
function sideNav() {
    $('.hamburger').on("click", function () {
        $(".mobile-menu").toggleClass("open");
    });
}

/** Initialisation of Materialize dropdown elements*/
function initialiseDropdown() {
    const elems = document.querySelectorAll('.dropdown-trigger');
    const instances = M.Dropdown.init(elems, {
        coverTrigger: false,
    });
}
  