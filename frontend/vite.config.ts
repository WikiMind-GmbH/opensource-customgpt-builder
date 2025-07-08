import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0", // Accept connections from Docker network
    port: 5173, // Ensure the correct port
    strictPort: true, // Prevent port conflicts
    watch: {
      usePolling: true, // Fix file watching inside Docker
    },
  },
});
