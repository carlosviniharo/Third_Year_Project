#!/usr/bin/python3.8

from controlpython_window_gui import *
from PIL import Image
from control_generic_class import *
from pprint import pprint


img_icon = Image.open(r'icons/snake.png')
img_icon = img_icon.resize((50,50))
img_icon.save('icons/icon_snake_main.png')


def get_GUI():
        all_windows = CreateWindow()
        # Create main window
        all_windows.get_main_window()
        # Create second window and pade
        window_l, window_r = all_windows.get_second_window()

        # get the graph element for ease of use later
        graph = window_l["-GRAPH-"]  # type: sg.Graph
        graph.draw_image(filename='icons/icon_snake_main.png', location=(0,90))

        dragging = False
        start_point = end_point = None
        prior_rect = 0
        drawing_setting = window_r.read(timeout=1)[1]

        window_r.move(window_l.current_location()[0] + window_l.size[0], window_l.current_location()[1])


        while True:
            window, event, values = sg.read_all_windows()
            #print(event, values)
            if window == window_r:
                drawing_setting = values

            if event == sg.WIN_CLOSED:
                break

            if event == '-GRAPH-':
                x, y = values['-GRAPH-']
                if not dragging:
                    start_point = (x, y)
                    dragging = True

                    lastxy = x, y
                else:
                    end_point = (x, y)
                if prior_rect:
                    graph.delete_figure(prior_rect)
                delta_x, delta_y = x - lastxy[0], y - lastxy[1]
                lastxy = x, y

                #print(drawing_setting)
                if None not in (start_point, end_point):

                    if drawing_setting['-TRANF_FUNCTION-']:
                        prior_rect = graph.draw_image(filename=r'icons/High_order_icon.png', location=(x, y))
                        all_windows.menu = 'Transfer Function'

                    if drawing_setting['-FEEDBACK-']:
                        prior_rect = graph.draw_image(filename=r'icons/Feedback_icon.png', location=(x, y))
                        all_windows.menu = 'Feedback'

                    if drawing_setting['-TIME_DELAY-']:
                        prior_rect = graph.draw_image(filename=r'icons/Delay_icon.png', location=(x, y))
                        all_windows.menu = 'Time Delay'

                    if drawing_setting['-PLOT-']:
                        prior_rect = graph.draw_image(filename=r'icons/Plot_icon.png', location=(x, y))
                        all_windows.menu = 'Plot'

                    if drawing_setting['-MOVE_ALL-']:
                        graph.move(delta_x, delta_y)
                        all_windows.menu = None

                    if drawing_setting['-MOVE-']:
                        for fig in graph.get_figures_at_location((x,y)):
                            graph.move_figure(fig, delta_x, delta_y)
                            all_windows.menu = None

                    if drawing_setting['-CLEAR-']:
                        drag_figures = graph.get_figures_at_location((x,y))
                        for fig in drag_figures:
                            graph.delete_figure(fig)
                            all_windows.dictionary_arguments_operations.pop(fig)
                        all_windows.menu = None

            if event == 'Erase all':
                graph.erase()
                all_windows.dictionary_arguments_operations = {}

            if event.endswith('+UP'):  # The drawing has ended because mouse up
                info = window["-INFO-"]
                info.update(value=f"Selected {all_windows.menu} #{prior_rect} from {start_point} to {end_point}")

                if all_windows.menu is not None:
                    print(all_windows)
                    all_windows.get_menu_options(prior_rect)
                try:
                    all_windows.dictionary_arguments_operations[prior_rect]
                except:
                        graph.delete_figure(prior_rect)
                print(prior_rect)
                start_point, end_point = None, None  # enable grabbing a new rect
                dragging = False
                prior_rect = None

            if event == 'Run':
                order_operations = get_order_graphs(graph)
                final_order_op = get_order_op(all_windows.dictionary_arguments_operations, order_operations)
                control_operations = GetControlTransferFunction(final_order_op)
                system_tf = None
                enable_internal_time_delay = False
                enable_feedback = False
                sum_time_delays = []

                for operation in final_order_op.values():

                    if operation[0] == 'Transfer Function':
                        if enable_internal_time_delay:
                            system_tf = control_operations.get_time_delay_pade(system_tf)
                            enable_internal_time_delay = False
                        system_tf = control_operations.add_transfer_fuction(operation[1], enable_internal_time_delay, system_tf)


                    if operation[0] == 'Feedback':
                        control_operations.feedback_tf = int(operation[1])
                        if enable_internal_time_delay:
                            system_tf = control_operations._get_internal_delay(system_tf)
                            control_operations.enable_time_delay = enable_internal_time_delay
                            enable_internal_time_delay = False

                        else:
                            system_tf = control_operations.get_negative_feedback(system_tf)
                            enable_feedback = True


                    if operation[0] == 'Time Delay':
                        control_operations.internal_delay_t = int(operation[1])
                        if enable_internal_time_delay:
                            system_tf = control_operations.get_time_delay_pade(system_tf)

                        enable_internal_time_delay = True

                    if operation[0] == 'Plot':
                        if enable_internal_time_delay:
                            system_tf = control_operations.get_time_delay_pade(system_tf)
                        print(final_order_op)
                        pprint(system_tf)
                        control_operations.stp_time = int(operation[1])
                        control_operations.evaluate_time_delays(system_tf)

        window.close()
if __name__ == '__main__':
    get_GUI()