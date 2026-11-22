from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
from Actions import state

# =========================
# ESCENARIOS (7 COMPLETOS)
# =========================
def draw_environment():

    if state.current_scene == 1:
        glClearColor(1,0.85,0.9,1)
        draw_floor(1,0.9,0.9)

        for x,z in [(-6,-6),(6,-6),(-6,6),(6,6)]:
            draw_sakura(x,z)

        for x in [-4,0,4]:
            draw_house(x,-8)

        draw_ramen(3,0)
        draw_katana(-3,0)
        draw_sun()

    elif state.current_scene == 2:

        glClearColor(0.9,0.9,0.9,1)

        # piso
        glPushMatrix()
        glTranslatef(0,-1,0)
        glColor3f(0.6,0.4,0.2)
        glScalef(50,0.2,50)
        glutSolidCube(1)
        glPopMatrix()

        # pizarrón
        glPushMatrix()
        glTranslatef(0,3,-10)
        glColor3f(0.1,0.4,0.1)
        glScalef(10,4,0.2)
        glutSolidCube(1)
        glPopMatrix()

        # escritorios
        desks=[(-4,-4),(4,-4),(-4,0),(4,0)]

        for d in desks:

            glPushMatrix()
            glTranslatef(d[0],-0.5,d[1])
            glColor3f(0.5,0.3,0.2)
            glScalef(3,0.4,2)
            glutSolidCube(1)
            glPopMatrix()

        # libreta
        glPushMatrix()
        glTranslatef(0,1.05,0)
        glColor3f(0.2,0.4,0.9)
        glScalef(1.2,0.05,0.8)
        glutSolidCube(1)
        glPopMatrix()

        # manzana
        glPushMatrix()
        glTranslatef(0.8,1.2,0)
        glColor3f(1,0,0)
        glutSolidSphere(0.15,20,20)

        # tallo
        glColor3f(0.3,0.2,0)
        glTranslatef(0,0.15,0)
        glutSolidCube(0.05)
        glPopMatrix()

        for i in range(3):
            glPushMatrix()
            glTranslatef(-3+i,0,-2)
            glColor3f(0.6,0.2,0.2)
            glScalef(0.6,0.2,0.9)
            glutSolidCube(1)
            glPopMatrix()
        glEnable(GL_LIGHTING)
    elif state.current_scene == 3:

        glClearColor(0.2,0.2,0.2,1)

        # escenario
        glPushMatrix()
        glTranslatef(0,-1,0)
        glColor3f(0.6,0.1,0.1)
        glScalef(12,0.5,12)
        glutSolidCube(1)
        glPopMatrix()

        # cortinas
        for x in [-5,5]:

            glPushMatrix()
            glTranslatef(x,2,-6)
            glColor3f(0.8,0,0)
            glScalef(1,5,0.2)
            glutSolidCube(1)
            glPopMatrix()

        # luces
        lights=[-4,-2,0,2,4]

        for l in lights:

            glPushMatrix()
            glTranslatef(l,4,-4)
            glColor3f(1,1,0)
            glutSolidSphere(0.3,20,20)
            glPopMatrix()

    elif state.current_scene == 4:

        glClearColor(0.4,0.1,0.1,1)

        # suelo de arena
        glColor3f(0.35,0.15,0.15)

        glBegin(GL_QUADS)
        glVertex3f(-60,-1,-60)
        glVertex3f(60,-1,-60)
        glVertex3f(60,-1,60)
        glVertex3f(-60,-1,60)
        glEnd()

        # ---------------- COLUMNAS ----------------

        columnas = [
            (-12,-12),(12,-12),(-12,12),(12,12),
            (-20,0),(20,0),(0,-20),(0,20)
        ]

        for c in columnas:

            glPushMatrix()

            glTranslatef(c[0],-1,c[1])
            glRotatef(-90,1,0,0)

            glColor3f(0.6,0.6,0.6)

            quad = gluNewQuadric()
            gluCylinder(quad,0.7,0.7,7,20,20)

            glPopMatrix()

        # ---------------- ROCAS ----------------

        rocas=[(-5,-3),(4,-6),(6,5),(-7,4)]

        for r in rocas:

            glPushMatrix()

            glTranslatef(r[0],-0.8,r[1])
            glColor3f(0.3,0.3,0.3)

            glutSolidSphere(1,20,20)

            glPopMatrix()

        # ---------------- ESPADAS ----------------

        espadas=[(-2,4),(3,2),(-4,-2)]

        for e in espadas:

            glPushMatrix()

            glTranslatef(e[0],-0.8,e[1])

            # hoja
            glPushMatrix()
            glRotatef(-90,1,0,0)
            glColor3f(0.8,0.8,0.8)

            quad = gluNewQuadric()
            gluCylinder(quad,0.05,0.05,2,10,10)

            glPopMatrix()

            # mango
            glPushMatrix()
            glTranslatef(0,0.2,0)
            glColor3f(0.4,0.2,0.1)
            glutSolidCube(0.2)
            glPopMatrix()

            glPopMatrix()

        # ---------------- ESCUDOS ----------------

        escudos=[(-6,0),(6,3),(-3,-5)]

        for s in escudos:

            glPushMatrix()

            glTranslatef(s[0],0,s[1])
            glColor3f(0.6,0.2,0.2)

            glutSolidTorus(0.2,0.8,20,20)

            glPopMatrix()

        # ---------------- ANTORCHAS ----------------

        antorchas=[(-15,-15),(15,-15),(-15,15),(15,15)]

        for a in antorchas:

            glPushMatrix()

            glTranslatef(a[0],-1,a[1])

            # palo
            glPushMatrix()
            glRotatef(-90,1,0,0)
            glColor3f(0.4,0.2,0.1)

            quad = gluNewQuadric()
            gluCylinder(quad,0.1,0.1,3,10,10)

            glPopMatrix()

            # fuego
            glPushMatrix()
            glTranslatef(0,3,0)
            glColor3f(1,0.5,0)

            glutSolidSphere(0.4,20,20)

            glPopMatrix()

            glPopMatrix()


    elif state.current_scene == 5:
        glClearColor(0.6,1,0.6,1)
        draw_floor(0.4,0.8,0.4)

        for i in range(-10,10,2):
            draw_tree(i,3)
            draw_tree(i,-3)

        draw_house(0,-6)
        draw_ramen(3,0)
        draw_sun()

    elif state.current_scene == 6:
        glClearColor(0.5,0.7,1,1)
        draw_floor(0.6,0.6,0.6)

        for i in range(-10,10,2):
            draw_building(i,-10)

        draw_sun()

    elif state.current_scene == 7:
        glClearColor(1,1,0.9,1)
        draw_floor(1,1,0.7)

        rocas=[(-5,-3),(4,-6),(6,5),(-7,4)]

        for r in rocas:

            glPushMatrix()

            glTranslatef(r[0],-0.8,r[1])
            glColor3f(0.3,0.3,0.3)

            glutSolidSphere(1,20,20)

            glPopMatrix()

        trees=[(-8,-8),(-5,-6),(6,-7),(8,3),(-7,4),(10,-3),(-10,5)]

        for t in trees:
            draw_tree(t[0],t[1])

        # flores
        flowers=[(-2,-3),(2,-3),(4,2),(-4,1),(3,5),(-3,6)]

        for f in flowers:
            draw_flower(f[0],f[1])

        draw_garu()

        draw_house(-3,-6)
        draw_house(3,-6)

        draw_sun()
