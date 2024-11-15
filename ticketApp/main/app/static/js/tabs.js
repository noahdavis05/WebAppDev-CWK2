// tabs.js

function openTab(evt, tabName) {
    // Hide all tab contents
    var tabcontents = document.getElementsByClassName("tabcontent");
    for (var i = 0; i < tabcontents.length; i++) {
        tabcontents[i].style.display = "none";
    }

    // Remove active class from all buttons
    var tablinks = document.getElementsByClassName("tablinks");
    for (var i = 0; i < tablinks.length; i++) {
        tablinks[i].classList.remove("active");
    }

    // Show the selected tab content
    document.getElementById(tabName).style.display = "block";

    // Add active class to the button that opened the tab
    evt.currentTarget.classList.add("active");
}

// Set default tab to "Your Events"
document.addEventListener("DOMContentLoaded", function() {
    document.getElementsByClassName("tablinks")[1].click();
});
