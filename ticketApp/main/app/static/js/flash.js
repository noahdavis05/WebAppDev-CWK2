// fade out the flash messages after 5 seconds
document.addEventListener("DOMContentLoaded", function () {
    const messages = document.querySelectorAll(".flash-message");
    messages.forEach((message) => {
        setTimeout(() => {
            message.style.transition = "opacity 1s ease";
            message.style.opacity = "0";
            setTimeout(() => {
                message.remove(); 
            }, 1000); 
        }, 5000);
    });
});
