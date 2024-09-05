document.addEventListener("DOMContentLoaded", function() {
    const meepForm = document.getElementById('meepForm');
    const meepBody = document.getElementById('meepBody');
    const meepList = document.querySelector('.list-group');  // The list where Meeps are displayed
    const loader = document.getElementById('loader');  // Loader during submission

    if (meepForm) {
        meepForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent the default form submission

            // Show loader and hide submit button
            loader.style.display = 'inline-block';

            const formData = new FormData(meepForm);

            fetch(meepForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
                },
            })
            .then(response => response.json())
            .then(data => {
                // Hide loader after response
                loader.style.display = 'none';

                if (data.success) {
                    // Add the new Meep to the top of the list
                    const newMeepHTML = `
                        <li class="list-group-item">
                            <strong>${data.user}</strong>: ${data.body}
                            <small class="text-muted">${data.created_at}</small>
                        </li>
                    `;
                    meepList.insertAdjacentHTML('afterbegin', newMeepHTML);
                    meepBody.value = '';  // Clear the textarea
                } else {
                    alert(data.error || 'Something went wrong!');
                }
            })
            .catch(error => {
                loader.style.display = 'none';
                alert('An error occurred: ' + error.message);
            });
        });
    }
});
