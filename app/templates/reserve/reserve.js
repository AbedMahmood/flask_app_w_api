document.addEventListener('DOMContentLoaded', function() {
    // Set today's date and max date for reservation date input
    var today = new Date();
    var minDate = new Date();
    minDate.setDate(today.getDate() + 1); // Tomorrow's date
    var maxDate = new Date();
    maxDate.setDate(today.getDate() + 14); // Two weeks from today

    // Format dates to YYYY-MM-DD
    var formatDate = function(date) {
        var year = date.getFullYear();
        var month = String(date.getMonth() + 1).padStart(2, '0'); // Months are zero-based
        var day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    };

    // Set min and max attributes for the reservation_date input
    document.getElementById('reservation_date').setAttribute('min', formatDate(minDate));
    document.getElementById('reservation_date').setAttribute('max', formatDate(maxDate));

    // Handle form submission
    document.getElementById('reservationForm').addEventListener('submit', function(e) {
        e.preventDefault();

        var formData = new FormData(this);
        var jsonData = {};
        
        formData.forEach(function(value, key) {
            jsonData[key] = value;
        });

        // Combine reservation date and time into a single Date object
        var reservationDate = new Date(jsonData.reservation_date + 'T' + jsonData.reservation_time);
        
        // Check if the reservation is within two weeks
        if (reservationDate < minDate || reservationDate > maxDate) {
            document.getElementById('message').innerText = 'Reservations can only be made for up to two weeks in advance and must be for tomorrow or later.';
            document.getElementById('message').style.display = 'block';
            return;
        }

        // Check if the time is within 9 AM to 4 PM
        var reservationHour = reservationDate.getHours();
        if (reservationHour < 9 || reservationHour >= 16) {
            document.getElementById('message').innerText = 'Reservations can only be made between 9 AM and 4 PM.';
            document.getElementById('message').style.display = 'block';
            return;
        }

        console.log('Sending data:', jsonData); // Log data being sent

        fetch('/api/reservation', {
            method: 'POST',
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
            if (response.success) {
                window.location.href = '/reservation?key=' + response.data.reservation_key;
            } else {
                document.getElementById('message').innerText = response.message;
                document.getElementById('message').style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Fetch error:', error);
            document.getElementById('message').innerText = 'An error occurred. Please try again.';
            document.getElementById('message').style.display = 'block';
        });
        
    });
});
