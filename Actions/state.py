# Actions/state.py — ProyectoUnido (EndGame + ProyectoFinal combinado)

# ── SELECCIÓN DE PERSONAJE ─────────────────────────────────────
# 'plasma', 'optimus', 'dee', 'kirby', 'pochaco', 'pucca'
personaje_activo = None   # None = en menú
menu_cursor_index = 0     # Índice del grid MK9 (0 a 5)

# ── MENÚ ──────────────────────────────────────────────────────
en_menu = True

# ── ESCENARIO ─────────────────────────────────────────────────
escenario_actual = 1   # 1-7

# ── CÁMARA ────────────────────────────────────────────────────
cam_distance = 12.0
cam_yaw      = 0.0
cam_pitch    = 18.0
rotate_x     = 0.0

# ── PERSONAJE (posición compartida) ───────────────────────────
fox_x = 0.0
fox_y = 0.0
fox_z = 0.0
fox_speed  = 0.12
fox_facing = 0.0

key_up    = False
key_down  = False
key_left  = False
key_right = False

# ── ARTICULACIONES — Plasma Pea ───────────────────────────────
cabeza_y   = 0.0
cabeza_x   = 0.0
canon_x    = 0.0
hoja_izq_z = 0.0
hoja_der_z = 0.0
hoja_izq_y = 0.0
hoja_der_y = 0.0
raiz_izq_x = 0.0
raiz_der_x = 0.0

# ── ARTICULACIONES — Optimus Prime ────────────────────────────
brazo_izq_x  = 0.0
brazo_der_x  = 0.0
pierna_izq_x = 0.0
pierna_der_x = 0.0

# ── CAÑÓN BRAZO DERECHO — Optimus Prime ───────────────────────
opt_cannon_visible = False
opt_cannon_scale   = 0.0
opt_cannon_recoil  = 0.0
opt_cannon_glow    = 0.0

# ── EXPRESIONES — Plasma Pea ──────────────────────────────────
ojo_escala_izq   = 1.0
ojo_escala_der   = 1.0
ojo_offset_y_izq = 0.0
ojo_offset_y_der = 0.0
ojo_color        = (0.4, 0.9, 1.0)
ceja_rot_izq     = 0.0
ceja_rot_der     = 0.0
ceja_offset_y    = 0.0
boca_escala_y    = 1.0
boca_curva       = 0.0
boca_abierta     = False
expresion_actual = "normal"

# ── EXPRESIONES — Optimus Prime ───────────────────────────────
color_ojos     = (0.1, 0.8, 1.0)
ojo_izq_escala = 1.0

# ── ANIMACIONES (compartidas y específicas) ───────────────────
is_walking    = False
walking       = False    # alias usado por Pochacco/Pucca
is_jumping    = False
jump_time     = 0.0
is_shooting   = False
shoot_timer   = 0
is_victory    = False
victory_timer = 0
is_spinning   = False
spin_angle    = 0.0
spin_timer    = 0
is_greeting   = False
greet_timer   = 0
is_crouching  = False
plasma_visible = False
plasma_scale   = 0.0

# ── COLISIONES — 6 objetos ────────────────────────────────────
zombie_x         = 5.0
zombie_z         = 0.0
zombie_activo    = True
zombie_hit       = False
zombie_hit_timer = 0

caja_x         = -4.0
caja_z         = 3.0
caja_activa    = True
caja_hit       = False
caja_hit_timer = 0

valla_x         = 0.0
valla_z         = -5.0
valla_hit       = False
valla_hit_timer = 0

obb_activo    = True
obb_hit       = False
obb_hit_timer = 0

cristal_x         = 3.0
cristal_z         = -3.0
cristal_activo    = True
cristal_hit       = False
cristal_hit_timer = 0

collision_color_override = None
collision_flash_timer    = 0

# ── AUDIO ─────────────────────────────────────────────────────
sonido_activado = True
sounds = {}

# ── UI ────────────────────────────────────────────────────────
show_instructions = False
show_about        = False

# ── SOMBREADO ─────────────────────────────────────────────────
shade_mode = 'gouraud'

# ── BOUNDING VOLUMES DEBUG ────────────────────────────────────
show_bv = False

