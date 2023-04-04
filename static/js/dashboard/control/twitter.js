
  // TABLAS DE TWITTER

  // Se obtiene el botón de ordenar y se le asigna la función ordenarTabla
  var drivertable = document.getElementById("sortDriverTable");
  var headers = drivertable.getElementsByTagName('th');
    for (var i = 0; i < headers.length; i++) {
    headers[i].addEventListener('click', function(event) {
        var columnIndex = this.cellIndex;
        var sortOrder = (this.getAttribute('data-order') === 'asc') ? 'desc' : 'asc';
        this.setAttribute('data-order', sortOrder);
        sortTable(columnIndex, sortOrder, drivertable);
    });
    }


    var teamtable = document.getElementById("sortTeamTable");
    var headers = teamtable.getElementsByTagName('th');
      for (var i = 0; i < headers.length; i++) {
      headers[i].addEventListener('click', function(event) {
          var columnIndex = this.cellIndex;
          var sortOrder = (this.getAttribute('data-order') === 'asc') ? 'desc' : 'asc';
          this.setAttribute('data-order', sortOrder);
          sortTeamTable(columnIndex, sortOrder, teamtable);
      });
      }

    function sortTable(columnIndex, sortOrder, table) {
        // código de ordenamiento aquí
        var rows = Array.from(table.rows);
        console.log(rows)
        var data = rows.slice(1);
        function compareRows(rowIndex1, rowIndex2, columnIndex) {
            var cell1 = rowIndex1.cells[columnIndex].textContent;
            var cell2 = rowIndex2.cells[columnIndex].textContent;
            
            if (cell1 < cell2) {
              return -1;
            } else if (cell1 > cell2) {
              return 1;
            } else {
              return 0;
            }
        }
        
        

        data.sort(function(rowIndex1, rowIndex2) {
            var sortOrderMultiplier = (sortOrder === 'asc') ? 1 : -1;
            return sortOrderMultiplier * compareRows(rowIndex1, rowIndex2, columnIndex);
        });

        // encabezado fijo
        table.appendChild(rows[0]);
        for (var i = 0; i < data.length; i++) {
            table.appendChild(data[i]);
        }
          
      }
    
      function sortTeamTable(columnIndex, sortOrder, table) {
        // código de ordenamiento aquí
        var rows = Array.from(table.rows);
        console.log(rows)
        var data = rows.slice(1);
        function compareRows(rowIndex1, rowIndex2, columnIndex) {
            var cell1 = rowIndex1.cells[columnIndex].textContent;
            var cell2 = rowIndex2.cells[columnIndex].textContent;
            
            if (cell1 < cell2) {
              return -1;
            } else if (cell1 > cell2) {
              return 1;
            } else {
              return 0;
            }
        }
        
        

        data.sort(function(rowIndex1, rowIndex2) {
            var sortOrderMultiplier = (sortOrder === 'asc') ? 1 : -1;
            return sortOrderMultiplier * compareRows(rowIndex1, rowIndex2, columnIndex);
        });

        // encabezado fijo
        table.appendChild(rows[0]);
        for (var i = 0; i < data.length; i++) {
            table.appendChild(data[i]);
        }
          
      }

  
  
  
