const form = document.getElementById("contactForm");
const feedback = document.getElementById("thank-you-feedback");


initTextArea();

/** Initialise Materialize text area */
function initTextArea() {
    const message = document.querySelector('#message');
    M.Forms.InitTextarea(message);
    M.Forms.textareaAutoResize(message);
}

/** Function to send mail once validated using emailjs */
function sendMail(contactForm) {
    if (validateForm(this)) {
        emailjs.send("service_93gheht", "template_pnxbum8", {
            from_name: contactForm.name.value,
            message: contactForm.message.value,
            reply_to: contactForm.email.value
        }).then(
            (response) => {
                form.style.display = "none";
                feedback.style.display = "block";
            },
            (error) => {
                console.log("FAILED", error);
            }
        );
        return false;
    } else {
        this.addEventListener('submit', function (event) {
            event.preventDefault();
        });
        console.log("ERROR: Unable to send form as the required fields have not been completed");
    }
}

/**Function to validate the form */
function validateForm() {
    let nameInput = document.forms.contactForm.name;
    let emailInput = document.forms.contactForm.email;
    let enquiryInput = document.forms.contactForm.message;
    if (nameInput.value === "") {
        return false;
    } else if (emailInput.value === "") {
        return false;
    } else if (enquiryInput.value === "") {
        return false;
    } else {
        return true;
    }
}