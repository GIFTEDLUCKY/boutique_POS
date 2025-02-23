document.getElementById("exportButton").addEventListener("click", function () {
    // Get the table element by id
    var table = document.getElementById("transactionTable");

    // Log the table rows for debugging
    var rows = table.getElementsByTagName("tr");
    console.log(rows); // Log all rows to see if they are populated

    if (rows.length > 1) {
        var wb = XLSX.utils.table_to_book(table, {sheet: "Sheet1"});
        XLSX.writeFile(wb, "transactions.xlsx");
    } else {
        alert("No data to export.");
    }
});
