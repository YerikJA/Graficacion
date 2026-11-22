# Resources/collisions.py
"""
ALGORITMOS DE COLISIÓN — Plasma Pea 3D (v2)
  1. Esfera/Círculo     — distancia euclidiana  → Zombie
  2. AABB cuadrado      — caja alineada a ejes  → Caja de munición
  3. AABB rectangular   — half-extents asimét.  → Valla
  4. Métrica del Rombo  — distancia Manhattan   → Orbe de plasma (Z)
  5. OBB simplificado   — rotación discreta     → Árbol rotado  [NUEVO]
  6. AABB + cristal     — respuesta especial    → Cristal de poder [NUEVO]
"""
import math
from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *
from Actions import state, audio


def _apply_expr(nombre):
    """Aplica la expresión correcta según el personaje activo."""
    from Resources.input_handlers import (
        _set_expression_enojo, _set_expression_alegria,
        _set_expression_miedo, _set_expression_sorpresa,
        _set_expression_guino, _set_expression_normal,
        _opt_enojo, _opt_alegria, _opt_miedo,
        _opt_sorpresa, _opt_guino, _opt_normal,
    )
    _map_plasma  = {"enojo": _set_expression_enojo, "alegria": _set_expression_alegria,
                    "miedo": _set_expression_miedo, "sorpresa": _set_expression_sorpresa,
                    "guino": _set_expression_guino, "normal": _set_expression_normal}
    _map_optimus = {"enojo": _opt_enojo, "alegria": _opt_alegria,
                    "miedo": _opt_miedo, "sorpresa": _opt_sorpresa,
                    "guino": _opt_guino, "normal": _opt_normal}
    m = _map_optimus if state.personaje_activo == "optimus" else _map_plasma
    fn = m.get(nombre)
    if fn:
        fn()

# Parámetros de volúmenes envolventes
R_PERSONAJE = 0.6
R_ZOMBIE    = 1.2
R_CAJA      = 0.8
R_VALLA_X   = 2.2
R_VALLA_Z   = 0.5
R_ORBE      = 1.4

# OBB — árbol rotado 35° en plano XZ
OBB_X   = -6.0
OBB_Z   =  4.0
OBB_HW  =  0.5   # half-width local
OBB_HD  =  0.5   # half-depth local
OBB_ROT = math.radians(35)

# Cristal de poder
R_CRISTAL = 0.9


# ── Algoritmo 1 ── Esfera (euclidiana) ─────────────────────────
def check_esfera_zombie(px, pz):
    if not state.zombie_activo or state.zombie_hit:
        return
    d = math.sqrt((px - state.zombie_x)**2 + (pz - state.zombie_z)**2)
    if d < R_ZOMBIE + R_PERSONAJE:
        state.zombie_hit       = True
        state.zombie_hit_timer = 90
        state.collision_color_override = (0.20, 1.0, 1.0)
        state.collision_flash_timer    = 40
        # Expresión + movimiento + escenario simultáneos
        state.escenario_actual = 3   # → Zgypt al chocar con zombie
        _apply_expr("enojo")
        audio.play_sound("hit_zombie"); audio.play_sound("enojo")
        dx  = px - state.zombie_x
        dz  = pz - state.zombie_z
        mag = max(0.001, math.sqrt(dx*dx + dz*dz))
        state.fox_x += (dx / mag) * 0.9
        state.fox_z += (dz / mag) * 0.9


# ── Algoritmo 2 ── AABB cuadrado ───────────────────────────────
def check_aabb_caja(px, pz):
    if not state.caja_activa or state.caja_hit:
        return
    if (abs(px - state.caja_x) < R_CAJA + R_PERSONAJE and
            abs(pz - state.caja_z) < R_CAJA + R_PERSONAJE):
        state.caja_hit       = True
        state.caja_hit_timer = 90
        state.collision_color_override = (1.0, 0.88, 0.15)
        state.collision_flash_timer    = 40
        if not state.is_victory:
            state.is_victory    = True
            state.victory_timer = 100
        _apply_expr("alegria")
        state.escenario_actual = 5   # → Roma al recoger la caja
        audio.play_sound("hit_caja"); audio.play_sound("victoria")


