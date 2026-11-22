from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
from Actions import state

# =================================================================
# UTILIDADES Y SISTEMAS DE PARTÍCULAS
# =================================================================

def get_current_color():
    """Calcula el color actual basado en el estado de parpadeo (flash)."""
    if state.color_flash_timer > 0:
        return (1.0, 1.0, 1.0)
    return state.dee_colors[state.current_color_idx]

def draw_particles():
    """Dibuja las partículas de efectos especiales (vórtices, impactos)."""
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

def draw_weather():
    """Dibuja las partículas de clima (nieve, pétalos) según el escenario."""
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    for wp in state.weather_particles:
        glPushMatrix()
        glTranslatef(wp['p'][0], wp['p'][1], wp['p'][2])
        glRotatef(state.breath_timer * 100 * wp['drift'], 1, 1, 0)
        glColor4f(wp['color'][0], wp['color'][1], wp['color'][2], 0.7)

        glBegin(GL_QUADS)
        s = wp['size']
        glVertex3f(-s, 0, 0); glVertex3f(0, s, 0)
        glVertex3f(s, 0, 0); glVertex3f(0, -s, 0)
        glEnd()
        glPopMatrix()

    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)

# =================================================================
# ANATOMÍA BASE DEL PERSONAJE
# =================================================================

def draw_body():
    """Cuerpo principal, incluye la esfera base y el parche de la cara."""
    glPushMatrix()
    r, g, b = get_current_color()
    glColor3f(r, g, b)
    glScalef(state.body_scale, state.body_scale, state.body_scale)

    # Esfera del cuerpo
    glutSolidSphere(0.8, 40, 40)

    # Parche de la cara (reacciona a expresiones)
    glDisable(GL_LIGHTING)
    if state.expression == "sad":
        glColor3f(0.85, 0.8, 0.7)
    elif state.expression == "angry":
        glColor3f(1.0, 0.75, 0.6)
    else:
        glColor3f(1.0, 0.9, 0.7)

    glPushMatrix()
    glTranslatef(0, -0.10, .15)
    glScalef(0.95, 0.75, 0.9)
    glutSolidSphere(0.78, 40, 40)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 0.050, .15)
    glScalef(0.9, 0.85, 0.9)
    glutSolidSphere(0.78, 40, 40)
    glPopMatrix()

    glEnable(GL_LIGHTING)
    glPopMatrix()

def draw_arms():
    """Dibuja ambos brazos con rotación dinámica según el estado."""
    r, g, b = get_current_color()
    glColor3f(r, g, b)
    for dx, side in [(-0.80, 1), (0.80, -1)]:
        glPushMatrix()
        glTranslatef(dx * state.body_scale, -0.1, 0)
        if state.is_floating:
            glRotatef(-30 * side, 0, 1, 0)
            glRotatef(60 * side, 0, 0, 1)
        else:
            glRotatef(state.arm_angle * side, 1, 0, 0)
            glRotatef(20 * side, 0, 0, 1)
        glutSolidSphere(0.28, 20, 20)
        glPopMatrix()

def draw_feet():
    """Dibuja los pies y cambia su color según el traje o estado."""
    if state.current_color_idx == 0:
        glColor3f(1.0, 0.7, 0.0)
    else:
        glColor3f(0.8, 0.3, 0.0)

    for dx, side in [(-0.5, 1), (0.5, -1)]:
        glPushMatrix()
        glTranslatef(dx * state.body_scale, -0.7 * state.body_scale, 0.1)
        if not state.is_floating:
            glRotatef(state.foot_angle * side, 1, 0, 0)
        else:
            glRotatef(10, 1, 0, 0)
        glScalef(1.5, 0.8, 1.8)
        glutSolidSphere(0.3, 20, 20)
        glPopMatrix()

# =================================================================
# RASGOS FACIALES Y EXPRESIONES
# =================================================================

