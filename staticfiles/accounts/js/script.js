const filterTransactionsUrl = "{% url 'billing:filter_transactions' %}";

// Function to handle the filter functionality
function filterTransactions() {
    const filterField = document.getElementById("filter_field").value;
    const filterValue = document.getElementById("filter_value").value;

    const url = "{% url 'billing:filter_transactions' %}?filter_field=" + filterField + "&filter_value=" + filterValue;

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const tableBody = document.querySelector("table tbody");
            tableBody.innerHTML = "";  // Clear existing rows

            data.transactions.forEach(transaction => {
                const row = document.createElement("tr");
                row.classList.add("even:bg-gray-100");

                row.innerHTML = `
                    <td class="border px-4 py-2">${transaction.cart_id}</td>
                    <td class="border px-4 py-2">${transaction.customer_name}</td>
                    <td class="border px-4 py-2">${transaction.payment_method}</td>
                    <td class="border px-4 py-2">${transaction.product_name}</td>
                    <td class="border px-4 py-2">${transaction.store_name}</td>
                    <td class="border px-4 py-2">${transaction.quantity}</td>
                    <td class="border px-4 py-2">${transaction.price}</td>
                    <td class="border px-4 py-2">${transaction.discount}</td>
                    <td class="border px-4 py-2">${transaction.subtotal}</td>
                    <td class="border px-4 py-2">${transaction.created_at}</td>
                `;
                
                tableBody.appendChild(row);
            });
        })
        .catch(error => {
            console.error("Error fetching filtered transactions:", error);
        });
}

function resetSearch() {
    const url = new URL(window.location.href);
    url.searchParams.delete('search');
    url.searchParams.delete('filter');
    url.searchParams.delete('start_date');
    url.searchParams.delete('end_date');
    url.searchParams.delete('filter_field');
    url.searchParams.delete('filter_value');
    window.location.href = url.origin + url.pathname;
}

document.getElementById('exportBtn').addEventListener('click', function() {
    const filterField = document.getElementById('filterField').value;
    const filterValue = document.getElementById('filterValue').value;
    fetch(`/billing/filter_transactions/?filter_field=${filterField}&filter_value=${filterValue}`)
        .then(response => response.json())
        .then(data => {
            const transactions = data.transactions;
            if (transactions.length > 0) {
                exportToExcel(transactions);
            } else {
                alert('No data to export.');
            }
        });
});






//=====================================================================
document.getElementById("exportButton").addEventListener("click", function() {
    // Get the start and end date values
    var startDate = document.getElementById("startDate").value;
    var endDate = document.getElementById("endDate").value;

    // Initialize the URL for exporting
    var url = '/billing/filter_transactions/?';

    // Add the start and end date to the URL if they're selected
    if (startDate && endDate) {
        url += `start_date=${startDate}&end_date=${endDate}`;
    }

    // Fetch the filtered transactions for export
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.transactions && data.transactions.length > 0) {
                var wb = XLSX.utils.json_to_sheet(data.transactions);
                var ws = XLSX.utils.book_new();
                XLSX.utils.book_append_sheet(ws, wb, "Transactions");
                XLSX.writeFile(ws, "transactions.xlsx");
            } else {
                alert("No data to export.");
            }
        })
        .catch(error => console.error("Error exporting data: ", error));
});

//===============================================

document.getElementById("filterButton").addEventListener("click", function() {
    var startDate = document.getElementById("startDate").value;
    var endDate = document.getElementById("endDate").value;

    var url = '/billing/filter_transactions/?';

    if (startDate && endDate) {
        url += `start_date=${startDate}&end_date=${endDate}`;
    }

    // Make an AJAX call to update the table with the filtered data
    fetch(url)
        .then(response => response.json())
        .then(data => {
            // Assuming you have a function to update your table with new data
            updateTableWithFilteredData(data.transactions);
        })
        .catch(error => console.error("Error filtering data: ", error));
});



//===============================================
