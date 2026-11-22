# Actions/update.py — ProyectoUnido (EndGame + ProyectoFinal combinado)
import math
from Actions.audio import play_english_word
import random
from OpenGL.GLUT import *
from Actions import state, audio
from Actions import rope_pull_game

def _lerp(a, b, t):
    return a + (b - a) * t

def _elapsed():
    return glutGet(GLUT_ELAPSED_TIME) / 1000.0


def update(value):
    # Actualizar mini-juego tira de cuerda si está activo
    game = rope_pull_game.game_instance
    if game.active:
        game.update(0.016)

    t = _elapsed()
    state.animation_angle += 0.05
    state.reaction_timer  = max(0.0, state.reaction_timer - 1)
    state.blink_timer     += 0.05
    state.breath_timer    += 0.05

    # Sync aliases used by Pochacco/Pucca
    state.current_scene = state.escenario_actual
    state.walking       = state.is_walking

    _update_movement(t)

    if state.personaje_activo == "plasma":
        _update_jump(t)
        _update_shoot(t)
        _update_victory(t)
        _update_spin(t)
        _update_greet(t)
    elif state.personaje_activo == "optimus":
        _update_jump_optimus(t)
        _update_shoot_optimus(t)
        _update_victory_optimus(t)
        _update_spin_optimus(t)
        _update_greet_optimus(t)
    elif state.personaje_activo in ("dee", "kirby"):
        _update_dee_kirby(t)
    elif state.personaje_activo in ("pochaco", "pucca"):
        _update_pochaco_pucca(t)

    _update_collision_flash()
    _update_scene_light()
    _update_particles()
    _update_tetris_minigame()
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)


# ── MOVIMIENTO (compartido, usa articulaciones del personaje activo) ──
def _update_movement(t):
    moved = False
    spd   = state.fox_speed
    cam_yaw_rad = math.radians(state.cam_yaw)
    fwd_x = -math.sin(cam_yaw_rad); fwd_z = -math.cos(cam_yaw_rad)
    rgt_x =  math.cos(cam_yaw_rad); rgt_z = -math.sin(cam_yaw_rad)
    move_x = move_z = 0.0

    if state.key_up:    move_x += fwd_x; move_z += fwd_z; moved = True
    if state.key_down:  move_x -= fwd_x; move_z -= fwd_z; moved = True
    if state.key_right: move_x += rgt_x; move_z += rgt_z; moved = True
    if state.key_left:  move_x -= rgt_x; move_z -= rgt_z; moved = True

    if moved:
        mag = math.sqrt(move_x**2 + move_z**2)
        if mag > 0.001:
            move_x = (move_x / mag) * spd
            move_z = (move_z / mag) * spd
        state.fox_x += move_x
        state.fox_z += move_z
        target = math.degrees(math.atan2(move_x, move_z))
        diff = (target - state.fox_facing + 540) % 360 - 180
        state.fox_facing += diff * 0.20

    state.is_walking = moved

    if moved:
        audio.play_walk_sound()
        angle = math.sin(t * 6.5) * 30.0
        if state.personaje_activo == "plasma":
            if not state.is_jumping:
                state.raiz_izq_x =  angle
                state.raiz_der_x = -angle
                state.hoja_izq_z =  math.sin(t * 6.5) * 7.0
                state.hoja_der_z = -math.sin(t * 6.5) * 7.0
        else:
            state.pierna_izq_x =  angle
            state.pierna_der_x = -angle
            state.brazo_izq_x  = -angle
            state.brazo_der_x  =  angle
    else:
        audio.stop_walk_sound()
        if state.personaje_activo == "plasma":
            if not state.is_crouching and not state.is_victory:
                state.raiz_izq_x = _lerp(state.raiz_izq_x, 0.0, 0.15)
                state.raiz_der_x = _lerp(state.raiz_der_x, 0.0, 0.15)
            if not state.is_greeting and not state.is_victory:
                state.hoja_izq_z = _lerp(state.hoja_izq_z, 0.0, 0.15)
                state.hoja_der_z = _lerp(state.hoja_der_z, 0.0, 0.15)
        else:
            if state.pierna_der_x not in [-45.0]:
                state.pierna_izq_x = _lerp(state.pierna_izq_x, 0.0, 0.15)
                state.pierna_der_x = _lerp(state.pierna_der_x, 0.0, 0.15)
            if state.brazo_izq_x not in [-135.0]:
                state.brazo_izq_x = _lerp(state.brazo_izq_x, 0.0, 0.15)
                state.brazo_der_x = _lerp(state.brazo_der_x, 0.0, 0.15)


