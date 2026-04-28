function predict() {
  const type = document.getElementById("type").value;
  const city = document.getElementById("city").value;
  const result = document.getElementById("result");
  redirectUrl = `/properties/?type=${type}&city=${city}`;
  window.location.href = redirectUrl;
}

function renderChart(labels, data, label) {
  new Chart(document.getElementById("grafico"), {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: label,
        data: data
      }]
    }
  });
}

function renderPropertyCharts(chartData, selectedType) {
  const priceCanvas = document.getElementById("grafico");
  const priceM2Canvas = document.getElementById("graficoM2");
  const priceTitle = document.getElementById("priceChartTitle");

  if (!priceCanvas || !priceM2Canvas || typeof Chart === "undefined") {
    return;
  }

  let chartType = "bar";
  let chartTitle = "Precio de compra por vivienda";

  if (selectedType === "rent_long") {
    chartType = "line";
    chartTitle = "Alquiler mensual por vivienda";
  }

  if (selectedType === "rent_short") {
    chartType = "doughnut";
    chartTitle = "Alquiler de temporada por vivienda";
  }

  if (priceTitle) {
    priceTitle.textContent = chartTitle;
  }

  new Chart(priceCanvas, {
    type: chartType,
    data: {
      labels: chartData.labels,
      datasets: [{
        label: chartTitle,
        data: chartData.prices,
        backgroundColor: [
          "#1f6feb",
          "#0f9f8f",
          "#d85b42",
          "#d6a73b",
          "#7557b8",
          "#344054",
        ],
        borderColor: "#1f6feb",
        borderWidth: 2,
        tension: 0.3,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: true,
        }
      }
    }
  });

  new Chart(priceM2Canvas, {
    type: "bar",
    data: {
      labels: chartData.labels,
      datasets: [{
        label: "Precio por metro cuadrado",
        data: chartData.prices_m2,
        backgroundColor: "#0f9f8f",
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: true,
        }
      }
    }
  });
}

async function checkScrapingStatus() {
    try {

        const response = await fetch("/scraping/status/");
        console.log(response);
        const data = await response.json();
        console.log(data);
        

        const overlay = document.getElementById("scraping-popup");
        console.log(overlay);
        

        if (data.running) {
            overlay.style.display = "flex";
        } else {
            clearInterval(scrapingStatusInterval);
            overlay.style.display = "none";
        }
    } catch (e) {
        console.error("Error checking scraping status", e);
    }
}
checkScrapingStatus();
setInterval(checkScrapingStatus, 10000);