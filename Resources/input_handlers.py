# Resources/input_handlers.py — Proyecto Combinado
"""
Teclado unificado para Plasma Pea + Optimus Prime.

IMPORTANTE — Movimientos especiales (Z, N para Plasma / Z, N para Optimus):
  • El cambio de escenario (teleporte visual) SOLO ocurre cuando el movimiento
    especial es activado POR una colisión (a través de collisions.py).
  • Cuando el jugador presiona la tecla directamente, se anima el personaje
    pero NO cambia de escenario.  Esto evita el "teleporte involuntario".
"""
from OpenGL.GL   import *
from OpenGL.GLUT import *
from Actions import state, camera, audio

_SHADE_CYCLE = ['gouraud', 'flat', 'phong']


def apply_shade_mode():
    if state.shade_mode == 'flat':
        glShadeModel(GL_FLAT)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR,  [0.1, 0.1, 0.1, 1.0])
        glMaterialf (GL_FRONT_AND_BACK, GL_SHININESS,  8.0)
    elif state.shade_mode == 'gouraud':
        glShadeModel(GL_SMOOTH)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR,  [0.40, 0.50, 0.60, 1.0])
        glMaterialf (GL_FRONT_AND_BACK, GL_SHININESS,  32.0)
    else:
        glShadeModel(GL_SMOOTH)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR,  [0.90, 0.95, 1.00, 1.0])
        glMaterialf (GL_FRONT_AND_BACK, GL_SHININESS,  128.0)
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT,   [0.05, 0.08, 0.15, 1.0])


# ══════════════════════════════════════════════════════════════
#  EXPRESIONES — Plasma Pea
# ══════════════════════════════════════════════════════════════
def _set_expression_normal():
    state.ojo_escala_izq = state.ojo_escala_der = 1.0
    state.ojo_offset_y_izq = state.ojo_offset_y_der = 0.0
    state.ojo_color = (0.4, 0.9, 1.0)
    state.ceja_rot_izq = state.ceja_rot_der = state.ceja_offset_y = 0.0
    state.boca_escala_y = 1.0; state.boca_curva = 0.0; state.boca_abierta = False
    state.expresion_actual = "normal"

def _set_expression_enojo():
    state.ojo_escala_izq = state.ojo_escala_der = 0.6
    state.ojo_offset_y_izq = state.ojo_offset_y_der = -0.05
    state.ojo_color = (1.0, 0.15, 0.15)
    state.ceja_rot_izq = state.ceja_rot_der = 25.0; state.ceja_offset_y = -0.08
    state.boca_escala_y = 0.7; state.boca_curva = -0.8; state.boca_abierta = False
    state.expresion_actual = "enojo"

def _set_expression_miedo():
    state.ojo_escala_izq = state.ojo_escala_der = 1.5
    state.ojo_offset_y_izq = state.ojo_offset_y_der = 0.06
    state.ojo_color = (0.8, 0.8, 0.2)
    state.ceja_rot_izq = state.ceja_rot_der = -20.0; state.ceja_offset_y = 0.12
    state.boca_escala_y = 1.4; state.boca_curva = -0.5; state.boca_abierta = True
    state.expresion_actual = "miedo"

def _set_expression_tristeza():
    state.ojo_escala_izq = state.ojo_escala_der = 0.75
    state.ojo_offset_y_izq = state.ojo_offset_y_der = -0.08
    state.ojo_color = (0.30, 0.55, 0.85)
    state.ceja_rot_izq = state.ceja_rot_der = -18.0; state.ceja_offset_y = -0.10
    state.boca_escala_y = 1.1; state.boca_curva = -1.0; state.boca_abierta = False
    state.expresion_actual = "tristeza"

def _set_expression_guino():
    state.ojo_escala_izq = 0.05; state.ojo_escala_der = 1.0
    state.ojo_offset_y_izq = state.ojo_offset_y_der = 0.0
    state.ojo_color = (0.4, 0.9, 1.0)
    state.ceja_rot_izq = state.ceja_rot_der = state.ceja_offset_y = 0.0
    state.boca_escala_y = 1.2; state.boca_curva = 1.0; state.boca_abierta = False
    state.expresion_actual = "guino"

