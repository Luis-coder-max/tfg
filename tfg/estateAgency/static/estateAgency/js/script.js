function predict() {
  const type = document.getElementById("type").value;
  const city = document.getElementById("city").value;
  const result = document.getElementById("result");

  let message = "";

  if (!city) {
    result.innerHTML = "Introduce una ciudad";
    return;
  }

  if (type === "compra") {
    message = `En ${city}, se espera una subida de precios del 5-8% en los próximos meses.`;
  } else if (type === "larga") {
    message = `En ${city}, el alquiler de larga estancia seguirá en alta demanda con subidas moderadas.`;
  } else {
    message = `En ${city}, el alquiler de temporada tendrá picos altos en fechas turísticas.`;
  }

  result.innerHTML = message;
}