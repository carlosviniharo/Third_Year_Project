import PySimpleGUI as sg
from control_generic_class import *


sg.theme('Dark Blue 3')

# Constants
DISPLAY_TIME_MILLISECONDS = 2000


# Define the window's content
layout_main = [[sg.Text("Chose the case", )],
               [sg.Button(button_text='First Order', image_filename=r'icons/first_order.png'),
                sg.Button(button_text='Second Order', image_filename=r'icons/second_order.png'),
                sg.Button(button_text='Higher Order', image_filename=r'icons/High_order.png')],
               [sg.Button('Quit', button_type=5, size=(5, 5))],
               ]


def get_window(window_type):
    """
    This function creates the second window of the GUI and defines the widgets, the buttons
    and inputs.
    :param window_type:
    :return: window PySimpleGUI object.
    """
    dic_second_window = {}
    layout_gen_sec_win = [[sg.T('Time stop T '), sg.In(key='-TIME_STOP-')],
                          [sg.T('Feedback'),
                           sg.InputOptionMenu(('Negative', 'Positive', 'No Feedback'),
                                              key='-FEEDBACK-')],
                          [sg.T('Time delay'),
                           sg.InputOptionMenu(('Internal delay', 'External delay', 'No Delay'),
                                              key='-TIME_DELAY-'),
                           sg.In(key='-DELAY_SEC-')],
                          [sg.Button('Clear'), sg.Button('Cancel'), sg.Button('Apply')]]

    layout_second_window = (
        ('First Order', [[sg.T("Fill the parameters")],
                         [sg.T('DC Gain a'), sg.In(key='-DC_GAIN-')],
                         [sg.T('Time constant b'), sg.In(key='-TIME_CONST-')]]
         ),

        ('Second Order', [[sg.T("Fill the parameters")],
                          [sg.T('Natural Frequency ω'), sg.In(key='-N_FREQ-')],
                          [sg.T('Damping Ratio ζ'), sg.In(key='-DAM_RATIO-')]]
         ),
        ('Higher Order', [[sg.T("Fill the parameters")],
                          [sg.T('Numerator Coefficients'), sg.In(key='-N_COEFF-')],
                          [sg.T('Denominator coefficient'), sg.In(key='-D_COEFF-')]]
         )
    )
    for key_sys_order, layout_values in layout_second_window:
        dic_second_window[key_sys_order] = layout_values + layout_gen_sec_win

    print(dic_second_window[window_type])
    return sg.Window(f'Menu {window_type} system',
                     dic_second_window[window_type],
                     auto_size_text=False,
                     default_element_size=(22, 1),
                     text_justification='right',
                     resizable=True).Finalize()


def get_feedback_time_delay_stoptime(val):
    """
    Copies the values from the user for the feedback and time delay from
    the return dictionary of PySimpleGUI
    :param val: Dictionary, contains the inputs from the second window
    :return: None
    """

    system_tf.stp_time = float(val['-TIME_STOP-'])
    if val['-FEEDBACK-'] == 'Negative':
        system_tf.feedback_tf = -1
    if val['-FEEDBACK-'] == 'Positive':
        system_tf.feedback_tf = 1

    if val['-TIME_DELAY-'] == 'Internal delay':
        system_tf.internal_delay_t = float(val['-DELAY_SEC-'])
    if val['-TIME_DELAY-'] == 'External delay':
        system_tf.time_delay = float(val['-DELAY_SEC-'])


# Initial window
sg.Window('Window Title', [[sg.Text("ControlPython",
                                    size=(26, 1),
                                    font=('TimesNewRoman', 30),
                                    justification='center')],
                           [sg.Image(filename=r'icons/snake.png', size=(500, 500))],
                           ]).read(timeout=DISPLAY_TIME_MILLISECONDS, close=True)

# Create the menu window
window = sg.Window('ControlPython', layout_main, resizable=True, text_justification='center').Finalize()

# Display and interact with the window using an Event loop
while True:
    event, values = window.read()
    system_tf = GetControlTransferFunction()

    if event == sg.WIN_CLOSED or event == 'Quit':
        break
    else:
        # Create a second window
        window_second_menu = get_window(event)
        enabler = True
        while enabler:
            # User options
            if event == 'First Order':
                event_fo, values_fo = window_second_menu.read()

                if event_fo in (sg.WIN_CLOSED, 'Cancel'):
                    window_second_menu.close()
                    enabler = False

                if event_fo == 'Apply':
                    if '' not in values_fo.values():
                        # TODO Include fractions in the inputs
                        system_tf.dc_gain = float(values_fo['-DC_GAIN-'])
                        system_tf.time_cons = 1 / float(values_fo['-TIME_CONST-'])
                        get_feedback_time_delay_stoptime(values_fo)
                        sys_tf = system_tf._get_first_order_transfer_function()
                        system_tf.evaluate_time_delays(sys_tf)

                    else:
                        sg.popup_auto_close('Please set all the parameters in '
                                            'case of no time delay set it as "0"')
                if event_fo == 'Clear':
                    for key_argument in window_second_menu.ReturnValuesDictionary.keys():
                        window_second_menu[key_argument].update('')

            if event == 'Second Order':
                event_so, values_so = window_second_menu.read()

                if event_so == sg.WIN_CLOSED or event_so == 'Cancel':
                    window_second_menu.close()
                    enabler = False

                if event_so == 'Apply':
                    if '' not in values_so.values():
                        # TODO Include fractions in the inputs
                        system_tf.damping_ratio = float(values_so['-DAM_RATIO-'])
                        system_tf.natural_frequency = float(values_so['-N_FREQ-'])
                        get_feedback_time_delay_stoptime(values_so)
                        sys_tf = system_tf._get_second_order_transfer_function()
                        system_tf.evaluate_time_delays(sys_tf)

                    else:
                        sg.popup_auto_close('Please set all the parameters in '
                                            'case of no time delay set it as "0"')
                if event_so == 'Clear':
                    for key_argument in window_second_menu.ReturnValuesDictionary.keys():
                        window_second_menu[key_argument].update('')

            if event == 'Higher Order':
                event_ho, values_ho = window_second_menu.read()

                if event_ho == sg.WIN_CLOSED or event_ho == 'Cancel':
                    window_second_menu.close()
                    enabler = False

                if event_ho == 'Apply':
                    if '' not in values_ho.values():
                        # TODO Include fractions in the inputs
                        system_tf.numerator_coeff = [float(num) for num in values_ho['-N_COEFF-'].split(' ')]
                        system_tf.denominator_coeff = [float(num) for num in values_ho['-D_COEFF-'].split(' ')]
                        get_feedback_time_delay_stoptime(values_ho)
                        sys_tf = system_tf._get_generic_transfer_function()
                        system_tf.evaluate_time_delays(sys_tf)
                    else:
                        sg.popup_auto_close('Please set all the parameters in '
                                            'case of no time delay set it as "0"')
                if event_ho == 'Clear':
                    for key_argument in window_second_menu.ReturnValuesDictionary.keys():
                        window_second_menu[key_argument].update('')

# Finish by removing from the screen
window.close()