def _set_expression_alegria():
    state.ojo_escala_izq = state.ojo_escala_der = 1.2
    state.ojo_offset_y_izq = state.ojo_offset_y_der = 0.05
    state.ojo_color = (0.20, 1.0, 0.60)
    state.ceja_rot_izq = state.ceja_rot_der = -12.0; state.ceja_offset_y = 0.08
    state.boca_escala_y = 1.3; state.boca_curva = 1.0; state.boca_abierta = False
    state.expresion_actual = "alegria"

def _set_expression_sorpresa():
    state.ojo_escala_izq = state.ojo_escala_der = 1.8
    state.ojo_offset_y_izq = state.ojo_offset_y_der = 0.10
    state.ojo_color = (0.9, 0.9, 1.0)
    state.ceja_rot_izq = state.ceja_rot_der = -30.0; state.ceja_offset_y = 0.18
    state.boca_escala_y = 1.6; state.boca_curva = 0.0; state.boca_abierta = True
    state.expresion_actual = "sorpresa"


# ══════════════════════════════════════════════════════════════
#  EXPRESIONES — Optimus Prime (color de ojos + guiño)
# ══════════════════════════════════════════════════════════════
def _opt_normal():
    state.color_ojos = (0.1, 0.8, 1.0); state.ojo_izq_escala = 1.0; state.expresion_actual = "normal"

def _opt_enojo():
    state.color_ojos = (1.0, 0.0, 0.0); state.ojo_izq_escala = 1.0; state.expresion_actual = "enojo"

def _opt_miedo():
    state.color_ojos = (1.0, 1.0, 0.0); state.ojo_izq_escala = 1.5; state.expresion_actual = "miedo"

def _opt_tristeza():
    state.color_ojos = (0.2, 0.2, 0.7); state.ojo_izq_escala = 0.6; state.expresion_actual = "tristeza"

def _opt_guino():
    state.color_ojos = (0.1, 0.8, 1.0); state.ojo_izq_escala = 0.05; state.expresion_actual = "guino"

def _opt_alegria():
    state.color_ojos = (0.2, 1.0, 0.4); state.ojo_izq_escala = 1.3; state.expresion_actual = "alegria"

def _opt_sorpresa():
    state.color_ojos = (1.0, 1.0, 1.0); state.ojo_izq_escala = 1.8; state.expresion_actual = "sorpresa"


# Helpers que aplican la expresión correcta según el personaje activo
def _expr_normal():
    if state.personaje_activo == "plasma": _set_expression_normal()
    else: _opt_normal()

def _expr_enojo():
    if state.personaje_activo == "plasma": _set_expression_enojo()
    else: _opt_enojo()

def _expr_miedo():
    if state.personaje_activo == "plasma": _set_expression_miedo()
    else: _opt_miedo()

def _expr_tristeza():
    if state.personaje_activo == "plasma": _set_expression_tristeza()
    else: _opt_tristeza()

def _expr_guino():
    if state.personaje_activo == "plasma": _set_expression_guino()
    else: _opt_guino()

def _expr_alegria():
    if state.personaje_activo == "plasma": _set_expression_alegria()
    else: _opt_alegria()

def _expr_sorpresa():
    if state.personaje_activo == "plasma": _set_expression_sorpresa()
    else: _opt_sorpresa()


def _sound(name):
    """Reproduce sonido usando variante Optimus si existe."""
    if state.personaje_activo == "optimus":
        # Algunos sonidos tienen versión Optimus
        opt_name = name + "_opt"
        if opt_name in state.sounds and state.sounds.get(opt_name):
            audio.play_sound(opt_name)
            return
    audio.play_sound(name)


