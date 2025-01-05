document.addEventListener('DOMContentLoaded', function() {
    // Set today's date and max date for reservation date input
    const today = new Date();
    const minDate = new Date();
    minDate.setDate(today.getDate() + 1); // Tomorrow's date
    const maxDate = new Date();
    maxDate.setDate(today.getDate() + 14); // Two weeks from today

    // Format dates to YYYY-MM-DD
    const formatDate = function(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are zero-based
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    };

    // Set min and max attributes for the reservation_date input
    const reservationDateInput = document.getElementById('reservation_date');
    if (reservationDateInput) {
        reservationDateInput.setAttribute('min', formatDate(minDate));
        reservationDateInput.setAttribute('max', formatDate(maxDate));
    } else {
        console.error('Reservation date input not found');
    }

    // Handle form submission
    const reservationForm = document.getElementById('reservationForm');
    if (reservationForm) {
        reservationForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            const jsonData = {};
            
            formData.forEach(function(value, key) {
                jsonData[key] = value;
            });

            // Ensure hash_key is included in the URL
            if (!jsonData.hash_key) {
                displayMessage('Hash key is missing.');
                return;
            }

            // Combine reservation date and time into a single Date object
            const reservationDate = new Date(jsonData.reservation_date + 'T' + jsonData.reservation_time);
            
            // Validate reservation date and time
            const validationMessage = validateReservation(reservationDate, minDate, maxDate);
            if (validationMessage) {
                displayMessage(validationMessage);
                return;
            }

            console.log('Sending data:', jsonData); // Log data being sent

            fetch(`/api/reservation/${jsonData.hash_key}`, {  
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(jsonData)
            })
            .then(response => {
                if (!response.ok) {
                    return response.text().then(text => {
                        throw new Error(`HTTP error! status: ${response.status}, message: ${text}`);
                    });
                }
                return response.json();
            })
            .then(response => {
                console.log('Response data:', response);
                // Check if the response indicates success
                if (response.message) {  // Assuming the server response contains a message on success
                    window.location.href = '/reservations'; // Redirect on success
                } else {
                    displayMessage(response.message || 'An unexpected error occurred.');
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
                displayMessage('An error occurred. Please try again.');
            });
        });
    } else {
        console.error('Reservation form not found');
    }

    function validateReservation(reservationDate, minDate, maxDate) {
        if (reservationDate < minDate || reservationDate > maxDate) {
            return 'Reservations can only be made for up to two weeks in advance and must be for tomorrow or later.';
        }

        const reservationHour = reservationDate.getHours();
        if (reservationHour < 9 || reservationHour >= 16) {
            return 'Reservations can only be made between 9 AM and 4 PM.';
        }

        return null; // No error
    }

    function displayMessage(message) {
        const messageElement = document.getElementById('message');
        if (messageElement) {
            messageElement.innerText = message;
            messageElement.style.display = 'block';
        } else {
            console.error('Message element not found');
        }
    }
});