# ── PLASMA PEA — animaciones específicas ─────────────────────────
def _update_jump(t):
    if state.is_jumping:
        state.jump_time += 0.05
        state.fox_y = max(0.0, math.sin(state.jump_time * math.pi) * 3.5)
        if state.jump_time >= 1.0:
            state.is_jumping = False; state.jump_time = 0.0; state.fox_y = 0.0


def _update_shoot(t):
    if state.is_shooting:
        state.shoot_timer -= 1
        state.canon_x = _lerp(state.canon_x, -20.0 if state.shoot_timer > 10 else 0.0, 0.3)
        if state.shoot_timer > 15:
            state.plasma_visible = True
            state.plasma_scale   = _lerp(state.plasma_scale, 1.2, 0.25)
        else:
            state.plasma_scale = _lerp(state.plasma_scale, 0.0, 0.3)
        if state.shoot_timer <= 0:
            state.is_shooting = False; state.plasma_visible = False
            state.plasma_scale = 0.0;  state.canon_x = 0.0


def _update_victory(t):
    if state.is_victory:
        state.victory_timer -= 1
        phase = math.sin(t * 8.0)
        state.hoja_izq_y = -60.0 + phase * 20.0
        state.hoja_der_y = -60.0 - phase * 20.0
        state.cabeza_x   = -15.0 + phase * 5.0
        if state.victory_timer <= 0:
            state.is_victory = False
            state.hoja_izq_y = state.hoja_der_y = state.cabeza_x = 0.0


def _update_spin(t):
    if state.is_spinning:
        state.spin_angle += 12.0; state.spin_timer -= 1
        if state.spin_timer <= 0:
            state.is_spinning = False; state.spin_angle = 0.0


def _update_greet(t):
    if state.is_greeting:
        state.greet_timer -= 1
        state.hoja_der_y = math.sin(t * 10.0) * 50.0 - 30.0
        if state.greet_timer <= 0:
            state.is_greeting = False; state.hoja_der_y = 0.0


# ── OPTIMUS PRIME — animaciones equivalentes ─────────────────────
def _update_jump_optimus(t):
    if state.is_jumping:
        state.jump_time += 0.05
        state.fox_y = max(0.0, math.sin(state.jump_time * math.pi) * 3.5)
        if state.jump_time >= 1.0:
            state.is_jumping = False; state.jump_time = 0.0; state.fox_y = 0.0


def _update_shoot_optimus(t):
    if not state.is_shooting:
        return
    state.shoot_timer -= 1
    if state.shoot_timer > 15:
        state.opt_cannon_visible = True
        state.brazo_der_x = _lerp(state.brazo_der_x, -75.0, 0.25)
        state.opt_cannon_scale = _lerp(state.opt_cannon_scale, 1.2, 0.22)
        state.opt_cannon_glow  = _lerp(state.opt_cannon_glow,  1.0, 0.25)
        state.opt_cannon_recoil = _lerp(state.opt_cannon_recoil, 0.0, 0.3)
    else:
        state.opt_cannon_scale  = _lerp(state.opt_cannon_scale,  0.0, 0.35)
        state.opt_cannon_glow   = _lerp(state.opt_cannon_glow,   0.0, 0.30)
        if state.shoot_timer > 8:
            state.opt_cannon_recoil = _lerp(state.opt_cannon_recoil, 0.5, 0.40)
        else:
            state.opt_cannon_recoil = _lerp(state.opt_cannon_recoil, 0.0, 0.30)
        state.brazo_der_x = _lerp(state.brazo_der_x, 0.0, 0.20)
    if state.shoot_timer <= 0:
        state.is_shooting        = False
        state.opt_cannon_visible = False
        state.opt_cannon_scale   = 0.0
        state.opt_cannon_glow    = 0.0
        state.opt_cannon_recoil  = 0.0
        state.brazo_der_x        = 0.0