# ══════════════════════════════════════════════════════════════
#  RESET DE ESTADO (al volver al menú)
# ══════════════════════════════════════════════════════════════
def _reset_state():
    state.fox_x = state.fox_y = state.fox_z = 0.0
    state.fox_facing = 0.0
    state.is_walking = state.is_jumping = state.is_shooting = False
    state.is_victory = state.is_spinning = state.is_greeting = state.is_crouching = False
    state.jump_time = state.spin_angle = 0.0
    state.spin_timer = state.greet_timer = state.victory_timer = state.shoot_timer = 0
    state.plasma_visible = False; state.plasma_scale = 0.0; state.canon_x = 0.0
    state.opt_cannon_visible = False; state.opt_cannon_scale = 0.0
    state.opt_cannon_glow = 0.0; state.opt_cannon_recoil = 0.0
    state.cabeza_y = state.cabeza_x = 0.0
    state.brazo_izq_x = state.brazo_der_x = 0.0
    state.pierna_izq_x = state.pierna_der_x = 0.0
    state.hoja_izq_z = state.hoja_der_z = state.hoja_izq_y = state.hoja_der_y = 0.0
    state.raiz_izq_x = state.raiz_der_x = 0.0
    # Reiniciar colisiones
    state.zombie_activo = state.caja_activa = state.obb_activo = state.cristal_activo = True
    state.zombie_hit = state.caja_hit = state.valla_hit = state.obb_hit = state.cristal_hit = False
    state.zombie_hit_timer = state.caja_hit_timer = state.valla_hit_timer = 0
    state.obb_hit_timer = state.cristal_hit_timer = 0
    state.collision_color_override = None; state.collision_flash_timer = 0
    state.escenario_actual = 1
    camera.reset_camera()
    _expr_normal()


