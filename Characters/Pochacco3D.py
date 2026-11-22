from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
from Actions import state

COL_WHITE = [1.0, 1.0, 1.0]
COL_BLACK = [0.05, 0.05, 0.05]
COL_YELLOW = [1.0, 0.8, 0.3]
COL_BROWN = [0.4, 0.2, 0.1]
COL_PINK = [1.0, 0.7, 0.8]
COL_WING = [0.9, 0.9, 1.0, 0.6]

def draw_tree(x,z):

    # tronco
    glPushMatrix()
    glTranslatef(x,-1,z)
    glRotatef(-90,1,0,0)
    glColor3f(0.4,0.2,0.1)

    quad=gluNewQuadric()
    gluCylinder(quad,0.3,0.3,3,20,20)
    glPopMatrix()

    # hojas
    glPushMatrix()
    glTranslatef(x,2,z)
    glColor3f(0.1,0.6,0.1)
    glutSolidSphere(1.5,20,20)
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


def draw_sun():

    glPushMatrix()
    glTranslatef(15,15,-20)
    glColor3f(1,1,0)
    glutSolidSphere(2,30,30)
    glPopMatrix()


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


def draw_building(x,z):

    glPushMatrix()
    glTranslatef(x,2,z)
    glColor3f(0.5,0.5,0.5)
    glScalef(4,6,4)
    glutSolidCube(1)
    glPopMatrix()


def draw_column(x,z):

    glPushMatrix()
    glTranslatef(x,-1,z)
    glRotatef(-90,1,0,0)

    glColor3f(0.6,0.6,0.6)
    quad=gluNewQuadric()
    gluCylinder(quad,0.7,0.7,6,20,20)

    glPopMatrix()


# ---------- ESCENARIOS ----------

def draw_environment():

    glDisable(GL_LIGHTING)

    # ===== ESCENARIO 1 PARQUE =====
    if state.current_scene == 1:

        glClearColor(0.5,0.8,1.0,1)

        # suelo
        glColor3f(0.2,0.7,0.2)

        glBegin(GL_QUADS)
        glVertex3f(-50,-1,-50)
        glVertex3f(50,-1,-50)
        glVertex3f(50,-1,50)
        glVertex3f(-50,-1,50)
        glEnd()

        draw_sun()

        # árboles
        trees=[(-8,-8),(-5,-6),(6,-7),(8,3),(-7,4),(10,-3),(-10,5)]

        for t in trees:
            draw_tree(t[0],t[1])

        # flores
        flowers=[(-2,-3),(2,-3),(4,2),(-4,1),(3,5),(-3,6)]

        for f in flowers:
            draw_flower(f[0],f[1])

        # colmena
        glPushMatrix()
        glTranslatef(-5,2,-6)
        glColor3f(0.9,0.7,0.2)
        glutSolidSphere(0.4,20,20)
        glPopMatrix()


    # ===== ESCENARIO 2 CALLE =====
    elif state.current_scene == 2:

        glClearColor(0.6,0.6,0.7,1)

        glColor3f(0.2,0.2,0.2)

        glBegin(GL_QUADS)
        glVertex3f(-50,-1,-50)
        glVertex3f(50,-1,-50)
        glVertex3f(50,-1,50)
        glVertex3f(-50,-1,50)
        glEnd()

        lamps=[(-6,-6),(6,-6),(-6,6),(6,6)]

        for l in lamps:
            draw_lamp(l[0],l[1])

        buildings=[(-10,-10),(10,-10),(-10,10),(10,10)]

        for b in buildings:
            draw_building(b[0],b[1])


    # ===== ESCENARIO 3 TEATRO =====
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


    # ===== ESCENARIO 4 ARENA =====
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


    # ===== ESCENARIO 5 AULA =====
    elif state.current_scene == 5:

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

