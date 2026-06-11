const http = require('http');
const fs = require('fs');
const path = require('path');
const port = process.env.PORT || 3000;

const mimeTypes = {
  '.html': 'text/html',
  '.js': 'application/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.txt': 'text/plain',
};

const server = http.createServer((req, res) => {
  const safeUrl = req.url.split('?')[0].replace(/\/+$/, '') || '/';
  let filePath = path.join(__dirname, safeUrl === '/' ? 'INICIAR.html' : safeUrl);

  if (!path.normalize(filePath).startsWith(__dirname)) {
    res.writeHead(400, { 'Content-Type': 'text/plain; charset=utf-8' });
    return res.end('Solicitud inválida');
  }

  fs.stat(filePath, (err, stats) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      return res.end('No encontrado');
    }

    if (stats.isDirectory()) {
      filePath = path.join(filePath, 'INICIAR.html');
    }

    fs.readFile(filePath, (readErr, data) => {
      if (readErr) {
        res.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' });
        return res.end('Error interno');
      }

      const ext = path.extname(filePath).toLowerCase();
      const mimeType = mimeTypes[ext] || 'application/octet-stream';
      res.writeHead(200, { 'Content-Type': `${mimeType}; charset=utf-8` });
      res.end(data);
    });
  });
});

server.listen(port, () => {
  console.log(`Servidor iniciado en http://localhost:${port}`);
});