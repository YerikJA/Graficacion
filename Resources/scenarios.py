# Resources/scenarios.py
"""
6 escenarios únicos, uno por personaje.
Cada escenario es sencillo pero temático, usando primitivas OpenGL puras.
"""
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from Actions import state

# ── utilidades ────────────────────────────────────────────────
def _set(r, g, b):
    glColor3f(r, g, b)

def _box(sx, sy, sz):
    glPushMatrix()
    glScalef(sx, sy, sz)
    glutSolidCube(1.0)
    glPopMatrix()

def _cylinder(r1, r2, h, sl=14):
    q = gluNewQuadric()
    gluCylinder(q, r1, r2, h, sl, 4)
    gluDeleteQuadric(q)

def _sphere(r, sl=14, st=12):
    q = gluNewQuadric()
    gluSphere(q, r, sl, st)
    gluDeleteQuadric(q)

def _disk(r, sl=16):
    q = gluNewQuadric()
    gluDisk(q, 0, r, sl, 1)
    gluDeleteQuadric(q)


# ═══════════════════════════════════════════════════════════════
#  ESCENARIO 1 — CIUDAD CHINA (Pucca)
#  Piso rojo, faroles, arco chino, muro lateral
# ═══════════════════════════════════════════════════════════════
def _draw_scenario_1():
    glClearColor(0.15, 0.08, 0.05, 1.0)   # cielo nocturno cálido

    # Piso rojo oscuro (adoquín)
    _set(0.55, 0.12, 0.10)
    glPushMatrix()
    glTranslatef(0, -0.05, 0)
    _box(40, 0.10, 40)
    glPopMatrix()

    # Líneas del piso (patrón adoquín)
    _set(0.45, 0.08, 0.08)
    for xi in range(-10, 11, 3):
        glPushMatrix()
        glTranslatef(xi, 0.01, 0)
        _box(0.05, 0.03, 40)
        glPopMatrix()

    # Arco chino (entrada) — al fondo
    _set(0.80, 0.15, 0.10)
    glPushMatrix()
    glTranslatef(0, 0, -12)
    # Columnas del arco
    for sx in (-3.0, 3.0):
        glPushMatrix()
        glTranslatef(sx, 2.5, 0)
        _box(0.6, 5.0, 0.6)
        glPopMatrix()
    # Viga superior
    glPushMatrix()
    glTranslatef(0, 5.2, 0)
    _box(7.0, 0.5, 0.8)
    glPopMatrix()
    # Techo inclinado
    _set(0.65, 0.10, 0.05)
    glPushMatrix()
    glTranslatef(0, 5.8, 0)
    _box(7.5, 0.3, 1.2)
    glPopMatrix()
    glPopMatrix()

    # Faroles rojos colgantes
    for (fx, fz) in [(-5, -4), (5, -4), (-5, 4), (5, 4)]:
        # Poste
        _set(0.40, 0.10, 0.08)
        glPushMatrix()
        glTranslatef(fx, 0, fz)
        glRotatef(-90, 1, 0, 0)
        _cylinder(0.08, 0.07, 3.5)
        # Farol rojo
        _set(0.95, 0.20, 0.10)
        glTranslatef(0, 0, 3.3)
        glRotatef(90, 1, 0, 0)
        _sphere(0.35)
        # Luz interior amarilla
        _set(1.0, 0.85, 0.30)
        _sphere(0.15)
        glPopMatrix()

    # Muro lateral izquierdo
    _set(0.60, 0.50, 0.40)
    glPushMatrix()
    glTranslatef(-10, 1.5, 0)
    _box(0.5, 3.0, 20)
    glPopMatrix()


