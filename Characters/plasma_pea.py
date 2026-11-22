# Characters/plasma_pea.py
"""
Plasma Pea — Plants vs Zombies GW2
Modelo 3D con OpenGL puro (glutSolid*, gluCylinder, gluSphere).
"""
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from Actions import state

# ── color palette ─────────────────────────────────────────────
C_BODY_MAIN   = (0.35, 0.55, 0.90)   # azul-plasma cuerpo
C_BODY_DARK   = (0.20, 0.35, 0.75)   # sombra/bordes
C_BODY_GLOW   = (0.55, 0.80, 1.00)   # brillo plasma
C_CANNON_OUT  = (0.25, 0.40, 0.80)   # exterior del cañón
C_CANNON_IN   = (0.05, 0.05, 0.15)   # interior del cañón (oscuro)
C_EYE_WHITE   = (0.90, 0.95, 1.00)
C_EYE_PUPIL   = (0.10, 0.15, 0.35)
C_LEAF        = (0.20, 0.75, 0.30)   # hoja verde
C_LEAF_DARK   = (0.10, 0.50, 0.15)
C_ROOT        = (0.45, 0.30, 0.15)   # raíz marrón
C_ROOT_TIP    = (0.30, 0.20, 0.08)
C_PLASMA_ORB  = (0.50, 0.85, 1.00)   # bola de plasma
C_PLASMA_CORE = (1.00, 1.00, 1.00)
C_CREST       = (1.00, 0.25, 0.25)   # cresta roja encima


def _set(color):
    glColor3f(*color)


def _sphere(r, sl=20, st=20):
    q = gluNewQuadric()
    gluSphere(q, r, sl, st)
    gluDeleteQuadric(q)


def _cylinder(r1, r2, h, sl=16):
    q = gluNewQuadric()
    gluCylinder(q, r1, r2, h, sl, 4)
    gluDeleteQuadric(q)


def _disk(r, sl=16):
    q = gluNewQuadric()
    gluDisk(q, 0, r, sl, 1)
    gluDeleteQuadric(q)


# ═══════════════════════════════════════════════════════════════
#  SUB-PARTS
# ═══════════════════════════════════════════════════════════════

def _draw_crest():
    """Cresta roja en la parte superior del cuerpo."""
    _set(C_CREST)
    for dx in (-0.18, 0.0, 0.18):
        glPushMatrix()
        glTranslatef(dx, 0.0, 0.0)
        glScalef(0.12, 0.35, 0.12)
        glutSolidSphere(1.0, 10, 10)
        glPopMatrix()


def _draw_cannon():
    """
    Cañón tubular que apunta hacia +Z (frente del personaje).
    gluCylinder crece en +Z por defecto, así que no necesitamos rotarlo.
    """
    glPushMatrix()

    # Recoil del disparo
    glRotatef(-state.canon_x, 1, 0, 0)

    # Base cuadrada pegada al cuerpo
    _set(C_CANNON_OUT)
    glPushMatrix()
    glScalef(0.55, 0.55, 0.22)   # Ahora aplanada en Z
    glutSolidCube(1.0)
    glPopMatrix()

    # Tubo principal — crece a lo largo de +Z
    glPushMatrix()
    _set(C_BODY_DARK)
    _cylinder(0.30, 0.28, 0.85)
    glPopMatrix()

    # Anillo exterior de la boca
    glPushMatrix()
    glTranslatef(0, 0, 0.85)     # TRASLADADO EN Z (profundidad)
    _set(C_CANNON_OUT)
    _cylinder(0.35, 0.32, 0.12)
    glPopMatrix()

    # Interior oscuro de la boca
    glPushMatrix()
    glTranslatef(0, 0, 0.85)     # TRASLADADO EN Z
    _set(C_CANNON_IN)
    _cylinder(0.22, 0.20, 0.14)
    glPopMatrix()

    # Bola de plasma al disparar
    if state.plasma_visible and state.plasma_scale > 0.05:
        glPushMatrix()
        glTranslatef(0, 0, 1.25) # Delante de la boca en Z
        _set(C_PLASMA_CORE)
        _sphere(0.20 * state.plasma_scale)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(*C_PLASMA_ORB, 0.55)
        _sphere(0.36 * state.plasma_scale)
        glDisable(GL_BLEND)
        glPopMatrix()

    glPopMatrix()


