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
                'X-CSRFToken': csrfToken, // Include CSRF token 
            },
            body: JSON.stringify({ ticket_id: ticket_id }), 
        });

        const data = await response.json(); 
        if (data.success) {
            // Find the ticket card by ID
            var ticketCard = document.getElementById('card-' + ticket_id);
            var ticketCardParent = ticketCard.parentNode;
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
    const classNames = ticketCardParent.className.split(' ');
    const lastClassName = classNames[classNames.length - 1];
    reArrange(lastClassName);
}


function reArrange(ticket_class){
    console.log(ticket_class);
    // get all the cards
    const cards = document.querySelectorAll('.' + ticket_class);
    console.log(cards);
    
    // remove these cards from the html
    for (let ticket of cards){
        ticket.remove();
    }

    // now re-enter these tickets in the correct placement
    var count = 0;
    const newRow = document.createElement('div');
    newRow.className = 'row';
    if (ticket_class == 'active-ticket'){
    ticket_list = document.getElementById('ticket-list');
    } else {
        ticket_list = document.getElementById('old-tickets');
    }
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

function reArrangeUsed(){
    // get all the used cards
    const cards = document.querySelectorAll('.used-ticket');
    console.log(cards);
    for (let ticket of cards){
        ticket.remove();
    }
    var count = 0;
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