# ═══════════════════════════════════════════════════════════════
#  ESCENARIO 2 — PRADERA VERDE (Pochacco)
#  Pasto brillante, cercas blancas, nubes, flores
# ═══════════════════════════════════════════════════════════════
def _draw_scenario_2():
    glClearColor(0.50, 0.78, 1.0, 1.0)   # cielo azul brillante

    # Pasto verde
    _set(0.30, 0.72, 0.25)
    glPushMatrix()
    glTranslatef(0, -0.05, 0)
    _box(40, 0.10, 40)
    glPopMatrix()

    # Cercas blancas (dos filas laterales)
    for zoff in (-8, 8):
        for xi in range(-8, 9, 2):
            # Poste
            _set(0.95, 0.95, 0.95)
            glPushMatrix()
            glTranslatef(xi, 0.5, zoff)
            _box(0.15, 1.0, 0.15)
            glPopMatrix()
        # Barra horizontal
        _set(0.92, 0.92, 0.92)
        glPushMatrix()
        glTranslatef(0, 0.7, zoff)
        _box(17.0, 0.12, 0.10)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0, 0.35, zoff)
        _box(17.0, 0.12, 0.10)
        glPopMatrix()

    # Flores simples (esferas de colores sobre tallos)
    flower_colors = [(1.0, 0.4, 0.5), (1.0, 0.8, 0.2), (0.6, 0.4, 1.0), (1.0, 0.5, 0.8)]
    flower_pos = [(-4, 3), (-2, 5), (3, 4), (5, 2), (-6, -3), (4, -5), (-3, -4), (6, -2)]
    for i, (fx, fz) in enumerate(flower_pos):
        # Tallo
        _set(0.25, 0.55, 0.15)
        glPushMatrix()
        glTranslatef(fx, 0, fz)
        glRotatef(-90, 1, 0, 0)
        _cylinder(0.03, 0.03, 0.5)
        glPopMatrix()
        # Flor
        cr, cg, cb = flower_colors[i % len(flower_colors)]
        _set(cr, cg, cb)
        glPushMatrix()
        glTranslatef(fx, 0.55, fz)
        _sphere(0.15)
        glPopMatrix()

    # Nubes blancas
    for (cx, cy, cz, sc) in [(-8, 9, -14, 1.8), (4, 10, -16, 2.2), (10, 8, -12, 1.5)]:
        _set(1.0, 1.0, 1.0)
        glPushMatrix()
        glTranslatef(cx, cy, cz)
        glScalef(sc * 2.0, sc * 0.7, sc * 0.6)
        _sphere(1.0)
        glPopMatrix()


# ═══════════════════════════════════════════════════════════════
#  ESCENARIO 3 — DREAM LAND (Kirby)
#  Piso rosa pastel, estrellas, bloques, arco iris
# ═══════════════════════════════════════════════════════════════
def _draw_scenario_3():
    glClearColor(0.70, 0.55, 0.85, 1.0)   # cielo morado pastel

    # Piso rosa pastel
    _set(0.95, 0.75, 0.80)
    glPushMatrix()
    glTranslatef(0, -0.05, 0)
    _box(40, 0.10, 40)
    glPopMatrix()

    # Estrellas decorativas (octaedros amarillos)
    star_pos = [(-5, 2.0, -6), (6, 2.5, -8), (-3, 1.8, 5), (4, 3.0, -4), (-7, 2.2, 2)]
    for (sx, sy, sz) in star_pos:
        _set(1.0, 0.90, 0.30)
        glPushMatrix()
        glTranslatef(sx, sy, sz)
        glScalef(0.35, 0.35, 0.35)
        glutSolidOctahedron()
        glPopMatrix()

    # Bloques de colores (cubos flotantes)
    block_colors = [(0.40, 0.70, 1.0), (1.0, 0.55, 0.70), (0.50, 1.0, 0.60), (1.0, 0.85, 0.40)]
    block_pos = [(-6, 0.5, -3), (7, 0.5, 2), (-4, 0.5, 6), (5, 0.5, -7)]
    for i, (bx, by, bz) in enumerate(block_pos):
        cr, cg, cb = block_colors[i]
        _set(cr, cg, cb)
        glPushMatrix()
        glTranslatef(bx, by, bz)
        glutSolidCube(1.0)
        glPopMatrix()

    # Arbol de Dream Land (tronco + copa redonda rosa)
    _set(0.50, 0.30, 0.15)
    glPushMatrix()
    glTranslatef(-8, 0, -8)
    glRotatef(-90, 1, 0, 0)
    _cylinder(0.3, 0.25, 3.0)
    glPopMatrix()
    _set(0.95, 0.60, 0.75)
    glPushMatrix()
    glTranslatef(-8, 3.5, -8)
    _sphere(1.5)
    glPopMatrix()

    # Nubes rosadas
    for (cx, cy, cz, sc) in [(-6, 8, -12, 1.5), (5, 9, -15, 2.0), (0, 10, -18, 1.8)]:
        _set(1.0, 0.85, 0.90)
        glPushMatrix()
        glTranslatef(cx, cy, cz)
        glScalef(sc * 1.8, sc * 0.6, sc * 0.5)
        _sphere(1.0)
        glPopMatrix()


