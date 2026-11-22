from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
from Actions import state

def get_current_color():
    if state.color_flash_timer > 0: return (1.0, 1.0, 1.0)
    return state.kirby_colors[state.current_color_idx]

def draw_particles():
    glDisable(GL_LIGHTING)
    for p in state.particles:
        r, g, b = p['color']
        alpha = p['life'] / 40.0
        glPushMatrix()
        glTranslatef(p['p'][0], p['p'][1], p['p'][2])
        scale = 0.05 * (p['life'] / 40.0)
        glScalef(scale, scale, scale)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(r, g, b, alpha)
        glutSolidOctahedron()
        glDisable(GL_BLEND)
        glPopMatrix()
    glEnable(GL_LIGHTING)

def draw_body():
    glPushMatrix()
    r, g, b = get_current_color()
    glColor3f(r, g, b)
    glScalef(state.body_scale, state.body_scale, state.body_scale)
    glutSolidSphere(0.8, 40, 40)
    glPopMatrix()

def draw_arms():
    r, g, b = get_current_color()
    glColor3f(r, g, b)
    for dx, side in [(-0.85, 1), (0.85, -1)]:
        glPushMatrix()
        glTranslatef(dx * state.body_scale, 0.1, 0)
        if state.is_floating:
            glRotatef(-30 * side, 0, 1, 0); glRotatef(60 * side, 0, 0, 1)
        else:
            glRotatef(state.arm_angle * side, 1, 0, 0); glRotatef(20 * side, 0, 0, 1)
        glutSolidSphere(0.3, 20, 20)
        glPopMatrix()

def draw_feet():
    glColor3f(0.3, 0.3, 0.3) if state.current_color_idx == 6 else glColor3f(0.8, 0.0, 0.1)
    for dx, side in [(-0.5, 1), (0.5, -1)]:
        glPushMatrix()
        glTranslatef(dx * state.body_scale, -0.7 * state.body_scale, 0.1)
        if not state.is_floating: glRotatef(state.foot_angle * side, 1, 0, 0)
        else: glRotatef(10, 1, 0, 0)
        glScalef(1.5, 0.8, 1.8); glutSolidSphere(0.3, 20, 20)
        glPopMatrix()

def draw_eyes():
    z_offset = 0.73 * state.body_scale
    if state.expression == "happy":
        glColor3f(0,0,0); glLineWidth(4.0)
        for dx in [-0.18, 0.18]:
            glPushMatrix()
            glTranslatef(dx * state.body_scale, 0.25 * state.body_scale, z_offset + 0.03)
            glBegin(GL_LINE_STRIP)
            for a in range(0, 181, 10):
                theta = math.radians(a)
                glVertex2f(0.12 * math.cos(theta), 0.1 * math.sin(theta))
            glEnd(); glPopMatrix()
        return
    if not state.ojos_abiertos:
        glColor3f(0,0,0)
        for dx in [-0.18, 0.18]:
            glPushMatrix()
            glTranslatef(dx * state.body_scale, 0.22 * state.body_scale, z_offset + 0.02)
            glScalef(1.2, 0.1, 0.1); glutSolidSphere(0.06, 10, 10); glPopMatrix()
        return
    for dx in [-0.18, 0.18]:
        glPushMatrix()
        glTranslatef(dx * state.body_scale, 0.22 * state.body_scale, z_offset)
        glPushMatrix(); glScalef(1.4, 3.4, 1); glColor3f(0,0,0); glutSolidSphere(0.06, 20, 20); glPopMatrix()
        glPushMatrix(); glTranslatef(0, 0.1, 0.04); glScalef(0.9, 1.7, 1); glColor3f(1,1,1); glutSolidSphere(0.04, 20, 20); glPopMatrix()
        glPopMatrix()