def _update_victory_optimus(t):
    if state.is_victory:
        state.victory_timer -= 1
        phase = math.sin(t * 8.0)
        state.brazo_izq_x = -120.0 + phase * 20.0
        state.brazo_der_x = -120.0 - phase * 20.0
        state.cabeza_y    =  phase * 10.0
        if state.victory_timer <= 0:
            state.is_victory  = False
            state.brazo_izq_x = 0.0
            state.brazo_der_x = 0.0
            state.cabeza_y    = 0.0


def _update_spin_optimus(t):
    if state.is_spinning:
        state.spin_angle += 12.0; state.spin_timer -= 1
        if state.spin_timer <= 0:
            state.is_spinning = False; state.spin_angle = 0.0


def _update_greet_optimus(t):
    if state.is_greeting:
        state.greet_timer -= 1
        state.brazo_der_x = math.sin(t * 10.0) * 50.0 - 90.0
        if state.greet_timer <= 0:
            state.is_greeting = False; state.brazo_der_x = 0.0


# ── DEE / KIRBY — animaciones ─────────────────────────────────────
def _update_dee_kirby(t):
    if state.blink_timer > 3.0:
        state.ojos_abiertos = False
        if state.blink_timer > 3.15:
            state.ojos_abiertos = True
            state.blink_timer = 0.0
    state.body_scale = 1.0 + math.sin(state.breath_timer * 1.2) * 0.015
    if state.is_greeting:
        state.greet_timer -= 1
        state.arm_angle = math.sin(t * 10.0) * 50.0 - 30.0
        if state.greet_timer <= 0:
            state.is_greeting = False; state.arm_angle = 0.0
    if state.is_walking:
        state.arm_angle  = math.sin(t * 6.0) * 30.0
        state.foot_angle = math.sin(t * 6.0) * 25.0
    else:
        state.arm_angle  = _lerp(state.arm_angle,  0.0, 0.15)
        state.foot_angle = _lerp(state.foot_angle, 0.0, 0.15)
    if state.is_jumping:
        state.jump_time += 0.05
        state.fox_y = max(0.0, math.sin(state.jump_time * math.pi) * 3.5)
        if state.jump_time >= 1.0:
            state.is_jumping = False; state.jump_time = 0.0; state.fox_y = 0.0
    if state.is_victory:
        state.victory_timer -= 1
        state.is_floating = True
        if state.victory_timer <= 0:
            state.is_victory  = False
            state.is_floating = False
    if state.is_spinning:
        state.spin_angle += 12.0; state.spin_timer -= 1
        if state.spin_timer <= 0:
            state.is_spinning = False; state.spin_angle = 0.0
    _sync_expression()


# ── POCHACO / PUCCA — animaciones ────────────────────────────────
def _update_pochaco_pucca(t):
    if state.reaction_timer <= 0:
        state.reaction_type = "normal"
    if state.is_greeting:
        state.greet_timer -= 1
        state.reaction_type = "wave"
        if state.greet_timer <= 0:
            state.is_greeting = False; state.reaction_type = "normal"
    if state.is_jumping:
        state.jump_time += 0.05
        state.fox_y = max(0.0, math.sin(state.jump_time * math.pi) * 3.5)
        if state.jump_time >= 1.0:
            state.is_jumping = False; state.jump_time = 0.0; state.fox_y = 0.0
            state.reaction_type = "normal"
    if state.is_spinning:
        state.spin_angle += 12.0; state.spin_timer -= 1
        state.reaction_type = "spin"
        state.reaction_timer = float(state.spin_timer)
        if state.spin_timer <= 0:
            state.is_spinning   = False
            state.spin_angle    = 0.0
            state.reaction_type = "normal"
    state.tail_angle = math.sin(t * 4.0) * 20.0
    if state.blink_timer > 3.0:
        if state.blink_timer > 3.15:
            state.blink_timer = 0.0
    _sync_expression()


