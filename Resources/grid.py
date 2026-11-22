# Resources/grid.py
from OpenGL.GL import *

def draw_grid(size=20, step=2):
    glDisable(GL_LIGHTING)
    glColor3f(0.35, 0.35, 0.35)
    glBegin(GL_LINES)
    for i in range(-size, size + 1, step):
        glVertex3f(i, 0, -size)
        glVertex3f(i, 0,  size)
        glVertex3f(-size, 0, i)
        glVertex3f( size, 0, i)
    glEnd()
    glEnable(GL_LIGHTING)