# ── Algoritmo 3 ── AABB rectangular ───────────────────────────
def check_aabb_valla(px, pz):
    if state.valla_hit:
        return
    if (abs(px - state.valla_x) < R_VALLA_X + R_PERSONAJE and
            abs(pz - state.valla_z) < R_VALLA_Z + R_PERSONAJE):
        state.valla_hit       = True
        state.valla_hit_timer = 70
        state.collision_color_override = (1.0, 0.42, 0.08)
        state.collision_flash_timer    = 35
        state.fox_z += 1.0 if state.key_up else -0.8
        _apply_expr("miedo")
        state.escenario_actual = 7   # → Noche del Parque al golpear la valla
        audio.play_sound("hit_valla"); audio.play_sound("miedo")


# ── Algoritmo 4 ── Métrica del Rombo (Manhattan) ───────────────
def check_manhattan_orbe(px, pz):
    # Para Optimus: is_shooting actúa como "puñetazo activo"
    activo = state.plasma_visible if state.personaje_activo == "plasma" else state.is_shooting
    if not activo or not state.zombie_activo:
        return
    rad  = math.radians(state.fox_facing)
    ox   = state.fox_x + math.sin(rad) * 1.5
    oz   = state.fox_z + math.cos(rad) * 1.5
    if abs(ox - state.zombie_x) + abs(oz - state.zombie_z) < R_ORBE:
        state.zombie_activo = False
        state.zombie_hit    = True
        state.collision_color_override = (0.80, 0.20, 1.00)
        state.collision_flash_timer    = 50
        _apply_expr("alegria")
        state.escenario_actual = 2   # → Dinolandz al destruir zombie
        audio.play_sound("disparo")


# ── Algoritmo 5 ── OBB simplificado (árbol rotado 35°) — NUEVO ─
def check_obb_arbol(px, pz):
    """
    Transforma la posición del personaje al espacio local del OBB
    aplicando una rotación inversa, luego hace prueba AABB estándar.
    """
    if not state.obb_activo or state.obb_hit:
        return
    cos_a = math.cos(-OBB_ROT)
    sin_a = math.sin(-OBB_ROT)
    dx    = px - OBB_X
    dz    = pz - OBB_Z
    lx    = cos_a * dx - sin_a * dz   # espacio local del OBB
    lz    = sin_a * dx + cos_a * dz
    if abs(lx) < OBB_HW + R_PERSONAJE and abs(lz) < OBB_HD + R_PERSONAJE:
        state.obb_hit       = True
        state.obb_hit_timer = 80
        state.collision_color_override = (1.0, 0.95, 0.10)
        state.collision_flash_timer    = 40
        _apply_expr("sorpresa")
        state.escenario_actual = 4   # → Azia al chocar con el árbol
        if not state.is_spinning:
            state.is_spinning = True
            state.spin_timer  = 30
            state.spin_angle  = 0.0
        audio.play_sound("sorpresa")


# ── Algoritmo 6 ── AABB cristal de poder — NUEVO ───────────────
def check_aabb_cristal(px, pz):
    """
    AABB estándar. Al tocarlo el personaje ejecuta victoria + guiño
    y salta al escenario Medieval.
    """
    if not state.cristal_activo or state.cristal_hit:
        return
    if (abs(px - state.cristal_x) < R_CRISTAL + R_PERSONAJE and
            abs(pz - state.cristal_z) < R_CRISTAL + R_PERSONAJE):
        state.cristal_hit       = True
        state.cristal_hit_timer = 90
        state.cristal_activo    = False
        state.collision_color_override = (0.80, 0.40, 1.00)
        state.collision_flash_timer    = 50
        _apply_expr("guino")
        state.escenario_actual = 6   # → Medieval al recoger el cristal
        if not state.is_victory:
            state.is_victory    = True
            state.victory_timer = 90
        audio.play_sound("victoria"); audio.play_sound("guino")


# ── Punto de entrada único (llamado cada frame) ─────────────────
def check_all_collisions():
    px, pz = state.fox_x, state.fox_z
    check_esfera_zombie(px, pz)    # Alg. 1
    check_aabb_caja(px, pz)        # Alg. 2
    check_aabb_valla(px, pz)       # Alg. 3
    check_manhattan_orbe(px, pz)   # Alg. 4
    check_obb_arbol(px, pz)        # Alg. 5 — NUEVO
    check_aabb_cristal(px, pz)     # Alg. 6 — NUEVO


