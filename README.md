Para el correcto funcionamiento de la aplicación necesitaremos desplegar:

- Un servidor de MySql
- El LLM requerido mediante LMStudio
- Importar la extensión de navegador

1. Servidor MySQL

En el proyecto encontrarás compose.yml, que pone en marcha MySQL junto con la creación automática de base de datos y tablas.

Pasos:
Instala Docker:
🔗 https://www.docker.com/

Abre una terminal en el directorio del proyecto.

Ejecuta el siguiente comando:

docker compose up -d

El contenedor se desplegará en localhost:3306 y ejecutará los scripts de inicialización incluidos.

2. Despliegue del LLM con LM Studio

Para consultar el modelo de lenguaje desde la aplicación, es necesario instalar y configurar LM Studio, una herramienta que permite ejecutar modelos LLM localmente y exponer una API compatible con OpenAI.

Pasos:

Descargar e instalar LM Studio desde:
👉 https://lmstudio.ai/

Abrir LM Studio.

Haz clic en el siguiente enlace para abrir directamente el modelo en LM Studio:
👉 Qwen2.5-7B-Instruct-1M-GGUF

En la vista del modelo, pulsa Download para descargarlo.

Accede a la pestaña Developer de LM Studio.

En la parte superior, selecciona el modelo descargado y asegúrate de que el servidor esté con Status: Running y Reachable at: http://127.0.0.1:1234

Una vez en funcionamiento, el servidor quedará expuesto por defecto en:
📍 http://localhost:1234/v1/chat/completions


3. Instalación de la extensión de navegador

Para utilizar la aplicación desde el navegador, sigue estos pasos:

Abre Google Chrome o cualquier navegador compatible con extensiones Chromium.

Accede al gestor de extensiones de tu navegador chrome://extensions/ en la barra de direcciones en la mayoría de casos.

Activa el modo Desarrollador (arriba a la derecha).

Haz clic en "Cargar descomprimida".

Selecciona la carpeta del proyecto que contiene la extensión "my-maps-extension".





