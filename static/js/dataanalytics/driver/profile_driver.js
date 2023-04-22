     
    const months = document.getElementById('x')
    const labels_months = JSON.parse(months.dataset.json);
    const y = document.getElementById('y')
    const valuesy = JSON.parse(y.dataset.json);

    const data = {
        labels: labels_months,
        datasets: [
          {
            label: 'Tendencia',
            data: valuesy,
            fill: false,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
          }
        ]
    };
      
      const config = {
        type: 'line',
        data: data,
        options: {
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      };
      
      const myChart = new Chart(
        document.getElementById('chartLinePurple'),
        config
      );


      // Gráfica de barras de tendencias en países

      const countries = document.getElementById('paises_tendencia')
      const labels_countries = JSON.parse(countries.dataset.json);
      const values = document.getElementById('valores_paises')
      const values_countries = JSON.parse(values.dataset.json);

      var ctx = document.getElementById('sectores').getContext('2d');
      var myCountryChart = new Chart(ctx, {
          type: 'bar',
          data: {
              labels: labels_countries,
              datasets: [{
                  label: 'Tendencia en países',
                  data: values_countries,
                  backgroundColor: [
                      'rgba(255, 99, 132, 0.2)',
                      'rgba(54, 162, 235, 0.2)',
                      'rgba(255, 206, 86, 0.2)',
                      'rgba(75, 192, 192, 0.2)',
                      'rgba(153, 102, 255, 0.2)',
                      'rgb(211, 211, 211)',
                      'rgb(255, 200, 87)',
                      'rgb(255, 182, 193)',
                      'rgb(144, 238, 144)',
                      'rgb(205, 133, 63)'
                  ],
                  borderColor: [
                      'rgba(255, 99, 132, 1)',
                      'rgba(54, 162, 235, 1)',
                      'rgba(255, 206, 86, 1)',
                      'rgba(75, 192, 192, 1)',
                      'rgba(153, 102, 255, 1)',
                      'rgb(211, 211, 211)',
                      'rgb(255, 200, 87)',                      
                      'rgb(255, 182, 193)',
                      'rgb(144, 238, 144)',
                      'rgb(205, 133, 63)'

                  ],
                  borderWidth: 1
              }]
          },
          options: {
              scales: {
                  y: {
                      beginAtZero: true
                  }
              }
          }
      });
