import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Encaminha /api para o backend Flask em dev (evita CORS e hardcode de host)
    proxy: {
      "/api": "http://127.0.0.1:5001",
    },
  },
});
