document.addEventListener('DOMContentLoaded', function () {
    fetchData();
});

function fetchData() {
    const endpoint = 'https://us-east1-weight-forecaster-poc.cloudfunctions.net/fetch_fitness_data';
    fetch(endpoint)
        .then(response => response.json())
        .then(data => {
            displayData(data);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            document.getElementById('data-container').innerText = 'Failed to load data.';
        });
}

function displayData(data) {
    const container = document.getElementById('data-container');
    container.innerHTML = ''; // Clear loading message
    const table = document.createElement('table');

    // Assuming your data is an array of objects
    data.forEach((row, index) => {
        if (index === 0) { // Create table headers from the keys of the first item
            const headerRow = document.createElement('tr');
            Object.keys(row).forEach(key => {
                const headerCell = document.createElement('th');
                headerCell.innerText = key;
                headerRow.appendChild(headerCell);
            });
            table.appendChild(headerRow);
        }
        const dataRow = document.createElement('tr');
        Object.values(row).forEach(value => {
            const dataCell = document.createElement('td');
            dataCell.innerText = value;
            dataRow.appendChild(dataCell);
        });
        table.appendChild(dataRow);
    });

    container.appendChild(table);
}