# ═══════════════════════════════════════════════════════════════
#  ESCENARIO 4 — CASTILLO (Waddle Dee)
#  Piso de piedra, torres simples, banderas, muralla
# ═══════════════════════════════════════════════════════════════
def _draw_scenario_4():
    glClearColor(0.45, 0.55, 0.75, 1.0)   # cielo gris-azulado

    # Piso de piedra gris
    _set(0.50, 0.48, 0.45)
    glPushMatrix()
    glTranslatef(0, -0.05, 0)
    _box(40, 0.10, 40)
    glPopMatrix()

    # Muralla al fondo
    _set(0.55, 0.50, 0.45)
    glPushMatrix()
    glTranslatef(0, 2.0, -14)
    _box(18, 4.0, 1.0)
    glPopMatrix()

    # Torres en las esquinas de la muralla
    for tx in (-9, 9):
        _set(0.50, 0.45, 0.40)
        glPushMatrix()
        glTranslatef(tx, 0, -14)
        glRotatef(-90, 1, 0, 0)
        _cylinder(1.0, 0.9, 6.0, 8)
        glPopMatrix()
        # Techo cónico
        _set(0.65, 0.20, 0.15)
        glPushMatrix()
        glTranslatef(tx, 6.0, -14)
        glRotatef(-90, 1, 0, 0)
        _cylinder(1.1, 0.05, 2.0, 8)
        glPopMatrix()

    # Banderas en las torres
    for tx in (-9, 9):
        # Poste
        _set(0.40, 0.30, 0.20)
        glPushMatrix()
        glTranslatef(tx, 6.0, -14)
        glRotatef(-90, 1, 0, 0)
        _cylinder(0.06, 0.05, 3.0)
        glPopMatrix()
        # Bandera naranja (color Waddle Dee)
        _set(0.98, 0.55, 0.18)
        glPushMatrix()
        glTranslatef(tx + 0.5, 8.5, -14)
        _box(0.8, 0.5, 0.05)
        glPopMatrix()

    # Antorchas laterales
    for (ax, az) in [(-3, -2), (3, -2)]:
        _set(0.40, 0.28, 0.12)
        glPushMatrix()
        glTranslatef(ax, 0, az)
        glRotatef(-90, 1, 0, 0)
        _cylinder(0.07, 0.06, 2.5)
        # Llama
        _set(1.0, 0.55, 0.10)
        glTranslatef(0, 0, 2.6)
        glRotatef(90, 1, 0, 0)
        _sphere(0.15)
        glPopMatrix()


