# 🃏 AS BAJO LA MANGA

Juego de cartas interactivo móvil-optimizado con **8 modos de juego**: **Toxic Cards**, **Poker Caliente**, **El Sabio del Guaro**, **¿Quién Es Más...?**, **Bomba de Palabras**, **Reto en Cadena**, **Dilema del Rey**, **Mímica Express** y **Biblioteca**.

## 🚀 Características
- **9 Modos de Juego Únicos**: Desde retos picantes hasta dilemas morales.
- **Sistema de Jugadores Unificado**: Añade participantes una vez y úsalos en los juegos grupales.
- **Sin Persistencia de Jugadores**: Privacidad total, la lista de borrachos se reinicia al recargar.
- **Modo Offline (PWA)**: Instálala en tu móvil y juega sin internet.
- **Diseño Glassmorphism**: Interfaz moderna y oscura con toques dorados y neón.
- **Más de 500 cartas y retos**: Contenido renovado y expandido.

## 🎮 Modos de Juego

### 🃏 Juegos de Cartas
1. **Toxic Cards**: Verdades incómodas y retos picantes. (300 cartas)
2. **Poker Caliente**: Dinámicas clásicas con baraja inglesa.
3. **El Sabio del Guaro**: Adivina si la siguiente carta es mayor o menor.
4. **Biblioteca**: Explora todas las cartas disponibles.

### 👥 Juegos de Grupo (NUEVO)
5. **¿Quién Es Más...?**: Votación grupal. El más señalado bebe. (100 preguntas)
6. **Bomba de Palabras**: Di una palabra de la categoría antes que explote. (50 categorías)
7. **Reto en Cadena**: Memoriza y repite la cadena de retos, añadiendo uno nuevo.
8. **Dilema del Rey**: Elige entre dos opciones difíciles. La minoría bebe.
9. **Mímica Express**: Actúa una palabra en 20 segundos. Si fallan, bebes.

- 📱 **Optimizado para Móvil**:
  - Gestos táctiles (swipe para navegar)
  - Feedback háptico (vibración)
  - Tamaños táctiles mínimos de 44px
  - Responsive design para portrait y landscape

- 🎨 **Experiencia Visual Premium**:
  - Animaciones 3D (flip, shake, slide)
  - Efectos ripple en botones
  - Notificaciones toast
  - Confeti para celebraciones
  - Glassmorphism design

- 💾 **Funcionalidad Offline**:
  - PWA (Progressive Web App)
  - Instalable en dispositivos móviles
  - Service Worker para cache
  - Persistencia con localStorage

## 🚀 Despliegue rápido en Vercel

### Opción 1: Desde GitHub (Recomendado)

1. **Sube tu proyecto a GitHub**:
```bash
git init
git add .
git commit -m "Initial commit - AS BAJO LA MANGA"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/as-bajo-la-manga.git
git push -u origin main
```

2. **Conecta con Vercel**:
   - Ve a [vercel.com](https://vercel.com)
   - Click en "Import Project"
   - Selecciona tu repositorio
   - Vercel detectará automáticamente la configuración
   - Click en "Deploy"

3. **¡Listo!** Tu app estará disponible en una URL como:
   - `https://as-bajo-la-manga.vercel.app`

### Opción 2: Desde línea de comandos

```bash
# Instala Vercel CLI
npm i -g vercel

# Despliega
vercel

# Para producción
vercel --prod
```

## 📂 Estructura de Archivos

```
as-bajo-la-manga/
├── INICIAR.html       # Aplicación principal (SPA)
├── manifest.json      # Configuración PWA
├── sw.js             # Service Worker
├── data.json         # Datos de cartas
├── README.md         # Este archivo
└── assets/           # Iconos PWA (crear carpeta)
    ├── icon-192.png
    └── icon-512.png
```

## 🎯 Cómo Jugar

### Toxic Cards
1. Añade jugadores (máximo 20)
2. Selecciona categoría o usa "TODAS"
3. Swipe izquierda o presiona "Siguiente" para repartir cartas
4. Cumple los retos o responde las verdades

### Poker Caliente
1. Presiona "REPARTIR" para sacar una carta
2. Sigue las instrucciones de la carta
3. Cada palo tiene desafíos diferentes

### El Sabio del Guaro
1. Se muestra una carta actual
2. Adivina el color, palo o si la siguiente será mayor/menor
3. Aciertos restan tragos, errores suman
4. ¡Llega a 0 tragos para ganar con confeti!

## 🎨 Personalización

### Cambiar Colores del Tema

Edita las variables CSS en `INICIAR.html`:

```css
:root {
  --gold: #D4AF37;      /* Color dorado principal */
  --bg-dark: #020617;   /* Fondo oscuro */
}
```

### Añadir Más Cartas

Edita el archivo `data.json` o modifica directamente los arrays `TOXIC_CARDS` y `POKER_CARDS` en el HTML.

## 📱 Instalar como App

### iOS (Safari):
1. Abre la página en Safari
2. Toca el botón "Compartir"
3. Selecciona "Añadir a pantalla de inicio"

### Android (Chrome):
1. Abre la página en Chrome
2. Toca el menú (⋮)
3. Selecciona "Añadir a pantalla de inicio"

## 🛠️ Tecnologías

- **HTML5** + **Vanilla JavaScript** (No frameworks)
- **Tailwind CSS** (CDN)
- **PWA APIs**: Service Worker, Web App Manifest, Vibration API
- **LocalStorage** para persistencia
- **CSS Grid** y **Flexbox** para layouts responsive

## 📝 Licencia

Este proyecto es de uso personal. Disfruta con moderación 🍻

## 🤝 Contribuciones

Si quieres añadir nuevas cartas o mejorar el juego, ¡los pull requests son bienvenidos!

---

**Hecho con ❤️ para diversión responsable**
