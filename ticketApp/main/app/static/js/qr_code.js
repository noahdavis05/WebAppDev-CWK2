function generateQRCode(ticket) {
    var qrData = {
        ticket_id: ticket.ticket_id,
        event_name: ticket.event_name,
        event_date: ticket.event_date,
        event_time: ticket.event_time,
        ticket_owner: ticket.ticket_owner
    };

    console.log("Generating QR for ticket:", qrData);

    // Create an image element for the QR code
    var imgElement = document.createElement('img');

    // Use toDataURL to generate the QR code as a data URL
    QRCode.toDataURL(JSON.stringify(qrData), {
        width: 256,
        height: 256
    }).then(function(url) {
        // Set the source of the image element to the QR code data URL
        imgElement.src = url;

        // Append the image element to the corresponding div
        document.getElementById("qr-" + ticket.ticket_id).appendChild(imgElement);
    }).catch(function(error) {
        console.error("Error generating QR code:", error);
    });
}


function initializeQRCodes() {
    // Ensure tickets is available
    if (tickets && Array.isArray(tickets)) {
        tickets.forEach(function(ticket) {
            generateQRCode(ticket);
        });
    } else {
        console.error("No tickets data found.");
    }
}

// Function to handle tab switching
function openTab(event, tabName) {
    // Get all elements with class "tabcontent" and hide them
    var tabContent = document.getElementsByClassName("tabcontent");
    for (var i = 0; i < tabContent.length; i++) {
        tabContent[i].style.display = "none";
    }

    // Get all elements with class "tablinks" and remove the "active" class
    var tabLinks = document.getElementsByClassName("tablinks");
    for (var i = 0; i < tabLinks.length; i++) {
        tabLinks[i].className = tabLinks[i].className.replace(" active", "");
    }

    // Show the current tab, and add an "active" class to the button that opened the tab
    document.getElementById(tabName).style.display = "block";
    event.currentTarget.className += " active";
}

// Ensure the first tab is open by default
document.addEventListener("DOMContentLoaded", function() {
    var defaultTab = document.querySelector(".tablinks");
    if (defaultTab) {
        defaultTab.click();
    }
});


// Include the QRCode.js library if not already included
// <script src="https://cdn.jsdelivr.net/npm/qrcode/build/qrcode.min.js"></script>