# ═══════════════════════════════════════════════════════════════
#  ESCENARIO 5 — BASE MILITAR (Optimus)
#  Piso metálico gris, cajas de munición, radar, torre
# ═══════════════════════════════════════════════════════════════
def _draw_scenario_5():
    glClearColor(0.30, 0.35, 0.45, 1.0)   # cielo gris industrial

    # Piso metálico
    _set(0.40, 0.42, 0.45)
    glPushMatrix()
    glTranslatef(0, -0.05, 0)
    _box(40, 0.10, 40)
    glPopMatrix()

    # Líneas amarillas en el piso (marcas de pista)
    _set(0.85, 0.75, 0.15)
    for zi in range(-8, 9, 4):
        glPushMatrix()
        glTranslatef(0, 0.01, zi)
        _box(2.0, 0.03, 0.15)
        glPopMatrix()

    # Cajas militares (verdes)
    crate_pos = [(-6, 0, 4), (-5, 0, 5), (7, 0, -3), (6, 0, -4)]
    for (cx, cy, cz) in crate_pos:
        _set(0.30, 0.42, 0.25)
        glPushMatrix()
        glTranslatef(cx, 0.5, cz)
        glutSolidCube(1.0)
        glPopMatrix()

    # Torre de vigilancia
    _set(0.45, 0.45, 0.48)
    glPushMatrix()
    glTranslatef(-8, 0, -10)
    # Columnas
    for (dx, dz) in [(-0.6, -0.6), (0.6, -0.6), (-0.6, 0.6), (0.6, 0.6)]:
        glPushMatrix()
        glTranslatef(dx, 2.5, dz)
        _box(0.15, 5.0, 0.15)
        glPopMatrix()
    # Plataforma
    glPushMatrix()
    glTranslatef(0, 5.0, 0)
    _box(2.0, 0.2, 2.0)
    glPopMatrix()
    glPopMatrix()

    # Antena/Radar
    _set(0.50, 0.50, 0.55)
    glPushMatrix()
    glTranslatef(8, 0, -8)
    glRotatef(-90, 1, 0, 0)
    _cylinder(0.12, 0.10, 5.0)
    glPopMatrix()
    # Plato del radar
    _set(0.60, 0.60, 0.65)
    glPushMatrix()
    glTranslatef(8, 5.0, -8)
    glRotatef(90, 0, 1, 0)
    _disk(1.0)
    glPopMatrix()


# ═══════════════════════════════════════════════════════════════
#  ESCENARIO 6 — JARDÍN (Plasma Pea / Canon)
#  Pasto con flores, macetas, cerca de madera
# ═══════════════════════════════════════════════════════════════
def _draw_scenario_6():
    glClearColor(0.45, 0.72, 1.0, 1.0)   # cielo azul claro

    # Pasto verde brillante
    _set(0.28, 0.68, 0.22)
    glPushMatrix()
    glTranslatef(0, -0.05, 0)
    _box(40, 0.10, 40)
    glPopMatrix()

    # Camino de tierra
    _set(0.65, 0.50, 0.30)
    glPushMatrix()
    glTranslatef(0, 0.0, 0)
    _box(2.5, 0.06, 20)
    glPopMatrix()

    # Cerca de madera al fondo
    for xi in range(-8, 9, 1):
        _set(0.55, 0.38, 0.18)
        glPushMatrix()
        glTranslatef(xi, 0.5, -10)
        _box(0.15, 1.0, 0.15)
        # Punta
        glTranslatef(0, 0.55, 0)
        glRotatef(45, 0, 0, 1)
        _set(0.50, 0.35, 0.15)
        _box(0.12, 0.12, 0.12)
        glPopMatrix()
    # Barandales horizontales
    _set(0.52, 0.36, 0.16)
    for hy in (0.25, 0.6):
        glPushMatrix()
        glTranslatef(0, hy, -10)
        _box(17.0, 0.10, 0.08)
        glPopMatrix()

    # Macetas con plantas
    maceta_pos = [(-4, 3), (4, 3), (-4, -3), (4, -3)]
    for (mx, mz) in maceta_pos:
        # Maceta (cilindro marrón)
        _set(0.60, 0.35, 0.15)
        glPushMatrix()
        glTranslatef(mx, 0, mz)
        glRotatef(-90, 1, 0, 0)
        _cylinder(0.35, 0.25, 0.5)
        glPopMatrix()
        # Planta (esfera verde)
        _set(0.25, 0.65, 0.20)
        glPushMatrix()
        glTranslatef(mx, 0.8, mz)
        _sphere(0.45)
        glPopMatrix()

    # Flores pequeñas en el pasto
    fcolors = [(1.0, 0.3, 0.4), (1.0, 0.7, 0.1), (0.8, 0.3, 0.9), (0.3, 0.6, 1.0)]
    fpos = [(-2, 5), (2, 6), (-3, -5), (3, -6), (-6, 1), (6, -1), (-1, 7), (1, -7)]
    for i, (fx, fz) in enumerate(fpos):
        _set(0.22, 0.50, 0.12)
        glPushMatrix()
        glTranslatef(fx, 0, fz)
        glRotatef(-90, 1, 0, 0)
        _cylinder(0.02, 0.02, 0.35)
        glPopMatrix()
        cr, cg, cb = fcolors[i % len(fcolors)]
        _set(cr, cg, cb)
        glPushMatrix()
        glTranslatef(fx, 0.40, fz)
        _sphere(0.10)
        glPopMatrix()

    # Nubes
    for (cx, cy, cz, sc) in [(-7, 9, -14, 1.5), (6, 10, -16, 2.0)]:
        _set(1.0, 1.0, 1.0)
        glPushMatrix()
        glTranslatef(cx, cy, cz)
        glScalef(sc * 2.0, sc * 0.7, sc * 0.5)
        _sphere(1.0)
        glPopMatrix()


