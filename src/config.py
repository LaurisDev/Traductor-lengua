# config.py
# Constantes y configuracion centralizada del proyecto.
# Responsabilidad unica: definir parametros reutilizables.

# Base de datos
DB_PATH = "database/senas.db"
DB_USERS_TABLE = "users"

# Validacion de credenciales
MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 50
MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 100

# Camara
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Reconocimiento de manos
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.5

# Interfaz
APP_TITLE = "Traductor de Lenguaje de Senas"
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600
