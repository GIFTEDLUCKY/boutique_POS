console.log("JavaScript loaded");


function filterTransactions() {
    const filterField = document.getElementById("filter_field").value;
    const filterValue = document.getElementById("filter_value").value;
    const startDate = document.getElementById("startDate") ? document.getElementById("startDate").value : '';
    const endDate = document.getElementById("endDate") ? document.getElementById("endDate").value : '';

    let url = `/billing/filter_transactions/?filter_field=${filterField}&filter_value=${filterValue}`;

    if (startDate && endDate) {
        url += `&start_date=${startDate}&end_date=${endDate}`;
    }

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log(data.transactions);
            const tableBody = document.querySelector("table tbody");
            tableBody.innerHTML = "";  // Clear existing rows

            let totalSales = 0;  // Initialize total sales

            // Loop through the filtered transactions and add new rows
            data.transactions.forEach(transaction => {
                const row = document.createElement("tr");
                row.classList.add("even:bg-gray-100");

                row.innerHTML = `
                    <td class="border px-4 py-2">${transaction.cashier_name}</td>
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

                // Append new row to the table body
                tableBody.appendChild(row);

                // Add subtotal to total sales
                totalSales += parseFloat(transaction.subtotal) || 0;
            });

            // Update total sales display
            const totalSalesElement = document.getElementById("total_sales");
            if (totalSalesElement) {
                totalSalesElement.textContent = `Total Sales: ${totalSales.toFixed(2)}`;
            }

            // Set a fixed width for each column (adjust as needed)
            const table = document.querySelector("table");
            const columns = table.querySelectorAll("th");
            const columnWidths = [150, 200, 250, 180, 200, 150, 100, 120, 130, 150, 200]; // Define column widths here

            columns.forEach((col, index) => {
                col.style.width = `${columnWidths[index]}px`;
            });

            // Adjust table layout
            table.style.width = "100%";
            table.style.tableLayout = "fixed";

            // Optional: Force recalculation to prevent shifting
            const rows = table.querySelectorAll("tr");
            rows.forEach(row => {
                row.style.tableLayout = "fixed";
            });
        })
        .catch(error => {
            console.error("Error fetching filtered transactions:", error);
        });
}





document.addEventListener("DOMContentLoaded", function () {
    const resetButton = document.getElementById("resetButton");

    if (resetButton) {
        resetButton.addEventListener("click", function () {
            window.location.href = 'http://127.0.0.1:8000/billing/transactions/all/';
        });
    } else {
        console.error("Reset button not found in the document.");
    }
});








// Export the filtered transactions to Excel
function exportToExcel(transactions) {
    var wb = XLSX.utils.json_to_sheet(transactions);
    var ws = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(ws, wb, "Transactions");
    XLSX.writeFile(ws, "transactions.xlsx");
}


// Event listeners
document.addEventListener("DOMContentLoaded", function() {
    // Filter transactions on button click
    const filterButton = document.getElementById("filterButton");
    if (filterButton) {
        filterButton.addEventListener("click", filterTransactions);
    }

    // Export filtered transactions to Excel
    const exportButton = document.getElementById("exportButton");
    if (exportButton) {
        exportButton.addEventListener("click", function() {
            const filterField = document.getElementById("filter_field").value;
            const filterValue = document.getElementById("filter_value").value;
            const startDate = document.getElementById("startDate") ? document.getElementById("startDate").value : '';
            const endDate = document.getElementById("endDate") ? document.getElementById("endDate").value : '';

            const url = `/billing/filter_transactions/?filter_field=${filterField}&filter_value=${filterValue}&start_date=${startDate}&end_date=${endDate}`;
            
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    if (data.transactions && data.transactions.length > 0) {
                        exportToExcel(data.transactions);
                    } else {
                        alert("No data to export.");
                    }
                })
                .catch(error => console.error("Error exporting data: ", error));
        });
    }
});



//=============================================================
$(document).ready(function() {
    // When the filter form is submitted
    $('#filter-form').on('submit', function(e) {
        e.preventDefault();  // Prevent the form from submitting normally

        // Get the filter parameters
        var filter = $('#filter').val();
        var start_date = $('#start_date').val();
        var end_date = $('#end_date').val();
        var payment_method = $('#payment_method').val();
        var store = $('#store').val();
        var invoice_number = $('#invoice_number').val();
        var customer_name = $('#customer_name').val();

        // Send the AJAX request
        $.ajax({
            url: '/billing/transactions/all/',  // The URL that handles the filter and returns the updated data
            type: 'GET',
            data: {
                filter: filter,
                filter_value: store || payment_method || invoice_number || customer_name,
                start_date: start_date,
                end_date: end_date,
            },
            success: function(response) {
                // Update the total sales dynamically
                $('#total-sales-amount').text(response.total_sales);

                // Update the transaction list with the new content
                $('#transaction-list').html(response.transactions);
            },
            error: function(xhr, status, error) {
                console.error('AJAX Error: ' + error);
            }
        });
    });
});


// Add an event listener for the filter button
const filterButton = document.getElementById("filterButton");

if (filterButton) {
    filterButton.addEventListener("click", function() {
        // Get the values from the filter inputs
        const filterField = document.getElementById("filter_field").value;
        const filterValue = document.getElementById("filter_value").value;
        const startDate = document.getElementById("startDate") ? document.getElementById("startDate").value : '';
        const endDate = document.getElementById("endDate") ? document.getElementById("endDate").value : '';

        // Construct the URL for filtering
        const url = `/billing/filter_transactions/?filter_field=${filterField}&filter_value=${filterValue}&start_date=${startDate}&end_date=${endDate}`;

        // Fetch filtered data
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.transactions && data.transactions.length > 0) {
                    // Here, you would update the table with the filtered transactions
                    updateTableWithFilteredData(data.transactions);
                } else {
                    alert("No transactions found for the selected filters.");
                }
            })
            .catch(error => console.error("Error filtering data:", error));
    });
}

function updateTableWithFilteredData(transactions) {
    const tableBody = document.querySelector("table tbody");
    tableBody.innerHTML = "";  // Clear existing rows

    // Loop through the filtered transactions and update the table
    transactions.forEach(transaction => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${transaction.cashier_name}</td>
            <td>${transaction.cart_id}</td>
            <td>${transaction.customer_name}</td>
            <td>${transaction.payment_method}</td>
            <td>${transaction.product_name}</td>
            <td>${transaction.store_name}</td>
            <td>${transaction.quantity}</td>
            <td>${transaction.price}</td>
            <td>${transaction.discount}</td>
            <td>${transaction.subtotal}</td>
            <td>${transaction.created_at}</td>
        `;
        
        // Append the new row to the table body
        tableBody.appendChild(row);
    });
}




document.addEventListener("DOMContentLoaded", function() {
    console.log("DOM fully loaded and parsed"); // Debugging line

    var productElement = document.querySelector(".product");
    var stockQuantity = productElement ? parseInt(productElement.getAttribute("data-stock")) : NaN;

    console.log("Stock quantity: " + stockQuantity); // Debugging line

    if (stockQuantity <= 10 && stockQuantity !== NaN) {
        var warningMessage = document.createElement("div");
        warningMessage.classList.add("alert", "alert-warning");
        warningMessage.textContent = "Warning: Stock for this product is running low!";
        document.body.appendChild(warningMessage);
    }
});



//==========================================================
//REFUND


