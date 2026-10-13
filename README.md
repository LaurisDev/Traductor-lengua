# Enseñando

Proyecto academico para la asignatura **Lenguajes y Paradigmas**. Aplicacion en Python que traduce letras del alfabeto espanol (A-Z) del lenguaje de senas a texto usando vision por computador con camara web.

## Requisitos

- Python 3.8 o superior
- Camara web
- Windows, Linux o macOS
- MongoDB Community Server (para usuarios) y MongoDB Compass (para visualizar)
- Microfono (para el modulo **Voz a texto**)
- Conexion a internet la **primera vez** que use voz o traduccion con manos (descarga de modelos Whisper / MediaPipe; despues puede funcionar offline)

## Instalacion

1. Abra una terminal en la **raiz del proyecto** (carpeta donde esta `run.py`).

2. (Opcional) Cree y active un entorno virtual:
   - Windows: `python -m venv venv` y luego `venv\Scripts\activate`
   - Linux/macOS: `python3 -m venv venv` y luego `source venv/bin/activate`

3. Instale las dependencias:
   ```text
   pip install -r requirements.txt
   ```

   O use el script de instalacion:
   - Windows: ejecute `install.bat`
   - Linux/macOS: `chmod +x install.sh` y luego `./install.sh`

## Como probar la aplicacion

### Paso 1: Verificar que todo esta listo (opcional)

En la raiz del proyecto ejecute:

```text
python verificar.py
```

Debe mostrar "Verificacion OK" y que la base de datos y los modulos cargan bien. Si falta alguna dependencia, el script lo indicara.

### Paso 2: Ejecutar la aplicacion

En la misma carpeta (raiz del proyecto):

```text
python run.py
```

Se abrira una ventana con el titulo "Enseñando".

### Interfaz (UI)

Por defecto, la app usa una **interfaz moderna en HTML/CSS** embebida como escritorio con **PyWebView**.

- UI web (recomendada): en `src/config.py` deja `USE_WEB_UI = True`
- UI Tkinter (anterior): pon `USE_WEB_UI = False`

**Nota:** La primera vez que abra "Abrir modulo de traduccion", la aplicacion descargara el modelo de deteccion de manos (necesita internet). En Windows se guarda en `%LOCALAPPDATA%\TraductorSenas\models` para evitar problemas con OneDrive; en otros sistemas, en la carpeta `models/` del proyecto.

### Paso 3: Probar registro y login

1. Pulse **Registrarse**.
2. Elija un usuario (por ejemplo `prueba`) y una contrasena (minimo 6 caracteres, por ejemplo `prueba123`). Confirme la contrasena.
3. Pulse **Registrarse**. Debe volver a la pantalla de inicio.
4. Escriba el mismo usuario y contrasena y pulse **Entrar**.
5. Debe aparecer el menu principal con "Bienvenido, prueba".

**MongoDB/Compass:** Al registrarte, el usuario se guarda en MongoDB y podras verlo en Compass en la BD `traductor_senas`, coleccion `users`. El identificador `_id` es el ID unico del usuario.

### Paso 4: Probar la pantalla de interacción (Voz + Señas)

1. En el menu principal pulse **Iniciar interacción (Voz + Señas)**.
2. La cámara se encenderá y verás el video en el panel de **Señas**.
3. Ponga **una mano** frente a la camara con buena luz.
4. La letra detectada (A-Z) se mostrará y se irá agregando al campo **Texto (señas)**. Por ejemplo:
   - Punio con el pulgar al lado suele dar **A**.
   - Mano abierta con todos los dedos extendidos y pulgar cerrado suele dar **B**.
5. Usa **Espacio / Borrar / Limpiar** para formar palabras y frases por deletreo.
6. Pulsa **Enviar señas** para mandarlo a la conversación como \"Persona (señas)\".
7. En el panel de **Voz**, pulsa **Grabar**, habla y luego **Detener** para que el texto aparezca en la conversación como \"Yo (voz)\".
7. Pulse **Volver** para regresar al menú (la cámara se apaga).

### Alfabetos de señas (LSC, Libras y ASL)

El idioma de aprendizaje elige el alfabeto y el modelo de reconocimiento, cada uno con sus propios datos:

| Idioma | Alfabeto | Datos y modelo | Imágenes |
|---|---|---|---|
| Español | LSC (incluye Ñ) | `data/sign_language/` | `src/gui_web/web/assets/letras/` |
| Portugués | Libras (incluye Ç) | `data/sign_language/libras/` | `src/gui_web/web/assets/letras/libras/` |
| Inglés | ASL (26 letras) | `data/sign_language/asl/` | `src/gui_web/web/assets/letras/asl/` |

