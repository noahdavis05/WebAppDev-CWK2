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
            // Find the ticket card by ID
            var ticketCard = document.getElementById('card-' + ticket_id);
            if (ticketCard && ticketCard.parentNode) {
                // Remove the parent div of the ticket card
                ticketCard.parentNode.remove();
            }
        
        } else {
            //console.log(message);
           alert('error');
        }
    } catch (error) {
        //console.error('Error sending ticket_id code to server:', error);
        //showPopup('An unexpected error occurred while sending the QR code.', 'error');
    }
    reArrange();
}


function reArrange(){
    // get all the cards
    const cards = document.querySelectorAll('.active-ticket')
    
    // remove these cards from the html
    for (let ticket of cards){
        ticket.remove();
    }

    // now re-enter these tickets in the correct placement
    var count = 0;
    const newRow = document.createElement('div');
    newRow.className = 'row';
    ticket_list = document.getElementById('ticket-list');
    ticket_list.appendChild(newRow); // this line
    for (let ticket of cards){
        if (count == 2){
            // now we need a new row element
            const newRow = document.createElement('div');
            newRow.className = 'row';
            ticket_list.appendChild(newRow);
            count = 0; // Reset count after creating a new row
        }
        ticket.classList.add('d-flex');
        ticket.classList.remove('d-none');
        newRow.appendChild(ticket);
        count += 1;
    }
}