def draw_head():
    glPushMatrix()
    glTranslatef(0, 0.5, 0)
    glRotatef(state.cabeza_y, 0, 1, 0)
    glColor3fv(COL_WHITE)
    glutSolidSphere(0.75, 40, 40)
    for dx in [-0.4, 0.4]:
        glPushMatrix()
        glTranslatef(dx, -0.1, 0.6)
        glColor3fv(COL_PINK)
        glScalef(1.0, 0.6, 0.2)
        glutSolidSphere(0.15, 20, 20)
        glPopMatrix()

    draw_eyebrows()
    glPopMatrix()


def draw_ears():

    ear_lift = 0

    if state.reaction_type == "ears_up":
        ear_lift = math.sin(state.reaction_timer*4)*25

    for dx in [-0.7,0.7]:

        glPushMatrix()

        glTranslatef(dx,0.9,0)

        if dx < 0:
            glRotatef(20+ear_lift,0,0,1)
        else:
            glRotatef(-20-ear_lift,0,0,1)

        glColor3fv(COL_BLACK)

        glScalef(0.4,0.15,0.2)

        glutSolidSphere(0.8,20,20)

        glPopMatrix()

def draw_face_details():
    blink = math.sin(state.blink_timer) > 0.95
    for dx in [-0.3, 0.3]:
        glPushMatrix()
        glTranslatef(dx, 0.55, 0.68)
        glColor3fv(COL_BLACK)
        # Expresiones
        if state.expression == "wink" and dx < 0: glScalef(1.0, 0.1, 1.0)
        elif state.expression == "happy": glRotatef(180, 1, 0, 0)
        elif state.expression == "sad": glTranslatef(0, -0.1, 0)
        elif state.expression == "angry" and dx > 0: glRotatef(45, 0, 0, 1)
        elif blink: glScalef(1.0, 0.1, 1.0)

        scale_y = 1.6 if state.expression == "surprised" else 1.1
        glScalef(1.0, scale_y, 1.0)
        glutSolidSphere(0.1, 25, 25)
        glPopMatrix()
    # Nariz
    glPushMatrix(); glTranslatef(0, 0.45, 0.75); glColor3fv(COL_BLACK); glutSolidSphere(0.04, 20, 20); glPopMatrix()

def draw_bee_body():
    glPushMatrix()
    glTranslatef(0, -0.2, 0)
    glRotatef(90, 1, 0, 0)
    colors = [COL_YELLOW, COL_BROWN, COL_YELLOW]
    offsets = [0, 0.3, 0.6]
    scales = [0.6, 0.58, 0.55]
    for i in range(3):
        glPushMatrix()
        glTranslatef(0, 0, offsets[i])
        glColor3fv(colors[i])
        glScalef(1.1 - (i*0.1), 1.0, 0.4)
        glutSolidSphere(scales[i], 30, 30)
        glPopMatrix()
    glPopMatrix()

def draw_arms():
    swing = math.sin(state.animation_angle) * 20
    for dx in [-1, 1]:
        glPushMatrix()
        glTranslatef(0.4 * dx, -0.1, 0.2)
        if state.is_walking: glRotatef(swing * dx, 1, 0, 0)
        if state.expression == "happy": glRotatef(-60, 0, 0, 1 if dx > 0 else -1)
        if state.is_greeting and dx > 0:
            glRotatef(math.sin(state.animation_angle * 8) * 50 - 90, 1, 0, 0)
        glRotatef(70 * dx, 0, 1, 0)
        glColor3fv(COL_WHITE)
        quad = gluNewQuadric(); gluCylinder(quad, 0.12, 0.1, 0.35, 20, 20)
        glTranslatef(0, 0, 0.35); glutSolidSphere(0.13, 20, 20)
        glPopMatrix()

