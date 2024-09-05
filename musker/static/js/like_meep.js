document.addEventListener("DOMContentLoaded", function() {
    function bindLikeButtons() {
        console.log("Binding like buttons");  
        document.querySelectorAll(".like-button").forEach(button => {
            button.removeEventListener("click", likeMeep); 
            button.addEventListener("click", likeMeep); 
        });
    }

    function likeMeep(event) {
        event.preventDefault();  
        console.log("Like button clicked, event prevented");  

        const meepId = this.dataset.meepId;
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

        fetch(`/meep_like/${meepId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const likeCount = document.querySelector(`#like-count-${meepId}`);
                likeCount.textContent = data.new_like_count;

                const icon = this.querySelector("i");
                if (data.liked) {
                    icon.classList.remove("far");
                    icon.classList.add("fas");
                } else {
                    icon.classList.remove("fas");
                    icon.classList.add("far");
                }
                console.log(`Meep ${meepId} liked status: ${data.liked}`);  
            }
        })
        .catch(error => console.error("Error:", error));
    }


    bindLikeButtons();


    document.addEventListener('newContentLoaded', function() {
        bindLikeButtons();
    });
});