# =========================
# PISO
# =========================
def draw_floor(r,g,b):

    glColor3f(1,0.9,0.95)

    glBegin(GL_QUADS)

    glVertex3f(-50,-1,-50)

    glVertex3f(50,-1,-50)

    glVertex3f(50,-1,50)

    glVertex3f(-50,-1,50)

    glEnd()
def draw_lamp(x,z):

    glPushMatrix()
    glTranslatef(x,-1,z)
    glRotatef(-90,1,0,0)

    glColor3f(0.3,0.3,0.3)
    quad=gluNewQuadric()
    gluCylinder(quad,0.1,0.1,4,20,20)

    glPopMatrix()

    glPushMatrix()
    glTranslatef(x,3,z)
    glColor3f(1,1,0.6)
    glutSolidSphere(0.3,20,20)
    glPopMatrix()


def draw_flower(x,z):


    glPushMatrix()
    glTranslatef(x,-0.9,z)

    # tallo
    glColor3f(0,0.7,0)
    glRotatef(-90,1,0,0)

    quad=gluNewQuadric()
    gluCylinder(quad,0.03,0.03,0.5,10,10)

    glRotatef(90,1,0,0)

    # flor
    glTranslatef(0,0.5,0)
    glColor3f(1,0,0)
    glutSolidSphere(0.15,10,10)

    glPopMatrix()