# ── Visualización de bounding volumes (tecla K) ─────────────────
def draw_bounding_volumes():
    if not getattr(state, 'show_bv', False):
        return
    glDisable(GL_LIGHTING)
    glLineWidth(2.0)
    Y = 0.05

    # 1. Círculo zombie (cian)
    if state.zombie_activo:
        glColor3f(0.0, 1.0, 1.0)
        r = R_ZOMBIE + R_PERSONAJE
        glBegin(GL_LINE_LOOP)
        for i in range(36):
            a = math.radians(i * 10)
            glVertex3f(state.zombie_x + r*math.cos(a), Y, state.zombie_z + r*math.sin(a))
        glEnd()

    # 2. AABB caja (azul)
    if state.caja_activa:
        glColor3f(0.2, 0.6, 1.0)
        hw = R_CAJA + R_PERSONAJE
        cx, cz = state.caja_x, state.caja_z
        glBegin(GL_LINE_LOOP)
        glVertex3f(cx-hw, Y, cz-hw); glVertex3f(cx+hw, Y, cz-hw)
        glVertex3f(cx+hw, Y, cz+hw); glVertex3f(cx-hw, Y, cz+hw)
        glEnd()

    # 3. AABB valla (rojo)
    glColor3f(1.0, 0.3, 0.1)
    hx = R_VALLA_X + R_PERSONAJE; hz = R_VALLA_Z + R_PERSONAJE
    vx, vz = state.valla_x, state.valla_z
    glBegin(GL_LINE_LOOP)
    glVertex3f(vx-hx, Y, vz-hz); glVertex3f(vx+hx, Y, vz-hz)
    glVertex3f(vx+hx, Y, vz+hz); glVertex3f(vx-hx, Y, vz+hz)
    glEnd()

    # 4. Rombo orbe (magenta)
    if state.plasma_visible:
        rad = math.radians(state.fox_facing)
        ox  = state.fox_x + math.sin(rad) * 1.5
        oz  = state.fox_z + math.cos(rad) * 1.5
        glColor3f(1.0, 0.0, 1.0)
        r = R_ORBE
        glBegin(GL_LINE_LOOP)
        glVertex3f(ox, Y, oz-r); glVertex3f(ox+r, Y, oz)
        glVertex3f(ox, Y, oz+r); glVertex3f(ox-r, Y, oz)
        glEnd()

    # 5. OBB árbol (amarillo) — NUEVO
    if state.obb_activo:
        glColor3f(1.0, 0.95, 0.10)
        hw = OBB_HW + R_PERSONAJE; hd = OBB_HD + R_PERSONAJE
        cos_a = math.cos(OBB_ROT); sin_a = math.sin(OBB_ROT)
        corners = [(-hw,-hd),(hw,-hd),(hw,hd),(-hw,hd)]
        glBegin(GL_LINE_LOOP)
        for lx, lz in corners:
            wx = OBB_X + cos_a*lx - sin_a*lz
            wz = OBB_Z + sin_a*lx + cos_a*lz
            glVertex3f(wx, Y, wz)
        glEnd()

    # 6. AABB cristal (violeta) — NUEVO
    if state.cristal_activo:
        glColor3f(0.80, 0.40, 1.00)
        hw = R_CRISTAL + R_PERSONAJE
        cx, cz = state.cristal_x, state.cristal_z
        glBegin(GL_LINE_LOOP)
        glVertex3f(cx-hw, Y, cz-hw); glVertex3f(cx+hw, Y, cz-hw)
        glVertex3f(cx+hw, Y, cz+hw); glVertex3f(cx-hw, Y, cz+hw)
        glEnd()

    # Radio personaje (verde)
    glColor3f(0.0, 1.0, 0.3)
    glBegin(GL_LINE_LOOP)
    for i in range(36):
        a = math.radians(i * 10)
        glVertex3f(state.fox_x + R_PERSONAJE*math.cos(a), Y,
                   state.fox_z + R_PERSONAJE*math.sin(a))
    glEnd()

    glLineWidth(1.0)
    glEnable(GL_LIGHTING)