def draw_eyes():
    """Dibuja los ojos: soporta estados normales, dormido y mareo (espirales)."""
    z_offset = 0.82 * state.body_scale
    for dx in [-0.22, 0.22]:
        glPushMatrix()
        glTranslatef(dx * state.body_scale, 0.22 * state.body_scale, z_offset)

        if state.expression == "dizzy":
            # Efecto de espiral mareada
            glDisable(GL_LIGHTING)
            glColor3f(0.1, 0.1, 0.1)
            glLineWidth(2.0)
            glBegin(GL_LINE_STRIP)
            for i in range(40):
                angle = 0.6 * i + (state.breath_timer * 12)
                radius = 0.0025 * i
                glVertex2f(math.cos(angle) * radius, math.sin(angle) * radius)
            glEnd()
            glEnable(GL_LIGHTING)
        else:
            # Ojos normales u ocluidos (parpadeo/sueño)
            glPushMatrix()
            glScalef(1.2, 2.8, 1)
            if not state.ojos_abiertos or state.is_sleeping:
                glColor3f(1.0, 0.9, 0.7)
            else:
                glColor3f(0.1, 0.1, 0.1)
            glutSolidSphere(0.06, 20, 20)
            glPopMatrix()

            # Brillo pupilar
            if state.ojos_abiertos and not state.is_sleeping:
                glPushMatrix()
                glTranslatef(0, 0.1, 0.04)
                glScalef(0.8, 1.2, 1)
                glColor3f(1, 1, 1)
                glutSolidSphere(0.035, 20, 20)
                glPopMatrix()
        glPopMatrix()

def draw_eyebrows():
    """Cejas que cambian de ángulo según el estado emocional."""
    z_offset = 0.85 * state.body_scale
    glColor3f(0.1, 0.1, 0.1)

    for dx, side in [(-0.25, 1), (0.25, -1)]:
        glPushMatrix()
        glTranslatef(dx * state.body_scale, 0.45 * state.body_scale, z_offset)

        if state.expression == "angry":
            glTranslatef(0, -0.05 * state.body_scale, 0)
            glRotatef(-35 * side, 0, 0, 1)
            glScalef(0.15, 0.04, 0.02)
        elif state.expression == "sad":
            glTranslatef(0, 0.05 * state.body_scale, 0)
            glRotatef(30 * side, 0, 0, 1)
            glScalef(0.18, 0.03, 0.02)
        elif state.expression == "happy":
            glRotatef(side * -10, 0, 1, 0)
            glScalef(0.15, 0.03, 0.02)
        else:
            glScalef(0.14, 0.03, 0.02)

        glutSolidCube(1.0)
        glPopMatrix()

def draw_cheeks():
    """Pequeño rubor en las mejillas."""
    if state.expression == "sad": return

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    if state.expression == "angry":
        glColor4f(1.0, 0.3, 0.3, 0.8)
    else:
        glColor4f(1.0, 0.5, 0.4, 0.7)

    z_offset = 0.85 * state.body_scale
    for dx in [-0.45, 0.45]:
        glPushMatrix()
        glTranslatef(dx * state.body_scale, 0.0, z_offset)
        glScalef(1.8, 1.0, 1.0)
        glutSolidSphere(0.06, 15, 15)
        glPopMatrix()
    glDisable(GL_BLEND)

def draw_mouth():
    """Boca polifacética: soporta felicidad, tristeza, enojo, mareo y succión."""
    z_offset = 0.85 * state.body_scale
    glPushMatrix()

    if state.expression == "dizzy":
        glColor3f(0.2, 0.15, 0.0)
        shake = math.sin(state.breath_timer * 25) * 0.015
        glTranslatef(shake, -0.25 * state.body_scale, z_offset)
        glScalef(1.6, 0.8, 1.0)
        glutSolidSphere(0.08, 20, 20)
        if int(state.breath_timer * 6) % 2 == 0:
            glDisable(GL_LIGHTING); glColor3f(0.4, 0.8, 0.2)
            glTranslatef(0, -0.12, 0.05); glutSolidSphere(0.025, 10, 10)
            glEnable(GL_LIGHTING)

    elif state.expression == "happy":
        glColor3f(0.4, 0.1, 0.1)
        glTranslatef(0, -0.22 * state.body_scale, z_offset)
        glRotatef(90, 1, 0, 0)
        glScalef(0.7, 0.7, 0.5)
        glutSolidCone(0.15, 0.2, 10, 2)

    elif state.expression == "sad":
        glColor3f(0.2, 0.2, 0.2)
        glTranslatef(0, -0.28 * state.body_scale, z_offset)
        glScalef(0.15, 0.03, 0.01)
        glutSolidCube(1.0)

    elif state.expression == "angry":
        glColor3f(0.1, 0.1, 0.1)
        glTranslatef(0, -0.25 * state.body_scale, z_offset)
        glRotatef(-90, 1, 0, 0)
        glScalef(0.7, 0.7, 0.5)
        glutSolidCone(0.1, 0.15, 8, 2)

    elif state.is_sucking:
        glColor3f(0.3, 0.1, 0.0)
        glTranslatef(0, -0.2 * state.body_scale, z_offset)
        glScalef(state.mouth_scale * 0.4, state.mouth_scale * 0.4, 1.0)
        glutSolidSphere(0.08, 20, 20)

    glPopMatrix()

