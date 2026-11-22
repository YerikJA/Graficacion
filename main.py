import math, random, copy
from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *

from Characters import plasma_pea
from Characters import optimusPrime
from Characters import Dee
from Characters import Kirby
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "kirby", "Kirby_3D"))
from Characters import Pochacco3D
from Characters import Pucca3D
from Actions    import camera, state, audio, update
from Actions.audio import (play_maze_music, stop_maze_music, stop_bg_music,
                           toggle_maze_music, is_maze_music_on,
                           play_english_word)
from Actions    import rope_pull_game
from Resources  import input_handlers
from Resources.scenarios  import draw_scenario
from Resources.grid       import draw_grid
from Resources.collisions import check_all_collisions, draw_bounding_volumes
from Resources.vocabulary import get_random_word
from Resources.maze import (draw_maze_scenario, draw_maze_fp_camera,
                             check_maze_collision, get_start_pos, get_goal_pos,
                             CELL, COLS as MAZE_COLS, ROWS as MAZE_ROWS, MAZE_MAP)


CHARS = [
    ("pucca",   "PUCCA",        "Ciudad China",  (1.00, 0.18, 0.35),   1),
    ("pochaco", "POCHACCO",     "Pradera",       (0.85, 0.85, 0.85),   2),
    ("kirby",   "KIRBY",        "Dream Land",    (1.00, 0.55, 0.78),   3),
    ("dee",     "WADDLE DEE",   "Castillo",      (0.98, 0.55, 0.18),   4),
    ("optimus", "OPTIMUS",      "Base Militar",  (0.35, 0.65, 1.00),   5),
    ("plasma",  "CANON",        "Jardin",        (0.70, 0.20, 0.90),   6),
]

# Estado del hover (-1 = ninguna card)
_hover_index = -1

# Estado del menu:
#   "browse"   -> navegando, ninguno confirmado
#   "greeting" -> Enter presionado, personaje saluda, gestos habilitados
_menu_state = "browse"

# ── ESTADOS DEL SISTEMA ──────────────────────────────────────────────
# Estados posibles: "endgame_menu", "char_select_mp", "char_select_1p",
#                   "laberinto_mode", "char_select_maze", "char_select_maze_mp",
#                   "rope_pull", "maze_game", "maze_end", "gameplay", "info_screen"
_current_screen = "endgame_menu"  # Pantalla actual del flujo del juego

# ── MENÚ PRINCIPAL END GAME ───────────────────────────────────────────
_ENDGAME_BUTTONS = [
    {"label": "NIVEL 1",   "sub": "Tetris"},
    {"label": "NIVEL 2",   "sub": "Laberinto"},
    {"label": "NIVEL 3",   "sub": "Juego de la Cuerda"},
    {"label": "Jugar Secuencialmente", "sub": ""},
    {"label": "Informacion", "sub": ""},
]
_endgame_hover = 0

# ── SUBMENU LABERINTO ─────────────────────────────────────────────────
_LAB_BUTTONS = [
    {"text": "JUGAR",         "mode": "single"},
    {"text": "MULTIJUGADOR",  "mode": "multi"},
]
_lab_hover = 0

# ── MODO DEL JUEGO ACTUAL ─────────────────────────────────────────────
# "tetris_1p", "tetris_2p", "maze_sp", "maze_mp", "rope_pull", "sequential"
_game_flow = "tetris_2p"

# ── SELECCION MULTIJUGADOR ─────────────────────────────────────────────
_mode_hover = 0  # kept for compatibility
_mp_char_1 = None  # Personaje seleccionado jugador 1
_mp_char_2 = None  # Personaje seleccionado jugador 2
_mp_selecting_player = 1  # 1 o 2
_maze_mp_char1_selected = None  # para flujo laberinto mp

# ── ESTADO DEL LABERINTO ──────────────────────────────────────────────
_maze_player_x   = 0.0
_maze_player_z   = 0.0
_maze_facing     = 0.0
_maze_keys       = {'up': False, 'down': False, 'left': False, 'right': False}
_maze_speed      = 0.18
_maze_mp_mode    = True   # siempre MP al llegar del Rope Pull
_maze_char_id    = "pucca"
_maze_char_id2   = "pochaco"
_maze_player2_x  = 0.0
_maze_player2_z  = 0.0
_maze_player2_facing = 0.0
_maze_keys2      = {'up': False, 'down': False, 'left': False, 'right': False}
_maze_items2     = []
_maze_active_question2 = None
_maze_input_text2 = ""
_maze_feedback2  = ""
_maze_feedback_timer2 = 0
_maze_selected_opt  = 0
_maze_selected_opt2 = 0
_MAZE_TIME_LIMIT = 180
_maze_time_start = 0.0
_maze_time_left  = _MAZE_TIME_LIMIT
_maze_questions = [
    {"q": "Como se dice AZUL en ingles?",      "a": 0, "opts": ["blue",   "black",  "brown",  "bold"],   "hint": "Es un color del cielo"},
    {"q": "Como se dice ROJO en ingles?",       "a": 1, "opts": ["rose",   "red",    "rack",   "road"],   "hint": "Color del fuego"},
    {"q": "Como se dice VERDE en ingles?",      "a": 2, "opts": ["grass",  "grove",  "green",  "great"],  "hint": "Color de las plantas"},
    {"q": "Como se dice AGUA en ingles?",       "a": 0, "opts": ["water",  "wafer",  "waver",  "wader"],  "hint": "Lo que bebemos"},
    {"q": "Como se dice CASA en ingles?",       "a": 1, "opts": ["hose",   "house",  "horse",  "hour"],   "hint": "Donde vivimos"},
    {"q": "Como se dice GATO en ingles?",       "a": 3, "opts": ["bat",    "rat",    "mat",    "cat"],    "hint": "Animal domestico que maulla"},
    {"q": "Como se dice PERRO en ingles?",      "a": 2, "opts": ["dig",    "dug",    "dog",    "dot"],    "hint": "El mejor amigo del hombre"},
    {"q": "Como se dice LIBRO en ingles?",      "a": 0, "opts": ["book",   "back",   "bock",   "buck"],   "hint": "Tiene paginas y letras"},
    {"q": "Como se dice SOL en ingles?",        "a": 1, "opts": ["son",    "sun",    "gun",    "run"],    "hint": "Estrella de nuestro sistema solar"},
    {"q": "Como se dice LUNA en ingles?",       "a": 3, "opts": ["mono",   "mane",   "mine",   "moon"],   "hint": "Satelite natural de la Tierra"},
    {"q": "Como se dice MANZANA en ingles?",    "a": 2, "opts": ["grape",  "melon",  "apple",  "peach"],  "hint": "Fruta roja o verde"},
    {"q": "Como se dice ESCUELA en ingles?",    "a": 0, "opts": ["school", "store",  "stool",  "scout"],  "hint": "Donde aprendemos"},
    {"q": "Como se dice AMIGO en ingles?",      "a": 1, "opts": ["fiend",  "friend", "freed",  "frond"],  "hint": "Persona de confianza"},
    {"q": "Como se dice TIEMPO en ingles?",     "a": 3, "opts": ["tame",   "tome",   "team",   "time"],   "hint": "El que pasa"},
    {"q": "Como se dice ARBOL en ingles?",      "a": 0, "opts": ["tree",   "trek",   "trey",   "tread"],  "hint": "Tiene hojas y ramas"},
    {"q": "Como se dice PELOTA en ingles?",     "a": 2, "opts": ["bell",   "bill",   "ball",   "bull"],   "hint": "Es redonda y se lanza"},
    {"q": "Como se dice FLOR en ingles?",       "a": 1, "opts": ["flour",  "flower", "floor",  "flair"],  "hint": "Las abejas la visitan"},
    {"q": "Como se dice NOCHE en ingles?",      "a": 3, "opts": ["knife",  "nice",   "might",  "night"],  "hint": "Cuando aparecen las estrellas"},
]
_MAZE_ITEM_CELLS = [
    (3, 8), (7, 4), (10, 11), (13, 3), (15, 10), (17, 1),
    (5, 5), (9, 3), (11, 7), (1, 3), (3, 12), (7, 10),
    (5, 11), (13, 9), (16, 6), (9, 9), (11, 1), (7, 6),
]
_maze_items = []
_maze_active_question = None
_maze_input_text = ""
_maze_feedback = ""
_maze_feedback_timer = 0
_maze_initialized = False

# ── PANEL DE INFORMACIÓN EN JUEGO ─────────────────────────────────────
_show_level_info_p1 = False   # Panel info J1 (maze_mp / single / gameplay)
_show_level_info_p2 = False   # Panel info J2 (maze_mp)

# Dimensiones de las cards
CARD_W = 208
CARD_H = 152
GAP_X  = 16
GAP_Y  = 16
COLS   = 3

# Escala del modelo dentro del cubiculo
_CHAR_SCALE = {
    "pucca":   0.95,
    "pochaco": 0.85,
    "kirby":   0.90,
    "dee":     0.90,
    "optimus": 0.65,
    "plasma":  0.85,
}

# Offset Y del modelo dentro del cubiculo
_CHAR_Y_OFF = {
    "pucca":   -0.55,
    "pochaco": -0.40,
    "kirby":   -0.50,
    "dee":     -0.50,
    "optimus": -1.00,
    "plasma":  -0.55,
}

# Colores acento por personaje
_ACCENT_COLORS = {
    "pucca":   (1.0,  0.4,  0.5),
    "pochaco": (0.9,  0.9,  1.0),
    "kirby":   (1.0,  0.7,  0.9),
    "dee":     (1.0,  0.75, 0.4),
    "optimus": (0.5,  0.8,  1.0),
    "plasma":  (0.85, 0.5,  1.0),
}




# ──────────────────────────────────────────────────────────────────────
# Panel de información en juego
# ──────────────────────────────────────────────────────────────────────
_LEVEL_INFO = {
    "tetris": {
        "title": "TETRIS ESPACIAL",
        "desc": [
            "Caen cubos de colores.",
            "Atrapa los del color que dice tu panel.",
            "El primero en 10 correctos gana.",
            "",
            "J1: A/D para moverse",
            "J2: Flechas IZQ/DER",
        ],
    },
    "maze": {
        "title": "LABERINTO MULTIJUGADOR",
        "desc": [
            "Camina por el laberinto en 1ra persona.",
            "Toca los objetos brillantes y",
            "responde la pregunta de inglés.",
            "Llega al octaedro DORADO para ganar.",
            "",
            "J1: W/A/S/D  |  Respuestas: 1/2/3/4",
            "J2: Flechas   |  Respuestas: 5/6/7/8",
            "ENTER: confirmar  |  I/P: info",
        ],
    },
    "maze_sp": {
        "title": "LABERINTO",
        "desc": [
            "Camina por el laberinto en 1ra persona.",
            "Toca los objetos brillantes y",
            "responde la pregunta de inglés.",
            "Llega al octaedro DORADO para ganar.",
            "",
            "W/S: Avanzar / Retroceder",
            "A/D: Girar",
            "I: Info  |  M: Música ON/OFF",
        ],
    },
    "rope": {
        "title": "TIRA DE LA CUERDA",
        "desc": [
            "Aparece una palabra mal escrita en inglés.",
            "Escríbela BIEN y presiona ENTER.",
            "Tienes 10 segundos por turno.",
            "",
            "Aciertas = rival pierde 1 vida.",
            "Fallas = tú pierdes 1 vida.",
            "Gana quien deje al otro sin vidas.",
        ],
    },
    "sequential": {
        "title": "MODO SECUENCIAL",
        "desc": [
            "Juega los 3 niveles en orden:",
            "  1. Tetris",
            "  2. Tira de la Cuerda",
            "  3. Laberinto",
            "",
            "Elige 2 personajes y compite.",
            "I (J1) o P (J2): ver info del nivel.",
        ],
    },
}


