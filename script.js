document.addEventListener("DOMContentLoaded", function () {
    console.log("Library Management System Loaded!");

    // Handle delete confirmations
    document.querySelectorAll(".delete-btn").forEach(button => {
        button.addEventListener("click", function () {
            if (!confirm("Are you sure you want to delete this?")) {
                event.preventDefault();
            }
        });
    });
});