document.addEventListener('DOMContentLoaded', function () {

    // Image/Video Preview Logic
    const imageUpload = document.getElementById('imageUpload');
    const videoUpload = document.getElementById('videoUpload');
    const previewSection = document.getElementById('previewSection');

    const replyImageUpload = document.getElementById('imageReplyUpload');
    const replyVideoUpload = document.getElementById('videoReplyUpload');
    const replyPreviewSection = document.getElementById('replyPreviewSection');

    function previewFile(input, previewSection) {
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = function (e) {
                previewSection.innerHTML = `<img src="${e.target.result}" alt="Image Preview" class="img-fluid rounded mt-2">`;
            };
            reader.readAsDataURL(input.files[0]);
        }
    }

    imageUpload.addEventListener('change', function () {
        previewFile(this, previewSection);
    });

    videoUpload.addEventListener('change', function () {
        previewSection.innerHTML = `<video controls class="img-fluid rounded mt-2">
                                        <source src="${URL.createObjectURL(this.files[0])}" type="video/mp4">
                                        Your browser does not support the video tag.
                                    </video>`;
    });

    replyImageUpload.addEventListener('change', function () {
        previewFile(this, replyPreviewSection);
    });

    replyVideoUpload.addEventListener('change', function () {
        replyPreviewSection.innerHTML = `<video controls class="img-fluid rounded mt-2">
                                            <source src="${URL.createObjectURL(this.files[0])}" type="video/mp4">
                                            Your browser does not support the video tag.
                                        </video>`;
    });

    // Client-Side Validation
    const meepForm = document.getElementById('meepForm');
    const replyForm = document.getElementById('replyForm');

    meepForm.addEventListener('submit', function (e) {
        if (document.getElementById('meepBody').value.trim() === '') {
            alert('Meep content cannot be empty!');
            e.preventDefault();
        }
    });

    replyForm.addEventListener('submit', function (e) {
        if (document.getElementById('replyBody').value.trim() === '') {
            alert('Reply content cannot be empty!');
            e.preventDefault();
        }
    });
});
