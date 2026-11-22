# Actions/camera.py — ProyectoUnido
import math
from OpenGL.GL  import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from Actions import state

_mouse_down = False
_last_x     = 0
_last_y     = 0

ZOOM_STEP  = 0.5
YAW_SPEED  = 0.3
PITCH_SPEED = 0.3
PITCH_MIN  = -60.0
PITCH_MAX  =  80.0
DIST_MIN   =  4.0
DIST_MAX   = 40.0


def apply_camera():
    d   = state.cam_distance
    if state.escenario_actual == 7:
        if state.tetris_2p:
            # ── CÁMARA ESTÁTICA CENTRADA para Tetris 2 jugadores ──
            # Vista desde el frente, centrada en el mapa completo
            # para ver ambos personajes simultáneamente
            gluLookAt(
                0.0,  8.0, 28.0,   # ojo: centrado en X, elevado, alejado en Z
                0.0,  2.0,  0.0,   # target: centro del mapa, un poco arriba del piso
                0.0,  1.0,  0.0    # up
            )
            return
        else:
            # Cámara 1 jugador: sigue al personaje con offset
            d += 8.0
            pit = math.radians(-2.0)
    else:
        pit = math.radians(state.cam_pitch)

    yaw = math.radians(state.cam_yaw)

    cx = d * math.cos(pit) * math.sin(yaw)
    cy = d * math.sin(pit)
    cz = d * math.cos(pit) * math.cos(yaw)

    tx = state.fox_x
    tz = state.fox_z

    if state.personaje_activo == "optimus":
        ty = state.fox_y + 2.5
    elif state.personaje_activo in ("dee", "kirby"):
        ty = state.fox_y + 1.4
    elif state.personaje_activo in ("pochaco", "pucca"):
        ty = state.fox_y + 1.0
    else:
        ty = state.fox_y + 1.05 + 0.60   # Plasma Pea

    if state.escenario_actual == 7:
        ty -= 0.3

    gluLookAt(
        tx + cx, ty + cy, tz + cz,
        tx,      ty,      tz,
        0.0,     1.0,     0.0
    )


def reset_camera():
    state.cam_distance = 12.0
    state.cam_yaw      = 0.0
    state.cam_pitch    = 18.0
    state.rotate_x     = 0.0
    glutPostRedisplay()


def mouse(button, btn_state, x, y):
    global _mouse_down, _last_x, _last_y

    if button == GLUT_LEFT_BUTTON:
        _mouse_down = (btn_state == GLUT_DOWN)
        _last_x, _last_y = x, y
    elif button == 3:
        state.cam_distance = max(DIST_MIN, state.cam_distance - ZOOM_STEP)
        glutPostRedisplay()
    elif button == 4:
        state.cam_distance = min(DIST_MAX, state.cam_distance + ZOOM_STEP)
        glutPostRedisplay()
    elif button == 5:
        state.rotate_x += 10.0
        glutPostRedisplay()
    elif button == 6:
        state.rotate_x -= 10.0
        glutPostRedisplay()


def motion(x, y):
    global _last_x, _last_y
    if not _mouse_down:
        return
    dx = x - _last_x
    dy = y - _last_y
    state.cam_yaw   += dx * YAW_SPEED
    state.cam_pitch += dy * PITCH_SPEED
    state.cam_pitch  = max(PITCH_MIN, min(PITCH_MAX, state.cam_pitch))
    _last_x, _last_y = x, y
    glutPostRedisplay()
