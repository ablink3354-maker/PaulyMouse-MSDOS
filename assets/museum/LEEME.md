# El Museo de Pauly — versión web independiente

Adaptación educativa nueva inspirada en Pauly Mouse. Incluye nueve salas, 36 fichas con fotografías reales, audioguías en español de México, nueve capítulos de una historia y retos. Conserva descubrimientos, favoritos y resultados en el almacenamiento local del navegador. No requiere cuentas, servicios de pago ni claves de API.

## Abrir y alojar

Descomprime el ZIP. Puedes abrir `index.html` directamente para una visita local. Para instalar la versión web y disponer de su caché sin conexión, sirve la carpeta completa mediante HTTPS o localhost. Por ejemplo, con Python instalado: `python -m http.server 8000`; después abre `http://localhost:8000`.

En tu alojamiento copia **toda** esta carpeta a `/museo-pauly/`, conservando nombres y subcarpetas. No hace falta compilar ni instalar dependencias. El primer acceso descarga los recursos para la caché sin conexión; espera a que termine antes de desconectarte. Los archivos multimedia también están incluidos en el ZIP.

## Integrar en otra página

Después de subir la carpeta, incorpora lo siguiente en tu página:

```html
<iframe src="/museo-pauly/index.html"
  title="El Museo de Pauly"
  style="width:100%;height:90vh;min-height:640px;border:0;border-radius:16px"
  allow="autoplay; fullscreen" loading="lazy"></iframe>
```

Si tu gestor de contenido bloquea iframes, utiliza un enlace a `/museo-pauly/index.html`. Los navegadores pueden impedir la voz automática; siempre están disponibles los botones para escuchar. El almacenamiento de progreso dentro de iframes de otro dominio depende de la política del navegador. Para conservarlo con mayor facilidad aloja el museo en el mismo dominio de tu página.

## Editar

- `index.html`: estructura y navegación.
- `style.css`: presentación adaptable a teléfonos, tabletas y computadoras.
- `app.js`: fichas, cuaderno, historia, retos, preferencias y reproducción de voz.
- `data.js`: contenido en español. Las respuestas correctas son el primer elemento de `answers`; al jugar se mezclan.
- `assets/backgrounds`: nueve ilustraciones HD.
- `assets/photos`: 36 fotografías reales.
- `assets/audio`: 58 narraciones MP3 incluidas, sin generación ni conexión durante la visita.
- `narration-script.json`: textos y voces utilizados.
- `photo-credits.json`: autores, licencias, fotografías y referencias por especie.
- `sw.js` y `offline-files.json`: caché de la versión web. Al modificar el contenido cambia la versión de `CACHE` en `sw.js` y actualiza la lista de archivos.

## Créditos

El personaje Pauly Mouse y el juego original pertenecen a sus respectivos titulares. Esta es una adaptación educativa independiente: no reproduce todos los minijuegos, diálogos ni animaciones originales y no incluye el ejecutable de Windows.

Las fotografías son reales, obtenidas de Wikimedia Commons y, cuando corresponde, iNaturalist. Cada imagen conserva su licencia individual; los enlaces, atribuciones y referencias están en `photo-credits.json` y en la sección Créditos del museo. No se concede una licencia conjunta sobre los recursos de terceros. Conserva las atribuciones y cumple las condiciones indicadas al reutilizarlos.

Los fondos y el retrato HD se crearon con generación de imágenes por IA tomando referencias visuales del juego. Los textos y la historia son nuevos para esta adaptación. Las voces sintéticas utilizadas son es-MX-JorgeNeural y es-MX-DaliaNeural; no son grabaciones ni imitaciones de las voces originales.

La APK es una aplicación Android con esta experiencia empaquetada localmente. Funciona sin conexión desde su instalación y no solicita permiso de Internet. Los enlaces de créditos se consultan en el navegador externo y sí requieren conexión.
