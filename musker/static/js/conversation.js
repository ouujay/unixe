document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById('chat-form');
    const chatMessagesContainer = document.getElementById('chat-messages');
    const messageInput = document.getElementById('chat-message-input');
    const imageUpload = document.getElementById('imageUpload');
    const videoUpload = document.getElementById('videoUpload');
    const triggerImageUpload = document.getElementById('triggerImageUpload');
    const triggerVideoUpload = document.getElementById('triggerVideoUpload');

    // Trigger image upload when the icon is clicked
    triggerImageUpload.addEventListener('click', function () {
        imageUpload.click();
    });

    // Trigger video upload when the icon is clicked
    triggerVideoUpload.addEventListener('click', function () {
        videoUpload.click();
    });

    // Handle form submission via AJAX
    chatForm.addEventListener('submit', function (e) {
        e.preventDefault();  // Prevent the form from submitting normally

        const recipientId = chatForm.dataset.recipientId;
        const formData = new FormData(chatForm);  // Create a FormData object to hold the form data

        // Send the message via an AJAX request
        fetch(`/send-message-ajax/${recipientId}/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Clear the input fields
                messageInput.value = "";
                imageUpload.value = "";
                videoUpload.value = "";

                // Add the new message to the chat window
                const newMessage = document.createElement('div');
                newMessage.classList.add('message', 'sent');
                let messageContent = `<div class="message-content"><p>${data.message.body}</p><small>Just now</small></div>`;

                if (data.message.image) {
                    messageContent += `<img src="${data.message.image}" class="img-fluid mt-2" alt="Sent Image">`;
                }

                if (data.message.video) {
                    messageContent += `
                        <video controls class="img-fluid mt-2">
                            <source src="${data.message.video}" type="video/mp4">
                            Your browser does not support the video tag.
                        </video>`;
                }

                newMessage.innerHTML = messageContent;
                chatMessagesContainer.appendChild(newMessage);

                // Scroll to the bottom of the chat window
                chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;

                // Optionally, update unread counts
                checkUnreadMessages();
            } else {
                alert("Message failed to send");
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    // Function to mark all messages as read
    function markMessagesAsRead() {
        fetch(`/mark-messages-read/${chatForm.dataset.recipientId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => {
            if (response.ok) {
                // Optionally refresh unread counts
                checkUnreadMessages();
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    // Function to check and update unread message counts
    function checkUnreadMessages() {
        fetch(`/check-unread-messages/`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => response.json())
        .then(data => {
            // Update the UI with the new unread counts
            const unreadBadge = document.querySelector('.badge-danger');
            if (unreadBadge) {
                unreadBadge.textContent = data.unread_count;
                if (data.unread_count === 0) {
                    unreadBadge.style.display = 'none';
                } else {
                    unreadBadge.style.display = 'inline-block';
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    // Scroll to the bottom of the chat window on page load
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;

    // Mark messages as read when the page is loaded
    markMessagesAsRead();
});
