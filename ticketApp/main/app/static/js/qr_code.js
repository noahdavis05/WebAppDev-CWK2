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
        width: 128,
        height: 128
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
