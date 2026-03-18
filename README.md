# Traductor de Lenguaje de Senas (A-Z)

Proyecto academico para la asignatura **Lenguajes y Paradigmas**. Aplicacion en Python que traduce letras del alfabeto espanol (A-Z) del lenguaje de senas a texto usando vision por computador con camara web.

## Requisitos

- Python 3.8 o superior
- Camara web
- Windows, Linux o macOS

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

Se abrira una ventana con el titulo "Traductor de Lenguaje de Senas".

**Nota:** La primera vez que abra "Abrir modulo de traduccion", la aplicacion descargara el modelo de deteccion de manos (necesita internet). En Windows se guarda en `%LOCALAPPDATA%\TraductorSenas\models` para evitar problemas con OneDrive; en otros sistemas, en la carpeta `models/` del proyecto.

### Paso 3: Probar registro y login

1. Pulse **Registrarse**.
2. Elija un usuario (por ejemplo `prueba`) y una contrasena (minimo 6 caracteres, por ejemplo `prueba123`). Confirme la contrasena.
3. Pulse **Registrarse**. Debe volver a la pantalla de inicio.
4. Escriba el mismo usuario y contrasena y pulse **Entrar**.
5. Debe aparecer el menu principal con "Bienvenido, prueba".

### Paso 4: Probar el modulo de traduccion

1. En el menu principal pulse **Abrir modulo de traduccion**.
2. La camara deberia encenderse y verse el video en la ventana.
3. Ponga **una mano** frente a la camara con buena luz.
4. La letra detectada (A-Z) aparecera encima del video. Por ejemplo:
   - Punio con el pulgar al lado suele dar **A**.
   - Mano abierta con todos los dedos extendidos y pulgar cerrado suele dar **B**.
5. Pulse **Volver al menu** para salir del modulo (la camara se apagara).

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

### Uso en celular

Esta aplicacion es de **escritorio** (Python + Tkinter + OpenCV). No funciona tal cual en el celular: los sistemas moviles no ejecutan este tipo de programa. Para usarla en el celular haria falta una version distinta, por ejemplo una app movil (Android/iOS) o una pagina web que use la camara del telefono desde el navegador; la logica de reconocimiento podria reutilizarse en un servidor o reescribirse en otro lenguaje.

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
    database/      SQLite y usuarios
    gui/           Interfaz Tkinter
    camera/        Captura OpenCV
    image_processing/  MediaPipe manos
    sign_language/    Clasificacion A-Z
  docs/            Documentacion
  database/        Base SQLite (se crea al ejecutar)
```

## Dependencias

- OpenCV (camara)
- MediaPipe (deteccion de manos)
- Pillow (mostrar video en la interfaz)
- Tkinter (incluido en Python)
- SQLite (incluido en Python)

## Documentacion

- `docs/documento_tecnico.md` - Arquitectura, paradigmas, limitaciones
- `docs/manual_usuario.md` - Uso detallado y solucion de problemas
- `docs/manual_tecnico.md` - Estructura del codigo y clases
