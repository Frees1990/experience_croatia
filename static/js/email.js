document.addEventListener('DOMContentLoaded', function () {
    M.AutoInit(); // Automatically initialize Materialize components
});

// Initialize EmailJS with your Public API Key
(function () {
    emailjs.init("YOUR_PUBLIC_API_KEY"); // Replace with your Public API Key
})();

// Form submission handler
document.getElementById('contact-form').addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent the form from submitting normally

    var formData = new FormData(this);
    var name = formData.get('name');
    var email = formData.get('email');
    var phone = formData.get('number') || 'Not Provided'; // Default to 'Not Provided' if empty
    var message = formData.get('message');

    // Send email using EmailJS
    emailjs.sendForm('YOUR_SERVICE_ID', 'YOUR_TEMPLATE_ID', this)
        .then(function (response) {
            // Success callback
            console.log('Email sent successfully!', response);
            document.getElementById('thank-you').style.display = 'block';
            document.getElementById('contact-form').reset(); // Reset form
        }, function (error) {
            // Error callback
            console.error('Error sending email:', error);
            alert('Failed to send message. Please try again later.');
        });
});