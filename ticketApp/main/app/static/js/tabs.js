function openTab(evt, tabName) {
    // Hide all tab contents
    var tabContents = document.getElementsByClassName("tabcontent");
    for (var i = 0; i < tabContents.length; i++) {
        tabContents[i].style.display = "none";
    }

    // Remove active class from all buttons
    var tabLinks = document.getElementsByClassName("tablinks");
    for (var i = 0; i < tabLinks.length; i++) {
        tabLinks[i].classList.remove("active");
    }

    // Show the selected tab content
    var selectedTab = document.getElementById(tabName);
    if (selectedTab) {
        selectedTab.style.display = "block";
    }

    // Add active class to the button that opened the tab
    if (evt && evt.currentTarget) {
        evt.currentTarget.classList.add("active");
    }
}

// Initialize the default tab
document.addEventListener("DOMContentLoaded", function() {
    const defaultTabIndex = 1; // Change this to the index of the default tab, e.g., 0 for "Create New Event"
    const tabButtons = document.getElementsByClassName("tablinks");
    
    // If buttons exist, click the default tab
    if (tabButtons[defaultTabIndex]) {
        tabButtons[defaultTabIndex].click();
    } else {
        console.error("Default tab button not found. Check your tablinks setup.");
    }
});
