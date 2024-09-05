document.addEventListener('DOMContentLoaded', function () {
    const toastContainer = document.getElementById('toast-container');

    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.classList.add('toast', `toast-${type}`, 'fade', 'show');
        toast.innerHTML = `
            <div class="toast-body">
                ${message}
            </div>
        `;
        toastContainer.appendChild(toast);

        // Auto-remove the toast after a few seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 200);
        }, 3000);
    }

    // Example usage
    // showToast('This is a success message!', 'success');
    // showToast('This is an error message!', 'error');
});
