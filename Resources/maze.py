# Resources/maze.py — Escenario Laberinto en Primera Persona
"""
Laberinto 3D en primera persona usando primitivas OpenGL (sin imagenes).
El laberinto es una cuadricula de celdas; las paredes se dibujan como
bloques usando glutSolidCube y cilindros para columnas.
"""
import math
from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *

# ─── Dimensiones de celda ────────────────────────────────────────────
CELL  = 4.0    # tamaño de cada celda en unidades world
WALL_H = 3.2   # altura de las paredes
WALL_T = 0.35  # grosor de las paredes

# ─── Mapa del laberinto (1=pared, 0=pasillo) ─────────────────────────
# 15 columnas x 19 filas — basado en la imagen proporcionada
MAZE_MAP = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,1,0,0,0,0,0,1,0,0,0,1],
    [1,0,1,0,1,0,1,1,1,0,1,0,1,0,1],
    [1,0,1,0,0,0,1,0,0,0,0,0,1,0,1],
    [1,0,1,1,1,0,1,0,1,1,1,0,1,0,1],
    [1,0,0,0,1,0,0,0,1,0,0,0,0,0,1],
    [1,1,1,0,1,1,1,0,1,0,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
    [1,0,1,1,1,0,1,1,1,1,1,0,1,0,1],
    [1,0,1,0,0,0,1,0,0,0,1,0,0,0,1],
    [1,0,1,0,1,1,1,0,1,0,1,1,1,0,1],
    [1,0,0,0,1,0,0,0,1,0,0,0,0,0,1],
    [1,1,1,0,1,0,1,1,1,0,1,0,1,1,1],
    [1,0,0,0,0,0,1,0,0,0,1,0,0,0,1],
    [1,0,1,1,1,0,0,0,1,0,0,0,1,0,1],
    [1,0,1,0,1,1,1,0,1,1,1,0,1,0,1],
    [1,0,0,0,0,0,1,0,0,0,0,0,0,0,1],
    [1,1,1,0,1,0,0,0,1,0,1,1,1,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

ROWS = len(MAZE_MAP)
COLS = len(MAZE_MAP[0])

# Colores
_WALL_COLOR   = (0.25, 0.55, 0.18)   # verde oscuro (seto)
_WALL_TOP     = (0.35, 0.70, 0.22)   # verde claro borde superior
_FLOOR_COLOR  = (0.78, 0.68, 0.50)   # beige arena
_SKY_COLOR    = (0.72, 0.88, 0.60)   # verde cielo suave
_COL_COLOR    = (0.20, 0.48, 0.12)   # verde oscuro columna
_STAR_COLOR   = (1.00, 0.85, 0.10)   # dorado para estrella coleccionable


def world_pos(row, col):
    """Convierte fila/col del mapa a coordenada world (x, z) del CENTRO de celda."""
    x = (col - COLS / 2.0 + 0.5) * CELL
    z = (row - ROWS / 2.0 + 0.5) * CELL
    return x, z


def is_wall(row, col):
    if row < 0 or row >= ROWS or col < 0 or col >= COLS:
        return True
    return MAZE_MAP[row][col] == 1


def _world_to_cell(px, pz):
    """Convierte coordenada world a fila/columna del mapa."""
    col = int(math.floor(px / CELL + COLS / 2.0 - 0.5 + 0.5))
    row = int(math.floor(pz / CELL + ROWS / 2.0 - 0.5 + 0.5))
    return row, col


def check_maze_collision(px, pz, radius=0.85):
    """
    Colision circulo-AABB correcta: verifica si el circulo del jugador (radio dado)
    se superpone con el bloque AABB de cualquier celda pared.
    Funciona correctamente para posiciones negativas y en bordes de celda.
    """
    half = CELL / 2.0
    # Rango de celdas que el bounding box del jugador puede tocar
    min_col = int(math.floor((px - radius) / CELL + COLS / 2.0 - 0.5 + 0.5))
    max_col = int(math.floor((px + radius) / CELL + COLS / 2.0 - 0.5 + 0.5))
    min_row = int(math.floor((pz - radius) / CELL + ROWS / 2.0 - 0.5 + 0.5))
    max_row = int(math.floor((pz + radius) / CELL + ROWS / 2.0 - 0.5 + 0.5))

    for row in range(min_row, max_row + 1):
        for col in range(min_col, max_col + 1):
            if not is_wall(row, col):
                continue
            # Centro exacto de la celda pared
            wx, wz = world_pos(row, col)
            # Punto más cercano del AABB de la celda al jugador
            closest_x = max(wx - half, min(px, wx + half))
            closest_z = max(wz - half, min(pz, wz + half))
            # Colision si la distancia al punto más cercano es menor que el radio
            dist_sq = (px - closest_x) ** 2 + (pz - closest_z) ** 2
            if dist_sq < radius * radius:
                return True
    return False


# ── Posicion de inicio y meta ──────────────────────────────────────────
def get_start_pos():
    """Devuelve (x, z) de la celda de inicio (fila 17, col 7)."""
    x, z = world_pos(17, 7)
    return x, z


def get_goal_pos():
    """Devuelve (x, z) de la meta (fila 1, col 13)."""
    x, z = world_pos(1, 13)
    return x, z


# ── Dibujo del laberinto ───────────────────────────────────────────────
def _box(sx, sy, sz):
    glPushMatrix()
    glScalef(sx, sy, sz)
    glutSolidCube(1.0)
    glPopMatrix()


def _draw_wall_block(x, y, z, sx, sy, sz):
    """Dibuja un bloque de pared con borde superior más claro."""
    glPushMatrix()
    glTranslatef(x, y, z)
    # Cuerpo de la pared
    glColor3f(*_WALL_COLOR)
    _box(sx, sy, sz)
    # Borde superior (capa plana verde claro)
    glColor3f(*_WALL_TOP)
    glTranslatef(0, sy / 2.0 + 0.04, 0)
    _box(sx + 0.06, 0.12, sz + 0.06)
    glPopMatrix()


def draw_maze_scenario():
    """Dibuja todo el escenario del laberinto."""
    # Cielo / fondo
    glClearColor(*_SKY_COLOR, 1.0)

    # ── Suelo ──────────────────────────────────────────────────────────
    glColor3f(*_FLOOR_COLOR)
    glPushMatrix()
    glTranslatef(0, -0.06, 0)
    floor_w = COLS * CELL
    floor_d = ROWS * CELL
    glScalef(floor_w, 0.12, floor_d)
    glutSolidCube(1.0)
    glPopMatrix()

    # Grilla del suelo (lineas de baldosas)
    glColor3f(0.65, 0.56, 0.40)
    for r in range(ROWS + 1):
        z = (r - ROWS / 2.0) * CELL
        glBegin(GL_LINES)
        glVertex3f(-COLS * CELL / 2, 0.01, z)
        glVertex3f( COLS * CELL / 2, 0.01, z)
        glEnd()
    for c in range(COLS + 1):
        x = (c - COLS / 2.0) * CELL
        glBegin(GL_LINES)
        glVertex3f(x, 0.01, -ROWS * CELL / 2)
        glVertex3f(x, 0.01,  ROWS * CELL / 2)
        glEnd()

    # ── Paredes ────────────────────────────────────────────────────────
    for row in range(ROWS):
        for col in range(COLS):
            if MAZE_MAP[row][col] == 1:
                wx, wz = world_pos(row, col)
                _draw_wall_block(wx, WALL_H / 2, wz,
                                 CELL, WALL_H, CELL)

    # ── Columnas en las esquinas de cada interseccion ──────────────────
    glColor3f(*_COL_COLOR)
    q = gluNewQuadric()
    for row in range(ROWS):
        for col in range(COLS):
            if MAZE_MAP[row][col] == 0:
                # Columna en cada esquina de celda vacia
                for dr, dc in ((0, 0), (0, 1), (1, 0), (1, 1)):
                    nr, nc = row + dr, col + dc
                    # Solo poner columna si todas las 4 celdas adyacentes son pared
                    # (para no saturar el espacio): omitir para mantenerlo limpio
                pass

    # ── Estrella meta (punto de llegada) ──────────────────────────────
    import time as _time
    t = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    gx, gz = get_goal_pos()
    glPushMatrix()
    glTranslatef(gx, 1.2 + math.sin(t * 2.0) * 0.25, gz)
    glRotatef(t * 80, 0, 1, 0)
    glColor3f(*_STAR_COLOR)
    glutSolidOctahedron()
    glPopMatrix()
    # Halo brillante
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glPushMatrix()
    glTranslatef(gx, 1.2 + math.sin(t * 2.0) * 0.25, gz)
    glColor4f(1.0, 1.0, 0.4, 0.18)
    gluSphere(q, 1.0, 12, 10)
    glPopMatrix()
    glDisable(GL_BLEND)

    # Rayos de luz en la meta
    glColor3f(1.0, 0.95, 0.5)
    for ang in range(0, 360, 45):
        rad = math.radians(ang + t * 30)
        glBegin(GL_LINES)
        glVertex3f(gx, 0.05, gz)
        glVertex3f(gx + math.cos(rad) * 2.2, 0.05, gz + math.sin(rad) * 2.2)
        glEnd()

    gluDeleteQuadric(q)

    # ── Arbustos decorativos en algunas celdas de pared ───────────────
    _draw_decorations(t)


def _draw_decorations(t):
    """Arbustos, flores y detalles en las paredes del laberinto."""
    q = gluNewQuadric()
    deco_cells = [
        (1,  1,  (0.20, 0.65, 0.20)),
        (1, 13,  (0.85, 0.35, 0.80)),
        (9,  7,  (0.20, 0.60, 0.18)),
        (4, 14,  (0.70, 0.30, 0.85)),
        (16, 1,  (0.30, 0.72, 0.22)),
        (17,14,  (0.75, 0.25, 0.80)),
    ]
    for (row, col, color) in deco_cells:
        wx, wz = world_pos(row, col)
        glPushMatrix()
        glTranslatef(wx, WALL_H + 0.55, wz)
        glColor3f(*color)
        bob = math.sin(t * 1.5 + row + col) * 0.07
        glTranslatef(0, bob, 0)
        gluSphere(q, 0.8, 12, 10)
        # Flores encima
        glTranslatef(0, 0.7, 0)
        glColor3f(min(color[0]+0.3,1), min(color[1]+0.2,1), min(color[2]+0.3,1))
        gluSphere(q, 0.25, 8, 8)
        glPopMatrix()

    # Estrellas coleccionables en pasillos
    star_cells = [(3,8),(7,4),(10,11),(13,3),(15,10),(17,1)]
    for (row, col) in star_cells:
        if MAZE_MAP[row][col] == 0:
            wx, wz = world_pos(row, col)
            spin = t * 60 + row * 37 + col * 13
            glPushMatrix()
            glTranslatef(wx, 0.8 + math.sin(t*2.5+row)*0.15, wz)
            glRotatef(spin, 0, 1, 0)
            glColor3f(1.0, 0.90, 0.20)
            glScalef(0.35, 0.55, 0.35)
            glutSolidOctahedron()
            glPopMatrix()

    gluDeleteQuadric(q)


def draw_maze_fp_camera(px, pz, facing_deg):
    """
    Configura la camara en primera persona dentro del laberinto.
    px, pz: posicion del jugador en world coords
    facing_deg: angulo de vision (grados, Y)
    """
    eye_h = 1.65   # altura de los ojos
    rad   = math.radians(facing_deg)
    lx = px - math.sin(rad)
    lz = pz - math.cos(rad)
    gluLookAt(px, eye_h, pz,
              lx, eye_h, lz,
              0.0, 1.0, 0.0)
