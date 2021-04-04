"""

"""

import OpenGL
import numpy
import math
from OpenGL.GL import *
import os
import glfw
import glutils


class RenderWindow:
    """GLFW Window Rendering Window Class"""

    # version hints
    glfw.glfwWindowHint(glfw.GLFW_CONTEXT_VERSION_MAJOR, 3)
    glfw.glfwWindowHint(glfw.GLFW_CONTEXT_VERSION_MINOR, 3)
    glfw.glfwWindowHint(glfw.GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE)
    glfw.glfwWindowHint(glfw.GLFW_OPENGL_PROFILE, glfw.GLFW_OPENGL_CORE_PROFILE)

    def __init__(self, str_vs, str_fs):
        cwd = os.getcwd()                   # get current working directory

        glfw.glfwInit()                     # glfw initialization

        os.chdir(cwd)                      # restore current directory

        # make a window
        self.width, self.height = 640, 480
        self.aspect = self.width / float(self.height)
        self.win = glfw.glfwCreateWindow(self.width, self.height, b'simpleglfw')

        glfw.glfwMakeContextCurrent(self.win)       # current context

        # initialize GL
        glViewport(0, 0, self.width, self.height)
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.5, 0.5, 0.5, 1.0)

        # set window callbacks
        glfw.glfwSetMouseButtonCallback(self.win, self.on_mouse_button)
        glfw.glfwSetKeyCallback(self.win, self.on_keyboard)
        glfw.glfwSetWindowSizeCallback(self.win, self.on_size)

        self.scene = Scene(str_vs, str_fs)                  # create 3D
        self.exit_now = False                   # exit flag

    def on_keyboard(self, win, key, scancode, action, mods):
        # print("keyboard button: ", win, key, scancode, action, mods)
        if action == glfw.GLFW_PRESS:
            if key == glfw.GLFW_KEY_ESCAPE:                      # ESC to exit
                self.exit_now = True
            else:
                self.scene.showCircle = not self.scene.showCircle

    def on_mouse_button(self, win, button, action, mods):
        # print('mouse button: ', win, button, action, mods)
        pass

    def on_size(self, win, width, height):
        self.width = width
        self.height = height
        self.aspect = width / float(height)
        glViewport(0, 0, self.width, self.height)

    def run(self):
        glfw.glfwSetTime(0)          # timer initialization
        t = 0.0
        while not glfw.glfwWindowShouldClose(self.win) and not self.exit_now:
            current_t = glfw.glfwGetTime()
            if current_t -t > 0.1:
                t = current_t         # time updated
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)                  # | = bitwise or

                # build projection matrix
                p_matrix = glutils.perspective(45.0, self.aspect, 0.1, 100.0)
                mv_matrix = glutils.lookAt([0.0, 0.0, -2.0], [0.0, 0.0, 0.0], [0.0, 1.0, 0.0])
                # model-view matrix: [[eye pos], [look at {origin in this case)], [direction vector]]

                self.scene.render(p_matrix, mv_matrix)                        # render
                self.scene.step()                                             # step

                glfw.glfwSwapBuffers(self.win)
                glfw.glfwPollEvents()

    glfw.glfwTerminate()                                              # end

    def step(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)                  # clear

        p_matrix = glutils.perspective(45.0, self.aspect, 0.1, 100.0)
        mv_matrix = glutils.lookAt([0.0, 0.0, -2.0], [0.0, 0.0, 0.0], [0.0, 1.0, 0.0])

        self.scene.render(p_matrix, mv_matrix)                        # render
        self.scene.step()                                             # step

        glfw.glfwSwapBuffers(self.win)
        glfw.glfwPollEvents()


class Scene:
    """OpenGL 3D scene class"""
    def __init__(self, strVS, strFS):
        self.program = glutils.loadShaders(strVS=strVS, strFS=strFS)
        glUseProgram(self.program)
        self.pMatrixUniform = glGetUniformLocation(self.program, b'uPMatrix')
        self.mvMatrixUniform = glGetUniformLocation(self.program, b'uMVMatrix')

        self.tex2D = glGetUniformLocation(self.program, b'tex2D')          # 2D texture

        # define triangle strip vertices
        vertex_data = numpy.array([-0.5, -0.5, 0.0,
                                   0.5, -0.5, 0.0,
                                   -0.5, 0.5, 0.0,
                                   0.5, 0.5, 0.0], numpy.float32)

        # set up vertex array object (VAO)
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # vertices
        self.vertex_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)

        glBufferData(GL_ARRAY_BUFFER, 4 * len(vertex_data), vertex_data, GL_STATIC_DRAW)  # set buffer data
        glEnableVertexAttribArray(0)            # enable vertex array
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)       # set buffer data pointer
        glBindVertexArray(0)              

        self.t = 0
        self.tex_id = glutils.loadTexture('star.png')
        self.showCircle = False                                 # show circle flag

    def render(self, pMatrix, mvMatrix):
        glUseProgram(self.program)       # use shader
        glUniformMatrix4fv(self.pMatrixUniform, 1, GL_FALSE, pMatrix)          # set projection matrix
        glUniformMatrix4fv(self.mvMatrixUniform, 1, GL_FALSE, mvMatrix)        # set model-view matrix
        glUniform1i(glGetUniformLocation(self.program, b'showCircle'), self.showCircle)     # show circle

        # enable texture
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.tex_id)
        glUniform1i(self.tex2D, 0)

        glBindVertexArray(self.vao)                      # bind VAO
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)            # draw
        glBindVertexArray(0)                             # unbind VAO

    def step(self):
        self.t = (self.t + 1) % 360     # increment angle
        # set shader angle in radians
        glUniform1f(glGetUniformLocation(self.program, 'uTheta'), math.radians(self.t))