# =================================================================
# EFECTOS ESPECIALES Y MECÁNICAS
# =================================================================

def draw_suction_vortex():
    """Efecto visual de succión (partículas y líneas de velocidad)."""
    if not state.is_sucking: return

    glPushMatrix()
    z_offset_base = (0.85 + (state.mouth_scale * 0.1)) * state.body_scale
    glTranslatef(0, -0.2 * state.body_scale, z_offset_base)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDisable(GL_LIGHTING)

    # Cono de partículas espirales
    glColor4f(0.9, 0.95, 1.0, 0.25)
    num_particles = 15
    for i in range(num_particles):
        angle = (state.breath_timer * -200) + (i * (360.0 / num_particles))
        rad = math.radians(angle)
        distance = ((state.breath_timer * 1.5) + (i * 0.1)) % 1.2
        distance = 1.2 - distance
        cone_radius = distance * 0.6

        glPushMatrix()
        glTranslatef(math.cos(rad) * cone_radius, math.sin(rad) * cone_radius, distance)
        glRotatef(angle * 2, 1, 1, 0)
        p_scale = 0.04 * (1.0 - (distance / 1.2))
        glScalef(p_scale, p_scale, p_scale)
        glutSolidOctahedron()
        glPopMatrix()

    # Líneas de velocidad
    glBegin(GL_LINES)
    glColor4f(1.0, 1.0, 1.0, 0.15)
    for i in range(20):
        angle = (state.breath_timer * -150) + (i * (360.0 / 20))
        rad = math.radians(angle)
        start_dist = (i * 0.05) % 1.0
        start_dist = 1.0 - start_dist
        end_dist = start_dist + 0.1
        glVertex3f(math.cos(rad) * start_dist * 0.6, math.sin(rad) * start_dist * 0.6, start_dist)
        glVertex3f(math.cos(rad) * end_dist * 0.6, math.sin(rad) * end_dist * 0.6, end_dist)
    glEnd()

    glEnable(GL_LIGHTING)
    glDisable(GL_BLEND)
    glPopMatrix()

def draw_sleep_bubble():
    """Burbuja de sueño animada que crece con la respiración."""
    if not state.is_sleeping: return

    bubble_size = (math.sin(state.breath_timer * 2) + 1.1) * 0.15
    glPushMatrix()
    glTranslatef(0.15, -0.05 * state.body_scale, 0.85 * state.body_scale)
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA); glDisable(GL_LIGHTING)

    glColor4f(0.7, 0.9, 1.0, 0.5)
    glutSolidSphere(bubble_size, 15, 15)

    glColor4f(1.0, 1.0, 1.0, 0.7)
    glTranslatef(bubble_size*0.3, bubble_size*0.3, bubble_size*0.3)
    glutSolidSphere(bubble_size * 0.3, 10, 10)

    glEnable(GL_LIGHTING); glDisable(GL_BLEND)
    glPopMatrix()

# =================================================================
# ACCESORIOS Y EQUIPAMIENTO (TRAJES)
# =================================================================

