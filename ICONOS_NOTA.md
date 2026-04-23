# AS BAJO LA MANGA - Nota sobre Iconos

## 🎨 Iconos PWA Necesarios

Para completar la configuración PWA, necesitas crear 2 iconos:

### Especificaciones:
- **icon-192.png**: 192x192 píxeles
- **icon-512.png**: 512x512 píxeles
- Formato: PNG con fondo sólido
- Ubicación: `/assets/` (crear carpeta)

### Opciones para Generar:

#### 1. Herramienta Online (Recomendado)
- **PWA Asset Generator**: https://progressier.com/pwa-icons-generator
- **RealFaviconGenerator**: https://realfavicongenerator.net/
  - Sube cualquier imagen relacionada con cartas
  - Genera automáticamente todos los tamaños

#### 2. Manualmente con Diseño
Si tienes Photoshop/GIMP/Figma:
- Crea un diseño de 512x512
- Tema: Cartas, juego, o el emoji 🃏
- Colores: Dorado (#D4AF37) y oscuro (#020617)
- Exporta a PNG en 512x512 y 192x192

#### 3. Placeholder Temporal
Para testing rápido, puedes usar emojis convertidos:
```bash
# Ejemplo con ImageMagick (si lo tienes instalado)
convert -size 512x512 -background "#020617" -fill "#D4AF37" -font Arial -pointsize 400 -gravity center label:"🃏" assets/icon-512.png
convert assets/icon-512.png -resize 192x192 assets/icon-192.png
```

### Una vez creados:
1. Coloca `icon-192.png` e `icon-512.png` en carpeta `assets/`
2. Los archivos ya están referenciados en:
   - `manifest.json` (iconos PWA)
   - `INICIAR.html` (apple-touch-icon)

**¡Tu app estará 100% lista para deployment!**
