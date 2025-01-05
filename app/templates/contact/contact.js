
function handleSubmit(event) {
    event.preventDefault(); // Prevent the default form submission

    const form = document.getElementById('contactForm');
    
    if (form.checkValidity()) {
        // Hide the form and show the thank you message
        document.getElementById('contact-form').style.display = 'none';
        document.getElementById('thank-you-message').style.display = 'block';
        
        // Here you could also send the form data using AJAX if needed
        console.log("Form submitted successfully!"); // Debugging line
        // You can use fetch or XMLHttpRequest to send data to your server here.
    } else {
        alert("Please fill out all required fields correctly.");
    }
}