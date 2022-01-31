#!/usr/env python3

##############################################################################################################
#### Command-Line Arguments
##############################################################################################################
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-p', '--positive', type=int, default=8)
parser.add_argument('-n', '--negative', type=int, default=8)

##############################################################################################################
#### Dependedncies
##############################################################################################################
import imgui, glfw
from imgui.integrations.glfw import GlfwRenderer
import OpenGL.GL as gl
import random
import numpy as np
from numpy.random import MT19937
from numpy.random import RandomState, SeedSequence
##############################################################################################################
# import local files (in ./local/ directory)
from local.simulate import *
##############################################################################################################


## config
WINDOW_TITLE  = 'NPQG Test'
SETTINGS_WIDTH       = 400
SETTINGS_LABEL_COL_W = 142



## globals (TEMP for first pass)
settings  = { }
particles = [ ]

## initialize graphics backend (GLFW)
def impl_glfw_init(width, height):
    window_name = WINDOW_TITLE
    if not glfw.init():
        print('====> ERROR: Could not initialize OpenGL context')
        exit(1)
    # OS X supports only forward-compatible core profiles from 3.2
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)
    # create a windowed mode window and its OpenGL context
    window = glfw.create_window(width, height, window_name, None, None)
    glfw.make_context_current(window)
    if not window:
        glfw.terminate()
        print('====> ERROR: Could not initialize GLFW window')
        exit(1)
    return window



#### CALLBACKS ####

## window resize callback
def resize_cb(window, w, h):
    global width, height
    width  = w
    height = h
    print("RESIZE! %d x %d" % (width, height))



#### HELPERS ####

## initialize particle states
def init_particles(n, p, pMin, pMax, vMaxInit):
    np.random.seed(abs(settings['seed']))
    return ([Particle(np.random.uniform(pMin, pMax),
                      np.random.uniform(-vMaxInit, vMaxInit),
                      -1.0) for i in range(n)] + # positive charged particles
            [Particle(np.random.uniform(pMin, pMax),
                      np.random.uniform(-vMaxInit, vMaxInit),
                      1.0)  for i in range(p)])  # negative charged particles

## draw ui for a particle (view/edit state)
def drawParticleUI(p, i):
    imgui.begin_group()
    imgui.text('Particle '+str(i))
    changed,pos    = imgui.input_float3('Position##p'+str(i), p.pos[0], p.pos[1], p.pos[2], '%.4f')
    changed,vel    = imgui.input_float3('Velocity##p'+str(i), p.vel[0], p.vel[1], p.vel[2], '%.4f')
    changed,charge = imgui.input_float ('Charge##p'+str(i),   p.charge, 0.1, 1.0, '%.4f')
    imgui.end_group()
    return Particle(pos, vel, charge)

## determine if a key was pressed given current and previous key states
def keyPressed(key, keys_down, keys_down_last):
    return (keys_down[key] and not keys_down_last[key])



#### MAIN ####