# ── ILUMINACIÓN DINÁMICA ──────────────────────────────────────
scene_light_pos   = (2.0, 8.0, 6.0, 1.0)
scene_light_color = (0.85, 0.85, 0.90, 1.0)

# ── VARIABLES IMPORTADAS (Dee, Kirby, Pochaco, Pucca) ──
animation_angle = 0.0
reaction_timer = 0.0
blink_timer = 0.0
breath_timer = 0.0
kirby_colors = [(1.0, 0.78, 0.87), (1.0, 0.50, 0.70), (0.60, 0.80, 1.0),
                (0.60, 1.0, 0.70), (1.0, 1.0, 0.60), (1.0, 0.70, 0.40), (0.55, 0.55, 0.55)]
dee_colors   = [(0.98, 0.55, 0.18), (1.0, 0.80, 0.30), (0.40, 0.70, 1.0),
                (0.60, 1.0, 0.60), (1.0, 0.40, 0.60), (0.80, 0.60, 1.0)]
current_color_idx = 0
color_flash_timer = 0
expression = "normal"
reaction_type = "normal"

# ── ATRIBUTOS PARA DEE / KIRBY / PUCCA / POCHACCO ─────────────────
current_scene = 1
arm_angle   = 0.0
foot_angle  = 0.0
body_scale  = 1.0
mouth_scale = 1.0
tail_angle  = 0.0
ojos_abiertos = True
particles        = []
weather_particles = []

spear_active        = False
bandana_active      = False
parasol_active      = False
is_chef_hat_active  = False
is_jester_hat_active= False
is_floating         = False
is_sleeping         = False
is_sucking          = False
reaction_duration = 0.0

# ── MULTIJUGADOR Y MINI-JUEGO ──────────────────────────────────
game_mode = "main_menu"  # "main_menu", "mode_select", "char_select_mp", "tetris", "rope_pull", "gameplay"
selected_mode = None  # "individual" o "multiplayer"
player1_selected = None  # ID del personaje jugador 1 (multijugador)
player2_selected = None  # ID del personaje jugador 2 (multijugador)

# ── MINIJUEGO TETRIS (Escenario 7) ───────────────────────────
TETRIS_COLORS = [
    ("RED",     (0.95, 0.15, 0.15)),
    ("YELLOW",  (0.95, 0.90, 0.10)),
    ("GREEN",   (0.15, 0.85, 0.20)),
    ("BLUE",    (0.15, 0.35, 0.95)),
    ("PURPLE",  (0.65, 0.10, 0.90)),
    ("BROWN",   (0.55, 0.27, 0.07)),
    ("PINK",    (0.95, 0.45, 0.75)),
]

# Jugador 1 — mitad izquierda
TETRIS_X_MIN = -10.0
TETRIS_X_MAX =   0.0
TETRIS_SPAWN_X = -5.0
TETRIS_SPAWN_Z =  0.0

# Jugador 2 — mitad derecha
TETRIS_P2_X_MIN =  0.0
TETRIS_P2_X_MAX = 10.0
TETRIS_P2_SPAWN_X = 5.0
TETRIS_P2_SPAWN_Z = 0.0

# Posición P2
p2_x = 5.0
p2_y = 0.0
p2_z = 0.0
p2_facing = 180.0
p2_key_left  = False
p2_key_right = False

# Color objetivo actual (índice en TETRIS_COLORS)
tetris_objetivo_idx   = 0
tetris_p2_objetivo_idx = 0

# Lista de cubos cayentes
tetris_cubos = []

# Puntuación P1
tetris_correctos = 0
# Puntuación P2
tetris_p2_correctos = 0

# Timer de reacción visual
tetris_reaccion_timer = 0
tetris_reaccion_tipo  = ""
tetris_p2_reaccion_timer = 0
tetris_p2_reaccion_tipo  = ""

# Intervalo de spawn
tetris_spawn_timer  = 0
tetris_spawn_intervalo = 60

# ¿El minijuego terminó?
tetris_ganado = False
tetris_ganado_timer = 0
tetris_activo = False
tetris_winner = 0  # 0=nadie, 1=P1, 2=P2

# ¿Modo 2 jugadores en tetris?
tetris_2p = False
tetris_show_instructions = False
