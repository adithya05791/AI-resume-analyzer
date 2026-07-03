document.addEventListener("DOMContentLoaded", () => {
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("resume");
    const dropzoneText = document.getElementById("dropzone-text");
    const form = document.getElementById("analyze-form");
    const submitBtn = document.getElementById("submit-btn");

    if (fileInput) {
        fileInput.addEventListener("change", () => {
            if (fileInput.files.length > 0) {
                dropzoneText.textContent = fileInput.files[0].name;
            }
        });
    }

    if (dropzone) {
        ["dragenter", "dragover"].forEach((evt) => {
            dropzone.addEventListener(evt, (e) => {
                e.preventDefault();
                dropzone.classList.add("is-dragover");
            });
        });
        ["dragleave", "drop"].forEach((evt) => {
            dropzone.addEventListener(evt, (e) => {
                e.preventDefault();
                dropzone.classList.remove("is-dragover");
            });
        });
        dropzone.addEventListener("drop", (e) => {
            if (e.dataTransfer.files.length > 0) {
                fileInput.files = e.dataTransfer.files;
                dropzoneText.textContent = e.dataTransfer.files[0].name;
            }
        });
    }

    if (form) {
        form.addEventListener("submit", () => {
            submitBtn.disabled = true;
            submitBtn.querySelector(".btn-label").textContent = "Analyzing…";
        });
    }
});
