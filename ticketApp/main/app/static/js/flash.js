// flash.js

document.addEventListener("DOMContentLoaded", function () {
    const messages = document.querySelectorAll(".flash-message");
    messages.forEach((message) => {
        // Set a timeout to fade the message
        setTimeout(() => {
            message.style.transition = "opacity 1s ease";
            message.style.opacity = "0"; // Start fade-out
            setTimeout(() => {
                message.remove(); // Remove the message from DOM
            }, 1000); // Wait for the fade-out to complete
        }, 5000); // Wait 5 seconds before starting fade-out
    });
});