# =========================
# OBJETOS
# =========================
def draw_sakura(x,z):
    glPushMatrix()
    glTranslatef(x,0,z)

    # TRONCO (VERTICAL CORRECTO)
    glPushMatrix()
    glRotatef(-90,1,0,0)
    glColor3f(0.5,0.2,0.1)
    glutSolidCylinder(0.2,2,15,15)
    glPopMatrix()

    # COPA
    glTranslatef(0,2,0)
    glColor3f(1,0.6,0.8)
    glutSolidSphere(1,20,20)

    glPopMatrix()


def draw_sun():
    glPushMatrix()
    glTranslatef(8,8,-10)
    glColor3f(1,1,0)
    glutSolidSphere(1,20,20)
    glPopMatrix()

def draw_building(x,z):
    glPushMatrix()
    glTranslatef(x,0,z)

    height = abs((x % 5) + 2)

    glColor3f(0.3,0.3,0.35)
    glScalef(1,height,1)
    glutSolidCube(1)

    glPopMatrix()

def draw_tree(x,z):
    glPushMatrix()
    glTranslatef(x,0,z)

    # TRONCO (VERTICAL)
    glPushMatrix()
    glRotatef(-90,1,0,0)
    glColor3f(0.4,0.2,0.1)
    glutSolidCylinder(0.3,2,15,15)
    glPopMatrix()

    # COPA
    glTranslatef(0,2,0)
    glColor3f(0,0.6,0)
    glutSolidSphere(1,20,20)

    glPopMatrix()

def draw_house(x,z):
    glPushMatrix()
    glTranslatef(x,0,z)
    glColor3f(0.6,0.3,0.2)
    glutSolidCube(3)
    glPopMatrix()

def draw_torii(x,z):
    glPushMatrix()
    glTranslatef(x,1,z)
    glColor3f(1,0,0)
    glScalef(5,0.5,1)
    glutSolidCube(1)
    glPopMatrix()

def draw_katana(x,z):
    glPushMatrix()
    glTranslatef(x,0,z)
    glColor3f(0.8,0.8,0.8)
    glutSolidCylinder(0.05,2,10,10)
    glPopMatrix()

def draw_ramen(x,z):
    glPushMatrix()
    glTranslatef(x,0,z)
    glColor3f(1,1,0)
    glutSolidSphere(0.5,20,20)
    glPopMatrix()

def draw_heart(x,z):
    glPushMatrix()
    glTranslatef(x,1,z)
    glColor3f(1,0,0)
    glutSolidSphere(0.3,20,20)
    glPopMatrix()

def draw_lantern(x,z):
    glPushMatrix()
    glTranslatef(x,1,z)
    glColor3f(1,0.5,0)
    glutSolidSphere(0.3,20,20)
    glPopMatrix()