ASL reutiliza las letras cuya seña es equivalente en LSC o Libras. Para rearmar su dataset, imágenes y modelo: `python build_asl_dataset.py`.
Las letras propias de ASL (F, M, N, Q, T) se graban con `python collect_sign_samples.py --lang en --only F` (ver `src/gui_web/web/assets/letras/asl/README.md`).

### Mejorar nombres en voz (hotwords)

Para ayudar con nombres propios (por ejemplo \"Xiomara\"), edite `data/hotwords_es.txt` y agregue nombres frecuentes (1 por línea). Whisper usará esa lista como sesgo leve al transcribir.

### Paso 5: Cerrar sesion

En el menu principal pulse **Cerrar sesion**. Volvera a la pantalla de inicio de sesion.

### Si la camara no inicia

1. Ejecute primero la prueba rapida: `python probar_camara.py`. Si dice "Camara OK", la app deberia poder usarla.
2. En Windows: vaya a **Configuracion > Privacidad > Camara** y permita el acceso a aplicaciones (y a "Aplicaciones de escritorio" si aparece).
3. Cierre **Chrome** y cualquier otra app que use la camara (Zoom, Teams, Skype, etc.). Aunque no tenga videollamada abierta, a veces el navegador reserva el dispositivo.
4. Vuelva a ejecutar `python run.py` y abra el modulo de traduccion de nuevo.

### Si algo mas falla

- **"No se pudo abrir la camara"**: Siga los pasos de "Si la camara no inicia".
- **Error al importar**: Ejecute `pip install -r requirements.txt` de nuevo.
- **La letra no cambia**: Ilumine bien la mano y mantenga el gesto estable unos segundos; el sistema confirma la letra tras varios frames iguales.
- **Voz a texto falla o es muy lento**: Compruebe permisos del microfono en Windows. Si aparece error de `compute_type`, pruebe en `src/config.py` con `WHISPER_COMPUTE_TYPE = "float32"`.

### Publicar una version web para pruebas

El modo de escritorio sigue disponible con `python run.py`. Para compartir un enlace, el repositorio incluye una version web para Render (`Dockerfile`, `render.yaml` y `web_server.py`). En este modo la camara del participante se usa desde el navegador y sus frames se procesan en el servidor. La interfaz necesita HTTPS para solicitar acceso a la camara.

1. Sube el proyecto a un repositorio de GitHub. No subas `venv/` ni credenciales.
2. Crea una cuenta gratuita en [MongoDB Atlas](https://www.mongodb.com/atlas), crea un cluster y un usuario de base de datos. En **Network Access**, permite conexiones desde Render (para una demo se puede autorizar `0.0.0.0/0`; usa una contraseña robusta).
3. En [Render](https://render.com/), crea un **Blueprint** y conecta el repositorio. Render detectara `render.yaml` y construira el servicio web.
4. En la configuración del servicio, agrega `MONGO_URI` con la cadena de conexión de Atlas. Sustituye la contraseña de ejemplo en la cadena y no la publiques en GitHub. `SESSION_SECRET` se genera automáticamente.
5. Espera a que el despliegue finalice y abre la URL `https://...onrender.com` que muestra Render. Comparte ese enlace con quienes harán las pruebas.
6. Cada participante debe permitir la cámara. Para voz a texto se recomienda Chrome o Edge; el navegador puede usar su proveedor de reconocimiento de voz. La detección de señas se ejecuta en Render, por lo que se recomienda el plan Starter para que el servicio tenga memoria y CPU suficientes.

Los participantes pueden registrarse desde la página. Cada navegador recibe una sesión independiente; para no sobrecargar el servidor, ejecuta las pruebas heurísticas de una en una. Render puede tardar en volver a despertar una instancia gratuita si se utiliza un plan que entre en suspensión.

## Estructura del proyecto

```text
Señas/
  run.py           Punto de entrada (python run.py)
  verificar.py     Comprueba dependencias e imports
  requirements.txt
  install.bat / install.sh
  src/
    main.py        Controlador principal
    config.py      Constantes
    auth/          Login y registro
    database/      MongoDB (conector) y modelos
    gui/           Interfaz Tkinter
    camera/        Captura OpenCV
    image_processing/  MediaPipe manos
    sign_language/    Clasificacion A-Z
    speech/           Voz a texto (faster-whisper)
  docs/            Documentacion
```

## Dependencias

- OpenCV (camara)
- MediaPipe (deteccion de manos)
- Pillow (mostrar video en la interfaz)
- Tkinter/TTK (incluido en Python) + ttkbootstrap (tema moderno)
- MongoDB (usuarios) con pymongo (cliente)
- faster-whisper + sounddevice (reconocimiento de voz local en espanol)
- pywebview (UI web embebida HTML/CSS)

## Documentacion

- `docs/documento_tecnico.md` - Arquitectura, paradigmas, limitaciones
- `docs/manual_usuario.md` - Uso detallado y solucion de problemas
- `docs/manual_tecnico.md` - Estructura del codigo y clases
