document.addEventListener("DOMContentLoaded", function () {

    if (!data || !columns) {
        console.error("Données non disponibles");
        return;
    }

    const container = document.getElementById("excelContainer");

    const table = document.createElement("table");

    // ===== HEADER =====
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");

    columns.forEach(col => {
        const th = document.createElement("th");
        th.textContent = col;
        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    // ===== BODY =====
    const tbody = document.createElement("tbody");

    data.forEach(row => {
        const tr = document.createElement("tr");

        columns.forEach(col => {
            const td = document.createElement("td");
            td.textContent = row[col] ?? "";
            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    container.appendChild(table);
});