if __name__ == "__main__":

    # parse cmdline arguments --> initial settings
    args = parser.parse_args()
    settings = { 'running'  : False,
                 'seed'     : 0,
                 'dt'       : 0.01,
                 'pMin'     : np.array((-100.0, -100.0, -100.0), dtype=np.float32),
                 'pMax'     : np.array(( 100.0,  100.0,  100.0), dtype=np.float32),
                 'vMaxInit' : np.array((  10.0,   10.0,    0.0), dtype=np.float32),
                 'kEM'      : 1000.0,
                 'p+'       : args.positive,
                 'p-'       : args.negative,
                }

    # create glfw window
    window = impl_glfw_init(1920, 1080) # create a window
    if not window:
        print('UI: Could not open window!')
        glfw.terminate()
        quit()

    # set glfw callbacks
    glfw.set_window_size_callback(window, resize_cb)

    # create imgui context
    imgui.create_context()                 # create imgui context
    impl = GlfwRenderer(window)            # initialize imgui renderer

    # set up imgui style
    style = imgui.get_style()
    io    = imgui.get_io()
    style.window_padding            = (20.0, 20.0) # padding between items and window edges
    style.item_spacing              = (15.0, 15.0) # padding between items
    style.display_safe_area_padding = ( 2.0,  2.0) # padding for main menu bar

    # load fonts
    main_font  = io.fonts.add_font_from_file_ttf('./local/res/fonts/UbuntuMono-R.ttf', 18)
    title_font = io.fonts.add_font_from_file_ttf('./local/res/fonts/UbuntuMono-R.ttf', 24)
    impl.refresh_font_texture()

    # initialize particles
    particles = init_particles(settings['p-'], settings['p+'], settings['pMin'], settings['pMax'], settings['vMaxInit'])

    keys_down_last = list(io.keys_down) # used to check if a key has been pressed

    ## main loop
    quitting = False
    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()
        width,height = glfw.get_window_size(window)

        imgui.new_frame()
        with imgui.font(main_font):
            # main menu bar
            if imgui.begin_main_menu_bar():
                if imgui.begin_menu('File', True):
                    clicked_quit, selected_quit = imgui.menu_item('Quit', 'Ctrl+Q', False, True)
                    if clicked_quit: # close window and quit program
                        quitting = True
                    imgui.end_menu()
                imgui.end_main_menu_bar()
                
            menubar_h  = (imgui.get_item_rect_max().y - imgui.get_item_rect_min().y) + 2*style.display_safe_area_padding.y

            # create a full-screen static/empty imgui window (blank canvas)
            window_flags = (imgui.WINDOW_NO_TITLE_BAR |
                            imgui.WINDOW_NO_COLLAPSE  |
                            imgui.WINDOW_NO_RESIZE    |
                            imgui.WINDOW_NO_MOVE      |
                            imgui.WINDOW_NO_SCROLLBAR )
            imgui.push_style_var(imgui.STYLE_WINDOW_ROUNDING, 0)
            imgui.set_next_window_size(width, height)
            imgui.set_next_window_position(0, menubar_h)
            imgui.begin("canvas", True, window_flags)
            imgui.pop_style_var()

            # handle key bindings
            if io.key_ctrl and keyPressed(glfw.KEY_ESCAPE, io.keys_down, keys_down_last): # Ctrl+Escape --> quit program
                quitting = True
            elif keyPressed(glfw.KEY_SPACE, io.keys_down, keys_down_last):                # Space       --> start/stop physics
                settings['running'] = (not settings['running'])
            elif keyPressed(glfw.KEY_F5, io.keys_down, keys_down_last):                   # F5          --> reset simulation
                particles = init_particles(settings['p-'], settings['p+'], settings['pMin'], settings['pMax'], settings['vMaxInit'])
            keys_down_last = list(io.keys_down)

            # draw left side bar
            p0 = imgui.get_cursor_pos()
            if imgui.begin_child('settings', SETTINGS_WIDTH, -style.window_padding.y, border=True):
                imgui.begin_group()

                ## draw simulation controls
                with imgui.font(title_font):
                    imgui.text("Controls")

                if imgui.button("Reset"):
                    particles = init_particles(settings['p-'], settings['p+'], settings['pMin'], settings['pMax'], settings['vMaxInit'])
                imgui.separator()

                ## draw settings
                with imgui.font(title_font):
                    imgui.text("Settings")

                for l,s in settings.items():
                    imgui.text_unformatted(l)
                    imgui.same_line()
                    imgui.set_cursor_pos((p0.x + SETTINGS_LABEL_COL_W, imgui.get_cursor_pos().y))
                    changed = False
                    lid = '##' + l
                    imgui.push_item_width(-1)
                    if   type(s) == bool:
                        changed, s = imgui.checkbox(lid, s)
                    elif type(s) == int:
                        changed, s = imgui.input_int(lid, s, 1, 10)
                    elif type(s) == float:
                        changed, s = imgui.input_float(lid, s, 0.001, 0.01, '%4f')
                    elif type(s) == str:
                        changed, s = imgui.input_text(lid, s)
                    elif type(s) == np.ndarray:
                        imgui.begin_group()
                        dim_labels = ['X', 'Y', 'Z', 'W']
                        for i in range(min(s.size, len(dim_labels))):
                            imgui.text_unformatted(dim_labels[i])
                            imgui.same_line()
                            imgui.push_item_width(-1)
                            changed, s[i] = imgui.input_float(lid+dim_labels[i], s[i], 0.1, 1.0, '%.4f')
                            imgui.pop_item_width()
                        imgui.end_group()
                    settings[l] = s;
                    imgui.pop_item_width()

                imgui.separator()

                ## draw particle state interfaces
                with imgui.font(title_font):
                    imgui.text("Particle States")

                imgui.begin_group()
                for i,p in enumerate(particles):
                    particles[i] = drawParticleUI(p, i)
                imgui.end_group()

                imgui.end_group()
                imgui.end_child() # end left side bar


            ## draw sim view (right)
            ##  NOTE: currently only drawn in 2D (X/Y -- Z ignored) utilizes imgui draw_list helpers
            ##  TODO: render using opengl and 3D projection camera
            imgui.same_line()
            p0 = imgui.get_cursor_screen_pos()
            view_flags = (imgui.WINDOW_NO_SCROLLBAR |
                          imgui.WINDOW_ALWAYS_AUTO_RESIZE)
            if imgui.begin_child('simView', 0, -style.window_padding.y, border=True, flags=view_flags):
                view_size = imgui.get_window_size()
                draw_list = imgui.get_window_draw_list()
                nCol = imgui.get_color_u32_rgba(1,0,0,1)
                pCol = imgui.get_color_u32_rgba(0,1,0,1)
                for p in particles:
                    pp = (p.pos - settings['pMin']) / (settings['pMax'] - settings['pMin'])
                    psp = p0 + np.array([pp[0]*view_size[0], pp[1]*view_size[1]])
                    draw_list.add_circle_filled(psp[0], psp[1], 5.0, nCol if p.charge < 0 else pCol)

                imgui.end_child() # end sim view


            imgui.end() # end main imgui window

        # update simulation
        if settings['running']:
            particles = simStep(particles, settings['kEM'], settings['dt'], settings['pMin'], settings['pMax'])

        # clear backbuffer
        gl.glClearColor(1., 1., 1., 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        # render
        imgui.render()
        impl.render(imgui.get_draw_data())
        # swap
        glfw.swap_buffers(window)

        if quitting:
            glfw.set_window_should_close(window, True)

    print('Quitting...')
    impl.shutdown()
    glfw.terminate()