def _draw_eye(side):
    """
    side: +1 = derecho, -1 = izquierdo
    """
    esc  = state.ojo_escala_der  if side > 0 else state.ojo_escala_izq
    offy = state.ojo_offset_y_der if side > 0 else state.ojo_offset_y_izq

    glPushMatrix()
    # Ojos mas arriba (+0.28) y bien separados al frente de la esfera
    glTranslatef(side * 0.28, 0.28 + offy, 0.0)
    glScalef(1.0, esc, 1.0)

    # Blanco del ojo
    _set(C_EYE_WHITE)
    _sphere(0.20)

    # Pupila / iris coloreada
    glPushMatrix()
    glTranslatef(0, 0, 0.14)
    _set((*state.ojo_color,))
    _sphere(0.12)
    glPopMatrix()

    # Brillo
    glPushMatrix()
    glTranslatef(side * 0.04, 0.06, 0.19)
    _set(C_EYE_WHITE)
    _sphere(0.045)
    glPopMatrix()

    glPopMatrix()


def _draw_eyebrow(side):
    """Ceja rectangular que rota para expresiones."""
    rot  = state.ceja_rot_der if side > 0 else state.ceja_rot_izq
    offy = state.ceja_offset_y

    glPushMatrix()
    # Cejas justo encima de los ojos
    glTranslatef(side * 0.28, 0.52 + offy, 0.0)
    glRotatef(rot * side, 0, 0, 1)
    _set(C_BODY_DARK)
    glScalef(0.28, 0.065, 0.10)
    glutSolidCube(1.0)
    glPopMatrix()


def _draw_mouth():
    """
    Boca debajo de los ojos, por encima del canon.
    boca_curva:  1=sonrisa, -1=tristeza, 0=neutral
    boca_abierta: True = muestra interior oscuro
    """
    glPushMatrix()
    # Posicion: debajo de los ojos, encima del canon
    glTranslatef(0.0, -0.10, 0.0)

    if state.boca_abierta:
        _set(C_CANNON_IN)
        glScalef(0.38, 0.22 * state.boca_escala_y, 0.12)
        glutSolidCube(1.0)
    else:
        segs = 7
        for i in range(segs):
            frac  = i / (segs - 1)
            xi    = (frac - 0.5) * 0.38
            curve = state.boca_curva * math.sin(frac * math.pi) * 0.10
            glPushMatrix()
            glTranslatef(xi, curve * state.boca_escala_y, 0.0)
            _set(C_BODY_DARK)
            glScalef(0.38 / segs + 0.008, 0.055 * state.boca_escala_y + 0.018, 0.08)
            glutSolidCube(1.0)
            glPopMatrix()

    glPopMatrix()


def _draw_face():
    """Cara frontal pegada al frente de la esfera."""
    glPushMatrix()
    glTranslatef(0.0, 0.0, 0.70)   # frente de la esfera

    _draw_eye(+1)
    _draw_eye(-1)
    _draw_eyebrow(+1)
    _draw_eyebrow(-1)
    
    # Comentado para que el cañón sea la única boca, fiel al diseño de PvZ
    # _draw_mouth()

    glPopMatrix()


def _draw_leaf(side):
    """
    Hoja / 'brazo' del Plasma Pea.
    side: +1 = derecho, -1 = izquierdo
    """
    rot_z = state.hoja_der_z if side > 0 else state.hoja_izq_z
    rot_y = state.hoja_der_y if side > 0 else state.hoja_izq_y

    glPushMatrix()
    glTranslatef(side * 0.72, 0.05, 0.0)
    glRotatef(rot_z, 0, 0, 1)
    glRotatef(rot_y, 0, 1, 0)

    # Tallo
    _set(C_LEAF_DARK)
    glPushMatrix()
    glTranslatef(side * 0.05, 0.0, 0.0)
    glRotatef(90 * side, 0, 1, 0)  # Gira sobre Y para apuntar lateralmente
    _cylinder(0.06, 0.05, 0.38)
    glPopMatrix()

    # Lámina de la hoja
    _set(C_LEAF)
    glPushMatrix()
    glTranslatef(side * 0.50, 0.0, 0.0)
    glScalef(0.38, 0.55, 0.12)
    glutSolidSphere(1.0, 14, 10)
    glPopMatrix()

    # Nervio central
    _set(C_LEAF_DARK)
    glPushMatrix()
    glTranslatef(side * 0.50, 0.0, 0.08)
    glScalef(0.06, 0.50, 0.04)
    glutSolidCube(1.0)
    glPopMatrix()

    glPopMatrix()


