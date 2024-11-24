const searchBar = document.getElementById('searchBar');
const datePicker = document.getElementById('datePicker');

// Search events based on the search input
function searchEvents() {
    const search = searchBar.value.toLowerCase();
    const dateFilter = datePicker.value; // Retrieve the selected date
    const elements = document.getElementsByClassName('event');

    for (let element of elements) {
        const title = element.querySelector('.card-title').textContent.toLowerCase();
        const subtitle = element.querySelector('.card-subtitle').textContent.toLowerCase();
        const description = element.querySelector('.card-text').textContent.toLowerCase();

        // Check if any of the fields match the search term
        const matchesSearch =
            title.includes(search) || subtitle.includes(search) || description.includes(search);

        console.log(matchesSearch);

        // Check if the event matches the date filter (if provided)
        const matchesDate = dateFilter
            ? subtitle.includes(dateFilter) // Assuming date is part of the subtitle
            : true; // No date filter means include all events

        // Show or hide the event
        if (matchesSearch && matchesDate) {
            element.classList.remove('d-none');
            element.classList.add('d-flex');
        } else {
            element.classList.add('d-none');
            element.classList.remove('d-flex');
        }
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