# ═══════════════════════════════════════════════════════════════
#  OBJETOS DE COLISIÓN (se dibujan en todos los escenarios)
# ═══════════════════════════════════════════════════════════════
def draw_collision_objects():
    """Dibuja zombie, caja de munición y valla."""

    # ── Zombie ────────────────────────────────────────────────
    if state.zombie_activo:
        col = (0.30, 0.75, 0.20) if not state.zombie_hit else (1.0, 0.1, 0.1)
        glPushMatrix()
        glTranslatef(state.zombie_x, 0, state.zombie_z)
        # cuerpo
        _set(*col)
        glPushMatrix()
        glTranslatef(0, 1.2, 0)
        _box(0.8, 2.0, 0.6)
        glPopMatrix()
        # cabeza
        _set(*col)
        glPushMatrix()
        glTranslatef(0, 2.7, 0)
        _sphere(0.55)
        glPopMatrix()
        # ojos zombi (rojo)
        _set(1.0, 0.1, 0.1)
        for sx in (-0.18, 0.18):
            glPushMatrix()
            glTranslatef(sx, 2.78, 0.50)
            _sphere(0.10)
            glPopMatrix()
        # brazos
        _set(*col)
        for sx in (-0.65, 0.65):
            glPushMatrix()
            glTranslatef(sx, 1.8, 0.2)
            glRotatef(-70, 1, 0, 0)
            _cylinder(0.12, 0.10, 0.9)
            glPopMatrix()
        glPopMatrix()

    # ── Caja de munición ──────────────────────────────────────
    if state.caja_activa:
        col = (0.60, 0.45, 0.15) if not state.caja_hit else (1.0, 0.85, 0.10)
        glPushMatrix()
        glTranslatef(state.caja_x, 0.4, state.caja_z)
        _set(*col)
        _box(0.9, 0.9, 0.9)
        # cruz verde encima
        _set(0.20, 0.80, 0.20)
        glPushMatrix()
        glTranslatef(0, 0.46, 0)
        _box(0.60, 0.06, 0.14)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0, 0.46, 0)
        _box(0.14, 0.06, 0.60)
        glPopMatrix()
        glPopMatrix()

    # ── Valla ─────────────────────────────────────────────────
    col_v = (0.55, 0.38, 0.18) if not state.valla_hit else (1.0, 0.6, 0.0)
    glPushMatrix()
    glTranslatef(state.valla_x, 0, state.valla_z)
    # postes
    for px in (-2.0, 0.0, 2.0):
        _set(*col_v)
        glPushMatrix()
        glTranslatef(px, 0.75, 0)
        glRotatef(-90, 1, 0, 0)
        _cylinder(0.10, 0.09, 1.5)
        glPopMatrix()
    # tablones horizontales
    for hy in (0.5, 1.1):
        _set(*col_v)
        glPushMatrix()
        glTranslatef(0, hy, 0)
        _box(4.2, 0.18, 0.14)
        glPopMatrix()
    glPopMatrix()