def _sync_expression():
    mapping = {
        "normal":   "normal",
        "enojo":    "angry",
        "miedo":    "fear",
        "tristeza": "sad",
        "guino":    "wink",
        "alegria":  "happy",
        "sorpresa": "surprised",
    }
    state.expression = mapping.get(state.expresion_actual, "normal")
    if state.is_crouching:
        state.reaction_type = "crouch"


# ── PARTÍCULAS ────────────────────────────────────────────────────
def _update_particles():
    for p in state.particles[:]:
        p['life'] -= 1
        p['p'][0] += p['v'][0]
        p['p'][1] += p['v'][1]
        p['p'][2] += p['v'][2]
        if p['life'] <= 0:
            state.particles.remove(p)
    for wp in state.weather_particles[:]:
        wp['p'][1] -= 0.02
        if wp['p'][1] < -2.0:
            wp['p'][1] = 5.0


# ── FLASH DE COLISIÓN ─────────────────────────────────────────────
def _update_collision_flash():
    if state.collision_flash_timer > 0:
        state.collision_flash_timer -= 1
        if state.collision_flash_timer <= 0:
            state.collision_color_override = None
    for attr_hit, attr_timer in [
        ('zombie_hit', 'zombie_hit_timer'),
        ('caja_hit',   'caja_hit_timer'),
        ('valla_hit',  'valla_hit_timer'),
        ('obb_hit',    'obb_hit_timer'),
        ('cristal_hit','cristal_hit_timer'),
    ]:
        timer = getattr(state, attr_timer)
        if timer > 0:
            setattr(state, attr_timer, timer - 1)
            if timer - 1 <= 0:
                setattr(state, attr_hit, False)


# ── ILUMINACIÓN DINÁMICA ─────────────────────────────────────────
_SCENE_LIGHTS = {
    1: ([2.0,  8.0,  6.0, 1.0], [0.70, 0.60, 0.50, 1.0]),
    2: ([3.0, 10.0,  5.0, 1.0], [0.70, 0.70, 0.65, 1.0]),
    3: ([0.0,  9.0,  4.0, 1.0], [0.65, 0.55, 0.70, 1.0]),
    4: ([2.0,  7.0,  5.0, 1.0], [0.60, 0.60, 0.65, 1.0]),
    5: ([-2.0, 8.0,  4.0, 1.0], [0.65, 0.65, 0.70, 1.0]),
    6: ([3.0, 10.0,  6.0, 1.0], [0.70, 0.70, 0.60, 1.0]),
    7: ([0.0, 12.0,  8.0, 1.0], [0.50, 0.50, 0.65, 1.0]),
}


def _update_scene_light():
    from OpenGL.GL import glLightfv, GL_LIGHT0, GL_POSITION, GL_DIFFUSE
    pos, col = _SCENE_LIGHTS.get(state.escenario_actual, _SCENE_LIGHTS[1])
    
    # Iluminación tipo discoteca en Tetris si hay reacción
    if state.escenario_actual == 7:
        if state.tetris_reaccion_timer > 0 and state.tetris_reaccion_tipo == "bien":
            _, color = state.TETRIS_COLORS[state.tetris_objetivo_idx]
            col = [color[0], color[1], color[2], 1.0]
        elif state.tetris_p2_reaccion_timer > 0 and state.tetris_p2_reaccion_tipo == "bien":
            _, color = state.TETRIS_COLORS[state.tetris_p2_objetivo_idx]
            col = [color[0], color[1], color[2], 1.0]

    glLightfv(GL_LIGHT0, GL_POSITION, pos)
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  col)


