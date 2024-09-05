document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById('liveSearch');
    const searchResults = document.getElementById('searchResults');

    searchInput.addEventListener('keyup', function () {
        const query = searchInput.value.trim();

        // Trigger search for any query length greater than 0
        if (query.length > 0) {
            fetch(`/live_search/?q=${query}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                // Clear previous results
                searchResults.innerHTML = '';

                if (data.user_results.length > 0 || data.meep_results.length > 0 || data.hashtag_results.length > 0) {
                    // Display users
                    if (data.user_results.length > 0) {
                        searchResults.innerHTML += `<h4>Users</h4><ul class="list-group">`;
                        data.user_results.forEach(user => {
                            searchResults.innerHTML += `<li class="list-group-item"><a href="/profile/${user.id}/">${user.username}</a></li>`;
                        });
                        searchResults.innerHTML += `</ul>`;
                    }

                    // Display meeps
                    if (data.meep_results.length > 0) {
                        searchResults.innerHTML += `<h4>Meeps</h4><ul class="list-group">`;
                        data.meep_results.forEach(meep => {
                            searchResults.innerHTML += `<li class="list-group-item">${meep.body} - <a href="/meep/${meep.id}/">View</a></li>`;
                        });
                        searchResults.innerHTML += `</ul>`;
                    }

                    // Display hashtags
                    if (data.hashtag_results.length > 0) {
                        searchResults.innerHTML += `<h4>Hashtags</h4><ul class="list-group">`;
                        data.hashtag_results.forEach(hashtag => {
                            searchResults.innerHTML += `<li class="list-group-item"><a href="/hashtag/${hashtag.name}/">#${hashtag.name}</a></li>`;
                        });
                        searchResults.innerHTML += `</ul>`;
                    }
                } else {
                    searchResults.innerHTML = '<p>No results found.</p>';
                }
            });
        } else {
            searchResults.innerHTML = '';
        }
    });
});