# ═══════════════════════════════════════════════════════════════
#  ESCENARIO 7 — TETRIS ESPACIAL
#  Fondo espacial, dos planetas a los lados y estrellas
# ═══════════════════════════════════════════════════════════════
def _draw_scenario_7():
    glClearColor(0.02, 0.02, 0.08, 1.0)   # cielo espacial muy oscuro

    # Piso oscuro
    _set(0.15, 0.15, 0.20)
    glPushMatrix()
    glTranslatef(0, -0.05, 0)
    _box(40, 0.10, 40)
    glPopMatrix()

    # Planeta Izquierdo
    _set(0.2, 0.4, 0.8) # Azul
    glPushMatrix()
    glTranslatef(-16, 8, -15)
    _sphere(4.0, 20, 20)
    glPopMatrix()

    # Planeta Derecho
    _set(0.8, 0.3, 0.2) # Rojo/Naranja
    glPushMatrix()
    glTranslatef(16, 6, -18)
    _sphere(3.5, 20, 20)
    glPopMatrix()

    # Estrellas pequeñas
    star_pos = [
        (-12, 14, -15), (10, 18, -18), (-6, 11, -25), (4, 16, -20), 
        (0, 9, -22), (-18, 5, -20), (14, 10, -20), (-8, 19, -12), (8, 13, -25)
    ]
    for (sx, sy, sz) in star_pos:
        _set(1.0, 1.0, 0.9)
        glPushMatrix()
        glTranslatef(sx, sy, sz)
        glScalef(0.15, 0.15, 0.15)
        glutSolidOctahedron()
        glPopMatrix()

    # ── Cubos cayentes del minijuego ─────────────────────────
    for cubo in state.tetris_cubos:
        if not cubo.get('activo', False):
            continue
        nombre, (cr, cg, cb) = state.TETRIS_COLORS[cubo['color_idx']]
        _set(cr, cg, cb)
        glPushMatrix()
        glTranslatef(cubo['x'], cubo['y'], cubo['z'])
        # Brillo interno (borde mas oscuro)
        glutSolidCube(0.80)
        # Contorno ligeramente mayor con wireframe
        _set(min(cr + 0.25, 1.0), min(cg + 0.25, 1.0), min(cb + 0.25, 1.0))
        glutWireCube(0.83)
        glPopMatrix()

    # Línea central que divide el mapa (visual de referencia)
    _set(0.40, 0.40, 0.60)
    glPushMatrix()
    glTranslatef(0, 0.02, 0)
    _box(0.05, 0.02, 20)
    glPopMatrix()



# ═══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════
_SCENARIO_DRAW = {
    1: _draw_scenario_1,
    2: _draw_scenario_2,
    3: _draw_scenario_3,
    4: _draw_scenario_4,
    5: _draw_scenario_5,
    6: _draw_scenario_6,
    7: _draw_scenario_7,
}

def draw_scenario():
    fn = _SCENARIO_DRAW.get(state.escenario_actual, _draw_scenario_1)
    glDisable(GL_LIGHTING)
    fn()
    draw_collision_objects()
    glEnable(GL_LIGHTING)