# ── MINIJUEGO TETRIS (Escenario 7) — SOPORTE 1P Y 2P ────────────
def _tetris_nuevo_objetivo():
    state.tetris_objetivo_idx = random.randint(0, len(state.TETRIS_COLORS) - 1)
    # Reproducir el nombre del nuevo color en inglés
    color_name = state.TETRIS_COLORS[state.tetris_objetivo_idx][0]
    try: play_english_word(color_name)
    except Exception: pass

def _tetris_p2_nuevo_objetivo():
    state.tetris_p2_objetivo_idx = random.randint(0, len(state.TETRIS_COLORS) - 1)
    # Reproducir el nombre del nuevo color en inglés
    color_name = state.TETRIS_COLORS[state.tetris_p2_objetivo_idx][0]
    try: play_english_word(color_name)
    except Exception: pass


def _tetris_spawn_cubo():
    """Lanza cubos en la mitad izquierda (P1) y en la derecha (P2) si es 2P."""
    # Cubo para P1 (mitad izquierda)
    x1 = random.uniform(state.TETRIS_X_MIN + 0.5, state.TETRIS_X_MAX - 0.5)
    z1 = state.TETRIS_SPAWN_Z + random.uniform(-0.3, 0.3)
    color_idx1 = random.randint(0, len(state.TETRIS_COLORS) - 1)
    state.tetris_cubos.append({
        'x': x1, 'y': 14.0, 'z': z1,
        'color_idx': color_idx1,
        'activo': True,
        'vel': random.uniform(0.04, 0.09),
        'side': 'left',
    })

    # Cubo para P2 (mitad derecha) — solo si es 2P
    if state.tetris_2p:
        x2 = random.uniform(state.TETRIS_P2_X_MIN + 0.5, state.TETRIS_P2_X_MAX - 0.5)
        z2 = state.TETRIS_P2_SPAWN_Z + random.uniform(-0.3, 0.3)
        color_idx2 = random.randint(0, len(state.TETRIS_COLORS) - 1)
        state.tetris_cubos.append({
            'x': x2, 'y': 14.0, 'z': z2,
            'color_idx': color_idx2,
            'activo': True,
            'vel': random.uniform(0.04, 0.09),
            'side': 'right',
        })


def _tetris_reset():
    state.tetris_cubos         = []
    state.tetris_correctos     = 0
    state.tetris_p2_correctos  = 0
    state.tetris_reaccion_timer = 0
    state.tetris_reaccion_tipo  = ""
    state.tetris_p2_reaccion_timer = 0
    state.tetris_p2_reaccion_tipo  = ""
    state.tetris_spawn_timer    = 60
    state.tetris_ganado         = False
    state.tetris_ganado_timer   = 0
    state.tetris_activo         = True
    state.tetris_winner         = 0
    _tetris_nuevo_objetivo()
    if state.tetris_2p:
        _tetris_p2_nuevo_objetivo()
    # Posicionar P1
    state.fox_x = state.TETRIS_SPAWN_X
    state.fox_z = state.TETRIS_SPAWN_Z
    state.fox_y = 0.0
    # Posicionar P2
    if state.tetris_2p:
        state.p2_x = state.TETRIS_P2_SPAWN_X
        state.p2_z = state.TETRIS_P2_SPAWN_Z
        state.p2_y = 0.0
        state.p2_facing = 180.0


