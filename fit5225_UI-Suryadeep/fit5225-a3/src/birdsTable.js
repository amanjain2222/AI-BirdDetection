function birdsTable(rowData) {
    const table = document.createElement('table');
    table.style.width = '100%';
    table.style.borderCollapse = 'collapse';
    table.style.backgroundColor = '#333';
    table.style.color = 'white';
    table.style.fontFamily = 'Arial, sans-serif';

    rowData.forEach((element, index) => {
        const row = document.createElement('tr');
        const indexCell = document.createElement('td');
        const dataCell = document.createElement('td');

        indexCell.textContent = index + 1;
        dataCell.textContent = element || '—';

        [indexCell, dataCell].forEach(cell => {
            cell.style.border = '1px solid #666';
            cell.style.padding = '10px';
            cell.style.wordBreak = 'break-word';
        });

        row.appendChild(indexCell);
        row.appendChild(dataCell);
        table.appendChild(row);
    });

    return table;
}

export default birdsTable;