# ══════════════════════════════════════════════════════════════
#  TECLADO PRINCIPAL
# ══════════════════════════════════════════════════════════════
def handle_keyboard(key, x, y):
    try:
        tecla = key.decode('utf-8').lower()
    except Exception:
        return

    # ── Menú: manejado por main.py — no hacer nada aquí ──────
    if state.en_menu:
        glutPostRedisplay()
        return

    # ── Tecla ESC: manejado por main.py ───────────────────────
    if ord(key) == 27:
        glutPostRedisplay()
        return

    # ── Controles generales ───────────────────────────────────
    if   tecla == 'i': state.show_instructions = not state.show_instructions; state.show_about = False
    elif tecla == 'h': state.show_about = not state.show_about; state.show_instructions = False
    elif tecla == 'k': state.show_bv = not state.show_bv
    elif tecla == 'm': state.sonido_activado = not state.sonido_activado; audio.toggle_music()
    elif tecla == 's':
        idx = _SHADE_CYCLE.index(state.shade_mode)
        state.shade_mode = _SHADE_CYCLE[(idx + 1) % 3]
        apply_shade_mode()
    elif tecla in [str(n) for n in range(1, 8)]:
        # Solo permitir si el número tecleado corresponde al escenario actual
        # (bloquear cambio de escenario por teclado durante el juego)
        if int(tecla) != state.escenario_actual:
            glutPostRedisplay()
            return
        state.escenario_actual = int(tecla)
        if state.escenario_actual == 7:
            state.fox_facing = 180.0
            # Reiniciar minijuego Tetris
            state.tetris_activo         = False   # update.py lo reiniciara en el siguiente tick
            state.tetris_cubos          = []
            state.tetris_correctos      = 0
            state.tetris_ganado         = False
            state.tetris_reaccion_timer = 0
            state.tetris_reaccion_tipo  = ""
            state.fox_x = state.TETRIS_SPAWN_X
            state.fox_z = state.TETRIS_SPAWN_Z
            state.key_up = state.key_down = False
        audio.on_scenario_change(state.escenario_actual)

    # ── Expresiones (comunes a ambos) ─────────────────────────
    elif tecla == 'q': _expr_normal();   _sound("normal")
    elif tecla == 'w': _expr_enojo();    _sound("enojo")
    elif tecla == 'e': _expr_miedo();    _sound("miedo")
    elif tecla == 't': _expr_tristeza(); _sound("tristeza")
    elif tecla == 'y': _expr_guino();    _sound("guino")
    elif tecla == 'u': _expr_alegria();  _sound("alegria")
    elif tecla == 'o': _expr_sorpresa(); _sound("sorpresa")

    # ── Movimientos especiales ────────────────────────────────
    # NOTA: ninguno de estos cambia el escenario aquí.
    # El cambio de escenario solo ocurre en collisions.py al detectar colisión.

    elif tecla == 'x':   # Saltar
        if not state.is_jumping:
            state.is_jumping = True; state.jump_time = 0.0
            _expr_sorpresa()
            _sound("salto")

    elif tecla == 'z':   # Disparar (Plasma) / Puñetazo (Optimus)
        if state.personaje_activo == "plasma":
            if not state.is_shooting:
                state.is_shooting = True; state.shoot_timer = 30
                state.plasma_visible = True
                _expr_normal()
                _sound("disparo")
        else:
            # Optimus: lanza puñetazo (brazo der hacia adelante)
            if not state.is_shooting:
                state.is_shooting = True; state.shoot_timer = 30
                _expr_enojo()
                _sound("brazos")

    elif tecla == 'c':   # Victoria → alegría
        if not state.is_victory:
            state.is_victory = True; state.victory_timer = 90
            _expr_alegria()
            _sound("victoria")

    elif tecla == 'v':   # Agacharse → tristeza
        state.is_crouching = not state.is_crouching
        if state.is_crouching:
            if state.personaje_activo == "plasma":
                state.raiz_izq_x = state.raiz_der_x = -40.0
                state.fox_y = -0.45
            else:
                state.pierna_izq_x = state.pierna_der_x = -45.0
                state.fox_y = -0.5
            _expr_tristeza()
            _sound("agachar")
        else:
            if state.personaje_activo == "plasma":
                state.raiz_izq_x = state.raiz_der_x = 0.0
            else:
                state.pierna_izq_x = state.pierna_der_x = 0.0
            state.fox_y = 0.0
            _expr_normal()
            _sound("agachar")

    elif tecla == 'b':   # Saludar → alegría
        if not state.is_greeting:
            state.is_greeting = True; state.greet_timer = 80
            _expr_alegria()
            _sound("saludo")

    elif tecla == 'n':   # Spin 360°
        if not state.is_spinning:
            state.is_spinning = True; state.spin_timer = 45; state.spin_angle = 0.0
            _expr_guino()
            _sound("spin")

    elif tecla == 'g':   # Girar cabeza
        if state.personaje_activo == "plasma":
            state.cabeza_y = 45.0 if state.cabeza_y == 0.0 else 0.0
        else:
            state.cabeza_y = 45.0 if state.cabeza_y == 0.0 else 0.0
        _sound("cabeza")

    elif tecla == 'r':
        camera.reset_camera()

    glutPostRedisplay()


def handle_special_down(key, x, y):
    if state.en_menu:
        # Las flechas del menu son manejadas por main.py
        return

    # En escenario 7 (Tetris) solo se permite movimiento lateral
    if state.escenario_actual == 7:
        if   key == GLUT_KEY_LEFT:  state.key_left  = True
        elif key == GLUT_KEY_RIGHT: state.key_right = True
        return

    if   key == GLUT_KEY_UP:    state.key_up    = True
    elif key == GLUT_KEY_DOWN:  state.key_down  = True
    elif key == GLUT_KEY_LEFT:  state.key_left  = True
    elif key == GLUT_KEY_RIGHT: state.key_right = True

def handle_special_up(key, x, y):
    if   key == GLUT_KEY_UP:    state.key_up    = False
    elif key == GLUT_KEY_DOWN:  state.key_down  = False
    elif key == GLUT_KEY_LEFT:  state.key_left  = False
    elif key == GLUT_KEY_RIGHT: state.key_right = False