def draw_paws():
    swing = math.sin(state.animation_angle) * 30
    for dx in [-0.4, 0.4]:
        glPushMatrix()
        glTranslatef(dx, -0.7, 0.3)
        if state.is_walking: glRotatef(-swing if dx < 0 else swing, 1, 0, 0)
        glColor3fv(COL_WHITE)
        glutSolidSphere(0.25, 20, 20)
        glTranslatef(0, 0, 0.2); glColor3fv(COL_BLACK); glutSolidSphere(0.08, 10, 10)
        glPopMatrix()

def draw_tail():
    glPushMatrix()
    glTranslatef(0, -0.4, -0.5)
    glRotatef(160 + math.sin(state.tail_angle) * 10, 1, 0, 0)
    glColor3fv(COL_WHITE)
    quad = gluNewQuadric()
    gluCylinder(quad, 0.08, 0.08, 0.5, 20, 20)
    glTranslatef(0, 0, 0.5); glutSolidSphere(0.1, 20, 20)
    glPopMatrix()

def draw_antennas_and_hair():
    glColor3fv(COL_BLACK)
    glLineWidth(3)
    for rx in [-15, 0, 15]:
        glPushMatrix()
        glTranslatef(0, 1.2, 0); glRotatef(rx, 0, 0, 1)
        glBegin(GL_LINES); glVertex3f(0,0,0); glVertex3f(0,0.15,0); glEnd()
        glPopMatrix()
    for dx in [-0.3, 0.3]:
        glPushMatrix()
        glTranslatef(dx, 1.15, 0); glColor3fv(COL_BLACK); glRotatef(-90, 1, 0, 0)
        quad = gluNewQuadric(); gluCylinder(quad, 0.01, 0.01, 0.3, 10, 10)
        glTranslatef(0, 0, 0.3); glColor3fv(COL_YELLOW); glutSolidSphere(0.06, 10, 10)
        glPopMatrix()

def draw_wings():
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4fv(COL_WING)
    for dx in [-0.5, 0.5]:
        glPushMatrix()
        glTranslatef(dx, -0.1, -0.4)
        wing_flap = math.sin(state.animation_angle * 4) * 15 if state.is_walking else 0
        glRotatef((20 + wing_flap) if dx < 0 else (-20 - wing_flap), 0, 1, 0)
        glScalef(0.4, 0.6, 0.1); glutSolidSphere(0.5, 20, 20)
        glPopMatrix()
    glDisable(GL_BLEND)
def draw_eyebrows():

    glColor3f(0,0,0)

    # ceja izquierda
    glPushMatrix()
    glTranslatef(-0.3,0.75,0.65)
    glRotatef(-20 if state.expression=="angry" else 0,0,0,1)
    glScalef(0.4,0.08,0.08)
    glutSolidCube(1)
    glPopMatrix()

    # ceja derecha
    glPushMatrix()
    glTranslatef(0.3,0.75,0.65)
    glRotatef(20 if state.expression=="angry" else 0,0,0,1)
    glScalef(0.4,0.08,0.08)
    glutSolidCube(1)
    glPopMatrix()

def draw_fox_full():
    glPushMatrix()

    # ANIMACIONES DE MOVIMIENTO
    if state.is_walking:
        bounce = abs(math.sin(state.animation_angle)) * 0.1
        glTranslatef(0, bounce, 0)

    if state.reaction_type == "jump":
        progress = state.reaction_timer / state.reaction_duration
        y_off = math.sin(math.pi * progress) * 1.5
        glTranslatef(0, y_off, 0)
    elif state.reaction_type == "spin":
        progress = state.reaction_timer / state.reaction_duration
        glRotatef(360 * progress, 0, 1, 0)
    elif state.reaction_type == "shake":
        shake = math.sin(state.reaction_timer * 0.8) * 0.2
        glTranslatef(shake, 0, 0)
    draw_bee_body()
    draw_wings()
    draw_paws()
    draw_tail()
    draw_arms()
    draw_head()
    draw_ears()
    draw_face_details()
    draw_antennas_and_hair()
    glPopMatrix()