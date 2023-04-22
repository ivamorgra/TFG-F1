
document.addEventListener("DOMContentLoaded", function(event) {
  // Tu código JavaScript aquí

  type = ['primary', 'info', 'success', 'warning', 'danger'];



  demo = {
    initPickColor: function() {
      $('.pick-class-label').click(function() {
        var new_class = $(this).attr('new-class');
        var old_class = $('#display-buttons').attr('data-class');
        var display_div = $('#display-buttons');
        if (display_div.length) {
          var display_buttons = display_div.find('.btn');
          display_buttons.removeClass(old_class);
          display_buttons.addClass(new_class);
          display_div.attr('data-class', new_class);
        }
      });
    },


    initDocChart: function() {
      chartColor = "#FFFFFF";

      // General configuration for the charts with Line gradientStroke
      gradientChartOptionsConfiguration = {
        maintainAspectRatio: false,
        legend: {
          display: false
        },
        tooltips: {
          bodySpacing: 4,
          mode: "nearest",
          intersect: 0,
          position: "nearest",
          xPadding: 10,
          yPadding: 10,
          caretPadding: 10
        },
        responsive: true,
        scales: {
          yAxes: [{
            display: 0,
            gridLines: 0,
            ticks: {
              display: false
            },
            gridLines: {
              zeroLineColor: "transparent",
              drawTicks: false,
              display: false,
              drawBorder: false
            }
          }],
          xAxes: [{
            display: 0,
            gridLines: 0,
            ticks: {
              display: false
            },
            gridLines: {
              zeroLineColor: "transparent",
              drawTicks: false,
              display: false,
              drawBorder: false
            }
          }]
        },
        layout: {
          padding: {
            left: 0,
            right: 0,
            top: 15,
            bottom: 15
          }
        }
      };

    
      ctx = document.getElementById('lineChartExample').getContext("2d");

      gradientStroke = ctx.createLinearGradient(500, 0, 100, 0);
      gradientStroke.addColorStop(0, '#80b6f4');
      gradientStroke.addColorStop(1, chartColor);

      gradientFill = ctx.createLinearGradient(0, 170, 0, 50);
      gradientFill.addColorStop(0, "rgba(128, 182, 244, 0)");
      gradientFill.addColorStop(1, "rgba(249, 99, 59, 0.40)");

      myChart = new Chart(ctx, {
        type: 'line',
        responsive: true,
        data: {
          labels: months,
          datasets: [{
            label: "Active Users",
            borderColor: "#f96332",
            pointBorderColor: "#FFF",
            pointBackgroundColor: "#f96332",
            pointBorderWidth: 2,
            pointHoverRadius: 4,
            pointHoverBorderWidth: 1,
            pointRadius: 4,
            fill: true,
            backgroundColor: gradientFill,
            borderWidth: 2,
            data: values
          }]
        },
        options: gradientChartOptionsConfiguration
      });
    },

    initDashboardPageCharts: function() {

      gradientChartOptionsConfigurationWithTooltipBlue = {
        maintainAspectRatio: false,
        legend: {
          display: false
        },

        tooltips: {
          backgroundColor: '#f5f5f5',
          titleFontColor: '#333',
          bodyFontColor: '#666',
          bodySpacing: 4,
          xPadding: 12,
          mode: "nearest",
          intersect: 0,
          position: "nearest"
        },
        responsive: true,
        scales: {
          yAxes: [{
            barPercentage: 1.6,
            gridLines: {
              drawBorder: false,
              color: 'rgba(29,140,248,0.0)',
              zeroLineColor: "transparent",
            },
            ticks: {
              suggestedMin: 60,
              suggestedMax: 125,
              padding: 20,
              fontColor: "#2380f7"
            }
          }],

          xAxes: [{
            barPercentage: 1.6,
            gridLines: {
              drawBorder: false,
              color: 'rgba(29,140,248,0.1)',
              zeroLineColor: "transparent",
            },
            ticks: {
              padding: 20,
              fontColor: "#2380f7"
            }
          }]
        }
      };

      gradientChartOptionsConfigurationWithTooltipPurple = {
        maintainAspectRatio: false,
        legend: {
          display: false
        },

        tooltips: {
          backgroundColor: '#f5f5f5',
          titleFontColor: '#333',
          bodyFontColor: '#666',
          bodySpacing: 4,
          xPadding: 12,
          mode: "nearest",
          intersect: 0,
          position: "nearest"
        },
        responsive: true,
        scales: {
          yAxes: [{
            barPercentage: 1.6,
            gridLines: {
              drawBorder: false,
              color: 'rgba(29,140,248,0.0)',
              zeroLineColor: "transparent",
            },
            ticks: {
              suggestedMin: 0,
              suggestedMax: 25,
              padding: 20,
              fontColor: "#9a9a9a"
            }
          }],

          xAxes: [{
            barPercentage: 1,
            gridLines: {
              drawBorder: false,
              color: 'rgba(225,78,202,0.1)',
              zeroLineColor: "transparent",
            },
            ticks: {
              padding: 5,
              fontColor: "#9a9a9a"
            }
          }]
        }
      };

      gradientChartOptionsConfigurationWithTooltipOrange = {
        maintainAspectRatio: false,
        legend: {
          display: false
        },

        tooltips: {
          backgroundColor: '#f5f5f5',
          titleFontColor: '#333',
          bodyFontColor: '#666',
          bodySpacing: 4,
          xPadding: 12,
          mode: "nearest",
          intersect: 0,
          position: "nearest"
        },
        responsive: true,
        scales: {
          yAxes: [{
            barPercentage: 1.6,
            gridLines: {
              drawBorder: false,
              color: 'rgba(29,140,248,0.0)',
              zeroLineColor: "transparent",
            },
            ticks: {
              suggestedMin: 50,
              suggestedMax: 110,
              padding: 20,
              fontColor: "#ff8a76"
            }
          }],

          xAxes: [{
            barPercentage: 1.6,
            gridLines: {
              drawBorder: false,
              color: 'rgba(220,53,69,0.1)',
              zeroLineColor: "transparent",
            },
            ticks: {
              padding: 20,
              fontColor: "#ff8a76"
            }
          }]
        }
      };

      gradientChartOptionsConfigurationWithTooltipGreen = {
        maintainAspectRatio: false,
        legend: {
          display: false
        },

        tooltips: {
          backgroundColor: '#f5f5f5',
          titleFontColor: '#333',
          bodyFontColor: '#666',
          bodySpacing: 4,
          xPadding: 12,
          mode: "nearest",
          intersect: 0,
          position: "nearest"
        },
        responsive: true,
        scales: {
          yAxes: [{
            barPercentage: 1.6,
            gridLines: {
              drawBorder: false,
              color: 'rgba(29,140,248,0.0)',
              zeroLineColor: "transparent",
            },
            ticks: {
              suggestedMin: 0,
              suggestedMax: 50,
              padding: 20,
              fontColor: "#9e9e9e"
            }
          }],

          xAxes: [{
            barPercentage: 1.6,
            gridLines: {
              drawBorder: false,
              color: 'rgba(0,242,195,0.1)',
              zeroLineColor: "transparent",
            },
            ticks: {
              padding: 20,
              fontColor: "#9e9e9e"
            }
          }]
        }
      };


      gradientBarChartConfiguration = {
        maintainAspectRatio: false,
        legend: {
          display: false
        },

        tooltips: {
          backgroundColor: '#f5f5f5',
          titleFontColor: '#333',
          bodyFontColor: '#666',
          bodySpacing: 4,
          xPadding: 10,
          mode: "nearest",
          intersect: 0,
          position: "nearest"
        },
        responsive: true,
        scales: {
          yAxes: [{

            gridLines: {
              drawBorder: false,
              color: 'rgba(29,140,248,0.1)',
              zeroLineColor: "transparent",
            },
            ticks: {
              suggestedMin: 0,
              suggestedMax: 50,
              padding: 5,
              fontColor: "#9e9e9e"
            }
          }],

          xAxes: [{

            gridLines: {
              drawBorder: false,
              color: 'rgba(29,140,248,0.1)',
              zeroLineColor: "transparent",
            },
            ticks: {
              padding: 40,
              fontColor: "#9e9e9e"
            }
          }]
        }
      };

      var ctxprogressive = document.getElementById("starProgresschart").getContext("2d");
      var ctxteamprogressive = document.getElementById("starProgressTeamchart").getContext("2d");

      /* Datos de la grafica Evolución 2 Pilotos */
      const races = document.getElementById('json_races_list')
      const x_races = JSON.parse(races.dataset.json);

      const piloto1 = document.getElementById('json_payload_driver1')
      const y_piloto1 = JSON.parse(piloto1.dataset.json);

      const piloto2 = document.getElementById('json_payload_driver2')
      const y_piloto2 = JSON.parse(piloto2.dataset.json);

      const names = document.getElementById('json_names_races')
      const labels_names = JSON.parse(names.dataset.json);

      const piloto1_name = document.getElementById('json_driver_name').getAttribute('data-json')

      const piloto2_name = document.getElementById('json_driver_name2').getAttribute('data-json')

      var gradientStroke = ctxprogressive.createLinearGradient(0, 230, 0, 50);
      
      gradientStroke.addColorStop(1, 'rgba(72,72,176,0.2)');
      gradientStroke.addColorStop(0.2, 'rgba(72,72,176,0.0)');
      gradientStroke.addColorStop(0, 'rgba(119,52,169,0)'); //purple colors

      var gradientStroke2 = ctxteamprogressive.createLinearGradient(0, 230, 0, 50);
      gradientStroke2.addColorStop(1, 'rgba(72,72,176,0.2)');
      gradientStroke2.addColorStop(0.2, 'rgba(72,72,176,0.0)');
      gradientStroke2.addColorStop(0, 'rgba(119,52,169,0)'); //purple colors

      var data = {
        labels: labels_names,
        datasets: [{
          label: piloto1_name +" en " + labels_names[0],
          fill: true,
          backgroundColor: gradientStroke,
          borderColor: '#d048b6',
          borderWidth: 2,
          borderDash: [],
          borderDashOffset: 0.0,
          pointBackgroundColor: '#d048b6',
          pointBorderColor: 'rgba(255,255,255,0)',
          pointHoverBackgroundColor: '#d048b6',
          pointBorderWidth: 20,
          pointHoverRadius: 4,
          pointHoverBorderWidth: 15,
          pointRadius: 4,
          data: y_piloto1,
        },
        {
          label: piloto2_name + " en " + labels_names[1],
          fill: true,
          backgroundColor: gradientStroke,
          borderColor: '#00d6b4',
          borderWidth: 2,
          borderDash: [],
          borderDashOffset: 0.0,
          pointBackgroundColor: '#00d6b4',
          pointBorderColor: 'rgba(255,255,255,0)',
          pointHoverBackgroundColor: '#00d6b4',
          pointBorderWidth: 20,
          pointHoverRadius: 4,
          pointHoverBorderWidth: 15,
          pointRadius: 4,
          data: y_piloto2,
        },
        ]};

        // Datos de la gráfica evolución 2 equipos

      const equipo1 = document.getElementById('json_payload_team1')
      const y_equipo1 = JSON.parse(piloto1.dataset.json);

      const equipo2 = document.getElementById('json_payload_team2')
      const y_equipo2 = JSON.parse(piloto2.dataset.json);

      const equipo1_name = document.getElementById('json_team1_name').getAttribute('data-json')

      const equipo2_name = document.getElementById('json_team2_name').getAttribute('data-json')
      


        var team_data = {
          labels: labels_names,
          datasets: [{
            label: equipo1_name +" en " + labels_names[0],
            fill: true,
            backgroundColor: gradientStroke2,
            borderColor: '#d048b6',
            borderWidth: 2,
            borderDash: [],
            borderDashOffset: 0.0,
            pointBackgroundColor: '#d048b6',
            pointBorderColor: 'rgba(255,255,255,0)',
            pointHoverBackgroundColor: '#d048b6',
            pointBorderWidth: 20,
            pointHoverRadius: 4,
            pointHoverBorderWidth: 15,
            pointRadius: 4,
            data: y_equipo1,
          },
          {
            label: equipo2_name + " en " + labels_names[1],
            fill: true,
            backgroundColor: gradientStroke2,
            borderColor: '#00d6b4',
            borderWidth: 2,
            borderDash: [],
            borderDashOffset: 0.0,
            pointBackgroundColor: '#00d6b4',
            pointBorderColor: 'rgba(255,255,255,0)',
            pointHoverBackgroundColor: '#00d6b4',
            pointBorderWidth: 20,
            pointHoverRadius: 4,
            pointHoverBorderWidth: 15,
            pointRadius: 4,
            data: y_equipo2,
          },
          ]};
    

      var myChart = new Chart(ctxprogressive, {
        type: 'line',
        data: data,
        options: gradientChartOptionsConfigurationWithTooltipPurple
      });

      var myTeamChart = new Chart(ctxteamprogressive, {
        type: 'line',
        data: team_data,
        options: gradientChartOptionsConfigurationWithTooltipPurple
      });

      /* GRÁFICO DE SECTORES */
      const percentage = document.getElementById('json_data_progress').getAttribute('data-json') 
      
      /* PARSEAR JSON A DOUBLE*/
    
      value = parseFloat( percentage.toString()) 

      
      value = value*100 
      rest_value = 100 - value
      
      /* DIAGRAMA DE SECTORES */
      var ctx = document.getElementById('sectorProgresschart').getContext('2d');
      var myChart = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: ['Progreso actual', 'Progreso restante'],
          datasets: [{
            label: 'Progreso de temporada',
            data: [value, rest_value],
            backgroundColor: [
              'rgba(255, 99, 132, 0.7)',
              'rgba(54, 162, 235, 0.7)',
              'rgba(255, 206, 86, 0.7)'
            ],
            borderColor: [
              'rgba(255, 99, 132, 1)',
              'rgba(54, 162, 235, 1)',
              'rgba(255, 206, 86, 1)'
            ],
            borderWidth: 1
          }]
        }
      });

      /* GRÁFICO EVOLUCIÓN TWITTER 2 PILOTOS */

      /* Datos de la grafica Evolución 2 Pilotos */

      var ctxtwitter = document.getElementById("twitterprogresschar").getContext("2d");

      /* LIKES PILOTOS */
      const likes_piloto1 = document.getElementById('json_twitter_likes1')
      const likes_1 = JSON.parse(likes_piloto1.dataset.json);

      const likes_piloto2 = document.getElementById('json_twitter_likes2')
      const likes_2 = JSON.parse(likes_piloto2.dataset.json);

      /* RETWEETS PILOTOS */
      const retweets_piloto1 = document.getElementById('json_twitter_rts1')
      const rts_1 = JSON.parse(retweets_piloto1.dataset.json);

      const retweets_piloto2 = document.getElementById('json_twitter_rts2')
      const rts_2 = JSON.parse(retweets_piloto2.dataset.json);

      /* SEGUIDORES PILOTOS */
      const seguidores_piloto1 = document.getElementById('json_twitter_seguidores1')
      const seguidores_1 = JSON.parse(seguidores_piloto1.dataset.json);

      const seguidores_piloto2 = document.getElementById('json_twitter_seguidores2')
      const seguidores_2 = JSON.parse(seguidores_piloto2.dataset.json);

      var gradientStroke = ctxtwitter.createLinearGradient(0, 230, 0, 50);

      gradientStroke.addColorStop(1, 'rgba(72,72,176,0.2)');
      gradientStroke.addColorStop(0.2, 'rgba(72,72,176,0.0)');
      gradientStroke.addColorStop(0, 'rgba(119,52,169,0)'); //purple colors

     

      /* LIKES EQUIPOS */
      const likes_equipo1 = document.getElementById('json_twitter_likes_equipos1')
      const likesequipo_1 = JSON.parse(likes_equipo1.dataset.json);

      const likes_equipo2 = document.getElementById('json_twitter_likes_equipos2')
      const likesequipo_2 = JSON.parse(likes_equipo2.dataset.json);

      /* RETWEETS PILOTOS */
      const retweets_equipo1 = document.getElementById('json_twitter_rts_equipos1')
      const rtsequipo_1 = JSON.parse(retweets_equipo1.dataset.json);

      const retweets_equipo2 = document.getElementById('json_twitter_rts_equipos2')
      const rtsequipo_2 = JSON.parse(retweets_equipo2.dataset.json);

      /* SEGUIDORES PILOTOS */
      const seguidores_equipo1 = document.getElementById('json_twitter_seguidores_equipos1')
      const seguidoresequipo_1 = JSON.parse(seguidores_equipo1.dataset.json);

      const seguidores_equipo2 = document.getElementById('json_twitter_seguidores_equipos2')
      const seguidoresequipo_2 = JSON.parse(seguidores_equipo2.dataset.json);

            
      // configuración y datos de la gráfica para pilotos
      var config = {
        type: 'line',
        data: {
          labels: ['Hace 1 mes','Hace 3 semanas','Hace 2 semanas','Hace 1 semana','Última semana'],
          datasets: [{
            label: 'Media de likes por semana de '+piloto1_name ,
            fill: true,
            backgroundColor: gradientStroke,
            borderColor: '#d048b6',
            borderWidth: 2,
            borderDash: [],
            borderDashOffset: 0.0,
            pointBackgroundColor: '#d048b6',
            pointBorderColor: 'rgba(255,255,255,0)',
            pointHoverBackgroundColor: '#d048b6',
            pointBorderWidth: 20,
            pointHoverRadius: 4,
            pointHoverBorderWidth: 15,
            pointRadius: 4,
            data: likes_1,
          },
          {
            label: 'Media de likes por semana de '+piloto2_name,
            fill: true,
            backgroundColor: gradientStroke,
            borderColor: '#00d6b4',
            borderWidth: 2,
            borderDash: [],
            borderDashOffset: 0.0,
            pointBackgroundColor: '#00d6b4',
            pointBorderColor: 'rgba(255,255,255,0)',
            pointHoverBackgroundColor: '#00d6b4',
            pointBorderWidth: 20,
            pointHoverRadius: 4,
            pointHoverBorderWidth: 15,
            pointRadius: 4,
            data: likes_2,
          },
          ]
        },
        options: gradientChartOptionsConfigurationWithTooltipPurple
      };
      
        var myChartData = new Chart(ctxtwitter, config);
        $("#0").click(function() {
          var data = myChartData.config.data;
          data.datasets[0].data = likes_1;

          data.datasets[1].data = likes_2;
          data.datasets[0].label = 'Media de likes por semana de '+piloto1_name;
          data.datasets[1].label = 'Media de likes por semana de '+piloto2_name;
          myChartData.update();
        });
        $("#1").click(function() {
          var data = myChartData.config.data;
          data.datasets[0].data = rts_1;
          data.datasets[1].data = rts_2;
          data.datasets[0].label = 'Media de retweets por semana de '+piloto1_name;
          data.datasets[1].label = 'Media de retweets por semana de '+piloto2_name;
          myChartData.update();
        });
    
        $("#2").click(function() {
          var data = myChartData.config.data;
          data.datasets[0].data = seguidores_1;
          data.datasets[1].data = seguidores_2;
          data.datasets[0].label = 'Media de seguidores por semana de '+piloto1_name;
          data.datasets[1].label = 'Media de seguidores por semana de '+piloto2_name;
          myChartData.update();
        });
      
      
       /* Datos de la grafica Evolución 2 Equipos */

      var ctxteamtwitter = document.getElementById("twitterTeamprogresschar").getContext("2d");

      var gradientStrokeequipo = ctxteamtwitter.createLinearGradient(0, 230, 0, 50);

      gradientStrokeequipo.addColorStop(1, 'rgba(72,72,176,0.2)');
      gradientStrokeequipo.addColorStop(0.2, 'rgba(72,72,176,0.0)');
      gradientStrokeequipo.addColorStop(0, 'rgba(119,52,169,0)'); //purple colors

      
      // configuración y datos de la gráfica para equipos
      var team_config = {
        type: 'line',
        data: {
          labels: ['Hace 1 mes','Hace 3 semanas','Hace 2 semanas','Hace 1 semana','Última semana'],
          datasets: [{
            label: 'Media de likes por semana de '+ equipo1_name ,
            fill: true,
            backgroundColor: gradientStrokeequipo,
            borderColor: '#d048b6',
            borderWidth: 2,
            borderDash: [],
            borderDashOffset: 0.0,
            pointBackgroundColor: '#d048b6',
            pointBorderColor: 'rgba(255,255,255,0)',
            pointHoverBackgroundColor: '#d048b6',
            pointBorderWidth: 20,
            pointHoverRadius: 4,
            pointHoverBorderWidth: 15,
            pointRadius: 4,
            data: likesequipo_1,
          },
          {
            label: 'Media de likes por semana de '+equipo2_name,
            fill: true,
            backgroundColor: gradientStrokeequipo,
            borderColor: '#00d6b4',
            borderWidth: 2,
            borderDash: [],
            borderDashOffset: 0.0,
            pointBackgroundColor: '#00d6b4',
            pointBorderColor: 'rgba(255,255,255,0)',
            pointHoverBackgroundColor: '#00d6b4',
            pointBorderWidth: 20,
            pointHoverRadius: 4,
            pointHoverBorderWidth: 15,
            pointRadius: 4,
            data: likesequipo_2,
          },
          ]
        },
        options: gradientChartOptionsConfigurationWithTooltipPurple
      };




      var myTeamChartData = new Chart(ctxteamtwitter, team_config);

        $("#teamLikes").click(function() {
          var data = myTeamChartData.config.data;
          data.datasets[0].data = likesequipo_1;
          data.datasets[1].data = likesequipo_2;
          data.datasets[0].label = 'Media de likes por semana de '+equipo1_name;
          data.datasets[1].label = 'Media de likes por semana de '+equipo2_name;
          myTeamChartData.update();
        });
        $("#TeamRetweets").click(function() {
          var team_data = myTeamChartData.config.data;
          team_data.datasets[0].data = rtsequipo_1;
          team_data.datasets[1].data = rtsequipo_2;
          team_data.datasets[0].label = 'Media de retweets por semana de '+equipo1_name;
          team_data.datasets[1].label = 'Media de retweets por semana de '+equipo2_name;
          myTeamChartData.update();
        });
    
        $("#TeamSeguidores").click(function() {
          var team_data = myTeamChartData.config.data;
          team_data.datasets[0].data = seguidoresequipo_1;
          team_data.datasets[1].data = seguidoresequipo_2;
          team_data.datasets[0].label = 'Media de seguidores por semana de '+equipo1_name;
          team_data.datasets[1].label = 'Media de seguidores por semana de '+equipo2_name;
          myTeamChartData.update();
        });

        /* CONTROL DE PESTAÑAS */

        // Obtener referencias a los botones y los elementos de contenido
        const btn1 = document.getElementById("btn1");
        const contenido1 = document.getElementById("contenido_pilotos");
        const btn2 = document.getElementById("btn2");
        const contenido2 = document.getElementById("contenido_equipos");
        contenido2.style.display = "none";
        // Agregar eventos click a los botones
        btn1.addEventListener("click", () => {
          if (contenido1.style.display === "none") {
            contenido2.style.display = "none";
            contenido1.style.display = "block";
          } else {
            contenido2.style.display = "none"
            contenido1.style.display = "block";
          }
        });

        btn2.addEventListener("click", () => {
          if (contenido2.style.display === "none") {
            contenido1.style.display = "none";
            contenido2.style.display = "block";
            myTeamChart.update({duration: 0});
          } else {
            contenido1.style.display = "none";
            contenido2.style.display = "block";
            myTeamChart.update({duration: 0, lazy: true});
          }
        });


        /* Tendencias en países */

        const abandonosEquipo1Element = document.getElementById('json_abandonos_t1')
        const abandonos_t1 = JSON.parse(abandonosEquipo1Element.dataset.json);


        const abandonosEquipo2Element = document.getElementById('json_abandonos_t2')
        const abandonos_t2 = JSON.parse(abandonosEquipo2Element.dataset.json);

        const seasons_t1 = document.getElementById('json_years_t1')
        const num_seasons_t1 = JSON.parse(seasons_t1.dataset.json);

        const seasons_t2 = document.getElementById('json_years_t2')
        const num_seasons_t2 = JSON.parse(seasons_t2.dataset.json);
        
        var fiabilityctx = document.getElementById("fiabilityChart").getContext("2d");

        var gradientFiabilityStroke = fiabilityctx.createLinearGradient(0, 230, 0, 50);

        gradientFiabilityStroke.addColorStop(1, 'rgba(29,140,248,0.2)');
        gradientFiabilityStroke.addColorStop(0.4, 'rgba(29,140,248,0.0)');
        gradientFiabilityStroke.addColorStop(0, 'rgba(29,140,248,0)'); //blue colors


        var myFiabilityChart = new Chart(fiabilityctx, {
          type: 'bar',
          responsive: true,
          legend: {
            display: false
          },
          data: {
            labels: num_seasons_t1,
            datasets: [{
              label: "Número de abandonos de "+equipo1_name,
              fill: true,
              backgroundColor: gradientFiabilityStroke,
              hoverBackgroundColor: gradientFiabilityStroke,
              borderColor: '#d048b6',
              borderWidth: 20,
              borderDash: [],
              borderDashOffset: 0.0,
              data: abandonos_t1,
            },
            {
              label: "Número de abandonos de "+equipo2_name,
              fill: true,
              backgroundColor: gradientFiabilityStroke,
              hoverBackgroundColor: gradientFiabilityStroke,
              borderColor: '#00d6b4',
              borderWidth: 20,
              borderDash: [],
              borderDashOffset: 0.0,
              data: abandonos_t2,
            }
            ]
          },
          options: gradientBarChartConfiguration
        });
       
      }
      
  };

});