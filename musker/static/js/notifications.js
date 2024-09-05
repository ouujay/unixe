document.addEventListener('DOMContentLoaded', function () {
    // Function to check unread messages and update the badge count
    function checkUnreadMessages() {
        fetch('/messages/unread_counts/')  // Endpoint to get unread message counts per conversation
            .then(response => response.json())
            .then(data => {
                // Iterate over each conversation to update the unread message count
                data.conversations.forEach(conversation => {
                    const conversationElement = document.querySelector(`.conversation-item[data-user-id="${conversation.other_user_id}"]`);
                    const unreadBadge = conversationElement.querySelector('.badge-danger');

                    if (conversation.unread_count > 0) {
                        // If there are unread messages, display or update the badge
                        if (!unreadBadge) {
                            conversationElement.insertAdjacentHTML('beforeend', `<span class="badge badge-danger">${conversation.unread_count}</span>`);
                        } else {
                            unreadBadge.textContent = conversation.unread_count;
                        }
                    } else {
                        // If there are no unread messages, remove the badge
                        if (unreadBadge) {
                            unreadBadge.remove();
                        }
                    }
                });
            })
            .catch(error => console.error('Error fetching unread message count:', error));
    }

    // Function to mark a conversation as read when clicked
    function markConversationAsRead(userId) {
        fetch(`/messages/mark_as_read/${userId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => {
            if (response.ok) {
                checkUnreadMessages();  // Update the unread counts after marking as read
            }
        })
        .catch(error => console.error('Error marking messages as read:', error));
    }

    // Attach event listeners to each conversation item
    document.querySelectorAll('.conversation-item').forEach(item => {
        item.addEventListener('click', function () {
            const userId = this.dataset.userId;
            markConversationAsRead(userId);  // Mark the conversation as read when clicked
        });
    });

    // Poll the server every 30 seconds to update unread message counts
    setInterval(checkUnreadMessages, 30000);

    // Initial check to update the counts when the page loads
    checkUnreadMessages();
});
