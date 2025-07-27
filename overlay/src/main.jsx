import { io } from "socket.io-client";

const fpsEl = document.getElementById("fps");
const tempEl = document.getElementById("gpu_temp");
const loadEl = document.getElementById("gpu_load");
const vramEl = document.getElementById("vram");

const socket = io("http://localhost:8502");

socket.on("telemetry", (data) => {
  fpsEl.textContent = data.fps;
  tempEl.textContent = data.gpu_temp;
  loadEl.textContent = data.gpu_load;
  vramEl.textContent = data.vram_used;
});