def _draw_root(side):
    """
    Raíz / 'pierna'. Dos segmentos articulados.
    side: +1 = derecho, -1 = izquierdo
    """
    rot = state.raiz_der_x if side > 0 else state.raiz_izq_x

    glPushMatrix()
    # Ajustado un poco en Y para compensar el nuevo ángulo
    glTranslatef(side * 0.30, -0.60, 0.0) 
    glRotatef(rot, 1, 0, 0)

    # Segmento superior
    _set(C_ROOT)
    glPushMatrix()
    glRotatef(90, 1, 0, 0)       # Fuerza al cilindro a crecer hacia abajo
    _cylinder(0.12, 0.09, 0.45)
    glPopMatrix()

    # Articulación (esfera pequeña)
    glTranslatef(0, -0.45, 0)
    _set(C_ROOT_TIP)
    _sphere(0.10)

    # Segmento inferior (punta de raíz)
    _set(C_ROOT)
    glPushMatrix()
    glRotatef(15 * side, 0, 0, 1)
    glRotatef(90, 1, 0, 0)       # Fuerza al cilindro a crecer hacia abajo
    _cylinder(0.09, 0.04, 0.38)
    glPopMatrix()

    glPopMatrix()


# ═══════════════════════════════════════════════════════════════
#  MAIN DRAW
# ═══════════════════════════════════════════════════════════════

def draw_plasma_pea():
    """
    Dibuja el Plasma Pea completo en su posición de mundo.
    GROUND_OFFSET eleva el centro del cuerpo sobre el piso de la escena,
    de modo que el personaje quede ENCIMA del suelo y no hundido en él.
    """
    GROUND_OFFSET = 1.05   # radio cuerpo (0.78) + raices (~0.27)

    # Color override por colision (flash)
    if state.collision_color_override:
        glColor3f(*state.collision_color_override)

    glPushMatrix()

    # ── escala general ────────────────────────────────────────
    glScalef(1.0, 1.0, 1.0)

    # ── CUERPO PRINCIPAL ──────────────────────────────────────
    # Esfera principal del cuerpo
    if not state.collision_color_override:
        _set(C_BODY_MAIN)
    glPushMatrix()
    glScalef(1.0, 1.05, 1.0)
    _sphere(0.78)
    glPopMatrix()

    # Anillo ecuatorial de brillo
    if not state.collision_color_override:
        _set(C_BODY_GLOW)
    glPushMatrix()
    glRotatef(90, 1, 0, 0)
    glScalef(1.0, 1.0, 0.18)
    _sphere(0.82)
    glPopMatrix()

    # ── CRESTA ────────────────────────────────────────────────
    glPushMatrix()
    glTranslatef(0.0, 0.75, 0.0)
    _draw_crest()
    glPopMatrix()

    # ── CARA (ojos y cejas en la mitad superior del cuerpo) ───
    glPushMatrix()
    glTranslatef(0.0, 0.20, 0.0)
    glRotatef(state.cabeza_y, 0, 1, 0)
    glRotatef(state.cabeza_x, 1, 0, 0)
    _draw_face()
    glPopMatrix()

    # ── CANON (sale desde la parte inferior-frontal, como la boca) ──
    # Bajado a y=-0.20 y empujado hacia adelante en z=0.55
    glPushMatrix()
    glTranslatef(0.0, -0.22, 0.55)
    _draw_cannon()
    glPopMatrix()

    # ── HOJAS ─────────────────────────────────────────────────
    _draw_leaf(+1)
    _draw_leaf(-1)

    # ── RAÍCES ────────────────────────────────────────────────
    _draw_root(+1)
    _draw_root(-1)

    glPopMatrix()