def _update_tetris_minigame():
    if state.en_menu or state.escenario_actual != 7:
        if state.tetris_activo:
            state.tetris_activo = False
        return

    if not state.tetris_activo:
        _tetris_reset()

    if state.tetris_ganado:
        if state.tetris_ganado_timer > 0:
            state.tetris_ganado_timer -= 1
        return

    # ── Limitar posición X del P1 a la mitad izquierda ─────
    state.fox_x = max(state.TETRIS_X_MIN, min(state.fox_x, state.TETRIS_X_MAX - 0.5))
    state.fox_z = state.TETRIS_SPAWN_Z
    state.key_up   = False
    state.key_down = False

    # ── Movimiento P2 (teclas A/D procesadas en main.py) ──
    if state.tetris_2p:
        spd = state.fox_speed
        if state.p2_key_left:
            state.p2_x -= spd
        if state.p2_key_right:
            state.p2_x += spd
        state.p2_x = max(state.TETRIS_P2_X_MIN + 0.5, min(state.p2_x, state.TETRIS_P2_X_MAX - 0.5))
        state.p2_z = state.TETRIS_P2_SPAWN_Z

    # ── Timer de spawn ─────────────────────────────
    state.tetris_spawn_timer -= 1
    if state.tetris_spawn_timer <= 0:
        _tetris_spawn_cubo()
        state.tetris_spawn_timer = state.tetris_spawn_intervalo

    # ── Timers de reacción ──────────────────────────
    if state.tetris_reaccion_timer > 0:
        state.tetris_reaccion_timer -= 1
        if state.tetris_reaccion_timer <= 0:
            state.tetris_reaccion_tipo = ""

    if state.tetris_p2_reaccion_timer > 0:
        state.tetris_p2_reaccion_timer -= 1
        if state.tetris_p2_reaccion_timer <= 0:
            state.tetris_p2_reaccion_tipo = ""

    # ── Mover cubos y detectar colisión ─────
    RADIO_JUGADOR = 1.0
    SUELO_Y       = 0.0

    for cubo in state.tetris_cubos[:]:
        if not cubo['activo']:
            state.tetris_cubos.remove(cubo)
            continue

        cubo['y'] -= cubo['vel']
        side = cubo.get('side', 'left')

        # Colisión con P1 (cubos del lado izquierdo)
        if side == 'left':
            dx = abs(cubo['x'] - state.fox_x)
            dz = abs(cubo['z'] - state.fox_z)
            dy = cubo['y']
            if dx < RADIO_JUGADOR and dz < RADIO_JUGADOR and -0.5 < dy < 3.0:
                cubo['activo'] = False
                state.tetris_cubos.remove(cubo)
                es_correcto = (cubo['color_idx'] == state.tetris_objetivo_idx)
                if es_correcto:
                    state.tetris_correctos += 1
                    state.tetris_reaccion_tipo  = "bien"
                    state.tetris_reaccion_timer = 80
                    state.is_victory    = True
                    state.victory_timer = 60
                    from Resources import input_handlers
                    input_handlers._expr_alegria()
                else:
                    state.tetris_correctos = max(0, state.tetris_correctos - 1)
                    state.tetris_reaccion_tipo  = "mal"
                    state.tetris_reaccion_timer = 80
                    from Resources import input_handlers
                    input_handlers._expr_enojo()
                _tetris_nuevo_objetivo()
                if state.tetris_correctos >= 10:
                    state.tetris_ganado = True
                    state.tetris_ganado_timer = 180
                    state.tetris_winner = 1
                continue

        # Colisión con P2 (cubos del lado derecho) — solo 2P
        if side == 'right' and state.tetris_2p:
            dx = abs(cubo['x'] - state.p2_x)
            dz = abs(cubo['z'] - state.p2_z)
            dy = cubo['y']
            if dx < RADIO_JUGADOR and dz < RADIO_JUGADOR and -0.5 < dy < 3.0:
                cubo['activo'] = False
                state.tetris_cubos.remove(cubo)
                es_correcto = (cubo['color_idx'] == state.tetris_p2_objetivo_idx)
                if es_correcto:
                    state.tetris_p2_correctos += 1
                    state.tetris_p2_reaccion_tipo  = "bien"
                    state.tetris_p2_reaccion_timer = 80
                else:
                    state.tetris_p2_correctos = max(0, state.tetris_p2_correctos - 1)
                    state.tetris_p2_reaccion_tipo  = "mal"
                    state.tetris_p2_reaccion_timer = 80
                _tetris_p2_nuevo_objetivo()
                if state.tetris_p2_correctos >= 10:
                    state.tetris_ganado = True
                    state.tetris_ganado_timer = 180
                    state.tetris_winner = 2
                continue

        # El cubo llegó al suelo
        if cubo['y'] < SUELO_Y:
            cubo['activo'] = False
            state.tetris_cubos.remove(cubo)