def draw_equipment():
    """Bandana y Lanza para el estado Bandana Dee."""
    if state.bandana_active:
        scale = 0.8 * state.body_scale
        glPushMatrix()
        glTranslatef(0, .85 * scale, 0)
        glColor3f(0.1, 0.1, 1.0)
        glPushMatrix(); glScalef(1.0, 0.25, 1.05); glutSolidCube(1.2); glPopMatrix()
        glColor3f(0.05, 0.05, 0.8)
        for dx, dy, dz in [(-0.25, 0, -0.72), (0.25, 0, -0.72)]:
            glPushMatrix(); glTranslatef(dx, dy, dz); glutSolidCube(0.2); glPopMatrix()
        glPopMatrix()

    if state.spear_active:
        glPushMatrix()
        glTranslatef(0.95 * state.body_scale, -0.05 * state.body_scale, 0.1)
        glRotatef(-30, 0, 0, 1)
        glColor3f(0.5, 0.3, 0.1)
        glPushMatrix(); glScalef(0.06, 2.5, 0.06); glutSolidCube(1.0); glPopMatrix()
        glColor3f(0.8, 0.8, 0.85)
        glPushMatrix(); glTranslatef(0, 1.25, 0); glRotatef(-90, 1, 0, 0); glutSolidCone(0.2, 0.6, 12, 4); glPopMatrix()
        glPopMatrix()

def draw_parasol():
    """Sombrilla icónica roja y blanca."""
    if not state.parasol_active: return

    glPushMatrix()
    glTranslatef(-0.8 * state.body_scale, 0.2 * state.body_scale, 0.2)
    glRotatef(15, 0, 0, 1)

    # Mango
    glColor3f(0.1, 0.4, 0.9); glPushMatrix(); glTranslatef(0, -0.2, 0); glutSolidSphere(0.12, 10, 10); glPopMatrix()
    glColor3f(0.8, 0.7, 0.5); glPushMatrix(); glScalef(0.05, 1.8, 0.05); glutSolidCube(1.0); glPopMatrix()

    # Tela
    glPushMatrix()
    glTranslatef(0, 0.5, 0); glRotatef(270, 1, 0, 0)
    for i in range(8):
        glRotatef(45, 0, 0, 1)
        if i % 2 == 0: glColor3f(1.0, 0.1, 0.1)
        else: glColor3f(0.95, 0.95, 0.95)
        glutSolidCone(0.9, 0.4, 10, 2)
    glPopMatrix()

    # Estrella superior
    glColor3f(1.0, 0.9, 0.0); glPushMatrix(); glTranslatef(0, 1.0, 0); glScalef(0.2, 0.2, 0.1)
    glutSolidSphere(0.6, 10, 10); glRotatef(45, 0, 0, 1); glutSolidCube(1.0); glPopMatrix()
    glPopMatrix()

def draw_sleeping_cap():
    """Gorro de dormir azul con pompón."""
    if not state.is_sleeping: return
    glPushMatrix()
    glTranslatef(0, 0.65 * state.body_scale, -0.1)
    glRotatef(-20, 1, 0, 0); glRotatef(15, 0, 0, 1)
    glColor3f(0.5, 0.7, 1.0); glPushMatrix(); glRotatef(-80, 1, 0, 0); glutSolidCone(0.6, 1.2, 16, 8); glPopMatrix()
    glColor3f(1.0, 1.0, 1.0); glPushMatrix(); glTranslatef(0, 1.3, .15); glutSolidSphere(0.20, 12, 12); glPopMatrix()
    if int(state.breath_timer * 2) % 2 == 0:
        glDisable(GL_LIGHTING); glColor3f(1, 1, 1)
        glPushMatrix(); glTranslatef(0.5, 0.8, 0.2); glScalef(0.2, 0.2, 0.1); glutSolidCube(1.0); glPopMatrix()
        glEnable(GL_LIGHTING)
    glPopMatrix()