def draw_cheeks():
    """Dibuja las mejillas rosadas de Kirby."""
    # Usar transparencia para que se mezcle mejor con el cuerpo
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    # Color rosa
    glColor4f(1.0, 0.4, 0.6, 0.8) # Rosa

    z_offset = 0.76 * state.body_scale
    # Posición relativa a los ojos
    for dx in [-0.35, 0.35]:
        glPushMatrix()
        glTranslatef(dx * state.body_scale, 0.05 * state.body_scale, z_offset)
        # Escalar para que sea un óvalo horizontal
        glScalef(1.5, 0.8, 1.0)
        glutSolidSphere(0.05, 15, 15)
        glPopMatrix()
    glDisable(GL_BLEND)

def draw_mouth():
    z_offset = 0.75 * state.body_scale
    glPushMatrix()
    if state.expression == "angry":
        glTranslatef(0, -0.15 * state.body_scale, z_offset + 0.03); glColor3f(0.4, 0, 0); glScalef(1.8, 0.15, 1); glutSolidSphere(0.07, 20, 20)
    elif state.expression == "sad":
        glTranslatef(0, -0.1 * state.body_scale, z_offset + 0.05); glColor3f(0,0,0); glLineWidth(3.0)
        glBegin(GL_LINE_STRIP)
        for a in range(0, 181, 10): glVertex2f(0.1 * math.cos(math.radians(a)), 0.08 * math.sin(math.radians(a)))
        glEnd()
    elif state.expression == "happy":
        glTranslatef(0, -0.12 * state.body_scale, z_offset + 0.05); glColor3f(0,0,0); glLineWidth(3.5)
        glBegin(GL_LINE_STRIP)
        for a in range(200, 341, 10): glVertex2f(0.14 * math.cos(math.radians(a)), 0.12 * math.sin(math.radians(a)))
        glEnd()
    else:
        # Aquí la boca crece dinámicamente con state.mouth_scale
        glTranslatef(0, -0.15 * state.body_scale, z_offset)
        glScalef(state.mouth_scale, state.mouth_scale, 1) # <--- Afecta la succión visualmente
        glColor3f(0.5, 0, 0); glutSolidSphere(0.07, 20, 20)
    glPopMatrix()

def draw_features():
    # Cejas y Lágrimas
    if state.expression == "angry":
        glColor3f(0,0,0); glLineWidth(4.0)
        for dx, s in [(-0.18, 1), (0.18, -1)]:
            glPushMatrix(); glTranslatef(dx * state.body_scale, 0.45 * state.body_scale, 0.75 * state.body_scale)
            glRotatef(-25 * s, 0, 0, 1); glBegin(GL_LINES); glVertex3f(-0.12, 0, 0); glVertex3f(0.12, 0, 0); glEnd(); glPopMatrix()
    elif state.expression == "sad":
        glColor3f(0.3, 0.6, 1.0)
        for dx in [-0.2, 0.2]:
            glPushMatrix(); glTranslatef(dx * state.body_scale, 0.05 * state.body_scale, 0.8 * state.body_scale)
            glScalef(0.6, 1.1, 0.6); glutSolidSphere(0.05, 15, 15); glPopMatrix()

def draw_weather():
    """Dibuja los pétalos de nieve."""
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    for wp in state.weather_particles:
        glPushMatrix()
        glTranslatef(wp['p'][0], wp['p'][1], wp['p'][2])
        # Rotación aleatoria para que parezcan pétalos cayendo
        glRotatef(state.breath_timer * 50, 1, 1, 0)

        glColor4f(0.9, 0.9, 1.0, 0.7) # Blanco azulado
        # Dibujamos un pequeño rombo/pétalo
        glBegin(GL_QUADS)
        glVertex3f(-0.05, 0, 0); glVertex3f(0, 0.05, 0)
        glVertex3f(0.05, 0, 0); glVertex3f(0, -0.05, 0)
        glEnd()
        glPopMatrix()

    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)

def draw_kirby_magician():
    draw_particles()
    glPushMatrix()
    if state.reaction_type == "shake":
        glTranslatef(math.sin(state.reaction_timer * 1.2) * 0.15, 0, 0)
    glRotatef(state.cabeza_y, 0, 1, 0)
    draw_body()
    draw_arms()
    draw_feet()
    draw_eyes()
    draw_cheeks()
    draw_mouth()
    draw_features()
    glPopMatrix()