def _draw_level_info_panel(W, H, player=1, offset_x=0, game_type="maze"):
    """Dibuja panel de información del nivel actual para el jugador indicado."""
    info = _LEVEL_INFO.get(game_type, _LEVEL_INFO["maze"])
    full_W = glutGet(GLUT_WINDOW_WIDTH)
    full_H = glutGet(GLUT_WINDOW_HEIGHT)
    _enter_2d(full_W, full_H)

    pw = min(480, W - 20)
    ph = 340
    cx = offset_x + W // 2
    cy = full_H // 2
    px = cx - pw // 2
    py = cy - ph // 2

    border_col = (0.30, 1.00, 0.30) if player == 1 else (0.30, 0.60, 1.00)
    _rect_filled(px, py, pw, ph, 0.02, 0.02, 0.08, 0.95)
    _rect_border(px, py, pw, ph, *border_col, 3.0)

    title = f"[ J{player}: {info['title']} ]"
    tw = _str_width_18(title)
    _text18(cx - tw // 2, py + ph - 32, title, border_col)

    glColor3f(*border_col)
    glBegin(GL_LINES)
    glVertex2f(px + 16, py + ph - 46)
    glVertex2f(px + pw - 16, py + ph - 46)
    glEnd()

    iy = py + ph - 68
    for line in info["desc"]:
        col = (1.0, 0.85, 0.25) if line.startswith("CONTROLES") else (0.85, 0.90, 1.0)
        lw = _str_width_12(line)
        _text(cx - lw // 2, iy, line, col)
        iy -= 20

    close_hint = "I - cerrar" if player == 1 else "P - cerrar"
    hw = _str_width_12(close_hint)
    _text(cx - hw // 2, py + 14, close_hint, (0.55, 0.60, 0.55))
    _exit_2d()

def _draw_endgame_menu():

    global _endgame_hover
    W = glutGet(GLUT_WINDOW_WIDTH)
    H = glutGet(GLUT_WINDOW_HEIGHT)
    t = glutGet(GLUT_ELAPSED_TIME) / 1000.0

    _enter_2d(W, H)

    # Fondo degradado azul oscuro
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBegin(GL_QUADS)
    glColor4f(0.02, 0.02, 0.12, 1.0); glVertex2f(0, 0);   glVertex2f(W, 0)
    glColor4f(0.06, 0.04, 0.20, 1.0); glVertex2f(W, H);   glVertex2f(0, H)
    glEnd()
    glDisable(GL_BLEND)

    GOLD   = (1.00, 0.85, 0.25)
    WHITE  = (1.00, 1.00, 1.00)
    GRAY   = (0.52, 0.52, 0.62)
    cx = W // 2

    # ── Título grande "END GAME" ──────────────────────────────────────
    pulse = (math.sin(t * 1.5) + 1.0) / 2.0
    title_color = (
        GOLD[0],
        GOLD[1] * (0.80 + pulse * 0.20),
        GOLD[2] * (0.10 + pulse * 0.15),
    )
    title = "END GAME"
    # Dibujar varias veces con offsets para simular texto grande
    for dy in range(4):
        _text18(cx - _str_width_18(title)//2 + 1, H - 60 - dy, title, title_color)
    _text18(cx - _str_width_18(title)//2, H - 60, title, title_color)

    sub_title = "Instituto Tecnologico de Toluca  -  Graficación"
    sw = _str_width_12(sub_title)
    _text(cx - sw // 2, H - 88, sub_title, GRAY)

    glColor3f(0.28, 0.28, 0.50)
    glBegin(GL_LINES)
    glVertex2f(cx - 300, H - 100); glVertex2f(cx + 300, H - 100)
    glEnd()

    # ── Botones ───────────────────────────────────────────────────────
    BTN_W   = 400
    BTN_H   = 70
    BTN_GAP = 14
    n_btns  = len(_ENDGAME_BUTTONS)
    total_h = n_btns * BTN_H + (n_btns - 1) * BTN_GAP
    start_y = (H - 100 + total_h) // 2 - 10

    for i, btn in enumerate(_ENDGAME_BUTTONS):
        bx = cx - BTN_W // 2
        by = start_y - i * (BTN_H + BTN_GAP)
        hov = (i == _endgame_hover)

        # Colores por nivel
        accent_colors = [
            (0.20, 0.55, 1.00),  # Azul - Tetris
            (0.20, 0.80, 0.30),  # Verde - Laberinto
            (1.00, 0.40, 0.15),  # Naranja - Cuerda
            (0.85, 0.20, 0.85),  # Magenta - Secuencial
            (0.60, 0.60, 0.70),  # Gris - Info
        ]
        ar, ag, ab = accent_colors[i]

        if hov:
            pulse2 = (math.sin(t * 4.0) + 1.0) / 2.0
            _rect_filled(bx, by, BTN_W, BTN_H,
                         ar * 0.28, ag * 0.28, ab * 0.28, 0.80)
            _rect_border(bx, by, BTN_W, BTN_H, ar, ag, ab, 3.0)
            _rect_border(bx - 2, by - 2, BTN_W + 4, BTN_H + 4,
                         ar * 0.5 * pulse2, ag * 0.5 * pulse2, ab * 0.5 * pulse2, 1.2)
            label_color = (1.0, 1.0, 1.0)
            sub_color   = (ar * 0.9 + 0.1, ag * 0.9 + 0.1, ab * 0.9 + 0.1)
        else:
            _rect_filled(bx, by, BTN_W, BTN_H,
                         ar * 0.06, ag * 0.06, ab * 0.06, 0.65)
            _rect_border(bx, by, BTN_W, BTN_H, ar * 0.5, ag * 0.5, ab * 0.5, 1.8)
            label_color = (ar * 0.85 + 0.15, ag * 0.85 + 0.15, ab * 0.85 + 0.15)
            sub_color   = GRAY

        # Texto principal del botón
        if btn["sub"]:
            # Etiqueta arriba centrada
            lw = _str_width_18(btn["label"])
            _text18(bx + BTN_W // 2 - lw // 2, by + BTN_H // 2 + 6, btn["label"], label_color)
            # Sub-etiqueta abajo
            sw2 = _str_width_12(btn["sub"])
            _text(bx + BTN_W // 2 - sw2 // 2, by + BTN_H // 2 - 14, btn["sub"], sub_color)
        else:
            lw = _str_width_18(btn["label"])
            _text18(bx + BTN_W // 2 - lw // 2, by + BTN_H // 2 - 8, btn["label"], label_color)

    # ── Instrucciones ─────────────────────────────────────────────────
    instr = "Flechas / CLICK para seleccionar  |  ENTER para confirmar  |  I/P: info en juego"
    iw = _str_width_12(instr)
    _text(cx - iw // 2, 22, instr, GRAY)

    _exit_2d()


def _draw_laberinto_mode_screen():
    """Submenu: Laberinto -> Jugar (1P) o Multijugador."""
    global _lab_hover
    W = glutGet(GLUT_WINDOW_WIDTH)
    H = glutGet(GLUT_WINDOW_HEIGHT)
    t = glutGet(GLUT_ELAPSED_TIME) / 1000.0

    _enter_2d(W, H)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBegin(GL_QUADS)
    glColor4f(0.02, 0.08, 0.04, 0.95)
    glVertex2f(0, 0); glVertex2f(W, 0)
    glVertex2f(W, H); glVertex2f(0, H)
    glEnd()
    glDisable(GL_BLEND)

    GOLD  = (1.00, 0.85, 0.25)
    GREEN = (0.30, 0.90, 0.30)
    GRAY  = (0.52, 0.52, 0.62)
    cx    = W // 2

    title = "* LABERINTO *"
    tw = _str_width_18(title)
    _text18(cx - tw // 2, H - 80, title, GOLD)

    sub = "Pon a prueba tu ingles mientras navegas el laberinto"
    sw = _str_width_12(sub)
    _text(cx - sw // 2, H - 110, sub, GRAY)

    btn_y_start = H // 2 + 50
    for i, btn in enumerate(_LAB_BUTTONS):
        y = btn_y_start - i * 120
        bx = cx - 180
        bw, bh = 360, 80
        hov = (i == _lab_hover)

        if hov:
            pulse = (math.sin(t * 4) + 1) / 2
            _rect_filled(bx, y, bw, bh, 0.10, 0.45 + pulse * 0.15, 0.10, 0.70)
            _rect_border(bx, y, bw, bh, 0.30, 1.00, 0.30, 3.0)
            tc = GREEN
        else:
            _rect_filled(bx, y, bw, bh, 0.04, 0.12, 0.04, 0.60)
            _rect_border(bx, y, bw, bh, 0.25, 0.55, 0.25, 2.0)
            tc = GRAY

        tw2 = _str_width_18(btn["text"])
        _text18(bx + bw // 2 - tw2 // 2, y + bh // 2 - 8, btn["text"], tc)

    hint = "CLICK / ENTER para seleccionar  |  ESC volver"
    hw = _str_width_12(hint)
    _text(cx - hw // 2, 30, hint, GRAY)
    _exit_2d()


def _draw_info_screen():
    """Pantalla de informacion de los desarrolladores."""
    W = glutGet(GLUT_WINDOW_WIDTH)
    H = glutGet(GLUT_WINDOW_HEIGHT)
    t = glutGet(GLUT_ELAPSED_TIME) / 1000.0

    _enter_2d(W, H)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBegin(GL_QUADS)
    glColor4f(0.04, 0.02, 0.10, 0.97)
    glVertex2f(0, 0); glVertex2f(W, 0)
    glVertex2f(W, H); glVertex2f(0, H)
    glEnd()
    glDisable(GL_BLEND)

    GOLD  = (1.00, 0.85, 0.25)
    CYAN  = (0.40, 0.90, 1.00)
    WHITE = (0.95, 0.95, 1.00)
    GRAY  = (0.52, 0.52, 0.62)
    cx    = W // 2

    pulse = (math.sin(t * 1.8) + 1.0) / 2.0
    tc = (GOLD[0], GOLD[1] * (0.80 + pulse * 0.20), GOLD[2] * 0.15)

    title = "INFORMACION"
    tw = _str_width_18(title)
    _text18(cx - tw // 2, H - 60, title, tc)

    glColor3f(0.30, 0.28, 0.55)
    glBegin(GL_LINES)
    glVertex2f(cx - 280, H - 78); glVertex2f(cx + 280, H - 78)
    glEnd()

    lines = [
        ("Instituto Tecnologico de Toluca", CYAN, True),
        ("Materia: Graficacion", WHITE, True),
        ("", GRAY, False),
        ("Desarrolladores:", GOLD, True),
        ("Valeria Esperanza Albino Hernandez", WHITE, False),
        ("Ian Axel Rojas Juarez", WHITE, False),
        ("Yerik Jardon Albarran", WHITE, False),
    ]

    line_h = 38
    total_lines_h = len(lines) * line_h
    start_ly = H // 2 + total_lines_h // 2 - 10

    for idx, (text, color, bold) in enumerate(lines):
        if not text:
            continue
        ly = start_ly - idx * line_h
        if bold:
            tw2 = _str_width_18(text)
            _text18(cx - tw2 // 2, ly, text, color)
        else:
            tw2 = _str_width_12(text)
            _text(cx - tw2 // 2, ly, text, color)

    hint = "ESC o CLICK para volver"
    hw = _str_width_12(hint)
    _text(cx - hw // 2, 25, hint, GRAY)

    _exit_2d()


def _draw_multiplayer_char_selection():
    """Pantalla de selección de personajes para todos los flujos"""
    global _mp_char_1, _mp_char_2, _mp_selecting_player, _hover_index, _game_flow
    
    W = glutGet(GLUT_WINDOW_WIDTH)
    H = glutGet(GLUT_WINDOW_HEIGHT)
    
    char_id = CHARS[state.menu_cursor_index][0]
    is_greeting_mode = (_menu_state == "greeting")
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, W / max(H, 1), 0.1, 120.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    total_w   = COLS * CARD_W + (COLS - 1) * GAP_X
    grid_x0   = (W - total_w) // 2
    top_row_y = H - 100 - CARD_H
    
    for i, (cid, name, subtitle, accent, _esc) in enumerate(CHARS):
        row = i // COLS
        col = i % COLS
        cx_card = grid_x0 + col * (CARD_W + GAP_X)
        cy_card = top_row_y - row * (CARD_H + GAP_Y)
        
        selected = (i == state.menu_cursor_index)
        hovered  = (i == _hover_index and not selected)
        
        if is_greeting_mode and selected:
            bright = 0.45
        elif selected:
            bright = 1.0
        elif hovered:
            bright = 0.50
        else:
            bright = 0.0
        
        _draw_char_in_card(cid, cx_card, cy_card, bright, W, H)
    
    _enter_2d(W, H)
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBegin(GL_QUADS)
    glColor4f(0.04, 0.04, 0.14, 0.80); glVertex2f(0, 0); glVertex2f(W, 0)
    glColor4f(0.06, 0.06, 0.22, 0.80); glVertex2f(W, H); glVertex2f(0, H)
    glEnd()
    glDisable(GL_BLEND)
    
    GOLD = (1.00, 0.85, 0.25)
    GRAY = (0.52, 0.52, 0.62)
    cx = W // 2

    # Título dinámico según el flujo
    flow_titles = {
        "tetris_2p":   "* NIVEL 1 - TETRIS: Elige 2 Personajes *",
        "rope_only":   "* NIVEL 3 - CUERDA: Elige 2 Personajes *",
        "sequential":  "* JUGAR SECUENCIALMENTE: Elige 2 Personajes *",
        "maze_mp":     "* LABERINTO MULTIJUGADOR: Elige 2 Personajes *",
        "maze_sp":     "* LABERINTO: Elige tu Personaje *",
    }
    title = flow_titles.get(_game_flow, "* SELECCIONA 2 PERSONAJES *")
    tw = _str_width_18(title)
    _text18(cx - tw // 2, H - 52, title, GOLD)
    
    if _game_flow == "maze_sp":
        if is_greeting_mode:
            sub = 'ENTER: Confirmar seleccion  ESC: Cancelar'
        else:
            sub = 'Elige tu personaje  -  ENTER / CLICK para seleccionar'
    else:
        if is_greeting_mode:
            sub = 'ENTER: Confirmar P' + str(_mp_selecting_player) + '  ESC: Cancelar'
        else:
            sub = 'Jugador ' + str(_mp_selecting_player) + ': Elige tu personaje  -  ENTER / CLICK para seleccionar'
    sw = _str_width_12(sub)
    _text(cx - sw // 2, H - 74, sub, GRAY)
    
    glColor3f(0.22, 0.22, 0.38)
    glBegin(GL_LINES)
    glVertex2f(cx - 260, H - 86)
    glVertex2f(cx + 260, H - 86)
    glEnd()
    
    for i, (cid, name, subtitle, accent, _esc) in enumerate(CHARS):
        row = i // COLS
        col = i % COLS
        cx_card = grid_x0 + col * (CARD_W + GAP_X)
        cy_card = top_row_y - row * (CARD_H + GAP_Y)
        
        selected = (i == state.menu_cursor_index)
        hovered  = (i == _hover_index and not selected)
        ar, ag, ab = accent
        
        if is_greeting_mode and selected:
            _rect_filled(cx_card, cy_card, CARD_W, CARD_H,
                         ar*0.08, ag*0.08, ab*0.08, 0.40)
        elif selected:
            _rect_filled(cx_card, cy_card, CARD_W, CARD_H,
                         ar*0.18, ag*0.18, ab*0.18, 0.50)
        elif hovered:
            _rect_filled(cx_card, cy_card, CARD_W, CARD_H,
                         ar*0.10, ag*0.10, ab*0.10, 0.48)
        else:
            _rect_filled(cx_card, cy_card, CARD_W, CARD_H,
                         0.03, 0.04, 0.10, 0.65)
        
        t = glutGet(GLUT_ELAPSED_TIME) / 1000.0
        if is_greeting_mode and selected:
            pulse = (math.sin(t * 4.0) + 1.0) / 2.0
            lw = 3.0
            br, bg_, bb = 1.0, 0.85*(0.7+pulse*0.3), 0.10*pulse
            _rect_border(cx_card, cy_card, CARD_W, CARD_H, br, bg_, bb, lw)
            _rect_border(cx_card-3, cy_card-3, CARD_W+6, CARD_H+6,
                         br*0.45, bg_*0.45, 0.0, 1.2)
        elif selected:
            lw = 2.8; br, bg_, bb = ar, ag, ab
            _rect_border(cx_card, cy_card, CARD_W, CARD_H, br, bg_, bb, lw)
            _rect_border(cx_card-2, cy_card-2, CARD_W+4, CARD_H+4,
                         ar*0.45, ag*0.45, ab*0.45, 1.2)
        elif hovered:
            lw = 2.0; br, bg_, bb = ar*0.80, ag*0.80, ab*0.80
            _rect_border(cx_card, cy_card, CARD_W, CARD_H, br, bg_, bb, lw)
            _rect_border(cx_card-1, cy_card-1, CARD_W+2, CARD_H+2,
                         ar*0.30, ag*0.30, ab*0.30, 1.0)
        else:
            lw = 1.2; br, bg_, bb = ar*0.30, ag*0.30, ab*0.30
            _rect_border(cx_card, cy_card, CARD_W, CARD_H, br, bg_, bb, lw)
        
        if is_greeting_mode and selected:
            nc = (1.0, 1.0, 0.30)
        elif selected:
            nc = (1.0, 1.0, 0.55)
        else:
            nc = (ar*0.85, ag*0.85, ab*0.85)
        
        nw = _str_width_18(name)
        _text18(cx_card + (CARD_W - nw)//2, cy_card + CARD_H - 36, name, nc)
        
        lx = cx_card + 18
        glColor3f(ar*0.50, ag*0.50, ab*0.50)
        glBegin(GL_LINES)
        glVertex2f(lx, cy_card + CARD_H - 48)
        glVertex2f(lx + CARD_W - 36, cy_card + CARD_H - 48)
        glEnd()
        
        PAD_X   = 10
        BADGE_H = 18
        TEXT_Y  = cy_card + CARD_H - 68
        BORD_Y  = TEXT_Y - 8
        
        sw2     = _str_width_12(subtitle)
        badge_w = sw2 + PAD_X * 2
        badge_x = cx_card + (CARD_W - badge_w) // 2
        text_bx = badge_x + PAD_X
        
        _text(text_bx, TEXT_Y, subtitle, (0.70, 0.70, 0.76))
        _rect_border(badge_x, BORD_Y, badge_w, BADGE_H,
                     ar*0.45, ag*0.45, ab*0.45, 1.0)
        
        _text(cx_card + CARD_W - 18, cy_card + 8,
              str(i+1), (0.32, 0.32, 0.42))
    
    status_text = ""
    if _mp_char_1:
        status_text += f"Jugador 1: {CHARS[[c[0] for c in CHARS].index(_mp_char_1)][1]}"
    if _mp_char_2:
        status_text += f"  |  Jugador 2: {CHARS[[c[0] for c in CHARS].index(_mp_char_2)][1]}"
    
    if status_text:
        status_w = _str_width_12(status_text)
        _text(cx - status_w // 2, 50, status_text, (0.7, 1.0, 0.7))

    # ---- Panel de prueba de personaje (modo greeting) ---
    if is_greeting_mode:
        cid, cname, _, accent, _ = CHARS[state.menu_cursor_index]
        ar, ag, ab = accent

        t2     = glutGet(GLUT_ELAPSED_TIME) / 1000.0
        pulse2 = (math.sin(t2 * 2.5) + 1.0) / 2.0

        # Nombre del personaje centrado arriba
        lbl = f"== {cname} =="
        lw2 = _str_width_18(lbl)
        _text18(cx - lw2 // 2, H - 82, lbl, (ar, ag, ab))

        # --- Panel de instrucciones (estilo imagen) --- derecha
        pp_w = 220
        pp_h = 115
        pp_x = W - pp_w - 8
        pp_y = H // 2 - 90
        _rect_filled(pp_x, pp_y, pp_w, pp_h, 0.0, 0.0, 0.0, 0.72)
        _rect_border(pp_x, pp_y, pp_w, pp_h, ar, ag, ab, 1.8)
        instr_lines = [
            "CONTROLES:",
            "  X  Saltar",
            "  B  Saludar",
            "  G  Girar cabeza",
        ]
        iy = pp_y + pp_h - 20
        for line in instr_lines:
            _text(pp_x + 12, iy, line, (0.80, 0.85, 0.95))
            iy -= 20

        # ENTER para confirmar (pulsante)
        confirm_color = (0.3 + pulse2*0.7, 0.85, 0.3 + pulse2*0.2)
        enter_lbl = ">> ENTER para confirmar <<"
        ew = _str_width_12(enter_lbl)
        _text(cx - ew // 2, H - 108, enter_lbl, confirm_color)

        # ESC para cancelar
        esc_lbl = "ESC: cancelar y volver a elegir"
        _text(cx - _str_width_12(esc_lbl)//2, H - 124, esc_lbl, (0.80, 0.45, 0.45))

    _exit_2d()

    # Restaurar proyeccion global
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, W / max(H, 1), 0.1, 120.0)
    glMatrixMode(GL_MODELVIEW)

    # Dibujar el personaje grande AL FINAL para que tape todo lo de atras
    if is_greeting_mode:
        _draw_selected_char_large(char_id, W, H)


def _draw_rope_pull_game():
    """Dibuja el mini-juego Tira de la Cuerda en 3D"""
    global rope_pull_game
    
    W = glutGet(GLUT_WINDOW_WIDTH)
    H = glutGet(GLUT_WINDOW_HEIGHT)
    
    game = rope_pull_game.game_instance
    
    # Configurar viewport 3D
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(50.0, W / max(H, 1), 0.1, 200.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    glClearColor(0.1, 0.15, 0.25, 1.0)
    
    # Cámara general (más zoom out) — pequeño zoom al jalar cuerda (suavizado)
    base_z = 20.0
    # Reducir la influencia del 'rope_shake' para que el zoom sea más suave
    eye_z = base_z + game.rope_shake * 3.0
    gluLookAt(0, 6, eye_z,   0, 2, 0,   0, 1, 0)
    
    # Iluminación adaptada al ciclo día/atardecer/noche
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

    # Determinar fase de ciclo
    t_cycle = game.game_time
    if t_cycle < 30:
        # Día: luz fuerte blanca, alta luminosidad
        ambient = (0.65, 0.65, 0.70)
        diffuse = (0.90, 0.90, 0.95)
    elif t_cycle < 60:
        # Atardecer: luz tibia naranja/dorada
        progress = (t_cycle - 30) / 30.0
        ambient_r = 0.65 - progress * 0.15
        ambient_g = 0.65 - progress * 0.25
        ambient_b = 0.70 - progress * 0.25
        diffuse_r = 0.90 - progress * 0.30
        diffuse_g = 0.90 - progress * 0.35
        diffuse_b = 0.95 - progress * 0.50
        ambient = (max(0.3, ambient_r), max(0.3, ambient_g), max(0.3, ambient_b))
        diffuse = (max(0.5, diffuse_r), max(0.5, diffuse_g), max(0.3, diffuse_b))
    else:
        # Noche: luz tenue azul (luna)
        ambient = (0.20, 0.25, 0.35)
        diffuse = (0.35, 0.40, 0.55)

    glLight(GL_LIGHT0, GL_POSITION,  (15.0, 12.0, 15.0, 1.0))
    glLight(GL_LIGHT0, GL_AMBIENT,   (*ambient, 1.0))
    glLight(GL_LIGHT0, GL_DIFFUSE,   (*diffuse, 1.0))
    
    # Dibujar terreno (cliff/acantilado)
    _draw_rope_pull_environment(game)
    
    # Dibujar personajes en posiciones de tira de cuerda
    _draw_rope_pull_characters(game)
    
    # Dibujar cuerda
    _draw_rope(game)
    
    # UI 2D superpuesta
    _enter_2d(W, H)
    _draw_rope_pull_hud(game, W, H)
    _exit_2d()


def _draw_rope_pull_environment(game):
    """Dibuja el escenario del juego tira de cuerda (acantilado, etc)"""
    glDisable(GL_LIGHTING)

    # Ciclo día/atardecer/noche basado en game.game_time
    # 0-30s: día (cielo azul), 30-60s: atardecer (naranja/morado), 60+: noche (negro/azul oscuro)
    t_cycle = game.game_time
    if t_cycle < 30:
        # Día: cielo azul claro
        sky_top_r, sky_top_g, sky_top_b = 0.45, 0.68, 0.95
        sky_bot_r, sky_bot_g, sky_bot_b = 0.90, 0.85, 0.70
        sun_brightness = 1.0
    elif t_cycle < 60:
        # Atardecer: naranja/morado gradual
        progress = (t_cycle - 30) / 30.0  # 0..1
        sky_top_r = 0.45 + progress * (0.35 - 0.45)
        sky_top_g = 0.68 - progress * 0.30
        sky_top_b = 0.95 - progress * 0.70
        sky_bot_r = 0.90 + progress * 0.08
        sky_bot_g = 0.85 - progress * 0.32
        sky_bot_b = 0.70 - progress * 0.40
        sun_brightness = 0.7
    else:
        # Noche: negro/azul muy oscuro
        sky_top_r, sky_top_g, sky_top_b = 0.05, 0.08, 0.15
        sky_bot_r, sky_bot_g, sky_bot_b = 0.10, 0.12, 0.25
        sun_brightness = 0.3

    glBegin(GL_QUADS)
    glColor3f(sky_top_r, sky_top_g, sky_top_b); glVertex3f(-50, 30, -50)
    glColor3f(sky_top_r, sky_top_g, sky_top_b); glVertex3f(50, 30, -50)
    glColor3f(sky_bot_r, sky_bot_g, sky_bot_b); glVertex3f(50, -5, -50)
    glColor3f(sky_bot_r, sky_bot_g, sky_bot_b); glVertex3f(-50, -5, -50)
    glEnd()

    # Plataformas MÁS ALARGADAS (horizontales) para ver mejor el recorrido hacia el barranco
    # Izquierda va de x=-12 a x=-2 (muy alargada)
    # Derecha va de x=2 a x=12 (muy alargada)
    left_x0 = -12.0; left_x1 = -2.0
    right_x0 = 2.0; right_x1 = 12.0
    glColor3f(0.20, 0.60, 0.25)  # Verde más oscuro
    glBegin(GL_QUADS)
    glVertex3f(left_x0, 0, -8); glVertex3f(left_x1, 0, -8)
    glVertex3f(left_x1, 0, 12); glVertex3f(left_x0, 0, 12)
    glEnd()

    glBegin(GL_QUADS)
    glVertex3f(right_x0, 0, -8); glVertex3f(right_x1, 0, -8)
    glVertex3f(right_x1, 0, 12); glVertex3f(right_x0, 0, 12)
    glEnd()

    # Precipicio central (gap)
    glColor3f(0.06, 0.02, 0.12)
    glBegin(GL_QUADS)
    glVertex3f(left_x1, -8, -8); glVertex3f(right_x0, -8, -8)
    glVertex3f(right_x0, -8, 12); glVertex3f(left_x1, -8, 12)
    glEnd()

    # NO dibujar postes café visibles (ya no necesarios, se ve mejor sin ellos)

    # Nubes simples (spheres) con color de sunset
    q2 = gluNewQuadric()
    glColor3f(0.98, 0.75, 0.45 * sun_brightness)
    glPushMatrix(); glTranslatef(-10, 20, -30); gluSphere(q2, 4.5, 16, 12); glPopMatrix()
    glColor3f(0.95, 0.55, 0.30 * sun_brightness)
    glPushMatrix(); glTranslatef(12, 18, -28); gluSphere(q2, 3.8, 14, 10); glPopMatrix()
    gluDeleteQuadric(q2)

    glEnable(GL_LIGHTING)


def _draw_rope_pull_characters(game):
    """Dibuja los 2 personajes en posiciones de tira de cuerda"""
    glEnable(GL_LIGHTING)

    # Función auxiliar para aplicar expresión temporal
    def apply_expression(char_id, expr):
        """Aplica expresión al módulo del personaje para que se vea immediatamente."""
        if expr == "normal":
            return  # No hacer nada si es normal
        
        if char_id == "pucca":
            if expr == "happy":
                input_handlers._set_expression_alegria()
            elif expr == "sad":
                input_handlers._set_expression_tristeza()
        elif char_id == "pochaco":
            if expr == "happy":
                state.expression = "happy"
            elif expr == "sad":
                state.expression = "sad"
        elif char_id == "kirby":
            if expr == "happy":
                state.expression = "happy"
                state.reaction_type = "happy"
            elif expr == "sad":
                state.expression = "sad"
                state.reaction_type = "sad"
        elif char_id == "dee":
            if expr == "happy":
                state.expression = "happy"
                state.reaction_type = "happy"
            elif expr == "sad":
                state.expression = "sad"
                state.reaction_type = "sad"
        elif char_id == "pucca3d" or char_id == "pochacco3d":
            if expr == "happy":
                state.expression = "happy"
            elif expr == "sad":
                state.expression = "sad"
        # otras lógicas por personaje...

    # Personajes se desplazan HORIZONTALMENTE hacia el centro (borde del precipicio)
    # Plataformas: izq [-12 .. -2], der [2 .. 12]
    left_start = -11.0
    left_edge  = -2.0
    right_start = 11.0
    right_edge  = 2.0

    # Calcular progreso (0.0 = vida completa, 1.0 = sin vidas)
    prog1 = (10 - max(0, game.health_1)) / 10.0
    prog2 = (10 - max(0, game.health_2)) / 10.0

    char1_x = left_start + prog1 * (left_edge - left_start)
    char2_x = right_start + prog2 * (right_edge - right_start)

    # Caída vertical (cuando pierde todas las vidas)
    fall_offset1 = -6.0 * game.fall_progress if game.falling_player == 1 else 0.0
    fall_offset2 = -6.0 * game.fall_progress if game.falling_player == 2 else 0.0

    # Aplicar expresiones temporales
    if game.expression_timer > 0:
        apply_expression(game.char1_id, game.char1_expression)
        apply_expression(game.char2_id, game.char2_expression)

    # Dibujar jugador 1 (izquierda)
    glPushMatrix()
    glTranslatef(char1_x, 0.8 + fall_offset1, 2.0)
    glRotatef(18 - game.rope_shake * 18, 0, 1, 0)
    glScalef(0.88, 0.88, 0.88)
    if game.char1_id:
        _draw_char_model(game.char1_id)
    glPopMatrix()

    # Dibujar jugador 2 (derecha)
    glPushMatrix()
    glTranslatef(char2_x, 0.8 + fall_offset2, 2.0)
    glRotatef(-18 + game.rope_shake * 18, 0, 1, 0)
    glScalef(0.88, 0.88, 0.88)
    if game.char2_id:
        _draw_char_model(game.char2_id)
    glPopMatrix()


def _draw_rope(game):
    """Dibuja la cuerda moviéndose entre los 2 personajes"""
    glDisable(GL_LIGHTING)
    center_y = 2.0
    # Calcular posiciones X de los personajes (debe coincidir con lógica en _draw_rope_pull_characters)
    left_start = -11.0; left_edge = -2.0
    right_start = 11.0; right_edge = 2.0
    prog1 = (10 - max(0, game.health_1)) / 10.0
    prog2 = (10 - max(0, game.health_2)) / 10.0
    left_x = left_start + prog1 * (left_edge - left_start)
    right_x = right_start + prog2 * (right_edge - right_start)

    # Map visual offset (0..1) to small z-offset for cuerda (curvatura)
    mid = (left_x + right_x) / 2
    z_range = 3.2
    left_z = (0.5 - game.rope_visual_offset) * z_range
    right_z = (game.rope_visual_offset - 0.5) * z_range

    # Shake effect (más suave)
    shake = 0.0
    if game.rope_shake > 0:
        shake = math.sin(glutGet(GLUT_ELAPSED_TIME) / 120.0) * game.rope_shake * 0.35

    glColor3f(0.85, 0.65, 0.12)
    glLineWidth(4.0)
    glBegin(GL_LINE_STRIP)
    glVertex3f(left_x, center_y, 2 + left_z + shake)
    glVertex3f(mid, center_y + 0.6 + abs(game.rope_visual_offset-0.5)*1.0, 0 + (left_z + right_z)/2)
    glVertex3f(right_x, center_y, 2 + right_z - shake)
    glEnd()
    glLineWidth(1.0)

    # Nudos en los extremos
    glColor3f(1.0, 0.85, 0.2)
    q = gluNewQuadric()
    glPushMatrix()
    glTranslatef(left_x - 0.4, center_y, 2 + left_z)
    gluSphere(q, 0.25, 10, 10)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(right_x + 0.4, center_y, 2 + right_z)
    gluSphere(q, 0.25, 10, 10)
    glPopMatrix()
    gluDeleteQuadric(q)

    glEnable(GL_LIGHTING)


def _draw_rope_pull_hud(game, W, H):
    """HUD 2D para el mini-juego tira de cuerda"""
    GOLD = (1.0, 0.85, 0.25)
    WHITE = (1.0, 1.0, 1.0)
    GREEN = (0.25, 0.95, 0.35)
    RED = (1.0, 0.35, 0.35)
    GRAY = (0.78, 0.78, 0.78)

    cx = W // 2

    if game.show_instructions:
        # Mostrar panel de instrucciones (espera ENTER)
        _rect_filled(cx - 360, H // 2 - 140, 720, 280, 0.02, 0.02, 0.04, 0.86)
        _rect_border(cx - 360, H // 2 - 140, 720, 280, GOLD[0], GOLD[1], GOLD[2], 3.0)

        title = "TIRA DE LA CUERDA - INSTRUCCIONES"
        _text32(cx - _str_width_32(title)//3, H // 2 + 90, title, GOLD)

        instr_lines = [
            "Aparece una palabra MAL ESCRITA en inglés.",
            "Abajo ves qué significa en español.",
            "Escríbela BIEN y presiona ENTER.",
            "Tienes 10 segundos.",
            "",
            "Si aciertas: tu rival pierde 1 vida.",
            "Si fallas: pierdes 1 vida tú.",
            "Gana quien deje al otro sin vidas.",
        ]
        y = H // 2 + 30
        for line in instr_lines:
            _text24(cx - _str_width_24(line)//2.8, y, line, WHITE)
            y -= 20
        return

    if game.paused:
        # Overlay pausa
        _rect_filled(cx - 220, H // 2 - 50, 440, 100, 0.01, 0.01, 0.02, 0.85)
        _rect_border(cx - 220, H // 2 - 50, 440, 100, 0.9, 0.9, 0.95, 2.0)
        _text32(cx - _str_width_32("PAUSA")//2, H // 2 + 10, "PAUSA", WHITE)
        _text24(cx - _str_width_24("ENTER para reanudar")//2, H // 2 - 20, "ENTER para reanudar", GRAY)
        return

    if game.game_over:
        # Pantalla de fin del juego
        winner_name = game.char1_name if game.winner == 1 else game.char2_name
        _rect_filled(cx - 300, H // 2 - 110, 600, 220, 0.02, 0.02, 0.02, 0.88)
        _rect_border(cx - 300, H // 2 - 110, 600, 220, GOLD[0], GOLD[1], GOLD[2], 3.0)
        title = f"¡{winner_name} HA GANADO!"
        _text32(cx - _str_width_32(title)//3, H // 2 + 40, title, GOLD)
        instr = "Presiona ENTER para continuar"
        _text24(cx - _str_width_24(instr)//2.7, H // 2 - 30, instr, GRAY)
        return

    # Mostrar palabra principal y traducción (fuente más grande)
    # Texto siempre en NEGRO para máxima visibilidad
    BLACK = (0.0, 0.0, 0.0)
    _text32(cx - _str_width_32(game.word_incomplete)//2, H - 60, game.word_incomplete, BLACK)
    _text24(cx - _str_width_24(game.word_translation)//2, H - 100, f"Significado: {game.word_translation}", BLACK)

    # Input del jugador (justo debajo de la traducción) - FUENTE MUY GRANDE
    input_display = game.player_input
    if game.input_cursor_blink > 0.5 and not game.paused:
        input_display += "|"
    _text32(cx - _str_width_32(input_display)//2, H - 140, input_display, GOLD)

    # Cronómetro y turno - POSICIÓN DINÁMICA SEGÚN JUGADOR ACTUAL
    timer_color = RED if game.timer < 3.0 else WHITE
    timer_text = f"{max(0, game.timer):.1f}s"

    player_text = f"Turno: {game.char1_name if game.current_player == 1 else game.char2_name}"
    # Mostrar cronómetro y turno con fuente más grande y posicionamiento elevado
    if game.current_player == 1:
        timer_x = 40
        _text32(timer_x, H - 85, timer_text, timer_color)
        _text24(timer_x, H - 135, player_text, GOLD)
    else:
        timer_x = W - 250
        _text32(timer_x, H - 85, timer_text, timer_color)
        _text24(timer_x, H - 135, player_text, GOLD)

    # Vidas (barras) arriba a los lados, con nombre grande
    # Jugador 1 (izquierda)
    _text32(40, H - 50, f"{game.char1_name}", (0.8,0.95,0.8))
    for i in range(game.health_1):
        glColor3f(*GREEN)
        glBegin(GL_QUADS)
        glVertex2f(40 + i * 18, H - 110)
        glVertex2f(40 + i * 18 + 16, H - 110)
        glVertex2f(40 + i * 18 + 16, H - 90)
        glVertex2f(40 + i * 18, H - 90)
        glEnd()

    # Jugador 2 (derecha)
    _text32(W - 300, H - 50, f"{game.char2_name}", (0.8,0.95,0.8))
    for i in range(game.health_2):
        glColor3f(*GREEN)
        glBegin(GL_QUADS)
        glVertex2f(W - 60 - i * 18, H - 110)
        glVertex2f(W - 60 - i * 18 - 16, H - 110)
        glVertex2f(W - 60 - i * 18 - 16, H - 90)
        glVertex2f(W - 60 - i * 18, H - 90)
        glEnd()


    # Mensaje temporal (correcto/incorrecto)
    if game.message_timer > 0:
        msg_color = GREEN if "ACERTÓ" in game.message else RED
        _text24(cx - _str_width_24(game.message)//2, H // 2 + 90, game.message, msg_color)

    # Mostrar palabra correcta cuando el jugador falló
    if game.correction_word and game.correction_timer > 0:
        corr_label = f"Respuesta correcta: {game.correction_word.upper()}"
        _rect_filled(cx - 260, H // 2 + 40, 520, 50, 0.0, 0.0, 0.0, 0.85)
        _rect_border(cx - 260, H // 2 + 40, 520, 50, 1.0, 0.85, 0.25, 2.5)
        cw = _str_width_24(corr_label)
        _text24(cx - int(cw // 2.6), H // 2 + 55, corr_label, (1.0, 0.85, 0.25))


# ═══════════════════════════════════════════════════════════════════
# ────────────────────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════

def _str_width_12(s):
    wide   = set("WMmwABCDEGHKNOQRSTUVXYZ0123456789")
    narrow = set("ijlf1!|.,:;' ")
    total  = 0
    for c in s:
        if c in wide:     total += 9
        elif c in narrow: total += 5
        else:             total += 7
    return total

def _str_width_18(s):
    wide   = set("WMmwABCDEGHKNOQRSTUVXYZ0123456789")
    narrow = set("ijlf1!|.,:;' ")
    total  = 0
    for c in s:
        if c in wide:     total += 13
        elif c in narrow: total += 7
        else:             total += 10
    return total

def _text(x, y, txt, color=(1, 1, 1), font=GLUT_BITMAP_HELVETICA_12):
    glColor3f(*color)
    glRasterPos2f(x, y)
    for ch in txt:
        glutBitmapCharacter(font, ord(ch))

def _text18(x, y, txt, color=(1, 1, 1)):
    _text(x, y, txt, color, GLUT_BITMAP_HELVETICA_18)

def _str_width_24(s):
    # Aproximación del ancho para fuente mayor
    return int(_str_width_18(s) * 1.45)

def _text24(x, y, txt, color=(1,1,1)):
    # Fuente mayor para HUD principal (usa Times Roman 24 si está disponible)
    try:
        _text(x, y, txt, color, GLUT_BITMAP_TIMES_ROMAN_24)
    except Exception:
        _text(x, y, txt, color, GLUT_BITMAP_HELVETICA_18)

def _str_width_32(s):
    # Estimación mayor para texto prominente (basada en _str_width_18)
    return int(_str_width_18(s) * 1.9)

def _text32(x, y, txt, color=(1,1,1)):
    # Intentamos usar la fuente más grande disponible para títulos (Times Roman 24)
    # Si no está disponible, se recurre a Helvetica 18.
    try:
        _text(x, y, txt, color, GLUT_BITMAP_TIMES_ROMAN_24)
    except Exception:
        _text(x, y, txt, color, GLUT_BITMAP_HELVETICA_18)

def _rect_filled(x, y, w, h, r, g, b, a=1.0):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(r, g, b, a)
    glBegin(GL_QUADS)
    glVertex2f(x,     y);     glVertex2f(x + w, y)
    glVertex2f(x + w, y + h); glVertex2f(x,     y + h)
    glEnd()
    glDisable(GL_BLEND)

def _rect_border(x, y, w, h, r, g, b, lw=1.5):
    glLineWidth(lw)
    glColor3f(r, g, b)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x,     y);     glVertex2f(x + w, y)
    glVertex2f(x + w, y + h); glVertex2f(x,     y + h)
    glEnd()
    glLineWidth(1.0)

def _enter_2d(W, H):
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, W, 0, H)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()

def _exit_2d():
    glPopMatrix()
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)


# -----------------------------------------------------------------------
#  Dibujar personaje por ID
# -----------------------------------------------------------------------
def _draw_char_model(char_id):
    if   char_id == "pucca":   Pucca3D.draw_pucca()
    elif char_id == "pochaco": Pochacco3D.draw_fox_full()
    elif char_id == "kirby":   Kirby.draw_kirby_magician()
    elif char_id == "dee":     Dee.draw_dee_magician()
    elif char_id == "optimus": optimusPrime.draw_optimus_full()
    elif char_id == "plasma":  plasma_pea.draw_plasma_pea()


# -----------------------------------------------------------------------
#  Iluminacion del cubiculo  (bright_level: 0=oscuro, 0.5=hover, 1=activo)
# -----------------------------------------------------------------------
def _setup_cubicle_lighting(char_id, bright_level):
    ac = _ACCENT_COLORS.get(char_id, (1.0, 1.0, 1.0))

    amb_main  = 0.18 + bright_level * 0.67
    diff_main = 0.22 + bright_level * 1.18

    glEnable(GL_LIGHT3)
    glLightfv(GL_LIGHT3, GL_POSITION, [0.0, 4.0, 8.0, 1.0])
    glLightfv(GL_LIGHT3, GL_AMBIENT,  [amb_main,  amb_main,  amb_main,  1.0])
    glLightfv(GL_LIGHT3, GL_DIFFUSE,  [diff_main, diff_main, diff_main, 1.0])
    glLightfv(GL_LIGHT3, GL_SPECULAR, [bright_level, bright_level, bright_level, 1.0])

    amb_fill  = 0.08 + bright_level * 0.52
    diff_fill = 0.10 + bright_level * 0.80

    glEnable(GL_LIGHT4)
    glLightfv(GL_LIGHT4, GL_POSITION, [0.0, -2.0, 7.0, 1.0])
    glLightfv(GL_LIGHT4, GL_AMBIENT,  [amb_fill, amb_fill, amb_fill, 1.0])
    glLightfv(GL_LIGHT4, GL_DIFFUSE,  [diff_fill, diff_fill, diff_fill, 1.0])
    glLightfv(GL_LIGHT4, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])

    accent_strength = max(0.0, (bright_level - 0.4) * 1.67)
    glEnable(GL_LIGHT5)
    glLightfv(GL_LIGHT5, GL_POSITION, [-6.0, 3.0, 4.0, 1.0])
    glLightfv(GL_LIGHT5, GL_AMBIENT,
              [ac[0]*0.35*accent_strength, ac[1]*0.35*accent_strength, ac[2]*0.35*accent_strength, 1.0])
    glLightfv(GL_LIGHT5, GL_DIFFUSE,
              [ac[0]*0.75*accent_strength, ac[1]*0.75*accent_strength, ac[2]*0.75*accent_strength, 1.0])
    glLightfv(GL_LIGHT5, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])

def _disable_cubicle_lighting():
    glDisable(GL_LIGHT3)
    glDisable(GL_LIGHT4)
    glDisable(GL_LIGHT5)


# -----------------------------------------------------------------------
#  Hit-test: devuelve el indice de la card o -1
# -----------------------------------------------------------------------
def _card_index_at(mx, my_glut, W, H):
    total_w   = COLS * CARD_W + (COLS - 1) * GAP_X
    grid_x0   = (W - total_w) // 2
    top_row_y = H - 100 - CARD_H
    oy = H - my_glut

    for i in range(len(CHARS)):
        row = i // COLS
        col = i % COLS
        cx_card = grid_x0 + col * (CARD_W + GAP_X)
        cy_card = top_row_y - row * (CARD_H + GAP_Y)
        if cx_card <= mx <= cx_card + CARD_W and cy_card <= oy <= cy_card + CARD_H:
            return i
    return -1


# -----------------------------------------------------------------------
#  Renderizar personaje 3D estatico en su cubiculo via sub-viewport
# -----------------------------------------------------------------------
def _draw_char_in_card(char_id, cx_card, cy_card, bright_level, W, H):
    PAD       = 6
    TEXT_AREA = 72
    vp_x = int(cx_card + PAD)
    vp_y = int(cy_card + PAD)
    vp_w = int(CARD_W - PAD * 2)
    vp_h = int(CARD_H - TEXT_AREA - PAD)

    if vp_w <= 0 or vp_h <= 0:
        return

    glPushAttrib(GL_VIEWPORT_BIT | GL_SCISSOR_BIT)

    glEnable(GL_SCISSOR_TEST)
    glScissor(vp_x, vp_y, vp_w, vp_h)
    glViewport(vp_x, vp_y, vp_w, vp_h)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluPerspective(38.0, vp_w / max(vp_h, 1), 0.1, 80.0)
    glMatrixMode(GL_MODELVIEW)

    glDisable(GL_LIGHT0)
    glDisable(GL_LIGHT1)
    glDisable(GL_LIGHT2)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.12, 0.12, 0.14, 1.0])

    _setup_cubicle_lighting(char_id, bright_level)

    glLoadIdentity()
    gluLookAt(0, 1.5, 7,   0, 0.8, 0,   0, 1, 0)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glClear(GL_DEPTH_BUFFER_BIT)

    glPushMatrix()
    sc = _CHAR_SCALE.get(char_id, 1.0)
    yo = _CHAR_Y_OFF.get(char_id, -0.5)
    glTranslatef(0.0, yo, 0.0)
    glScalef(sc, sc, sc)
    _draw_char_model(char_id)
    glPopMatrix()

    _disable_cubicle_lighting()

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glPopAttrib()
    glViewport(0, 0, W, H)

    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_LIGHT2)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
    glDisable(GL_SCISSOR_TEST)


# -----------------------------------------------------------------------
#  Renderizar el personaje seleccionado (modo greeting) — PANEL CENTRAL
# -----------------------------------------------------------------------
def _draw_platform(accent_color):
    """Dibuja la plataforma circular bajo el personaje."""
    ar, ag, ab = accent_color
    q = gluNewQuadric()

    # Disco superior (plataforma)
    glPushMatrix()
    glColor3f(ar * 0.55, ag * 0.55, ab * 0.55)
    glRotatef(-90, 1, 0, 0)
    gluDisk(q, 0.0, 1.35, 32, 2)
    glPopMatrix()

    # Borde brillante del disco
    glPushMatrix()
    glColor3f(ar, ag, ab)
    glRotatef(-90, 1, 0, 0)
    gluDisk(q, 1.20, 1.35, 32, 1)
    glPopMatrix()

    # Cilindro lateral (grosor de la plataforma)
    glPushMatrix()
    glTranslatef(0.0, -0.14, 0.0)
    glColor3f(ar * 0.30, ag * 0.30, ab * 0.30)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(q, 1.35, 1.35, 0.14, 32, 1)
    glPopMatrix()

    gluDeleteQuadric(q)


# Offset Y para posicionar cada personaje SOBRE la plataforma (Y=-1.05)
# El valor es: -1.05 + altura_del_pivot_al_suelo_del_modelo
_CHAR_PLATFORM_Y = {
    "pucca":   -0.05,   # pivot en centro, pies ~1.0 abajo -> -1.05+1.0 = -0.05
    "pochaco": -0.15,
    "kirby":   -0.20,
    "dee":     -0.15,
    "optimus":  0.80,   # personaje alto, pivot mas arriba
    "plasma":  -0.10,
}


def _draw_selected_char_large(char_id, W, H):
    # Panel centrado
    PANEL_W = min(500, int(W * 0.46))
    PANEL_H = min(560, int(H * 0.75))
    vp_x = (W - PANEL_W) // 2
    vp_y = (H - PANEL_H) // 2
    vp_w = PANEL_W
    vp_h = PANEL_H

    if vp_w <= 0 or vp_h <= 0:
        return

    glPushAttrib(GL_VIEWPORT_BIT | GL_SCISSOR_BIT)

    glEnable(GL_SCISSOR_TEST)
    glScissor(vp_x, vp_y, vp_w, vp_h)
    glViewport(vp_x, vp_y, vp_w, vp_h)

    # ── Paso 1: dibujar fondo negro solido con quad 2D ortho ──────────────
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1, 0, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glColor3f(0.0, 0.0, 0.0)
    glBegin(GL_QUADS)
    glVertex2f(0, 0); glVertex2f(1, 0)
    glVertex2f(1, 1); glVertex2f(0, 1)
    glEnd()
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    # Limpiar solo el depth buffer del viewport
    glEnable(GL_DEPTH_TEST)
    glClear(GL_DEPTH_BUFFER_BIT)

    # ── Paso 2: escena 3D con iluminacion Gouraud SUTIL ───────────────────
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluPerspective(38.0, vp_w / max(vp_h, 1), 0.1, 80.0)
    glMatrixMode(GL_MODELVIEW)

    glLoadIdentity()
    gluLookAt(0, 2, 10,   0, 1, 0,   0, 1, 0)

    # Apagar luces globales del menu — usamos solo una luz propia
    glDisable(GL_LIGHT0)
    glDisable(GL_LIGHT1)
    glDisable(GL_LIGHT2)
    glDisable(GL_LIGHT3)
    glDisable(GL_LIGHT4)
    glDisable(GL_LIGHT5)

    # Ambiente global alto: preserva ~82% del color original en sombras
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.82, 0.82, 0.82, 1.0])

    # Una sola luz suave frontal-superior: agrega volumen sin quemar
    #   diffuse 0.28 -> solo un 28% de variacion entre cara iluminada y sombra
    #   sin especular -> cero brillos blancos
    glEnable(GL_LIGHT3)
    glLightfv(GL_LIGHT3, GL_POSITION, [1.0, 4.0, 10.0, 1.0])
    glLightfv(GL_LIGHT3, GL_AMBIENT,  [0.0, 0.0, 0.0, 1.0])   # no suma al ambient global
    glLightfv(GL_LIGHT3, GL_DIFFUSE,  [0.28, 0.28, 0.28, 1.0]) # toque sutil de volumen
    glLightfv(GL_LIGHT3, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])   # sin brillos

    glEnable(GL_LIGHTING)
    glShadeModel(GL_SMOOTH)  # Gouraud

    # Material: ambient=1 preserva el glColor3f exacto; diffuse=1 recibe la luz suave
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT,  [1.0, 1.0, 1.0, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE,  [1.0, 1.0, 1.0, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])  # sin brillo
    glMaterialf (GL_FRONT_AND_BACK, GL_SHININESS, 0.0)

    ac = _ACCENT_COLORS.get(char_id, (1.0, 1.0, 1.0))
    t = glutGet(GLUT_ELAPSED_TIME) / 1000.0

    # Plataforma
    glPushMatrix()
    glTranslatef(0.0, -1.05, 0.0)
    _draw_platform(ac)
    glPopMatrix()

    # Personaje con iluminacion Gouraud suave
    sc = _CHAR_SCALE.get(char_id, 1.0) * 1.20
    yo = _CHAR_PLATFORM_Y.get(char_id, -0.05)
    rot = math.sin(t * 1.2) * 6.0

    # ── Lamina blanca solo para Pucca ─────────────────────────────────────
    # Un quad blanco plano en Z=-0.5 (detras del personaje).
    # Sus caras dobles desaparecen porque el modelo NO se dibuja en blanco.
    if char_id == "pucca":
        glDisable(GL_LIGHTING)
        glColor3f(1.0, 1.0, 1.0)
        # Bounds de Pucca (world space) + ~0.13 u de margen ≈ 10 px
        hw  = 0.95 * sc + 0.13   # mitad ancho: moños son lo mas ancho (±0.95 unsc.)
        top = yo + 0.62 * sc + 0.13  # tope de cabeza/moños + margen
        bot = -1.10               # justo bajo la plataforma
        glBegin(GL_QUADS)
        glVertex3f(-hw, bot, -0.5)
        glVertex3f( hw, bot, -0.5)
        glVertex3f( hw, top, -0.5)
        glVertex3f(-hw, top, -0.5)
        glEnd()
        glEnable(GL_LIGHTING)

    # ── Animaciones de preview (Saltar / Saludar / Girar cabeza) ─────────────
    import math as _mth
    preview_y  = yo   # desplazamiento vertical por salto
    preview_rot = rot  # rotacion base (senoidal)

    if state.is_jumping and state.jump_time <= 1.0:
        # Arco de salto simple
        arc = _mth.sin(state.jump_time * _mth.pi)
        preview_y += arc * 1.8
        state.jump_time += 0.04
        if state.jump_time > 1.0:
            state.is_jumping = False; state.jump_time = 0.0

    if state.is_greeting and state.greet_timer > 0:
        state.greet_timer -= 1
        # Oscila brazo der (se aplica en draw_char_model via state.brazo_der_x)
        state.brazo_der_x = _mth.sin(state.greet_timer * 0.25) * 55.0
        if state.greet_timer == 0:
            state.is_greeting = False; state.brazo_der_x = 0.0

    # Girar cabeza se aplica via state.cabeza_y en los modelos

    # ── Personaje (una sola pasada, sin duplicado) ─────────────────────────
    glPushMatrix()
    glTranslatef(0.0, preview_y, 0.0)
    glRotatef(preview_rot, 0, 1, 0)
    glScalef(sc, sc, sc)
    _draw_char_model(char_id)
    glPopMatrix()

    glDisable(GL_LIGHT3)

    # Restaurar material
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT,  [0.45, 0.45, 0.50, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE,  [1.0,  1.0,  1.0,  1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.60, 0.70, 0.80, 1.0])
    glMaterialf (GL_FRONT_AND_BACK, GL_SHININESS, 48.0)

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glPopAttrib()
    glViewport(0, 0, W, H)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_LIGHT2)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
    glDisable(GL_SCISSOR_TEST)


# -----------------------------------------------------------------------
#  MENU PRINCIPAL
# -----------------------------------------------------------------------
def draw_menu():
    global _current_screen
    if _current_screen == "endgame_menu":
        _draw_endgame_menu()
    elif _current_screen == "laberinto_mode":
        _draw_laberinto_mode_screen()
    elif _current_screen == "info_screen":
        _draw_info_screen()
    elif _current_screen in ("char_select_mp", "char_select_1p", "char_select_maze", "char_select_maze_mp"):
        _draw_multiplayer_char_selection()
    else:
        _draw_original_menu()


def _draw_original_menu():
    W = glutGet(GLUT_WINDOW_WIDTH)
    H = glutGet(GLUT_WINDOW_HEIGHT)

    char_id = CHARS[state.menu_cursor_index][0]
    is_greeting_mode = (_menu_state == "greeting")

    # Reconfigurar proyeccion global
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, W / max(H, 1), 0.1, 120.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Calcular posiciones de cards
    total_w   = COLS * CARD_W + (COLS - 1) * GAP_X
    grid_x0   = (W - total_w) // 2
    top_row_y = H - 100 - CARD_H

    # Dibujar cada personaje en su cubiculo
    for i, (cid, name, subtitle, accent, _esc) in enumerate(CHARS):
        row = i // COLS
        col = i % COLS
        cx_card = grid_x0 + col * (CARD_W + GAP_X)
        cy_card = top_row_y - row * (CARD_H + GAP_Y)

        selected = (i == state.menu_cursor_index)
        hovered  = (i == _hover_index and not selected)

        if is_greeting_mode and selected:
            bright = 0.45  # cubiculo oscurecido al mostrar el grande
        elif selected:
            bright = 1.0
        elif hovered:
            bright = 0.50
        else:
            bright = 0.0

        _draw_char_in_card(cid, cx_card, cy_card, bright, W, H)

    # NOTA: el personaje grande en modo greeting se dibuja AL FINAL
    # (despues de todo el UI 2D) para que el fondo negro no sea sobredibujado.

    # ---- UI 2D superpuesta -------------------------------------------
    _enter_2d(W, H)

    # Fondo semitransparente
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBegin(GL_QUADS)
    glColor4f(0.04, 0.04, 0.14, 0.80); glVertex2f(0, 0); glVertex2f(W, 0)
    glColor4f(0.06, 0.06, 0.22, 0.80); glVertex2f(W, H); glVertex2f(0, H)
    glEnd()
    glDisable(GL_BLEND)

    GOLD = (1.00, 0.85, 0.25)
    GRAY = (0.52, 0.52, 0.62)
    cx = W // 2

    # Titulo
    title = "* SELECT YOUR CHARACTER *"
    tw = _str_width_18(title)
    _text18(cx - tw // 2, H - 52, title, GOLD)

    if is_greeting_mode:
        sub = "ENTER: confirmar e ir al juego   ESC: cancelar seleccion"
    else:
        sub = "elige tu personaje  -  ENTER / CLICK para seleccionar"
    sw = _str_width_12(sub)
    _text(cx - sw // 2, H - 74, sub, GRAY)

    # Linea separadora
    glColor3f(0.22, 0.22, 0.38)
    glBegin(GL_LINES)
    glVertex2f(cx - 260, H - 86)
    glVertex2f(cx + 260, H - 86)
    glEnd()

    # ---- Grid de cards -----------------------------------------------
    for i, (cid, name, subtitle, accent, _esc) in enumerate(CHARS):
        row = i // COLS
        col = i % COLS
        cx_card = grid_x0 + col * (CARD_W + GAP_X)
        cy_card = top_row_y - row * (CARD_H + GAP_Y)

        selected = (i == state.menu_cursor_index)
        hovered  = (i == _hover_index and not selected)
        ar, ag, ab = accent

        # Fondo semitransparente de la card
        if is_greeting_mode and selected:
            _rect_filled(cx_card, cy_card, CARD_W, CARD_H,
                         ar*0.08, ag*0.08, ab*0.08, 0.40)
        elif selected:
            _rect_filled(cx_card, cy_card, CARD_W, CARD_H,
                         ar*0.18, ag*0.18, ab*0.18, 0.50)
        elif hovered:
            _rect_filled(cx_card, cy_card, CARD_W, CARD_H,
                         ar*0.10, ag*0.10, ab*0.10, 0.48)
        else:
            _rect_filled(cx_card, cy_card, CARD_W, CARD_H,
                         0.03, 0.04, 0.10, 0.65)

        # Borde luminoso del color del personaje
        t = glutGet(GLUT_ELAPSED_TIME) / 1000.0
        if is_greeting_mode and selected:
            pulse = (math.sin(t * 4.0) + 1.0) / 2.0
            lw = 3.0
            br, bg_, bb = 1.0, 0.85*(0.7+pulse*0.3), 0.10*pulse
            _rect_border(cx_card, cy_card, CARD_W, CARD_H, br, bg_, bb, lw)
            _rect_border(cx_card-3, cy_card-3, CARD_W+6, CARD_H+6,
                         br*0.45, bg_*0.45, 0.0, 1.2)
        elif selected:
            lw = 2.8; br, bg_, bb = ar, ag, ab
            _rect_border(cx_card, cy_card, CARD_W, CARD_H, br, bg_, bb, lw)
            _rect_border(cx_card-2, cy_card-2, CARD_W+4, CARD_H+4,
                         ar*0.45, ag*0.45, ab*0.45, 1.2)
        elif hovered:
            lw = 2.0; br, bg_, bb = ar*0.80, ag*0.80, ab*0.80
            _rect_border(cx_card, cy_card, CARD_W, CARD_H, br, bg_, bb, lw)
            _rect_border(cx_card-1, cy_card-1, CARD_W+2, CARD_H+2,
                         ar*0.30, ag*0.30, ab*0.30, 1.0)
        else:
            lw = 1.2; br, bg_, bb = ar*0.30, ag*0.30, ab*0.30
            _rect_border(cx_card, cy_card, CARD_W, CARD_H, br, bg_, bb, lw)

        # Nombre centrado
        if is_greeting_mode and selected:
            nc = (1.0, 1.0, 0.30)
        elif selected:
            nc = (1.0, 1.0, 0.55)
        else:
            nc = (ar*0.85, ag*0.85, ab*0.85)

        nw = _str_width_18(name)
        _text18(cx_card + (CARD_W - nw)//2, cy_card + CARD_H - 36, name, nc)

        # Linea bajo nombre
        lx = cx_card + 18
        glColor3f(ar*0.50, ag*0.50, ab*0.50)
        glBegin(GL_LINES)
        glVertex2f(lx, cy_card + CARD_H - 48)
        glVertex2f(lx + CARD_W - 36, cy_card + CARD_H - 48)
        glEnd()

        # Badge subtitulo
        PAD_X   = 10
        BADGE_H = 18
        TEXT_Y  = cy_card + CARD_H - 68
        BORD_Y  = TEXT_Y - 8

        sw2     = _str_width_12(subtitle)
        badge_w = sw2 + PAD_X * 2
        badge_x = cx_card + (CARD_W - badge_w) // 2
        text_bx = badge_x + PAD_X

        _text(text_bx, TEXT_Y, subtitle, (0.70, 0.70, 0.76))
        _rect_border(badge_x, BORD_Y, badge_w, BADGE_H,
                     ar*0.45, ag*0.45, ab*0.45, 1.0)

        _text(cx_card + CARD_W - 18, cy_card + 8,
              str(i+1), (0.32, 0.32, 0.42))

    # ---- Panel de prueba de personaje (modo greeting) ---
    if is_greeting_mode:
        cid, cname, _, accent, _ = CHARS[state.menu_cursor_index]
        ar, ag, ab = accent

        t2     = glutGet(GLUT_ELAPSED_TIME) / 1000.0
        pulse2 = (math.sin(t2 * 2.5) + 1.0) / 2.0

        # Nombre del personaje centrado arriba
        lbl = f"== {cname} =="
        lw2 = _str_width_18(lbl)
        _text18(cx - lw2 // 2, H - 82, lbl, (ar, ag, ab))

        # --- Panel de instrucciones (estilo imagen) --- derecha
        pp_w = 220
        pp_h = 115
        pp_x = W - pp_w - 8
        pp_y = H // 2 - 90
        _rect_filled(pp_x, pp_y, pp_w, pp_h, 0.0, 0.0, 0.0, 0.72)
        _rect_border(pp_x, pp_y, pp_w, pp_h, ar, ag, ab, 1.8)
        instr_lines = [
            "CONTROLES:",
            "  X  Saltar",
            "  B  Saludar",
            "  G  Girar cabeza",
        ]
        iy = pp_y + pp_h - 20
        for line in instr_lines:
            _text(pp_x + 12, iy, line, (0.80, 0.85, 0.95))
            iy -= 20

        # ENTER para confirmar (pulsante)
        confirm_color = (0.3 + pulse2*0.7, 0.85, 0.3 + pulse2*0.2)
        enter_lbl = ">> ENTER para confirmar <<"
        ew = _str_width_12(enter_lbl)
        _text(cx - ew // 2, H - 108, enter_lbl, confirm_color)

        # ESC para cancelar
        esc_lbl = "ESC: cancelar y volver a elegir"
        _text(cx - _str_width_12(esc_lbl)//2, H - 124, esc_lbl, (0.80, 0.45, 0.45))

    # ---- Instrucciones inferiores -----------------------------------
    if not is_greeting_mode:
        line1 = "Flechas: mover seleccion   ENTER / CLICK: elegir personaje"
        line2 = "Camara: Click+Arrastrar  |  Scroll = Zoom  |  1-6: Cambiar escenario"
        _text(cx - _str_width_12(line1)//2, 32, line1, GRAY)
        _text(cx - _str_width_12(line2)//2, 14, line2, GRAY)

        t3    = glutGet(GLUT_ELAPSED_TIME) / 1000.0
        alpha = (math.sin(t3 * 3.0) + 1.0) / 2.0
        arrow = f"v  SELECCIONA JUGADOR {_mp_selecting_player} PARA COMENZAR  v"
        _text(cx - _str_width_12(arrow)//2, 56, arrow, (alpha, alpha*0.85, 0.0))
    else:
        esc_lbl = "ESC: cancelar y volver a elegir"
        _text(cx - _str_width_12(esc_lbl)//2, 14, esc_lbl, (0.80, 0.45, 0.45))

    _exit_2d()

    # Restaurar proyeccion global
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, W / max(H, 1), 0.1, 120.0)
    glMatrixMode(GL_MODELVIEW)

    # Dibujar el personaje grande AL FINAL para que tape todo lo de atras
    if is_greeting_mode:
        _draw_selected_char_large(char_id, W, H)


# -----------------------------------------------------------------------
#  Objetos extra en escena
# -----------------------------------------------------------------------
def _draw_obb_tree():
    glPushMatrix()
    glTranslatef(-6.0, 0.0, 4.0)
    glRotatef(35, 0, 1, 0)
    glColor3f(0.45, 0.28, 0.10)
    q = gluNewQuadric()
    glRotatef(-90, 1, 0, 0)
    gluCylinder(q, 0.25, 0.20, 1.8, 12, 4)
    gluDeleteQuadric(q)
    glColor3f(0.20, 0.65, 0.20)
    glTranslatef(0, 0, 1.8)
    q2 = gluNewQuadric()
    gluSphere(q2, 0.80, 14, 12)
    gluDeleteQuadric(q2)
    glPopMatrix()


def _draw_cristal():
    if not state.cristal_activo:
        return
    t = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    glPushMatrix()
    glTranslatef(state.cristal_x, 0.8 + math.sin(t*2.0)*0.2, state.cristal_z)
    glRotatef(t*60.0, 0, 1, 0)
    glColor3f(0.75, 0.30, 1.00)
    glScalef(0.45, 0.80, 0.45)
    glutSolidOctahedron()
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.85, 0.50, 1.00, 0.30)
    glutSolidSphere(1.15, 14, 12)
    glDisable(GL_BLEND)
    glPopMatrix()


def _draw_cubo_2d(cx, cy, size, r, g, b):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(r, g, b, 0.95)
    glBegin(GL_QUADS)
    glVertex2f(cx,          cy)
    glVertex2f(cx + size,   cy)
    glVertex2f(cx + size,   cy + size)
    glVertex2f(cx,          cy + size)
    glEnd()
    glColor4f(1.0, 1.0, 1.0, 0.9)
    glLineWidth(2.5)
    glBegin(GL_LINE_LOOP)
    glVertex2f(cx,          cy)
    glVertex2f(cx + size,   cy)
    glVertex2f(cx + size,   cy + size)
    glVertex2f(cx,          cy + size)
    glEnd()
    glLineWidth(1.0)
    glDisable(GL_BLEND)


def draw_hud_tetris():
    if state.escenario_actual != 7 or not state.tetris_activo:
        return

    W = glutGet(GLUT_WINDOW_WIDTH)
    H = glutGet(GLUT_WINDOW_HEIGHT)
    _enter_2d(W, H)

    PANEL_W = 170
    PANEL_H = 90
    
    # ── P1 HUD (Izquierda) ──
    px1 = 12
    py1 = 12
    _rect_filled(px1, py1, PANEL_W, PANEL_H, 0.0, 0.0, 0.08, 0.80)
    _rect_border(px1, py1, PANEL_W, PANEL_H, 0.6, 0.6, 1.0, 1.5)
    
    nombre_obj1, (cr1, cg1, cb1) = state.TETRIS_COLORS[state.tetris_objetivo_idx]
    _text(px1 + 8, py1 + PANEL_H - 18, "P1 CAPTURA:", (0.85, 0.85, 1.0))
    CUBE_SIZE = 40
    cube_x1 = px1 + (PANEL_W - CUBE_SIZE) // 2
    cube_y1 = py1 + 10
    _draw_cubo_2d(cube_x1, cube_y1, CUBE_SIZE, cr1, cg1, cb1)
    nw1 = _str_width_12(nombre_obj1.upper())
    _text(px1 + (PANEL_W - nw1) // 2, cube_y1 + CUBE_SIZE + 4, nombre_obj1.upper(), (cr1, cg1, cb1))
    score_txt1 = f"P1: {state.tetris_correctos} / 10"
    _text18(px1, H - 40, score_txt1, (0.40, 1.0, 0.60))

    # ── P2 HUD (Derecha) ──
    if state.tetris_2p:
        px2 = W - PANEL_W - 12
        py2 = 12
        _rect_filled(px2, py2, PANEL_W, PANEL_H, 0.0, 0.0, 0.08, 0.80)
        _rect_border(px2, py2, PANEL_W, PANEL_H, 1.0, 0.6, 0.6, 1.5)
        
        nombre_obj2, (cr2, cg2, cb2) = state.TETRIS_COLORS[state.tetris_p2_objetivo_idx]
        _text(px2 + 8, py2 + PANEL_H - 18, "P2 CAPTURA:", (1.0, 0.85, 0.85))
        cube_x2 = px2 + (PANEL_W - CUBE_SIZE) // 2
        cube_y2 = py2 + 10
        _draw_cubo_2d(cube_x2, cube_y2, CUBE_SIZE, cr2, cg2, cb2)
        nw2 = _str_width_12(nombre_obj2.upper())
        _text(px2 + (PANEL_W - nw2) // 2, cube_y2 + CUBE_SIZE + 4, nombre_obj2.upper(), (cr2, cg2, cb2))
        score_txt2 = f"P2: {state.tetris_p2_correctos} / 10"
        _text18(px2, H - 40, score_txt2, (1.0, 0.60, 0.40))
        
        hint = "P1: A/D (WASD) | P2: Flechas IZQ/DER"
    else:
        hint = "Flechas IZQ/DER para moverte"
        
    hw = _str_width_12(hint)
    _text(W // 2 - hw // 2, H - 30, hint, (0.70, 0.70, 0.90))

    _exit_2d()

def _draw_tetris_instructions():
    W = glutGet(GLUT_WINDOW_WIDTH)
    H = glutGet(GLUT_WINDOW_HEIGHT)
    _enter_2d(W, H)
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    _rect_filled(0, 0, W, H, 0.05, 0.05, 0.15, 0.85)
    glDisable(GL_BLEND)

    cx = W // 2
    cy = H // 2

    title = "* TETRIS ESPACIAL *"
    tw = _str_width_18(title)
    _text18(cx - tw // 2, cy + 100, title, (1.0, 0.85, 0.25))

    lines = [
        "Caen cubos de colores. Atrapa solo los del color",
        "que aparece en tu panel (abajo).",
        "",
        "J1: Teclas A y D    |    J2: Flechas",
        "",
        "El primero en atrapar 10 correctos gana!"
    ]
    
    y = cy + 40
    for line in lines:
        lw = _str_width_12(line)
        _text(cx - lw // 2, y, line, (0.8, 0.85, 0.95))
        y -= 25

    btn = ">> PRESIONA ENTER PARA COMENZAR <<"
    bw = _str_width_12(btn)
    _text(cx - bw // 2, 30, btn, (0.4, 1.0, 0.6))

    _exit_2d()

# -----------------------------------------------------------------------
#  HUD durante el juego
# -----------------------------------------------------------------------
def draw_hud():
    W = glutGet(GLUT_WINDOW_WIDTH)
    H = glutGet(GLUT_WINDOW_HEIGHT)
    _enter_2d(W, H)

    _ESCENARIOS = {1: "Ciudad China", 2: "Pradera", 3: "Dream Land",
                   4: "Castillo", 5: "Base Militar", 6: "Jardin"}
    esc_nombre = _ESCENARIOS.get(state.escenario_actual, "?")
    _SHADE_LABELS = {'gouraud': "Gouraud (GL_SMOOTH)",
                     'flat':    "Flat (GL_FLAT)",
                     'phong':   "Phong (aprox. alta especular)"}
    shade_str = _SHADE_LABELS.get(state.shade_mode, state.shade_mode)

    char_map    = {c[0]: c for c in CHARS}
    cinfo       = char_map.get(state.personaje_activo, ("?", "Desconocido", "", (1,1,1), 1))
    pers_nombre = cinfo[1]
    pers_color  = cinfo[3]

    _text(10, H-20,  f"Personaje: {pers_nombre}",                   pers_color)
    _text(10, H-36,  f"Escenario [{state.escenario_actual}]: {esc_nombre}", (0.7,1.0,0.7))
    _text(10, H-52,  f"Expresion: {state.expresion_actual.capitalize()}",   (0.8,0.9,1.0))
    _text(10, H-68,  f"Sombreado: {shade_str}",                             (1.0,0.75,0.3))
    _text(10, H-84,  f"Sonido: {'ON' if state.sonido_activado else 'OFF'}", (1.0,0.9,0.6))
    _text(10, H-100, "BV [K]  I:Instrucciones  H:Acerca de  ESC:Menu",      (0.7,0.7,0.7))

    if state.show_instructions:
        lines = [
            f"=== CONTROLES - {pers_nombre} ===",
            " Flechas     Caminar",
            " X           Saltar",
            " Z           Disparar / Punetazo",
            " C           Victoria (alegria)",
            " V           Agacharse (tristeza)",
            " B           Saludar (alegria)",
            " N           Spin 360 (guino)",
            " G           Girar cabeza",
            "",
            " Q Normal  W Enojo  E Miedo",
            " T Tristeza Y Guino U Alegria O Sorpresa",
            "",
            " S  Ciclo sombreado",
            " K  Bounding Volumes  M Silencio",
            " 1-6 Escenarios  R Reset camara",
            " ESC Volver al menu",
            " I Cerrar panel",
        ]
        bx, by = 10, H-120
        for line in lines:
            _text(bx, by, line, (0.95, 0.95, 0.80))
            by -= 16

    if state.show_bv:
        leyenda = [
            " BOUNDING VOLUMES",
            " CIAN    Esfera zombie  (Alg.1 eucl.)",
            " AZUL    AABB caja      (Alg.2)",
            " ROJO    AABB valla     (Alg.3)",
            " MAGENTA Rombo orbe     (Alg.4 Manhattan)",
            " AMARIL. OBB arbol      (Alg.5)",
            " VIOLETA AABB cristal   (Alg.6)",
            " VERDE   Radio personaje",
        ]
        bx = W-370; by = H-20
        for line in leyenda:
            _text(bx, by, line, (0.90, 0.85, 1.00))
            by -= 16

    if state.show_about:
        lines = [
            "=== ACERCA DE ===",
            f" Personaje activo: {pers_nombre}",
            " Materia: Graficacion por Computadora",
            " Alumno: Yerik Jardon Albarran",
            " No.Ctrl: 24280842",
            " Docente: Rocio Elizabeth Pulido Alba",
            "",
            " Colisiones: 1.Esfera 2.AABB 3.AABBrect",
            "             4.Manhattan 5.OBB 6.Cristal",
            " Python + PyOpenGL + GLUT",
            " H para cerrar",
        ]
        bx, by = 10, H-90
        for line in lines:
            _text(bx, by, line, (0.85, 1.0, 0.95))
            by -= 16

    _exit_2d()


# -----------------------------------------------------------------------
#  LABERINTO — funciones de lógica y renderizado
# -----------------------------------------------------------------------

def _init_maze():
    global _maze_player_x, _maze_player_z, _maze_facing
    global _maze_player2_x, _maze_player2_z, _maze_player2_facing
    global _maze_active_question, _maze_input_text, _maze_feedback, _maze_feedback_timer
    global _maze_active_question2, _maze_input_text2, _maze_feedback2, _maze_feedback_timer2
    global _maze_keys, _maze_keys2, _maze_selected_opt, _maze_selected_opt2
    global _maze_items, _maze_items2, _maze_initialized, _maze_time_start, _maze_time_left
    sx, sz = get_start_pos()
    _maze_player_x = sx; _maze_player_z = sz; _maze_facing = 0.0
    gx2 = (1 - MAZE_COLS / 2.0 + 0.5) * CELL
    gz2 = (1 - MAZE_ROWS / 2.0 + 0.5) * CELL
    _maze_player2_x = gx2; _maze_player2_z = gz2; _maze_player2_facing = 180.0
    _maze_active_question = None; _maze_input_text = ""; _maze_feedback = ""; _maze_feedback_timer = 0
    _maze_active_question2 = None; _maze_input_text2 = ""; _maze_feedback2 = ""; _maze_feedback_timer2 = 0
    _maze_keys  = {'up': False, 'down': False, 'left': False, 'right': False}
    _maze_keys2 = {'up': False, 'down': False, 'left': False, 'right': False}
    _maze_selected_opt = 0; _maze_selected_opt2 = 0
    _maze_time_start = -1.0   # Se inicializa en el primer frame de render
    _maze_time_left  = _MAZE_TIME_LIMIT
    q_pool = list(range(len(_maze_questions))); random.shuffle(q_pool)
    _maze_items = []; _maze_items2 = []; used = set(); qi = 0
    for (row, col) in _MAZE_ITEM_CELLS:
        if MAZE_MAP[row][col] == 0 and (row, col) not in used:
            wx = (col - MAZE_COLS / 2.0 + 0.5) * CELL
            wz = (row - MAZE_ROWS / 2.0 + 0.5) * CELL
            item = {"row": row, "col": col, "wx": wx, "wz": wz,
                    "collected": False, "q_index": q_pool[qi % len(q_pool)]}
            _maze_items.append(item)
            _maze_items2.append(copy.deepcopy(item))
            used.add((row, col)); qi += 1
    _maze_initialized = True
    state.maze_show_instructions = True
    # NOTA: play_maze_music() se llama explícitamente en _start_maze_mp_game/_start_maze_sp_game,
    # NO aquí, para que al resetear el estado al salir no se reinicie la música.


def _start_maze_mp_game(char1_id, char2_id):
    global _maze_char_id, _maze_char_id2, _current_screen, _maze_mp_mode
    _maze_char_id  = char1_id
    _maze_char_id2 = char2_id
    _maze_mp_mode  = True
    state.en_menu  = False
    _init_maze()
    try: stop_bg_music()
    except Exception: pass
    try: play_maze_music()
    except Exception: pass
    _current_screen = "maze_game"


def _start_maze_sp_game(char1_id):
    """Lanza el laberinto en modo individual (1 jugador)."""
    global _maze_char_id, _maze_char_id2, _current_screen, _maze_mp_mode
    _maze_char_id  = char1_id
    _maze_char_id2 = None
    _maze_mp_mode  = False
    state.en_menu  = False
    _init_maze()
    try: stop_bg_music()
    except Exception: pass
    try: play_maze_music()
    except Exception: pass
    _current_screen = "maze_game"


def _maze_handle_key(k):
    global _maze_active_question, _maze_selected_opt
    global _maze_active_question2, _maze_selected_opt2
    global _current_screen
    if _maze_active_question is not None:
        if   k == ord('1'): _maze_selected_opt = 0
        elif k == ord('2'): _maze_selected_opt = 1
        elif k == ord('3'): _maze_selected_opt = 2
        elif k == ord('4'): _maze_selected_opt = 3
        elif k in (13, 10): _check_maze_answer(1)
        elif k == 27:       _maze_active_question = None
        return
    if _maze_mp_mode and _maze_active_question2 is not None:
        if   k == ord('5'): _maze_selected_opt2 = 0
        elif k == ord('6'): _maze_selected_opt2 = 1
        elif k == ord('7'): _maze_selected_opt2 = 2
        elif k == ord('8'): _maze_selected_opt2 = 3
        elif k in (13, 10): _check_maze_answer(2)
        elif k == 27:       _maze_active_question2 = None
        return
    # Tecla M: toggle música del laberinto
    if k in (ord('m'), ord('M')):
        try: toggle_maze_music()
        except Exception: pass
        return
    if k == 27:
        try: stop_maze_music()
        except Exception: pass
        if _maze_mp_mode:
            _current_screen = "endgame_menu"; state.en_menu = True
        else:
            _current_screen = "laberinto_mode"; state.en_menu = True
        _init_maze()


def _check_maze_answer(player=1):
    global _maze_active_question, _maze_feedback, _maze_feedback_timer
    global _maze_active_question2, _maze_feedback2, _maze_feedback_timer2
    if player == 1:
        if _maze_active_question is None: return
        q_data = _maze_questions[_maze_active_question["q_index"]]
        correct = q_data["a"]
        correct_word = q_data["opts"][correct]
        # Reproducir sonido de la respuesta correcta siempre
        try: play_english_word(correct_word)
        except Exception: pass
        if _maze_selected_opt == correct:
            _maze_feedback = "correcto"; _maze_feedback_timer = 120
            _maze_active_question["collected"] = True; _maze_active_question = None
        else:
            _maze_feedback = "incorrecto"; _maze_feedback_timer = 80
    else:
        if _maze_active_question2 is None: return
        q_data = _maze_questions[_maze_active_question2["q_index"]]
        correct = q_data["a"]
        correct_word = q_data["opts"][correct]
        # Reproducir sonido de la respuesta correcta siempre
        try: play_english_word(correct_word)
        except Exception: pass
        if _maze_selected_opt2 == correct:
            _maze_feedback2 = "correcto"; _maze_feedback_timer2 = 120
            _maze_active_question2["collected"] = True; _maze_active_question2 = None
        else:
            _maze_feedback2 = "incorrecto"; _maze_feedback_timer2 = 80


def _maze_update_movement():
    global _maze_player_x, _maze_player_z, _maze_facing
    global _maze_player2_x, _maze_player2_z, _maze_player2_facing
    global _maze_active_question, _maze_active_question2, _current_screen
    global _maze_input_text, _maze_input_text2
    global _maze_feedback, _maze_feedback_timer, _maze_feedback2, _maze_feedback_timer2
    global _maze_time_left, _maze_selected_opt, _maze_selected_opt2
    global _maze_time_start
    import math as _math
    now = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    # Inicializar timer en el primer frame de render (evita problemas en callback de teclado)
    if _maze_time_start < 0:
        _maze_time_start = now
    _maze_time_left = max(0.0, _MAZE_TIME_LIMIT - (now - _maze_time_start))
    if _maze_time_left <= 0:
        try: stop_maze_music()
        except Exception: pass
        _current_screen = "maze_end"; return
    if _maze_feedback_timer > 0:
        _maze_feedback_timer -= 1
        if _maze_feedback_timer == 0: _maze_feedback = ""
    if _maze_feedback_timer2 > 0:
        _maze_feedback_timer2 -= 1
        if _maze_feedback_timer2 == 0: _maze_feedback2 = ""
    if _maze_active_question is None:
        spd = _maze_speed; rad = _math.radians(_maze_facing)
        nx = _maze_player_x; nz = _maze_player_z
        if _maze_keys.get('up'):    nx -= _math.sin(rad)*spd; nz -= _math.cos(rad)*spd
        if _maze_keys.get('down'):  nx += _math.sin(rad)*spd; nz += _math.cos(rad)*spd
        if _maze_keys.get('left'):  _maze_facing -= 2.5
        if _maze_keys.get('right'): _maze_facing += 2.5
        if not check_maze_collision(nx, _maze_player_z): _maze_player_x = nx
        if not check_maze_collision(_maze_player_x, nz): _maze_player_z = nz
        for item in _maze_items:
            if item["collected"]: continue
            dx = _maze_player_x - item["wx"]; dz = _maze_player_z - item["wz"]
            if dx*dx + dz*dz < 2.5:
                _maze_active_question = item; _maze_input_text = ""; _maze_selected_opt = 0; break
        gx, gz = get_goal_pos()
        if (_maze_player_x-gx)**2 + (_maze_player_z-gz)**2 < 3.0:
            try: stop_maze_music()
            except Exception: pass
            _current_screen = "maze_end"; return
    if _maze_mp_mode and _maze_active_question2 is None:
        spd = _maze_speed; rad2 = _math.radians(_maze_player2_facing)
        nx2 = _maze_player2_x; nz2 = _maze_player2_z
        if _maze_keys2.get('up'):    nx2 -= _math.sin(rad2)*spd; nz2 -= _math.cos(rad2)*spd
        if _maze_keys2.get('down'):  nx2 += _math.sin(rad2)*spd; nz2 += _math.cos(rad2)*spd
        if _maze_keys2.get('left'):  _maze_player2_facing -= 2.5
        if _maze_keys2.get('right'): _maze_player2_facing += 2.5
        if not check_maze_collision(nx2, _maze_player2_z): _maze_player2_x = nx2
        if not check_maze_collision(_maze_player2_x, nz2): _maze_player2_z = nz2
        for item in _maze_items2:
            if item["collected"]: continue
            dx = _maze_player2_x - item["wx"]; dz = _maze_player2_z - item["wz"]
            if dx*dx + dz*dz < 2.5:
                _maze_active_question2 = item; _maze_input_text2 = ""; _maze_selected_opt2 = 0; break
        gx, gz = get_goal_pos()
        if (_maze_player2_x-gx)**2 + (_maze_player2_z-gz)**2 < 3.0:
            try: stop_maze_music()
            except Exception: pass
            _current_screen = "maze_end"; return


def _draw_maze_question_overlay(W, H, player=1, offset_x=0):
    import math as _math
    active  = _maze_active_question  if player == 1 else _maze_active_question2
    sel_opt = _maze_selected_opt     if player == 1 else _maze_selected_opt2
    fb      = _maze_feedback         if player == 1 else _maze_feedback2
    if active is None: return
    q_data = _maze_questions[active["q_index"]]
    question = q_data["q"]; hint = q_data["hint"]; opts = q_data["opts"]
    full_W = glutGet(GLUT_WINDOW_WIDTH); full_H = glutGet(GLUT_WINDOW_HEIGHT)
    _enter_2d(full_W, full_H)
    cx = offset_x + W // 2; cy = full_H // 2
    pw, ph = min(520, W - 20), 280; px = cx - pw // 2; py = cy - ph // 2
    
    # Fondo claro para texto negro
    border_col = (0.20, 0.60, 0.20) if player == 1 else (0.20, 0.40, 0.80)
    _rect_filled(px, py, pw, ph, 0.95, 0.95, 0.95, 0.95)
    _rect_border(px, py, pw, ph, *border_col, 4.0)
    
    label = f"[ J{player} PREGUNTA ]"
    iw = _str_width_18(label)
    _text18(cx - iw // 2, py + ph - 30, label, border_col)
    
    qw = _str_width_12(question)
    _text(cx - qw // 2, py + ph - 62, question, (0.0, 0.0, 0.0))
    hw = _str_width_12("Pista: " + hint)
    _text(cx - hw // 2, py + ph - 82, "Pista: " + hint, (0.2, 0.2, 0.2))
    
    opt_labels = ["1", "2", "3", "4"] if player == 1 else ["5", "6", "7", "8"]; opt_w = (pw - 40) // 2; opt_h = 34
    positions = [(px+20, py+108), (px+20+opt_w+8, py+108), (px+20, py+68), (px+20+opt_w+8, py+68)]
    for i, (opt, (ox, oy)) in enumerate(zip(opts, positions)):
        is_sel = (i == sel_opt)
        bg_col = (0.7, 0.9, 0.7, 1.0) if is_sel else (0.85, 0.85, 0.85, 1.0)
        bd_col = (0.3, 0.8, 0.3) if is_sel else (0.5, 0.5, 0.5)
        _rect_filled(ox, oy, opt_w, opt_h, *bg_col)
        _rect_border(ox, oy, opt_w, opt_h, *bd_col, 2.5 if is_sel else 1.5)
        key_lbl = f"{opt_labels[i]}. {opt}"; tw2 = _str_width_12(key_lbl)
        tc = (0.0, 0.0, 0.0)
        _text(ox + opt_w // 2 - tw2 // 2, oy + opt_h // 2 - 5, key_lbl, tc)
        
    if fb == "correcto":   fb_c = (0.1, 0.7, 0.1); fb_t = "CORRECTO!"
    elif fb == "incorrecto": fb_c = (0.8, 0.1, 0.1); fb_t = "INCORRECTO"
    else: fb_t = ""; fb_c = (0,0,0)
    
    if fb_t:
        fw = _str_width_12(fb_t)
        _text(cx - fw // 2, py + 50, fb_t, fb_c)
        
    keys_hint = "Elige: 1/2/3/4 | ENTER confirmar" if player == 1 else "Elige: 5/6/7/8 | ENTER confirmar"
    hw2 = _str_width_12(keys_hint)
    _text(cx - hw2 // 2, py + 28, keys_hint, (0.3, 0.3, 0.3))
    
    _exit_2d()

def _draw_maze_instructions():
    W = glutGet(GLUT_WINDOW_WIDTH)
    H = glutGet(GLUT_WINDOW_HEIGHT)
    _enter_2d(W, H)
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    _rect_filled(0, 0, W, H, 0.05, 0.15, 0.05, 0.85)
    glDisable(GL_BLEND)

    cx = W // 2
    cy = H // 2

    title = "* LABERINTO MULTIJUGADOR *"
    tw = _str_width_18(title)
    _text18(cx - tw // 2, cy + 100, title, (0.4, 1.0, 0.4))

    lines = [
        "Camina por el laberinto en 1ra persona.",
        "Toca los objetos brillantes y responde las",
        "preguntas de inglés para recogerlos.",
        "",
        "J1: W/A/S/D | Respuestas: 1/2/3/4",
        "J2: Flechas | Respuestas: 5/6/7/8",
        "",
        "Llega al octaedro DORADO para ganar."
    ]
    
    y = cy + 40
    for line in lines:
        lw = _str_width_12(line)
        _text(cx - lw // 2, y, line, (0.8, 0.95, 0.8))
        y -= 25

    btn = ">> PRESIONA ENTER PARA COMENZAR <<"
    bw = _str_width_12(btn)
    _text(cx - bw // 2, 30, btn, (1.0, 0.85, 0.25))

    _exit_2d()


def _draw_maze_hud(W, H):
    items_collected = sum(1 for it in _maze_items if it["collected"])
    total_items = len(_maze_items)
    _enter_2d(W, H)
    mins = int(_maze_time_left) // 60; secs = int(_maze_time_left) % 60
    timer_str = f"TIEMPO: {mins}:{secs:02d}"
    timer_col = (1.0, 0.2, 0.2) if _maze_time_left < 30 else (1.0, 1.0, 0.3)
    char_ids = [c[0] for c in CHARS]; char_names = [c[1] for c in CHARS]
    name1 = char_names[char_ids.index(_maze_char_id)]
    if not _maze_mp_mode:
        # ── HUD individual: centrado ──
        tw = _str_width_18(timer_str)
        _text18(W // 2 - tw // 2, H - 22, timer_str, timer_col)
        _text(10, H - 20, f"Personaje: {name1}", (0.8, 1.0, 0.8))
        _text(10, H - 36, f"Objetos: {items_collected}/{total_items}", (1.0, 1.0, 0.6))
        _text(10, H - 52, "WASD: mover/girar  ESC: salir", (0.6, 0.7, 0.6))
        _text(10, H - 68, "I=Info  M=Musica  META: octaedro DORADO", (1.0, 0.85, 0.3))
        try:
            music_lbl = "Musica: ON" if is_maze_music_on() else "Musica: OFF"
            _text(10, H - 84, music_lbl, (1.0, 0.85, 0.3))
        except Exception: pass
        if _maze_feedback == "correcto":   _text18(W // 2 - 50, H // 2 + 20, "CORRECTO!", (0.2, 1.0, 0.2))
        elif _maze_feedback == "incorrecto": _text(W // 2 - 80, H // 2 + 20, "INCORRECTO", (1.0, 0.3, 0.3))
    else:
        # ── HUD multijugador: pantalla dividida ──
        name2 = char_names[char_ids.index(_maze_char_id2)]
        c1 = sum(1 for it in _maze_items  if it["collected"])
        c2 = sum(1 for it in _maze_items2 if it["collected"])
        tw = _str_width_18(timer_str)
        _text18(W // 2 - tw // 2, H // 2 - 14, timer_str, timer_col)
        _text(10, H // 2 - 20, f"J1 {name1}: {c1}/{total_items}", (0.5, 1.0, 0.5))
        _text(10, H // 2 - 36, "WASD: mover/girar  I=Info  M=Musica", (0.6, 0.7, 0.6))
        _text(10, H // 2 - 52, "META: llega al octaedro DORADO", (1.0, 0.85, 0.3))
        _text(W // 2 + 10, H - 20, f"J2 {name2}: {c2}/{total_items}", (0.5, 0.7, 1.0))
        _text(W // 2 + 10, H - 36, "Flechas: mover/girar  P=Info  M=Musica", (0.5, 0.6, 0.8))
        try:
            music_str2 = "Musica: ON" if is_maze_music_on() else "Musica: OFF"
            _text(10, H // 2 - 68, music_str2, (1.0, 0.85, 0.3))
        except Exception: pass
        _text(W // 2 + 10, H - 52, "META: llega al octaedro DORADO", (1.0, 0.85, 0.3))
        if _maze_feedback == "correcto":   _text18(W // 4 - 50, H // 2 + 20, "CORRECTO!", (0.2, 1.0, 0.2))
        elif _maze_feedback == "incorrecto": _text(W // 4 - 80, H // 2 + 20, "INCORRECTO", (1.0, 0.3, 0.3))
        if _maze_feedback2 == "correcto":  _text18(W*3//4-50, H // 2 + 20, "CORRECTO!", (0.2, 1.0, 0.2))
        elif _maze_feedback2 == "incorrecto": _text(W*3//4-80, H // 2 + 20, "INCORRECTO", (1.0, 0.3, 0.3))
    _exit_2d()


def _draw_maze_items_3d(items, t):
    import math as _math
    q2 = gluNewQuadric()
    for item in items:
        if item["collected"]: continue
        bob = 0.8 + _math.sin(t * 2.0 + item["row"]) * 0.2
        glPushMatrix(); glTranslatef(item["wx"], bob, item["wz"])
        glRotatef(t * 90 + item["row"] * 17, 0, 1, 0)
        glColor3f(0.8, 0.2, 1.0); glScalef(0.5, 0.5, 0.5); glutSolidOctahedron(); glPopMatrix()
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glPushMatrix(); glTranslatef(item["wx"], bob, item["wz"])
        glColor4f(0.8, 0.3, 1.0, 0.18); gluSphere(q2, 0.8, 10, 8); glPopMatrix()
        glDisable(GL_BLEND)
    gluDeleteQuadric(q2)


def _draw_maze_viewport(vx, vy, vw, vh, px, pz, facing, items):
    glViewport(vx, vy, vw, vh)
    glMatrixMode(GL_PROJECTION); glLoadIdentity()
    gluPerspective(70.0, vw / max(vh, 1), 0.05, 200.0)
    glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    glScissor(vx, vy, vw, vh); glEnable(GL_SCISSOR_TEST)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    draw_maze_fp_camera(px, pz, facing)
    draw_maze_scenario()
    t = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    _draw_maze_items_3d(items, t)
    glDisable(GL_SCISSOR_TEST)


def _draw_maze_game():
    _maze_update_movement()
    W = glutGet(GLUT_WINDOW_WIDTH); H = glutGet(GLUT_WINDOW_HEIGHT)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glDisable(GL_LIGHTING)
    if _maze_mp_mode:
        # ── Pantalla dividida: Jugador 1 izquierda, Jugador 2 derecha ──
        half = W // 2
        _draw_maze_viewport(0, 0, half - 2, H, _maze_player_x, _maze_player_z, _maze_facing, _maze_items)
        _draw_maze_viewport(half + 2, 0, half - 2, H, _maze_player2_x, _maze_player2_z, _maze_player2_facing, _maze_items2)
        glViewport(0, 0, W, H); glDisable(GL_SCISSOR_TEST)
        glMatrixMode(GL_PROJECTION); glLoadIdentity(); glOrtho(0, W, 0, H, -1, 1)
        glMatrixMode(GL_MODELVIEW); glLoadIdentity()
        glDisable(GL_DEPTH_TEST); glColor3f(0.0, 0.0, 0.0)
        glBegin(GL_QUADS)
        glVertex2f(half-2, 0); glVertex2f(half+2, 0)
        glVertex2f(half+2, H); glVertex2f(half-2, H)
        glEnd()
        glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING)
        _draw_maze_hud(W, H)
        if _maze_active_question  is not None: _draw_maze_question_overlay(W // 2, H, player=1)
        if _maze_active_question2 is not None: _draw_maze_question_overlay(W // 2, H, player=2, offset_x=W // 2)
        if _show_level_info_p1: _draw_level_info_panel(W // 2, H, player=1, offset_x=0, game_type='maze')
        if _show_level_info_p2: _draw_level_info_panel(W // 2, H, player=2, offset_x=W // 2, game_type='maze')
    else:
        # ── Modo individual: pantalla completa ──
        glViewport(0, 0, W, H)
        glMatrixMode(GL_PROJECTION); glLoadIdentity()
        gluPerspective(70.0, W / max(H, 1), 0.05, 200.0)
        glMatrixMode(GL_MODELVIEW); glLoadIdentity()
        draw_maze_fp_camera(_maze_player_x, _maze_player_z, _maze_facing)
        draw_maze_scenario()
        t = glutGet(GLUT_ELAPSED_TIME) / 1000.0
        _draw_maze_items_3d(_maze_items, t)
        glEnable(GL_LIGHTING)
        _draw_maze_hud(W, H)
        if _maze_active_question is not None: _draw_maze_question_overlay(W, H)
        if _show_level_info_p1: _draw_level_info_panel(W, H, player=1, offset_x=0, game_type='maze_sp')


def _draw_maze_end_screen():
    # Asegurar que la música pare al llegar a esta pantalla
    try: stop_maze_music()
    except Exception: pass
    import math as _math
    W = glutGet(GLUT_WINDOW_WIDTH); H = glutGet(GLUT_WINDOW_HEIGHT)
    _enter_2d(W, H)
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBegin(GL_QUADS); glColor4f(0.02, 0.05, 0.02, 0.95)
    glVertex2f(0,0); glVertex2f(W,0); glVertex2f(W,H); glVertex2f(0,H); glEnd()
    glDisable(GL_BLEND)
    GOLD = (1.00, 0.85, 0.25); GREEN = (0.30, 0.90, 0.30); BLUE = (0.40, 0.70, 1.00)
    cx = W // 2; t = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    pulse = (_math.sin(t * 3.0) + 1.0) / 2.0
    total_items = len(_maze_items)
    char_ids = [c[0] for c in CHARS]; char_names = [c[1] for c in CHARS]
    name1 = char_names[char_ids.index(_maze_char_id)]
    if _maze_mp_mode:
        # ── Resultados multijugador ──
        c1 = sum(1 for it in _maze_items  if it["collected"])
        c2 = sum(1 for it in _maze_items2 if it["collected"])
        name2 = char_names[char_ids.index(_maze_char_id2)]
        if c1 > c2:   winner = f"GANA {name1}!"; winner_col = GREEN
        elif c2 > c1: winner = f"GANA {name2}!"; winner_col = BLUE
        else:         winner = "EMPATE!";         winner_col = GOLD
        tw = _str_width_18(winner)
        _text18(cx - tw // 2, H - 100, winner,
                (winner_col[0]*0.5 + pulse*winner_col[0]*0.5, winner_col[1]*0.5 + pulse*winner_col[1]*0.5, winner_col[2]))
        sub = "LABERINTO COMPLETADO — Resultados:"; sw = _str_width_18(sub)
        _text18(cx - sw // 2, H - 140, sub, GOLD)
        s1 = f"{name1}: {c1}/{total_items} objetos"; s2 = f"{name2}: {c2}/{total_items} objetos"
        _text18(cx - _str_width_18(s1) // 2, H // 2 + 60, s1, GREEN)
        _text18(cx - _str_width_18(s2) // 2, H // 2 + 30, s2, BLUE)
    else:
        # ── Resultados un jugador ──
        items_collected = sum(1 for it in _maze_items if it["collected"])
        title = "FELICIDADES!"
        tw = _str_width_18(title)
        _text18(cx - tw // 2, H - 120, title, (0.3 + pulse * 0.7, 1.0, 0.3))
        sub = "Llegaste al final del laberinto"
        sw = _str_width_18(sub)
        _text18(cx - sw // 2, H - 160, sub, GOLD)
        score_txt = f"Objetos encontrados: {items_collected} / {total_items}"
        stw = _str_width_18(score_txt)
        _text18(cx - stw // 2, H // 2 + 40, score_txt, (0.8, 1.0, 0.8))
    bx = cx - 180; by = H // 2 - 80; bw, bh = 360, 70
    _rect_filled(bx, by, bw, bh, 0.05, 0.25, 0.05, 0.80)
    _rect_border(bx, by, bw, bh, 0.30 + pulse * 0.70, 1.00, 0.30, 3.0)
    lbl = "VOLVER AL MENU"; lw = _str_width_18(lbl)
    _text18(cx - lw // 2, by + bh // 2 - 8, lbl, GREEN)
    hint = "Presiona ENTER o CLICK para continuar"; hw = _str_width_12(hint)
    _text(cx - hw // 2, 30, hint, (0.60, 0.65, 0.60))
    _exit_2d()


# -----------------------------------------------------------------------
#  Inicializacion OpenGL
# -----------------------------------------------------------------------
def init():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_NORMALIZE)

    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, [2.0,  10.0,  8.0, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.30, 0.30, 0.30, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [0.75, 0.75, 0.75, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.30, 0.30, 0.30, 1.0])

    glEnable(GL_LIGHT1)
    glLightfv(GL_LIGHT1, GL_POSITION, [-5.0, 5.0, -4.0, 1.0])
    glLightfv(GL_LIGHT1, GL_AMBIENT,  [0.15, 0.15, 0.20, 1.0])
    glLightfv(GL_LIGHT1, GL_DIFFUSE,  [0.40, 0.40, 0.45, 1.0])
    glLightfv(GL_LIGHT1, GL_SPECULAR, [0.10, 0.10, 0.10, 1.0])

    glEnable(GL_LIGHT2)
    glLightfv(GL_LIGHT2, GL_POSITION, [0.0, 2.0, 8.0, 1.0])
    glLightfv(GL_LIGHT2, GL_AMBIENT,  [0.10, 0.10, 0.10, 1.0])
    glLightfv(GL_LIGHT2, GL_DIFFUSE,  [0.25, 0.25, 0.25, 1.0])
    glLightfv(GL_LIGHT2, GL_SPECULAR, [0.0,  0.0,  0.0,  1.0])

    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR,  [0.60, 0.70, 0.80, 1.0])
    glMaterialf (GL_FRONT_AND_BACK, GL_SHININESS,  48.0)
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT,   [0.45, 0.45, 0.50, 1.0])


# -----------------------------------------------------------------------
#  Bucle de renderizado
# -----------------------------------------------------------------------
def display():
    global _current_screen
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Pantalla de Tira de la Cuerda
    if _current_screen == "rope_pull":
        _draw_rope_pull_game()
        glutSwapBuffers()
        return

    # Laberinto en juego
    if _current_screen == "maze_game":
        try:
            if getattr(state, 'maze_show_instructions', False):
                _draw_maze_instructions()
                glutSwapBuffers()
                return
            _draw_maze_game()
        except Exception as _e:
            import traceback; traceback.print_exc()
            print(f"[DEBUG-display] EXCEPCION en _draw_maze_game: {_e}")
            _current_screen = "endgame_menu"; state.en_menu = True
        glutSwapBuffers()
        return

    # Pantalla final del laberinto
    if _current_screen == "maze_end":
        glClearColor(0.02, 0.05, 0.02, 1.0)
        try:
            _draw_maze_end_screen()
        except Exception as _e:
            import traceback; traceback.print_exc()
            _current_screen = "endgame_menu"; state.en_menu = True
        glutSwapBuffers()
        return

    # Menú principal y selecciones
    if state.en_menu or _current_screen in (
        "endgame_menu", "laberinto_mode", "info_screen",
        "char_select_mp", "char_select_1p", "char_select_maze", "char_select_maze_mp"
    ):
        glClearColor(0.02, 0.02, 0.08, 1.0)
        draw_menu()
        glutSwapBuffers()
        return

    # Gameplay normal
    input_handlers.apply_shade_mode()
    camera.apply_camera()
    draw_scenario()
    draw_grid(size=25, step=2)
    Kirby.draw_weather()

    _draw_obb_tree()
    _draw_cristal()

    _CHAR_Y_OFFSET = {
        "pucca":   1.15,
        "pochaco": 0.95,
        "kirby":   0.80,
        "dee":     0.80,
        "optimus": 1.90,
        "plasma":  1.15,
    }
    y_off = _CHAR_Y_OFFSET.get(state.personaje_activo, 0.15)

    glPushMatrix()
    glTranslatef(state.fox_x, state.fox_y + y_off, state.fox_z)
    glRotatef(state.fox_facing, 0, 1, 0)
    if state.is_spinning:
        glRotatef(state.spin_angle, 0, 1, 0)

    if   state.personaje_activo == "plasma":  plasma_pea.draw_plasma_pea()
    elif state.personaje_activo == "optimus": optimusPrime.draw_optimus_full()
    elif state.personaje_activo == "dee":     Dee.draw_dee_magician()
    elif state.personaje_activo == "kirby":   Kirby.draw_kirby_magician()
    elif state.personaje_activo == "pochaco": Pochacco3D.draw_fox_full()
    elif state.personaje_activo == "pucca":   Pucca3D.draw_pucca()

    glPopMatrix()

    check_all_collisions()
    draw_bounding_volumes()
    
    # ── Dibujar al Jugador 2 si es Tetris 2P ──
    if state.escenario_actual == 7 and state.tetris_2p:
        glPushMatrix()
        c2 = _mp_char_2
        y_off_2 = _CHAR_Y_OFFSET.get(c2, 0.15)
        glTranslatef(state.p2_x, state.p2_y + y_off_2, state.p2_z)
        glRotatef(state.p2_facing, 0, 1, 0)
        # Reutilizamos _mp_char_2 para saber qué personaje pintar
        if c2 == "plasma":   plasma_pea.draw_plasma_pea()
        elif c2 == "optimus": optimusPrime.draw_optimus_full()
        elif c2 == "dee":     Dee.draw_dee_magician()
        elif c2 == "kirby":   Kirby.draw_kirby_magician()
        elif c2 == "pochaco": Pochacco3D.draw_fox_full()
        elif c2 == "pucca":   Pucca3D.draw_pucca()
        glPopMatrix()

    if state.escenario_actual == 7:
        if state.tetris_show_instructions:
            _draw_tetris_instructions()
        else:
            draw_hud_tetris()
            
        if state.tetris_ganado:
            W = glutGet(GLUT_WINDOW_WIDTH)
            H = glutGet(GLUT_WINDOW_HEIGHT)
            _enter_2d(W, H)
            cx = W // 2
            cy = H // 2
            win_msg = f"¡JUGADOR {state.tetris_winner} GANA!"
            ww = _str_width_18(win_msg)
            _rect_filled(cx - ww//2 - 20, cy - 30, ww + 40, 60, 0, 0, 0, 0.7)
            _text18(cx - ww//2, cy - 8, win_msg, (1.0, 0.85, 0.25))
            _exit_2d()

        # Paneles de info en tetris (tecla I=J1, P=J2)
        if _show_level_info_p1:
            W2 = glutGet(GLUT_WINDOW_WIDTH)
            H2 = glutGet(GLUT_WINDOW_HEIGHT)
            gt = 'sequential' if _game_flow == 'sequential' else 'tetris'
            _draw_level_info_panel(W2 // 2, H2, player=1, offset_x=0, game_type=gt)
        if _show_level_info_p2:
            W2 = glutGet(GLUT_WINDOW_WIDTH)
            H2 = glutGet(GLUT_WINDOW_HEIGHT)
            gt = 'sequential' if _game_flow == 'sequential' else 'tetris'
            _draw_level_info_panel(W2 // 2, H2, player=2, offset_x=W2 // 2, game_type=gt)

        # Verificar victoria del Tetris para pasar al siguiente juego según _game_flow
        if state.tetris_ganado and state.tetris_2p and state.tetris_ganado_timer <= 0:
            if _game_flow == "sequential":
                # Secuencial: Tetris -> Cuerda -> Laberinto
                print(f"[Tetris] Ganador P{state.tetris_winner}. Pasando a Rope Pull (secuencial)...")
                game = rope_pull_game.game_instance
                game.active = True
                game.char1_id = _mp_char_1
                game.char2_id = _mp_char_2
                game.char1_name = CHARS[[c[0] for c in CHARS].index(_mp_char_1)][1]
                game.char2_name = CHARS[[c[0] for c in CHARS].index(_mp_char_2)][1]
                game.show_instructions = True
                game.next_screen_after = "maze_mp"
                _current_screen = "rope_pull"
                state.escenario_actual = 1
                audio.play_rope_music()
            else:
                # tetris_2p puro (NIVEL 1): al terminar volver al menú END GAME
                print(f"[Tetris] Ganador P{state.tetris_winner}. Volviendo al menú principal...")
                try: stop_bg_music()
                except Exception: pass
                _reset_full_state()
                _current_screen = "endgame_menu"
                state.en_menu = True
    else:
        draw_hud()
        
    glutSwapBuffers()


def reshape(w, h):
    if h == 0: h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, w/h, 0.1, 120.0)
    glMatrixMode(GL_MODELVIEW)


# -----------------------------------------------------------------------
#  Reset completo
# -----------------------------------------------------------------------
def _reset_full_state():
    state.fox_x = 0.0; state.fox_y = 0.0; state.fox_z = 0.0
    state.fox_facing = 0.0; state.rotate_x = 0.0
    state.key_up = state.key_down = state.key_left = state.key_right = False

    state.is_walking = False; state.is_jumping = False
    state.is_shooting = False; state.is_victory = False
    state.is_spinning = False; state.is_greeting = False
    state.is_crouching = False
    state.jump_time = 0.0; state.spin_angle = 0.0
    state.spin_timer = 0; state.greet_timer = 0
    state.victory_timer = 0; state.shoot_timer = 0

    state.plasma_visible = False; state.plasma_scale = 0.0
    state.canon_x = 0.0; state.cabeza_y = 0.0; state.cabeza_x = 0.0
    state.hoja_izq_z = state.hoja_der_z = 0.0
    state.hoja_izq_y = state.hoja_der_y = 0.0
    state.raiz_izq_x = state.raiz_der_x = 0.0

    state.opt_cannon_visible = False; state.opt_cannon_scale = 0.0
    state.opt_cannon_glow = 0.0; state.opt_cannon_recoil = 0.0
    state.brazo_izq_x = state.brazo_der_x = 0.0
    state.pierna_izq_x = state.pierna_der_x = 0.0

    state.zombie_activo = True; state.caja_activa = True
    state.obb_activo = True; state.cristal_activo = True
    state.zombie_hit = False; state.caja_hit = False
    state.valla_hit = False; state.obb_hit = False; state.cristal_hit = False
    state.zombie_hit_timer = 0; state.caja_hit_timer = 0
    state.obb_hit_timer = 0; state.cristal_hit_timer = 0
    if hasattr(state, 'valla_hit_timer'): state.valla_hit_timer = 0
    state.collision_color_override = None; state.collision_flash_timer = 0

    state.expresion_actual = "normal"; state.expression = "normal"
    state.ojo_escala_izq = state.ojo_escala_der = 1.0
    state.ojo_offset_y_izq = state.ojo_offset_y_der = 0.0
    state.ojo_color = (0.4, 0.9, 1.0)
    state.ceja_rot_izq = state.ceja_rot_der = 0.0
    state.ceja_offset_y = 0.0; state.boca_escala_y = 1.0
    state.boca_curva = 0.0; state.boca_abierta = False
    state.color_ojos = (0.1, 0.8, 1.0); state.ojo_izq_escala = 1.0
    state.color_flash_timer = 0; state.current_color_idx = 0
    state.arm_angle = 0.0; state.foot_angle = 0.0
    state.mouth_scale = 1.0; state.ojos_abiertos = True
    state.reaction_type = "normal"
    state.particles = []; state.weather_particles = []

    state.escenario_actual = 1; state.current_scene = 1
    camera.reset_camera()
    state.show_instructions = False; state.show_about = False
    state.tetris_show_instructions = False
    global _show_level_info_p1, _show_level_info_p2
    _show_level_info_p1 = False; _show_level_info_p2 = False



def _enter_game(index):
    global _menu_state, _current_screen
    cid, name, _, _, esc = CHARS[index]
    _reset_full_state()
    state.personaje_activo = cid
    state.escenario_actual = 7
    state.current_scene    = 7
    state.tetris_2p        = False
    state.en_menu = False
    _menu_state = "browse"
    _current_screen = "gameplay"
    print(f"[Menu] Seleccionado: {name}  ->  Tetris (1P)")


def _preview_action(tecla):
    """Activa animacion de prueba (G=girar cabeza, X=saltar, B=saludar) en el panel de greeting."""
    if tecla == 'x':   # Saltar
        if not state.is_jumping:
            state.is_jumping = True
            state.jump_time  = 0.0
    elif tecla == 'b':  # Saludar
        if not state.is_greeting:
            state.is_greeting  = True
            state.greet_timer  = 80
    elif tecla == 'g':  # Girar cabeza
        state.cabeza_y = 45.0 if state.cabeza_y == 0.0 else 0.0


def _trigger_greeting(index):
    global _menu_state
    _menu_state = "greeting"
    state.menu_cursor_index = index
    state.is_greeting = True
    state.greet_timer = 90
    # Activar el personaje para que sus movimientos especiales funcionen
    state.personaje_activo = CHARS[index][0]
    print(f"[Menu] Saludando: {CHARS[index][1]}")


def _cancel_greeting():
    global _menu_state
    _menu_state = "browse"
    state.is_greeting = False; state.greet_timer = 0
    state.brazo_der_x = 0.0; state.hoja_der_y = 0.0
    state.personaje_activo = None
    print("[Menu] Seleccion cancelada")


# -----------------------------------------------------------------------
#  Helpers para navegación de menús END GAME
# -----------------------------------------------------------------------
def _handle_endgame_button_select():
    """Ejecuta la acción del botón seleccionado en el menú END GAME."""
    global _current_screen, _mp_char_1, _mp_char_2, _mp_selecting_player
    global _menu_state, _game_flow, _maze_mp_char1_selected

    i = _endgame_hover
    if i == 0:  # NIVEL 1 - Tetris (2 jugadores)
        _game_flow = "tetris_2p"
        _mp_char_1 = None; _mp_char_2 = None; _mp_selecting_player = 1
        state.menu_cursor_index = 0; _menu_state = "browse"
        _current_screen = "char_select_mp"
        state.en_menu = True
    elif i == 1:  # NIVEL 2 - Laberinto
        _current_screen = "laberinto_mode"
        state.en_menu = True
    elif i == 2:  # NIVEL 3 - Cuerda (2 jugadores)
        _game_flow = "rope_only"
        _mp_char_1 = None; _mp_char_2 = None; _mp_selecting_player = 1
        state.menu_cursor_index = 0; _menu_state = "browse"
        _current_screen = "char_select_mp"
        state.en_menu = True
    elif i == 3:  # Jugar Secuencialmente
        _game_flow = "sequential"
        _mp_char_1 = None; _mp_char_2 = None; _mp_selecting_player = 1
        state.menu_cursor_index = 0; _menu_state = "browse"
        _current_screen = "char_select_mp"
        state.en_menu = True
    elif i == 4:  # Informacion
        _current_screen = "info_screen"
        state.en_menu = True


def _handle_lab_button_select():
    """Ejecuta la acción del botón seleccionado en el submenú Laberinto."""
    global _current_screen, _mp_char_1, _mp_char_2, _mp_selecting_player
    global _menu_state, _game_flow, _maze_mp_char1_selected

    mode = _LAB_BUTTONS[_lab_hover]["mode"]
    if mode == "single":
        _game_flow = "maze_sp"
        state.menu_cursor_index = 0; _menu_state = "browse"
        _current_screen = "char_select_maze"
        state.en_menu = True
    else:  # multi
        _game_flow = "maze_mp"
        _mp_char_1 = None; _mp_char_2 = None; _mp_selecting_player = 1
        _maze_mp_char1_selected = None
        state.menu_cursor_index = 0; _menu_state = "browse"
        _current_screen = "char_select_maze_mp"
        state.en_menu = True


def _handle_char_confirm_keyboard():
    """Confirma selección de personaje según el flujo actual."""
    global _current_screen, _mp_char_1, _mp_char_2, _mp_selecting_player
    global _menu_state, _game_flow, _maze_mp_char1_selected

    screen = _current_screen
    idx    = state.menu_cursor_index
    cid    = CHARS[idx][0]

    # ─ Selección individual (laberinto 1P o selección 1P tetris) ─
    if screen == "char_select_maze":
        _start_maze_sp_game(cid)
        _menu_state = "browse"
        return

    # ─ Selección multijugador laberinto ─
    if screen == "char_select_maze_mp":
        if _mp_selecting_player == 1:
            _maze_mp_char1_selected = cid
            _mp_selecting_player = 2
            _menu_state = "browse"
            state.menu_cursor_index = 0
        else:
            _start_maze_mp_game(_maze_mp_char1_selected, cid)
            _menu_state = "browse"
        return

    # ─ Selección 2 jugadores (Tetris, Cuerda, Secuencial) ─
    if screen in ("char_select_mp", "char_select_1p"):
        if _mp_selecting_player == 1:
            _mp_char_1 = cid
            _mp_selecting_player = 2
            _menu_state = "browse"
            state.menu_cursor_index = 0
            _cancel_greeting()
            print(f"[Menu] Seleccionado P1: {_mp_char_1}")
        else:
            _mp_char_2 = cid
            _launch_two_player_game()
        return

    # ─ Fallback: flujo heredado ─
    if _mp_selecting_player == 1:
        _mp_char_1 = cid
        _mp_selecting_player = 2
        _menu_state = "browse"
        state.menu_cursor_index = 0
        _cancel_greeting()
    else:
        _mp_char_2 = cid
        _launch_two_player_game()


def _launch_two_player_game():
    """Lanza el juego correcto para 2 jugadores según _game_flow."""
    global _current_screen, _menu_state, _game_flow
    _reset_full_state()
    _menu_state = "browse"

    if _game_flow == "tetris_2p":
        state.personaje_activo = _mp_char_1
        state.escenario_actual = 7; state.current_scene = 7
        state.tetris_2p = True; state.tetris_show_instructions = True
        state.en_menu = False
        _current_screen = "gameplay"
        audio.play_tetris_music()
        print(f"[Menu] Tetris 2P: {_mp_char_1} vs {_mp_char_2}")

    elif _game_flow == "rope_only":
        import Actions.rope_pull_game as rpg
        rpg.game_instance = rpg.RopePullGameState()
        game = rpg.game_instance
        game.active = True
        game.char1_id   = _mp_char_1
        game.char2_id   = _mp_char_2
        game.char1_name = CHARS[[c[0] for c in CHARS].index(_mp_char_1)][1]
        game.char2_name = CHARS[[c[0] for c in CHARS].index(_mp_char_2)][1]
        game.show_instructions = True
        game.next_screen_after = "endgame_menu"
        state.en_menu = False
        _current_screen = "rope_pull"
        audio.play_rope_music()
        print(f"[Menu] Cuerda: {_mp_char_1} vs {_mp_char_2}")

    elif _game_flow == "sequential":
        state.personaje_activo = _mp_char_1
        state.escenario_actual = 7; state.current_scene = 7
        state.tetris_2p = True; state.tetris_show_instructions = True
        state.en_menu = False
        _current_screen = "gameplay"
        audio.play_tetris_music()
        print(f"[Menu] Secuencial: Tetris -> Laberinto -> Cuerda con {_mp_char_1}/{_mp_char_2}")


def _handle_char_select_esc():
    """Maneja ESC desde pantalla de selección de personajes."""
    global _current_screen, _mp_char_1, _mp_char_2, _mp_selecting_player
    global _menu_state, _maze_mp_char1_selected

    screen = _current_screen
    if screen in ("char_select_maze", "char_select_maze_mp"):
        _current_screen = "laberinto_mode"
    else:
        _current_screen = "endgame_menu"

    _mp_char_1 = None; _mp_char_2 = None; _mp_selecting_player = 1
    _maze_mp_char1_selected = None
    _menu_state = "browse"
    state.en_menu = True


# -----------------------------------------------------------------------
#  Teclado
# -----------------------------------------------------------------------
def handle_keyboard(key, x, y):
    global _menu_state, _current_screen, _mp_char_1, _mp_char_2, _mp_selecting_player
    global _show_level_info_p1, _show_level_info_p2

    k = ord(key)
    
    # ── PANTALLA DE TIRA DE LA CUERDA ──
    if _current_screen == "rope_pull":
        game = rope_pull_game.game_instance

        # ESC: pausar / reanudar (si estamos en instrucciones, volver al menú)
        if k == 27:
            if game.show_instructions:
                _current_screen = "endgame_menu"
                state.en_menu = True
                rope_pull_game.game_instance = rope_pull_game.RopePullGameState()
                try: stop_bg_music()
                except Exception: pass
                glutPostRedisplay()
                return
            else:
                game.paused = not game.paused
                glutPostRedisplay()
                return

        # ENTER en instrucciones / fin de juego / pausa
        if game.show_instructions or game.game_over or game.paused:
            if k in (13, 10):  # ENTER
                if game.show_instructions:
                    game.show_instructions = False
                    game.reset()
                elif game.paused:
                    game.paused = False
                elif game.game_over:
                    # Decidir a dónde ir según el flujo actual
                    next_scr = getattr(game, 'next_screen_after', None)
                    if next_scr == "endgame_menu" or _game_flow == "rope_only":
                        # Solo cuerda: volver al menú principal
                        try: stop_bg_music()
                        except Exception: pass
                        rope_pull_game.game_instance = rope_pull_game.RopePullGameState()
                        _current_screen = "endgame_menu"; state.en_menu = True
                    else:
                        # Modo secuencial o directo: ir al Laberinto
                        print(f"[DEBUG] ENTER en game_over. _mp_char_1={_mp_char_1} _mp_char_2={_mp_char_2}")
                        try:
                            rope_pull_game.game_instance = rope_pull_game.RopePullGameState()
                            c1 = _mp_char_1 if _mp_char_1 is not None else CHARS[0][0]
                            c2 = _mp_char_2 if _mp_char_2 is not None else CHARS[1][0]
                            print(f"[DEBUG] Llamando _start_maze_mp_game({c1}, {c2})")
                            _start_maze_mp_game(c1, c2)
                            print(f"[DEBUG] Despues de start, _current_screen={_current_screen}")
                        except Exception as _e:
                            import traceback; traceback.print_exc()
                            _current_screen = "endgame_menu"; state.en_menu = True
            glutPostRedisplay()
            return

        # Durante el juego activo: entrada de texto
        if k in (13, 10):  # ENTER - enviar respuesta
            game.submit_answer()
        elif k == 8:  # Backspace - borrar último carácter
            game.player_input = game.player_input[:-1]
        elif 32 <= k <= 126:  # Caracteres imprimibles
            if len(game.player_input) < 60:
                game.player_input += chr(k)

        glutPostRedisplay()
        return

    # ── LABERINTO EN JUEGO ──
    if _current_screen == "maze_game":
        if getattr(state, 'maze_show_instructions', False):
            if k in (13, 10):  # ENTER
                state.maze_show_instructions = False
                # Start timing here if needed, handled by _maze_time_start < 0
            glutPostRedisplay()
            return
            
        # J1 usa WASD
        if k in (ord('w'), ord('W')): _maze_keys['up']    = True
        elif k in (ord('s'), ord('S')): _maze_keys['down'] = True
        elif k in (ord('a'), ord('A')): _maze_keys['right'] = True
        elif k in (ord('d'), ord('D')): _maze_keys['left'] = True
        # Tecla I: toggle panel info J1
        elif k in (ord('i'), ord('I')):
            _show_level_info_p1 = not _show_level_info_p1
            glutPostRedisplay(); return
        # Tecla P: toggle panel info J2
        elif k in (ord('p'), ord('P')):
            _show_level_info_p2 = not _show_level_info_p2
            glutPostRedisplay(); return
        _maze_handle_key(k)
        glutPostRedisplay(); return

    # ── PANTALLA FINAL DEL LABERINTO ──
    if _current_screen == "maze_end":
        if k in (13, 10, 27):
            try: stop_maze_music()
            except Exception: pass
            _current_screen = "endgame_menu"; state.en_menu = True; _init_maze()
        glutPostRedisplay(); return

    # ── MENÚ PRINCIPAL END GAME ──
    if _current_screen == "endgame_menu":
        if k in (13, 10):  # ENTER
            _handle_endgame_button_select()
        elif k == 27:
            pass  # ESC en menú raíz no hace nada
        glutPostRedisplay()
        return

    # ── SUBMENU LABERINTO ──
    if _current_screen == "laberinto_mode":
        if k == 27:
            _current_screen = "endgame_menu"
            glutPostRedisplay()
            return
        if k in (13, 10):
            _handle_lab_button_select()
        glutPostRedisplay()
        return

    # ── PANTALLA DE INFORMACION ──
    if _current_screen == "info_screen":
        if k in (27, 13, 10):
            _current_screen = "endgame_menu"
        glutPostRedisplay()
        return

    # ── SELECCIÓN DE PERSONAJES (todos los flujos) ──
    if _current_screen in ("char_select_mp", "char_select_1p", "char_select_maze", "char_select_maze_mp"):
        if _menu_state == "greeting":
            if k in (13, 10):  # ENTER - confirmar selección
                _handle_char_confirm_keyboard()
            elif k == 27:
                _menu_state = "browse"
            else:
                # G=Girar cabeza, X=Saltar, B=Saludar — activar animacion directamente
                try:
                    tecla = key.decode('utf-8').lower() if isinstance(key, bytes) else chr(k).lower()
                except Exception:
                    tecla = ''
                _preview_action(tecla)
            glutPostRedisplay()
            return
        else:
            if k in (13, 10):
                _trigger_greeting(state.menu_cursor_index)
            elif k == 27:
                _handle_char_select_esc()
            glutPostRedisplay()
            return

    # ── MENÚ PRINCIPAL (original, si quedara en_menu sin pantalla explícita) ──
    if state.en_menu:
        if _menu_state == "greeting":
            if k in (13, 10):
                _handle_char_confirm_keyboard()
            elif k == 27:
                _cancel_greeting()
            else:
                try:
                    tecla = key.decode('utf-8').lower() if isinstance(key, bytes) else chr(k).lower()
                except Exception:
                    tecla = ''
                _preview_action(tecla)
        else:
            if k in (13, 10):
                _trigger_greeting(state.menu_cursor_index)
        glutPostRedisplay()
        return
    
    # ── GAMEPLAY NORMAL ──
    if state.escenario_actual == 7 and state.tetris_show_instructions:
        if k in (13, 10):  # ENTER
            state.tetris_show_instructions = False
        glutPostRedisplay()
        return

    if k == 27:
        try: stop_bg_music()
        except Exception: pass
        try: stop_maze_music()
        except Exception: pass
        _reset_full_state()
        state.en_menu = True
        state.personaje_activo = None
        _menu_state = "browse"
        _current_screen = "endgame_menu"
        glutPostRedisplay()
        return
        
    # Controles P1 en Tetris con WASD
    if state.escenario_actual == 7 and state.tetris_2p:
        tecla = key.decode('utf-8').lower() if type(key) == bytes else key.lower()
        if tecla == 'a':
            state.key_left = True
        elif tecla == 'd':
            state.key_right = True
        # Panel de info J1 (tecla I) y J2 (tecla P) en tetris
        elif tecla == 'i':
            _show_level_info_p1 = not _show_level_info_p1
            glutPostRedisplay(); return
        elif tecla == 'p':
            _show_level_info_p2 = not _show_level_info_p2
            glutPostRedisplay(); return
    
    input_handlers.handle_keyboard(key, x, y)


def handle_keyboard_up(key, x, y):
    k = ord(key)
    # Laberinto: liberar WASD de J1
    if _current_screen == "maze_game":
        if k in (ord('w'), ord('W')): _maze_keys['up']    = False
        elif k in (ord('s'), ord('S')): _maze_keys['down'] = False
        elif k in (ord('a'), ord('A')): _maze_keys['right'] = False
        elif k in (ord('d'), ord('D')): _maze_keys['left'] = False
        glutPostRedisplay(); return
    # Tetris P1 (WASD)
    if state.escenario_actual == 7 and state.tetris_2p:
        try:
            tecla = key.decode('utf-8').lower() if type(key) == bytes else key.lower()
            if tecla == 'a': state.key_left = False
            elif tecla == 'd': state.key_right = False
        except: pass


def handle_special(key, x, y):
    global _menu_state, _current_screen, _mode_hover, _maze_selected_opt, _maze_selected_opt2, _endgame_hover, _lab_hover

    # ── Laberinto: flechas mueven siempre al J2 (respuestas: J1=1234, J2=5678) ──
    if _current_screen == "maze_game":
        if key == GLUT_KEY_UP:    _maze_keys2['up']    = True
        elif key == GLUT_KEY_DOWN:  _maze_keys2['down']  = True
        elif key == GLUT_KEY_LEFT:  _maze_keys2['right'] = True
        elif key == GLUT_KEY_RIGHT: _maze_keys2['left']  = True
        glutPostRedisplay(); return

    # ── Menú END GAME: flechas navegan botones ──
    if _current_screen == "endgame_menu":
        if key == GLUT_KEY_UP:
            _endgame_hover = max(0, _endgame_hover - 1)
        elif key == GLUT_KEY_DOWN:
            _endgame_hover = min(len(_ENDGAME_BUTTONS) - 1, _endgame_hover + 1)
        glutPostRedisplay()
        return

    # ── Submenú Laberinto ──
    if _current_screen == "laberinto_mode":
        if key == GLUT_KEY_UP:
            _lab_hover = max(0, _lab_hover - 1)
        elif key == GLUT_KEY_DOWN:
            _lab_hover = min(len(_LAB_BUTTONS) - 1, _lab_hover + 1)
        glutPostRedisplay()
        return

    # ── Selección de personajes (todos los flujos) ──
    if _current_screen in ("char_select_mp", "char_select_1p", "char_select_maze", "char_select_maze_mp"):
        if _menu_state == "browse":
            if   key == GLUT_KEY_RIGHT: state.menu_cursor_index = (state.menu_cursor_index + 1) % 6
            elif key == GLUT_KEY_LEFT:  state.menu_cursor_index = (state.menu_cursor_index - 1) % 6
            elif key == GLUT_KEY_DOWN:  state.menu_cursor_index = (state.menu_cursor_index + 3) % 6
            elif key == GLUT_KEY_UP:    state.menu_cursor_index = (state.menu_cursor_index - 3) % 6
        glutPostRedisplay()
        return

    # Menú principal / en_menu genérico
    if state.en_menu:
        if _menu_state == "browse":
            if   key == GLUT_KEY_RIGHT: state.menu_cursor_index = (state.menu_cursor_index+1)%6
            elif key == GLUT_KEY_LEFT:  state.menu_cursor_index = (state.menu_cursor_index-1)%6
            elif key == GLUT_KEY_DOWN:  state.menu_cursor_index = (state.menu_cursor_index+3)%6
            elif key == GLUT_KEY_UP:    state.menu_cursor_index = (state.menu_cursor_index-3)%6
        glutPostRedisplay()
        return
    # Flechas mueven P2 en Tetris 2P
    if state.escenario_actual == 7 and state.tetris_2p:
        if key == GLUT_KEY_LEFT:  state.p2_key_left  = True
        elif key == GLUT_KEY_RIGHT: state.p2_key_right = True
        # Panel de info J2 en tetris (tecla P via handle_keyboard)
        glutPostRedisplay(); return
    input_handlers.handle_special_down(key, x, y)


def handle_special_up(key, x, y):
    """Libera teclas de flecha al soltar (laberinto J1)."""
    if _current_screen == "maze_game":
        # J2 usa flechas
        if key == GLUT_KEY_UP:    _maze_keys2['up']    = False
        elif key == GLUT_KEY_DOWN:  _maze_keys2['down']  = False
        elif key == GLUT_KEY_LEFT:  _maze_keys2['right'] = False
        elif key == GLUT_KEY_RIGHT: _maze_keys2['left']  = False
        return
    # Tetris P2: liberar flechas
    if state.escenario_actual == 7 and state.tetris_2p:
        if key == GLUT_KEY_LEFT:  state.p2_key_left  = False
        elif key == GLUT_KEY_RIGHT: state.p2_key_right = False
        return
    input_handlers.handle_special_up(key, x, y)

# -----------------------------------------------------------------------
#  Mouse
# -----------------------------------------------------------------------
def handle_mouse(button, btn_state, x, y):
    global _hover_index, _menu_state, _current_screen, _mp_char_1, _mp_char_2, _mp_selecting_player
    global _endgame_hover, _lab_hover

    # Desactivar mouse durante mini-juego rope_pull
    if _current_screen == "rope_pull":
        return

    # Pantalla final laberinto: click para volver
    if _current_screen == "maze_end":
        if button == GLUT_LEFT_BUTTON and btn_state == GLUT_DOWN:
            try: stop_maze_music()
            except Exception: pass
            _current_screen = "endgame_menu"; state.en_menu = True; _init_maze(); glutPostRedisplay()
        return

    # Desactivar mouse durante laberinto
    if _current_screen == "maze_game":
        return

    if button == GLUT_LEFT_BUTTON and btn_state == GLUT_DOWN:
        W = glutGet(GLUT_WINDOW_WIDTH)
        H = glutGet(GLUT_WINDOW_HEIGHT)
        cx = W // 2

        # ── Menú END GAME ──
        if _current_screen == "endgame_menu":
            BTN_W, BTN_H, BTN_GAP = 400, 70, 14
            n = len(_ENDGAME_BUTTONS)
            total_h = n * BTN_H + (n - 1) * BTN_GAP
            start_y = (H - 100 + total_h) // 2 - 10
            for i in range(n):
                bx = cx - BTN_W // 2
                # Convertir coordenadas GLUT (y=0 en top) a OpenGL (y=0 en bottom)
                by_gl = start_y - i * (BTN_H + BTN_GAP)
                by_sc = H - by_gl - BTN_H  # en coordenadas de pantalla (GLUT)
                if bx <= x <= bx + BTN_W and by_sc <= y <= by_sc + BTN_H:
                    _endgame_hover = i
                    _handle_endgame_button_select()
                    break
            glutPostRedisplay()
            return

        # ── Submenú Laberinto ──
        if _current_screen == "laberinto_mode":
            btn_y_start = H // 2 + 50
            for i, btn in enumerate(_LAB_BUTTONS):
                by_gl = btn_y_start - i * 120
                by_sc = H - by_gl - 80
                bx = cx - 180
                if bx <= x <= bx + 360 and by_sc <= y <= by_sc + 80:
                    _lab_hover = i
                    _handle_lab_button_select()
                    break
            glutPostRedisplay()
            return

        # ── Pantalla Información ──
        if _current_screen == "info_screen":
            _current_screen = "endgame_menu"
            glutPostRedisplay()
            return

        # ── Selección de personajes ──
        if _current_screen in ("char_select_mp", "char_select_1p", "char_select_maze", "char_select_maze_mp"):
            idx = _card_index_at(x, y, W, H)
            if idx >= 0:
                if _menu_state == "browse":
                    if idx == state.menu_cursor_index:
                        _trigger_greeting(idx)
                    else:
                        state.menu_cursor_index = idx
                elif _menu_state == "greeting":
                    if idx == state.menu_cursor_index:
                        _handle_char_confirm_keyboard()
                    else:
                        _cancel_greeting()
                        state.menu_cursor_index = idx
            glutPostRedisplay()
            return

        # ── en_menu genérico ──
        if state.en_menu:
            idx = _card_index_at(x, y, W, H)
            if idx >= 0:
                if _menu_state == "browse":
                    if idx == state.menu_cursor_index:
                        _trigger_greeting(idx)
                    else:
                        state.menu_cursor_index = idx
                elif _menu_state == "greeting":
                    if idx == state.menu_cursor_index:
                        _handle_char_confirm_keyboard()
                    else:
                        _cancel_greeting()
                        state.menu_cursor_index = idx
            glutPostRedisplay()
            return

    camera.mouse(button, btn_state, x, y)


def handle_passive_motion(x, y):
    global _hover_index, _endgame_hover, _lab_hover, _current_screen

    if _current_screen == "rope_pull":
        return

    W = glutGet(GLUT_WINDOW_WIDTH)
    H = glutGet(GLUT_WINDOW_HEIGHT)
    cx = W // 2

    # ── Hover END GAME ──
    if _current_screen == "endgame_menu":
        BTN_W, BTN_H, BTN_GAP = 400, 70, 14
        n = len(_ENDGAME_BUTTONS)
        total_h = n * BTN_H + (n - 1) * BTN_GAP
        start_y = (H - 100 + total_h) // 2 - 10
        new_h = _endgame_hover
        for i in range(n):
            bx = cx - BTN_W // 2
            by_gl = start_y - i * (BTN_H + BTN_GAP)
            by_sc = H - by_gl - BTN_H
            if bx <= x <= bx + BTN_W and by_sc <= y <= by_sc + BTN_H:
                new_h = i
                break
        if new_h != _endgame_hover:
            _endgame_hover = new_h
            glutPostRedisplay()
        return

    # ── Hover Laberinto ──
    if _current_screen == "laberinto_mode":
        btn_y_start = H // 2 + 50
        new_h = _lab_hover
        for i in range(len(_LAB_BUTTONS)):
            by_gl = btn_y_start - i * 120
            by_sc = H - by_gl - 80
            if cx - 180 <= x <= cx + 180 and by_sc <= y <= by_sc + 80:
                new_h = i
                break
        if new_h != _lab_hover:
            _lab_hover = new_h
            glutPostRedisplay()
        return

    if _current_screen in ("char_select_mp", "char_select_1p", "char_select_maze", "char_select_maze_mp") or state.en_menu:
        new = _card_index_at(x, y, W, H)
        if new != _hover_index:
            _hover_index = new
            glutPostRedisplay()
        return




def handle_motion(x, y):
    if state.en_menu or _current_screen in (
        "endgame_menu", "laberinto_mode", "info_screen",
        "char_select_mp", "char_select_1p", "char_select_maze", "char_select_maze_mp",
        "rope_pull", "maze_game"
    ):
        return
    camera.motion(x, y)


# -----------------------------------------------------------------------
#  Punto de entrada
# -----------------------------------------------------------------------
def main():
    global _current_screen
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1100, 740)
    glutCreateWindow(b"END GAME - Instituto Tecnologico de Toluca")
    init()
    audio.init_audio()

    _current_screen = "endgame_menu"
    state.en_menu = True

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(handle_keyboard)
    glutKeyboardUpFunc(handle_keyboard_up)
    glutSpecialFunc(handle_special)
    glutSpecialUpFunc(handle_special_up)
    glutMouseFunc(handle_mouse)
    glutMotionFunc(handle_motion)
    glutPassiveMotionFunc(handle_passive_motion)
    glutTimerFunc(16, update.update, 0)

    print("=" * 62)
    print("  END GAME — Instituto Tecnologico de Toluca")
    print("  Materia: Graficacion")
    print("  Desarrolladores:")
    print("    Valeria Esperanza Albino Hernandez")
    print("    Ian Axel Rojas Juarez")
    print("    Yerik Jardon Albarran")
    print("=" * 62)
    print("  NIVEL 1: Tetris (2 jugadores)")
    print("  NIVEL 2: Laberinto (1P o 2P)")
    print("  NIVEL 3: Juego de la Cuerda (2 jugadores)")
    print("  Jugar Secuencialmente: Tetris -> Laberinto -> Cuerda")
    print("=" * 62)

    glutMainLoop()


if __name__ == "__main__":
    main()

