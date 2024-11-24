function deleteTicket(ticket_id){
    let text = "Are you sure you want to delete?";
    if (confirm(text) == true) {
      query_server(ticket_id);
    } else {
      return;
    }
    
}

async function query_server(ticket_id){
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    //console.log(ticket_id)
    try {
        const response = await fetch('/home', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken, // Include CSRF token in the request header
            },
            body: JSON.stringify({ ticket_id: ticket_id }), // Send the QR code data as JSON
        });

        const data = await response.json(); // Parse JSON response from the server
        if (data.success) {
            // delete the ticket from the webpage
            var ticketCard = document.getElementById('card-' + ticket_id);
            if (ticketCard) {
                ticketCard.remove();
            }
        } else {
            //console.log(message);
           alert('error');
        }
    } catch (error) {
        //console.error('Error sending ticket_id code to server:', error);
        //showPopup('An unexpected error occurred while sending the QR code.', 'error');
    }
}