# =========================
# GARU
# =========================
def draw_garu():
    glPushMatrix()
    glTranslatef(3,0,3)

    # cuerpo negro
    glPushMatrix()
    glTranslatef(0,-0.5,0)
    glColor3f(0,0,0)
    glutSolidSphere(0.5,30,30)
    glPopMatrix()

    # cabeza
    glTranslatef(0,0.8,0)
    glColor3f(1,0.8,0.7)
    glutSolidSphere(0.5,30,30)

    # cabello negro
    glPushMatrix()
    glTranslatef(0,0.2,0)
    glColor3f(0,0,0)
    glutSolidSphere(0.5,30,30)
    glPopMatrix()

    # ojos rasgados
    glDisable(GL_LIGHTING)
    glColor3f(0,0,0)

    glBegin(GL_LINES)
    glVertex3f(-0.2,0.1,0.55)
    glVertex3f(-0.05,0.15,0.55)

    glVertex3f(0.05,0.15,0.55)
    glVertex3f(0.2,0.1,0.55)
    glEnd()

    glEnable(GL_LIGHTING)

    glPopMatrix()
# =========================
# PUCCA
# =========================
def draw_head():
    glPushMatrix()
    glRotatef(state.cabeza_y, 0, 1, 0)

    # =========================
    # CABEZA
    # =========================
    glColor3f(1,0.8,0.7)
    glutSolidSphere(0.6,40,40)

    # =========================
    # CABELLO (ATRÁS)
    # =========================
    glPushMatrix()
    glTranslatef(0,0.15,-0.15)
    glColor3f(0,0,0)
    glScalef(1.1,0.8,1.1)
    glutSolidSphere(0.6,30,30)
    glPopMatrix()

    # =========================
    # MOÑOS
    # =========================
    for dx in [-0.7,0.7]:
        glPushMatrix()
        glTranslatef(dx,0.25,0)

        glColor3f(0,0,0)
        glutSolidSphere(0.25,20,20)

        glColor3f(1,0,0)
        glutSolidTorus(0.05,0.15,10,20)

        glPopMatrix()

    # =========================
    # CARA (EMOCIONES)
    # =========================
    glDisable(GL_LIGHTING)

    z = 0.63

    # ===== OJOS =====
    for dx in [-0.22, 0.22]:

        glPushMatrix()
        glTranslatef(dx, 0.05, z)
        glColor3f(0,0,0)

        # NORMAL
        if state.expression == "neutral":
            glutSolidSphere(0.05, 20, 20)

        # FELIZ
        elif state.expression == "happy":
            glBegin(GL_LINES)
            glVertex3f(-0.05,0,0)
            glVertex3f(0,0.05,0)
            glVertex3f(0,0.05,0)
            glVertex3f(0.05,0,0)
            glEnd()

        # TRISTE
        elif state.expression == "sad":
            glBegin(GL_LINES)
            glVertex3f(-0.05,0.05,0)
            glVertex3f(0,0,0)
            glVertex3f(0,0,0)
            glVertex3f(0.05,0.05,0)
            glEnd()

        # ENOJADO
        elif state.expression == "angry":
            glBegin(GL_LINES)
            glVertex3f(-0.05,0.05,0)
            glVertex3f(0.05,0,0)
            glEnd()

        # SORPRESA
        elif state.expression == "surprised":
            glutSolidSphere(0.07, 20, 20)

        # GUIÑO
        elif state.expression == "wink" and dx < 0:
            glBegin(GL_LINES)
            glVertex3f(-0.05,0,0)
            glVertex3f(0.05,0,0)
            glEnd()

        else:
            glutSolidSphere(0.05, 20, 20)

        glPopMatrix()

    # ===== BOCA =====
    glPushMatrix()
    glTranslatef(0, -0.2, z)

    # FELIZ
    if state.expression == "happy":
        glBegin(GL_LINE_STRIP)
        glVertex3f(-0.12,0,0)
        glVertex3f(0,-0.05,0)
        glVertex3f(0.12,0,0)
        glEnd()

    # TRISTE
    elif state.expression == "sad":
        glBegin(GL_LINE_STRIP)
        glVertex3f(-0.12,-0.05,0)
        glVertex3f(0,0,0)
        glVertex3f(0.12,-0.05,0)
        glEnd()

    # ENOJADO
    elif state.expression == "angry":
        glBegin(GL_LINES)
        glVertex3f(-0.12,0,0)
        glVertex3f(0.12,0,0)
        glEnd()

    # SORPRESA
    elif state.expression == "surprised":
        glutSolidSphere(0.06,20,20)

    # AMOR
    elif state.expression == "love":
        glutSolidSphere(0.05,20,20)

    # PENSANDO
    elif state.expression == "thinking":
        glBegin(GL_LINES)
        glVertex3f(-0.05,0,0)
        glVertex3f(0.05,0,0)
        glEnd()

    # DEFAULT
    else:
        glBegin(GL_LINES)
        glVertex3f(-0.1,0,0)
        glVertex3f(0.1,0,0)
        glEnd()

    glPopMatrix()

    glEnable(GL_LIGHTING)

    glPopMatrix()
