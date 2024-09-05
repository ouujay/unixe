let page = 2;
let isLoading = false;
let hasMorePosts = true;

window.onscroll = function() {
    if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight && hasMorePosts && !isLoading) {
        loadMoreMeeps();
    }
};

function loadMoreMeeps() {
    if (!hasMorePosts) {
        return;
    }

    const spinner = document.getElementById('loading-spinner');
    spinner.style.display = 'block';
    isLoading = true;

    fetch(`/?page=${page}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok.');
        }
        return response.text();
    })
    .then(html => {
        spinner.style.display = 'none';
        if (html.trim()) {
            const meepList = document.getElementById('meep-list');
            meepList.insertAdjacentHTML('beforeend', html);
            page += 1;

            // Trigger custom event after new content is loaded
            document.dispatchEvent(new Event('newContentLoaded'));
        } else {
            console.log('No more meeps to load.');
            hasMorePosts = false;
        }
        isLoading = false;
    })
    .catch(error => {
        console.error('Error loading more meeps:', error);
        spinner.style.display = 'none';
        isLoading = false;
    });
}
