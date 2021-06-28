$(document).ready(function () {
    const notes = document.querySelectorAll('.summernote')
    $(notes).summernote({
        height: 150,
        disableResizeEditor: true
    });
});