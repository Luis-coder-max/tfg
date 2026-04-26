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