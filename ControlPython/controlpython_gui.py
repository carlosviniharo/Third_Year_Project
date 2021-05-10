#!/usr/bin/python3.8

from controlpython_window_gui import *
from control_generic_class import *
import base64


def get_gui():
    window_l, window_r = windows
    # get the graph element for ease of use later
    graph = window_l["-GRAPH-"]  # type: sg.Graph
    graph.draw_image(filename='icons/icon_snake_main.png', location=(0, 46))

    dragging = False
    start_point = end_point = None
    prior_rect = 0
    drawing_setting = window_r.read(timeout=1)[1]
    window_r.move(window_l.current_location()[0] + window_l.size[0], window_l.current_location()[1])
    open_windows = True
    lastxy = []

    while open_windows:
        values_screen = []

        window, event, values = sg.read_all_windows()

        if event == sg.WIN_CLOSED:
            break

        if window == window_r:
            drawing_setting = values

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

            if None not in (start_point, end_point):
                if drawing_setting['-TRANSF_FUNCTION-']:
                    prior_rect = graph.draw_image(filename=r'icons/icon_transf.png', location=(x, y))
                    all_windows.menu = 'Transfer Function'

                if drawing_setting['-FEEDBACK-']:
                    prior_rect = graph.draw_image(filename=r'icons/icon_feedback.png', location=(x, y))
                    all_windows.menu = 'Feedback'

                if all_windows.beta and drawing_setting['-TIME_DELAY-']:
                    prior_rect = graph.draw_image(filename=r'icons/icon_delay.png', location=(x, y))
                    all_windows.menu = 'Time Delay'

                if drawing_setting['-PLOT-']:
                    prior_rect = graph.draw_image(filename=r'icons/icon_plot.png', location=(x, y))
                    all_windows.menu = 'Plot'

                if drawing_setting['-MOVE_ALL-']:
                    graph.move(delta_x, delta_y)
                    all_windows.menu = None

                if drawing_setting['-MOVE-']:
                    for fig in graph.get_figures_at_location((x, y)):
                        graph.move_figure(fig, delta_x, delta_y)
                        all_windows.menu = None

                if drawing_setting['-CLEAR-']:
                    drag_figures = graph.get_figures_at_location((x, y))
                    for fig in drag_figures:
                        graph.delete_figure(fig)
                        all_windows.dictionary_arguments_operations.pop(fig)
                    all_windows.menu = None

        if event == 'Erase all':
            graph.erase()
            all_windows.dictionary_arguments_operations = {}

        if event.endswith('+UP'):
            # The drawing has ended because mouse up
            info = window["-INFO-"]
            info.update(value=f"Selected {all_windows.menu} #{prior_rect} from {start_point} to {end_point}")

            if end_point:
                if any([end_point[0] > 871, end_point[1] > 310,
                        end_point[0] is None, end_point[1] is None]):
                    open_windows = False

                if all_windows.menu is not None:
                    print(all_windows)
                    all_windows.get_menu_options(prior_rect)
                try:
                    all_windows.dictionary_arguments_operations[prior_rect]
                except KeyError:
                    graph.delete_figure(prior_rect)
                print(all_windows.dictionary_arguments_operations)
                numeric_exp = window["-NUMBERS-"]
                for operation in all_windows.dictionary_arguments_operations.values():
                    values_screen.append(operation)
                    numeric_exp.update(value=f"Operation:\n{operation[0]}\n\nValue:\n{operation[1]}"
                                             f"\n\nExpression:\n{values_screen}")
                start_point, end_point = None, None  # enable grabbing a new rect
                dragging = False
                prior_rect = None
            elif not start_point:
                open_windows = False
            else:
                sg.popup('Please drag or keep pressing'
                         ' the left bottom of the mouse'
                         ' to create an operation')
                dragging = False
            all_windows.menu = None

        if event == 'Run':
            control_operations = GetControlTransferFunction()
            final_order_op = get_list_of_operations(graph, all_windows.dictionary_arguments_operations)
            system_tf = None
            enable_internal_time_delay = False

            if final_order_op[0][0] != 'Transfer Function':
                sg.popup_auto_close('The simulation always should start with the operation '
                                    '"Transfer Function"')
            elif final_order_op[-1][0] != 'Plot':
                sg.popup_auto_close('Please include the operation '
                                    '"Plot" to obtain the result and plots',
                                    keep_on_top=True)

            else:

                if final_order_op[-2][0] == 'Time Delay':
                    control_operations.time_delay = int(final_order_op[-2][1])
                    final_order_op.pop(-2)

                for operation in final_order_op:

                    if operation[0] == 'Transfer Function':
                        if enable_internal_time_delay:
                            system_tf = control_operations.get_time_delay_pade(system_tf)
                            enable_internal_time_delay = False
                        system_tf = control_operations.add_transfer_fuction(operation[1], system_tf)

                    elif operation[0] == 'Feedback':
                        control_operations.feedback_tf = int(operation[1])
                        if enable_internal_time_delay:
                            system_tf = control_operations.get_internal_delay(system_tf)
                            control_operations.enable_time_delay = enable_internal_time_delay
                            enable_internal_time_delay = False

                        else:
                            system_tf = control_operations.get_feedback(system_tf)

                    elif operation[0] == 'Time Delay':
                        control_operations.internal_delay_t = int(operation[1])
                        if enable_internal_time_delay:
                            system_tf = control_operations.get_time_delay_pade(system_tf)

                        enable_internal_time_delay = True

                    elif operation[0] == 'Plot':
                        result = window["-RESULT-"]
                        result.update(value=f"{system_tf}")
                        print(system_tf)
                        if enable_internal_time_delay:
                            system_tf = control_operations.get_time_delay_pade(system_tf)
                        print(final_order_op)
                        control_operations.stp_time = int(operation[1])
                        control_operations.evaluate_time_delays(system_tf).show()
                        sg.Print(final_order_op, no_titlebar=True)

    window_l.close()
    window_r.close()
# End function GUI


def get_list_of_operations(graph, dictionary_arguments_operations):

    order_operations = get_order_graphs(graph)
    final_order_op = get_order_op(dictionary_arguments_operations, order_operations)

    return list(final_order_op.values())


if __name__ == '__main__':
    # Formatting  the png fot the icon of the app
    with open(r'icons/snake.png', "rb") as f:
        image_binary = f.read()
    base64_encode = base64.b64encode(image_binary)
    sg.SetGlobalIcon(base64_encode)

    # Initializes the Class for all the windows.
    all_windows = CreateWindow()
    # Create main window
    all_windows.get_main_window()
    while True:
        windows = all_windows.get_version_win()
        all_windows.dictionary_arguments_operations = {}
        if windows:
            get_gui()
            all_windows.beta = None
        else:
            break
