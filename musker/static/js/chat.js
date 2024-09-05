document.getElementById('send-button').addEventListener('click', function() {
    const messageInput = document.getElementById('chat-message-input');
    const message = messageInput.value.trim();

    if (message !== "") {
        // Create a new FormData object to handle the POST request
        const formData = new FormData();
        formData.append('message', message);

        // Send the message via an AJAX request
        fetch(window.location.href, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Clear the input field
                messageInput.value = "";

                // Optionally, add the message to the chat window
                const chatWindow = document.getElementById('chat-messages');
                const newMessage = document.createElement('div');
                newMessage.classList.add('message', 'sent');
                newMessage.innerHTML = `<div class="message-content"><p>${message}</p><small>Just now</small></div>`;
                chatWindow.appendChild(newMessage);

                // Scroll to the bottom of the chat window
                chatWindow.scrollTop = chatWindow.scrollHeight;
            } else {
                alert("Message failed to send");
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
});
document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById('chat-form');
    const chatMessagesContainer = document.getElementById('chat-messages');
    const recipientId = chatForm.dataset.recipientId;  // Retrieve recipient ID from the form dataset

    chatForm.addEventListener('submit', function (e) {
        e.preventDefault();  // Prevent the form from submitting normally

        const messageInput = document.getElementById('chat-message-input');
        const message = messageInput.value.trim();

        if (message) {
            fetch(`/send-message-ajax/${recipientId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const newMessageHtml = `
                        <div class="message sent">
                            <div class="message-content">
                                <p>${data.message.body}</p>
                                <small>${data.message.timestamp}</small>
                            </div>
                        </div>
                    `;
                    chatMessagesContainer.insertAdjacentHTML('beforeend', newMessageHtml);
                    messageInput.value = '';  // Clear the input
                    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;  // Scroll to the bottom
                } else {
                    alert('Failed to send message.');
                }
            })
            .catch(error => console.error('Error:', error));  // Handle any errors
        }
    });
});
