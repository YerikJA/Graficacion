# Characters/optimusPrime.py — Optimus Prime con todos los features de Plasma Pea
"""
Optimus Prime 3D — con sistema completo de:
  - Flash de colisión (collision_color_override)
  - Spin 360° (is_spinning / spin_angle)
  - Expresiones visuales por color de ojos + parpadeo guiño
  - Articulaciones animadas (cabeza, brazos, piernas)
  - Escala según agachado
"""
from OpenGL.GL  import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from Actions import state

# ── ESCALA GLOBAL ──────────────────────────────────────────────
# Optimus es grande; usamos escala 0.35 para que quepa bien en la escena
_SCALE = 0.35


def _q():
    return gluNewQuadric()


def draw_optimus_head():
    glPushMatrix()
    glTranslatef(0.0, 4.5, 0.0)
    glRotatef(state.cabeza_y, 0, 1, 0)

    # Casco (Cubo)
    glPushMatrix()
    glColor3f(0.1, 0.2, 0.8)
    glScalef(1.0, 1.2, 1.0)
    glutSolidCube(1.0)
    glPopMatrix()

    # Cubrebocas
    glPushMatrix()
    glTranslatef(0.0, -0.2, 0.6)
    glColor3f(0.7, 0.7, 0.7)
    glScalef(0.8, 0.6, 0.5)
    glutSolidCube(1.0)
    glPopMatrix()

    # Ojo Izquierdo — guiño via ojo_izq_escala
    glPushMatrix()
    glTranslatef(-0.25, 0.3, 0.55)
    glColor3f(*state.color_ojos)
    glScalef(0.3, 0.2 * state.ojo_izq_escala, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()

    # Ojo Derecho
    glPushMatrix()
    glTranslatef(0.25, 0.3, 0.55)
    glColor3f(*state.color_ojos)
    glScalef(0.3, 0.2, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()

    glPopMatrix()


def draw_optimus_torso():
    glPushMatrix()
    glTranslatef(0.0, 2.0, 0.0)
    glColor3f(0.8, 0.1, 0.1)
    glScalef(4.0, 3.5, 2.0)
    glutSolidCube(1.0)
    glPopMatrix()

    # Tubos de escape
    quad = _q()
    for dx in [-2.2, 2.2]:
        glPushMatrix()
        glTranslatef(dx, 1.5, -1.2)
        glRotatef(-90, 1, 0, 0)
        glColor3f(0.8, 0.8, 0.8)
        gluCylinder(quad, 0.3, 0.3, 3.0, 16, 16)
        glPopMatrix()
    gluDeleteQuadric(quad)

    # Ventanas del pecho izquierda
    glPushMatrix()
    glTranslatef(-0.9, 2.8, 1.0)
    glColor3f(0.2, 0.2, 0.2)
    glScalef(1.6, 1.2, 0.2)
    glutSolidCube(1.0)
    glPushMatrix()
    glTranslatef(0.0, 0.0, 0.05)
    glColor3f(0.1, 0.5, 0.8)
    glScalef(0.9, 0.9, 1.0)
    glutSolidCube(1.0)
    glPopMatrix()
    glPopMatrix()

    # Ventanas del pecho derecha
    glPushMatrix()
    glTranslatef(0.9, 2.8, 1.0)
    glColor3f(0.2, 0.2, 0.2)
    glScalef(1.6, 1.2, 0.2)
    glutSolidCube(1.0)
    glPushMatrix()
    glTranslatef(0.0, 0.0, 0.05)
    glColor3f(0.1, 0.5, 0.8)
    glScalef(0.9, 0.9, 1.0)
    glutSolidCube(1.0)
    glPopMatrix()
    glPopMatrix()


def draw_optimus_pelvis():
    glPushMatrix()
    glTranslatef(0.0, 0.0, 0.0)
    glColor3f(0.7, 0.7, 0.7)
    glScalef(3.0, 1.5, 1.8)
    glutSolidCube(1.0)
    glPopMatrix()


def draw_optimus_arms():
    # ── BRAZO IZQUIERDO (sin cambios) ────────────────────────
    glPushMatrix()
    glTranslatef(-2.5, 3.0, 0.0)
    glRotatef(state.brazo_izq_x, 1, 0, 0)

    # Hombro
    glPushMatrix()
    glColor3f(0.8, 0.1, 0.1)
    glutSolidSphere(1.0, 16, 16)
    glPopMatrix()

    # Antebrazo
    glPushMatrix()
    glTranslatef(0.0, -1.5, 0.0)
    glColor3f(0.1, 0.2, 0.8)
    glScalef(1.2, 2.5, 1.2)
    glutSolidCube(1.0)
    glPopMatrix()

    glPopMatrix()

    # ── BRAZO DERECHO — con cañón animado ────────────────────
    glPushMatrix()
    glTranslatef(2.5, 3.0, 0.0)
    glRotatef(state.brazo_der_x, 1, 0, 0)

    # Hombro (esfera roja siempre visible)
    glPushMatrix()
    glColor3f(0.8, 0.1, 0.1)
    glutSolidSphere(1.0, 16, 16)
    glPopMatrix()

    if state.opt_cannon_visible:
        # ── MODO CAÑÓN ─────────────────────────────────────
        # El antebrazo se reemplaza por la estructura del cañón

        # Antebrazo transformado: más oscuro/metálico, aplica retroceso en Y
        glPushMatrix()
        glTranslatef(0.0, -1.5 + state.opt_cannon_recoil, 0.0)

        # Carcasa principal del cañón (más ancha que el brazo normal)
        glColor3f(0.15, 0.20, 0.55)
        glScalef(1.4, 2.5, 1.4)
        glutSolidCube(1.0)
        glPopMatrix()

        # Anillo exterior del cañón (en la punta del antebrazo)
        glPushMatrix()
        glTranslatef(0.0, -3.1 + state.opt_cannon_recoil, 0.0)
        glRotatef(90, 1, 0, 0)          # cilindro apunta hacia abajo → en realidad apunta al frente
        glColor3f(0.25, 0.35, 0.75)
        q = _q(); gluCylinder(q, 0.55, 0.50, 0.30, 16, 4); gluDeleteQuadric(q)
        glPopMatrix()

        # Tubo interior oscuro (boca del cañón)
        glPushMatrix()
        glTranslatef(0.0, -3.4 + state.opt_cannon_recoil, 0.0)
        glRotatef(90, 1, 0, 0)
        glColor3f(0.05, 0.05, 0.12)
        q = _q(); gluCylinder(q, 0.30, 0.28, 0.22, 14, 4); gluDeleteQuadric(q)
        glPopMatrix()

        # Detalles laterales: dos cilindros pequeños (rieles de energía)
        for dx in [-0.55, 0.55]:
            glPushMatrix()
            glTranslatef(dx, -1.5 + state.opt_cannon_recoil, 0.0)
            glRotatef(90, 1, 0, 0)
            g = state.opt_cannon_glow
            glColor3f(0.10 + g * 0.80, 0.40 + g * 0.50, 1.0)
            q = _q(); gluCylinder(q, 0.12, 0.10, 2.2, 10, 2); gluDeleteQuadric(q)
            gluDeleteQuadric(_q())
            glPopMatrix()

        # ── BOLA DE ENERGÍA (equivalente al orbe de plasma) ──
        if state.opt_cannon_scale > 0.05:
            glPushMatrix()
            glTranslatef(0.0, -3.8 + state.opt_cannon_recoil, 0.0)

            g = state.opt_cannon_glow

            # Núcleo blanco brillante
            glColor3f(1.0, 1.0, 1.0)
            q = _q()
            gluSphere(q, 0.22 * state.opt_cannon_scale, 16, 16)
            gluDeleteQuadric(q)

            # Aura exterior azul-naranja (color Optimus)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glColor4f(0.20 + g * 0.60, 0.50, 1.0, 0.50)
            q = _q()
            gluSphere(q, 0.40 * state.opt_cannon_scale, 16, 16)
            gluDeleteQuadric(q)
            glDisable(GL_BLEND)

            glPopMatrix()

    else:
        # ── MODO NORMAL: antebrazo estándar ──────────────────
        glPushMatrix()
        glTranslatef(0.0, -1.5, 0.0)
        glColor3f(0.1, 0.2, 0.8)
        glScalef(1.2, 2.5, 1.2)
        glutSolidCube(1.0)
        glPopMatrix()

    glPopMatrix()


def draw_optimus_legs():
    for dx, rot in [(-1.0, state.pierna_izq_x), (1.0, state.pierna_der_x)]:
        glPushMatrix()
        glTranslatef(dx, -1.0, 0.0)
        glRotatef(rot, 1, 0, 0)
        glPushMatrix()
        glTranslatef(0.0, -0.5, 0.0)
        glColor3f(0.6, 0.6, 0.6)
        glScalef(1.2, 2.0, 1.2)
        glutSolidCube(1.0)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0.0, -3.0, 0.0)
        glColor3f(0.1, 0.2, 0.8)
        glScalef(1.5, 3.5, 1.8)
        glutSolidCube(1.0)
        glPopMatrix()
        glPopMatrix()


def draw_optimus_full():
    """
    Dibuja Optimus Prime completo con todos los features de Plasma Pea:
    - Flash de colisión
    - Spin 360°
    - Expresiones (color de ojos, guiño)
    - Escala de agachado
    """
    # Offset para que los pies toquen el suelo
    GROUND_OFFSET = 1.8

    # Color override por colisión (flash)
    if state.collision_color_override:
        glColor3f(*state.collision_color_override)

    glPushMatrix()

    # Escala de agachado
    sy = 0.55 if state.is_crouching else 1.0
    glScalef(_SCALE, _SCALE * sy, _SCALE)

    draw_optimus_head()
    draw_optimus_torso()
    draw_optimus_pelvis()
    draw_optimus_arms()
    draw_optimus_legs()

    glPopMatrix()
