document.addEventListener("DOMContentLoaded", function() {
    const replyForm = document.getElementById('replyForm');
    
    replyForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the form from submitting the traditional way

        // Get form data
        const formData = new FormData(replyForm);
        
        // Send an AJAX POST request to submit the reply
        fetch(replyForm.action, {
            method: 'POST',
            body: formData,
            headers: {
                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Clear the form
                replyForm.reset();

                // Append the new reply to the replies list
                const repliesList = document.querySelector('.list-group');
                const newReplyHTML = `
                    <li class="list-group-item">
                        <strong>${data.reply.user.username}</strong>: ${data.reply.body}
                        <small class="text-muted">${data.reply.created_at}</small>
                    </li>
                `;
                repliesList.insertAdjacentHTML('beforeend', newReplyHTML);

                // Optionally, scroll to the new reply or show a success message
            } else {
                // Handle error (e.g., show a message)
                alert(data.error || "An error occurred while submitting your reply.");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("An error occurred. Please try again.");
        });
    });
});
