import { io } from "socket.io-client";
import { Chart, LineController, LineElement, PointElement, LinearScale, Title, CategoryScale } from 'chart.js';
Chart.register(LineController, LineElement, PointElement, LinearScale, Title, CategoryScale);

const socket = io("http://localhost:8000");

// FPS chart
const ctx = document.getElementById("fpsChart").getContext("2d");
const fpsData = {
  labels: Array(30).fill(""),
  datasets: [{
    label: "FPS",
    data: Array(30).fill(0),
    borderColor: "#00ff88",
    tension: 0.3
  }]
};

const chart = new Chart(ctx, {
  type: "line",
  data: fpsData,
  options: {
    animation: false,
    scales: {
      y: { beginAtZero: true, max: 300 }
    },
    plugins: {
      legend: { display: false }
    }
  }
});

// UI Elements
const tempEl = document.getElementById("temp");
const gpuEl = document.getElementById("gpu");
const vramEl = document.getElementById("vram");

// Update from server
socket.on("telemetry", (data) => {
  // FPS chart
  fpsData.datasets[0].data.push(data.fps);
  fpsData.datasets[0].data.shift();
  chart.update();

  // Stats
  tempEl.textContent = `GPU Temp: ${data.temp} °C`;
  gpuEl.textContent = `GPU Load: ${data.load}%`;
  vramEl.textContent = `VRAM Used: ${data.vram} GB`;
});
