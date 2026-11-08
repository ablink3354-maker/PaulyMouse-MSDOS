# Recursos y doblaje

La aplicación se construye conassets/game yassets/museum. El motor oficial se
descarga con tools/download-engine.py y se verifica con SHA256. No necesitas generar
imágenes o voces de nuevo para compilar la APK.

Los scripts de producción de tools/ conservan sus rutaswork/ para reproducir la
preparación original desde una copia del juego. Para regenerar bitmaps/scripts,
extrae primero los DXR originales con drxtract. Mantén PMNL sin modificar y crea
PMES como carpeta de salida. Orden:

1. localize-director-books.py
2. localize-director-buttons.py
3. patch-pauly-book-access.py
4. patch-pauly-navigation.py
5. patch-pauly-frog-audio.py

Los textos revisados están en pauly-spanish-reviewed.json y los diálogos adaptados
en pauly-character-dialogues-es.json. Los 72 archivos con preserveOriginal=false se
doblan; los demás mantienen sonidos y reacciones originales. Los 222 audios del
libro usan los nombres originales de archivo, mapeados por pauly-book-audio-map.json.

Las voces ya están incluidas como archivos locales. Los conectores de generación
en línea no se publican; puedes sustituir los audios con tus propios archivos.
Los audios resultantes se pueden volver a mezclar con pauly-mdx-separate.py y
mix-pauly-character-audio.py. Dependencias opcionales: av,numpy,torchCPU,
onnxruntime y Pillow; Python 3.12 para aifc.

Modelo empleado para separar diálogo: UVR_MDXNET_KARA_2.onnx, SHA256
bf32e15105a09c0f7dddd2b67346146334d6f3ecb399ed7638eba2ab07cbf5f4.
Fuente:https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/UVR_MDXNET_KARA_2.onnx
Parámetros:https://raw.githubusercontent.com/TRvlvr/application_data/main/mdx_model_data/model_data.json
Los pesos y cachés de modelos no se incluyen en el repositorio ni en la APK.

La mezcla mantiene duración original de los efectos/dialogados a 22050 Hz, mono 16 bit
AIFF. Se restaura el audio original fuera de las zonas de voz. Aplicar al final
restore-pauly-nonverbal.py para conservar música, rugidos y reacciones sin palabras.
La separación no es una recuperación perfecta de pistas maestras originales.

La rana reproduce pregunta y respuesta mediante estados por frame; no debe
reintroducirse el bucle repeat while soundBusy ... nothing que bloqueaba los toques.
El renderer nativo ocupa solamente el rectángulo 4:3 para no tapar los paneles
durante transiciones. Los atajos b/r/l/n/p son compartidos por esos accesos.
