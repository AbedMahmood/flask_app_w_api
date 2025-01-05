document.addEventListener('DOMContentLoaded', function() {
    const deleteButton = document.getElementById('deleteButton');

    if (deleteButton) {
        deleteButton.addEventListener('click', function() {
            const hashKey = document.getElementById('hash_key').value;

            if (!hashKey) {
                displayMessage('Hash key is missing.');
                return;
            }

            fetch(`/api/reservation/${hashKey}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        throw new Error(`HTTP error! status: ${response.status}, message: ${err.error}`);
                    });
                }
                return response.json();
            })
            .then(response => {
                console.log('Response data:', response);
                
                // Check if the response indicates success
                if (response.message) {
                    displayMessage(response.message); // Show success message
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
        console.error('Delete button not found');
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
