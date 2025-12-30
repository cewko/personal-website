function updateTime() {
  const now = new Date();

  const polandTime = new Intl.DateTimeFormat("en-US", {
    timeZone: "Europe/Warsaw",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(now);

  const timeElement = document.querySelector(".weather-time");
  if (timeElement) {
    timeElement.textContent = `Time: ${polandTime}`;
  }
}

function initClock() {
  updateTime();
  setInterval(updateTime, 60000);
}