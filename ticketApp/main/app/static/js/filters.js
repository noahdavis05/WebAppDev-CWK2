const searchBar = document.getElementById('searchBar');
const datePicker = document.getElementById('datePicker');

// Search events based on the search input
function searchEvents() {
    const search = searchBar.value.toLowerCase();
    const dateFilter = datePicker.value; // Retrieve the selected date
    const elements = document.getElementsByClassName('event');

    // delete everything within id events-section
    const events_section = document.getElementById('events-section');
    // iterate through events section to get each card value from each row
    const rows = events_section.getElementsByClassName('row');
    const eventsArray = [];

    for (let row of rows) {
        const cards = row.getElementsByClassName('event');
        for (let card of cards) {
            eventsArray.push(card);
        }
    }

    const filteredEventsArray = [];
    const invalidEventsArray = [];

    eventsArray.forEach(event => {
        const title = event.querySelector('.card-title').textContent.toLowerCase();
        const subtitle = event.querySelector('.card-subtitle').textContent.toLowerCase();
        const description = event.querySelector('.card-text').textContent.toLowerCase();

        const matchesSearch =
            title.includes(search) || subtitle.includes(search) || description.includes(search);

        const matchesDate = dateFilter
            ? subtitle.includes(dateFilter) // Assuming date is part of the subtitle
            : true; // No date filter means include all events

        if (matchesDate && matchesSearch) {
            filteredEventsArray.push(event);
        } else {
            invalidEventsArray.push(event);
        }
    });

    console.log(filteredEventsArray);
    console.log(invalidEventsArray);

    console.log(filteredEventsArray);
    
    events_section.innerHTML = '';

    var count = 0;
    const newRow = document.createElement('div');
    newRow.className = 'row';
    events_section.appendChild(newRow);
    for (let event of filteredEventsArray){
        if (count == 2){
            // now we need a new row element
            const newRow = document.createElement('div');
            newRow.className = 'row';
            events_section.appendChild(newRow);
            count = 0; // Reset count after creating a new row
        }
        event.classList.add('d-flex');
        event.classList.remove('d-none');
        newRow.appendChild(event);
        count += 1;
    }

    for (let event of invalidEventsArray){
        if (count == 2){
            const newRow = document.createElement('div');
            newRow.className = 'row';
            events_section.appendChild(newRow);
            count =0;
        }
        event.classList.add('d-none');
        event.classList.remove('d-flex');
        newRow.appendChild(event);
        count += 1
    }
    


}




function toggleFilters() {
    var filters_element = document.getElementById("filter-container");

    if (filters_element.style.display === "flex") {
        filters_element.style.display = "none";
    } else {
        filters_element.style.display = "flex";
    }
}

searchBar.addEventListener('keyup', searchEvents);
datePicker.addEventListener('change', searchEvents); // U