def draw_body():
    glPushMatrix()
    glTranslatef(0,-0.5,0)
    glScalef(0.9,1,0.9)
    glColor3f(1,0,0)
    glutSolidSphere(0.5,30,30)
    glPopMatrix()

def draw_legs():

    for dx in [-0.2,0.2]:

        glPushMatrix()


        if state.is_walking:
            angle = math.sin(state.animation_angle * 10) * 30

            if dx < 0:
                glRotatef(angle,1,0,0)
            else:
                glRotatef(-angle,1,0,0)

        glTranslatef(dx,-1,0)

        glColor3f(0,0,0)
        glutSolidCylinder(0.1,0.5,10,10)

        glTranslatef(0,0.5,0)
        glutSolidSphere(0.15,20,20)

        glPopMatrix()

def draw_arms():

    for dx in [-0.45, 0.45]:

        glPushMatrix()

        glTranslatef(dx, -0.3, 0.2)

        glRotatef(-30, 1, 0, 0)

        # animación de saludo (solo brazo derecho)
        if state.reaction_type == "wave" and dx > 0:
            glRotatef(math.sin(state.animation_angle*6)*60, 1, 0, 0)


        if dx < 0:
            glRotatef(90, 0, 0, 1)
        else:
            glRotatef(-90, 0, 0, 1)

        # =====================
        # MANGA (roja)
        # =====================
        glColor3f(1,0,0)
        glutSolidCylinder(0.12, 0.5, 15, 15)

        # =====================
        # MANO
        # =====================
        glTranslatef(0, 0, 0.5)
        glColor3f(1,0.8,0.7)
        glutSolidSphere(0.12, 20, 20)

        glPopMatrix()

# =========================
# ANIMACION
# =========================
def draw_pucca():

    glPushMatrix()

    # ===== ANIMACIONES =====
    if state.reaction_type == "jump":
        glTranslatef(0, abs(math.sin(state.animation_angle))*1.5, 0)

    elif state.reaction_type == "spin":
        glRotatef(state.animation_angle * 10, 0,1,0)

    elif state.reaction_type == "shake":
        glTranslatef(math.sin(state.animation_angle*10)*0.2,0,0)

    elif state.reaction_type == "crouch":
        glTranslatef(0,-0.5,0)

    elif state.reaction_type == "shake":
        # Movimiento rápido de izquierda a derecha
        glTranslatef(math.sin(state.animation_angle * 20) * 0.3, 0, 0)

    # ===== DIBUJO =====
    draw_head()
    draw_body()
    draw_arms()
    draw_legs()

    glPopMatrix()