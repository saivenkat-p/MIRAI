import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'node:fs';
import path from 'node:path';

export default defineConfig({
  plugins: [
    react(),
    {
      name: 'decart-frame-metadata-worker-resolver',
      configureServer(server) {
        const workerDiskPath = path.resolve(
          __dirname,
          'node_modules/@decartai/sdk/dist/realtime/browser/frame-metadata-worker.js'
        );

        server.middlewares.use((req, res, next) => {
          if (req.url && req.url.includes('frame-metadata-worker.js')) {
            if (fs.existsSync(workerDiskPath)) {
              res.setHeader('Content-Type', 'application/javascript');
              res.setHeader('Access-Control-Allow-Origin', '*');
              res.end(fs.readFileSync(workerDiskPath));
              return;
            }
          }
          next();
        });
      },
    },
  ],
  server: {
    port: 5173,
    host: true,
  },
});
