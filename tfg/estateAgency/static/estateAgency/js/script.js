function predict() {
  const type = document.getElementById("type").value;
  const city = document.getElementById("city").value;
  const result = document.getElementById("result");
  redirectUrl = `/properties/?type=${type}&city=${city}`;
  window.location.href = redirectUrl;
}