def draw_jester_hat():
    """Sombrilla de bufón con cuernos de colores."""
    if not state.is_jester_hat_active: return
    scale = 1.0 * state.body_scale
    glPushMatrix()
    glTranslatef(0, 0.75 * scale, 0.05 * scale); glRotatef(-10, 1, 0, 0)
    for dx, color in [(0.35, (1.0, 0.2, 0.2)), (-.35, (0.2, 0.2, 1.0))]:
        glPushMatrix()
        glTranslatef(dx * scale, 0.001 * scale, 0)
        glRotatef(-35 if dx > 0 else 35, 0, 0, 1)
        glRotatef(math.sin(state.breath_timer * 3) * 5, 1, 0, 0)
        glColor3f(*color)
        glPushMatrix(); glRotatef(-90, 1, 0, 0); glutSolidCone(0.3 * scale, 1.0 * scale, 12, 6); glPopMatrix()
        glColor3f(1.0, 0.9, 0.0); glPushMatrix(); glTranslatef(0, 1.0 * scale, 0); glutSolidSphere(0.08 * scale, 10, 10); glPopMatrix()
        glPopMatrix()
    glPopMatrix()

def draw_chef_hat():
    """Sombrero de chef blanco."""
    if not state.is_chef_hat_active: return
    scale = 1.0 * state.body_scale
    glPushMatrix()
    glTranslatef(0, 0.8 * scale, 0)
    glColor3f(1.0, 1.0, 1.0)
    glPushMatrix(); glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 0.4 * scale, 0.4 * scale, 0.4 * scale, 16, 1); glPopMatrix()
    glPushMatrix(); glTranslatef(0, 0.5 * scale, 0); glScalef(1.3, 0.8, 1.3); glutSolidSphere(0.45 * scale, 20, 20); glPopMatrix()
    glDisable(GL_LIGHTING); glColor3f(0.8, 0.8, 0.8)
    glPushMatrix(); glTranslatef(0, 0.05 * scale, 0); glRotatef(-90, 1, 0, 0); gluDisk(gluNewQuadric(), 0.405 * scale, 0.41 * scale, 16, 1); glPopMatrix()
    glEnable(GL_LIGHTING)
    glPopMatrix()

def draw_chef_tools():
    """Herramientas de cocina (espátula y sartén)."""
    if not state.is_chef_hat_active: return

    # Espátula
    glPushMatrix()
    glTranslatef(-0.85 * state.body_scale, 0.1, 0.45); glRotatef(45, 1, 0, 0)
    glColor3f(0.5, 0.3, 0.1); glPushMatrix(); glScalef(0.04, 0.4, 0.04); glutSolidCube(1.5); glPopMatrix()
    glColor3f(0.7, 0.7, 0.7); glPushMatrix(); glTranslatef(0, 0.35, 0); glScalef(0.15, 0.2, 0.02); glutSolidCube(1.5); glPopMatrix()
    glPopMatrix()

    # Sartén
    glPushMatrix()
    glTranslatef(0.85 * state.body_scale, -0.1, .8); glRotatef(-20, 0, 1, 0)
    glColor3f(0.1, 0.1, 0.1); glPushMatrix(); glTranslatef(-.1, 0,-.6); glScalef(0.05, 0.02, 0.4); glutSolidCube(1.5); glPopMatrix()
    glPushMatrix(); glRotatef(90, 1, 0, 0); q = gluNewQuadric(); gluDisk(q, 0, 0.3, 20, 1); gluCylinder(q, 0.3, 0.32, 0.1, 20, 1); glPopMatrix()
    glPopMatrix()

# =================================================================
# FUNCIÓN RENDERIZADO PRINCIPAL
# =================================================================

def draw_dee_magician():
    """Ensamblado final de Dee con todos sus componentes y estados."""
    draw_particles()

    glPushMatrix()
    if state.reaction_type == "shake":
        glTranslatef(math.sin(state.reaction_timer * 1.2) * 0.15, 0, 0)
    glRotatef(state.cabeza_y, 0, 1, 0)

    # Orden de dibujado de capas
    draw_body()
    draw_eyebrows()
    draw_arms()
    draw_feet()
    draw_eyes()
    draw_cheeks()
    draw_suction_vortex()
    draw_mouth()
    draw_sleep_bubble()

    # Equipamiento y transformaciones
    draw_equipment()
    draw_parasol()
    draw_sleeping_cap()
    draw_jester_hat()
    draw_chef_hat()
    draw_chef_tools()

    glPopMatrix()