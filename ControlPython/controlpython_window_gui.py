#!/usr/bin/python39
import re
import PySimpleGUI as sg
from collections import OrderedDict


canvas_x = 1000
canvas_y = 300


class CreateWindow:

    time_display = 2000
    sg.theme('DarkGrey9')

    def __init__(self):

        self.menu = None
        self.window_menu = None
        self.dictionary_arguments_operations = {}
        self.beta = None

    def get_main_window(self):
        layout_main = [[sg.Text("ControlPython",
                                size=(26, 1),
                                font=('arial', 30),
                                justification='center'),
                        ],
                       [sg.Image(filename=r'icons/snake.png', size=(300, 300))],
                       ]
        return sg.Window('ControlPython',
                         layout_main,
                         element_justification='center').read(timeout=self.time_display, close=True)

    def get_version_win(self):
        layout_select = [[sg.Text("ControlPython",
                                  size=(26, 1),
                                  font=('arial', 30),
                                  justification='center')
                          ],
                         [sg.Image(filename=r'icons/snake.png', size=(300, 300))],
                         [sg.B('RC Version', size=(10, 2), font=('arial', 15)),
                          sg.B('Beta Version', size=(10, 2), font=('arial', 15))]
                         ]
        window_select = get_option_window(layout_select)

        event, values = window_select.read()
        if event == sg.WIN_CLOSED:
            window_select.close()
        elif event == 'RC Version':
            window_select.close()
            return self.get_second_window()
        elif event == 'Beta Version':
            window_select.close()
            self.beta = 1
            return self.get_second_window()

    def get_second_window(self):
        # Define layout for the pade menu of the second window
        layout_r = [[sg.T('Choose the operation',
                          enable_events=True,)
                     ],
                    [sg.Text('Transfer function')],
                    [sg.R('', 1,
                          key='-TRANSF_FUNCTION-',
                          enable_events=True),
                     sg.Image(filename=r'icons/transfer_menu.png',
                              size=(120, 60),
                              tooltip='Transfer function')
                     ],
                    [sg.Text('Feedback')],
                    [sg.R('', 1,
                          key='-FEEDBACK-',
                          enable_events=True),
                     sg.Image(filename=r'icons/feedback_menu.png',
                              size=(120, 60),
                              tooltip='Feedback'),
                     ],
                    [sg.Text('Time delay')],
                    [sg.R('', 1,
                          key='-TIME_DELAY-',
                          enable_events=True),
                     sg.Image(filename=r'icons/time_delay_menu.png',
                              size=(120, 60),
                              tooltip='Time delay')
                     ],
                    [sg.Text('Draw plot')],
                    [sg.R('', 1,
                          key='-PLOT-',
                          enable_events=True),
                     sg.Image(filename=r'icons/plot_menu.png',
                              size=(120, 60),
                              tooltip='Draw plot')
                     ],
                    [sg.R('Move Everything', 1,
                          key='-MOVE_ALL-',
                          enable_events=True,
                          size=(22, 1))
                     ],
                    [sg.R('Move Stuff', 1,
                          key='-MOVE-',
                          enable_events=True,
                          size=(22, 1))
                     ],
                    [sg.R('Erase item', 1,
                          key='-CLEAR-',
                          enable_events=True,
                          tooltip='Transfer function',
                          size=(22, 1),)
                     ],
                    [sg.B('Erase all', size=(30, 1))],
                    [sg.B('Run', size=(30, 1))],
                    [sg.T('Result', enable_events=True)],
                    [sg.Text(key='-RESULT-',
                             size=(35, 9),
                             justification='center')]
                    ]

        # Define layout for the left side of the second window
        layout_l = [[sg.Graph(canvas_size=(canvas_x, canvas_y),
                              graph_bottom_left=(0, 0),
                              graph_top_right=(canvas_x, canvas_y),
                              key="-GRAPH-",
                              enable_events=True,
                              background_color='white',
                              drag_submits=True)],
                    [sg.Text('Console', font=('arial', 14))],
                    [sg.Text(key='-NUMBERS-', size=(60, 6),
                             font=('arial', 12)),
                     ],
                    [sg.Text(key='-INFO-', size=(60, 2))],
                    ]
        # Beta version do not include time delays
        if not self.beta:
            layout_r.pop(5)
            layout_r.pop(5)

        window_l = sg.Window("Drawing and Moving Stuff Around",
                             layout_l, resizable=True,
                             location=(50, 50),
                             finalize=True)
        window_r = sg.Window("ControlPython Palette",
                             layout_r, keep_on_top=False,
                             resizable=True,
                             location=(1000, 50),
                             default_element_size=(22, 1))
        return window_l, window_r

    def get_menu_options(self, figure_id):
        self.window_menu = get_window_dialog(self.menu)
        enable_window = True

        while enable_window:
            event, values = self.window_menu.read()

            if event == sg.WIN_CLOSED or event == 'Cancel':
                self.window_menu.close()
                enable_window = False

            if event == 'Apply':

                if '' not in values.values() and self.menu == 'Transfer Function':
                    if any([values['-N_COEFF-'].endswith(','),
                            values['-D_COEFF-'].endswith(','),
                            values['-N_COEFF-'][0] == ',',
                            values['-D_COEFF-'][0] == ',']):
                        sg.popup_auto_close('"Transfer Function" only '
                                            'supports commas to separate numbers',
                                            keep_on_top=True)
                        self.window_menu.close()

                    else:
                        input_check_num = values['-N_COEFF-'].replace(',', '')
                        input_check_num = re.sub('[.-]', '', input_check_num, re.IGNORECASE)
                        input_check_num = re.findall(r"\D|\s", input_check_num, re.IGNORECASE)
                        input_check_den = values['-D_COEFF-'].replace(',', '')
                        input_check_den = re.sub('[.-]', '', input_check_den, re.IGNORECASE)
                        input_check_den = re.findall(r"\D|\s", input_check_den, re.IGNORECASE)

                        if [] == input_check_num == input_check_den:
                            if len(values['-N_COEFF-'].split(',')) > len(values['-D_COEFF-'].split(',')):
                                sg.popup_auto_close('The values given to the transfer function can not be '
                                                    'processed as they will produce a non-causal system',
                                                    auto_close=False,
                                                    keep_on_top=True)
                                self.window_menu.close()
                            else:
                                self.dictionary_arguments_operations[figure_id] = \
                                    (self.menu, ([float(num) for num in values['-N_COEFF-'].split(',')],
                                     [float(num) for num in values['-D_COEFF-'].split(',')])
                                     )
                        else:
                            sg.popup_auto_close('"Transfer Function" only '
                                                'supports numbers please check the input',
                                                keep_on_top=True)
                            self.window_menu.close()

                if self.menu == 'Feedback':
                    # TODO include a transfer function object as an option
                    #  for the feedback
                    if values['-FEEDBACK-'] == 'Negative':
                        self.dictionary_arguments_operations[figure_id] = (self.menu, '-1')
                    if values['-FEEDBACK-'] == 'Positive':
                        self.dictionary_arguments_operations[figure_id] = (self.menu, '1')

                if '' not in values.values() and self.menu == 'Time Delay':
                    input_check = re.fullmatch(r"\d+", values['-TIME_DELAY-'])
                    if input_check:
                        self.dictionary_arguments_operations[figure_id] = (self.menu, values['-TIME_DELAY-'])
                    else:
                        sg.popup_auto_close('"Time  Delay " only supports numbers please check the input',
                                            keep_on_top=True)
                        self.window_menu.close()

                if '' not in values.values() and self.menu == 'Plot':
                    input_check = re.fullmatch(r"\d+", values['-TIME_STOP-'])
                    if input_check:
                        self.dictionary_arguments_operations[figure_id] = (self.menu, values['-TIME_STOP-'])
                    else:
                        sg.popup_auto_close('"Time  Stop " only supports numbers please check the input',
                                            keep_on_top=True)
                        self.window_menu.close()

                if '' in values.values() and self.menu != 'Feedback':
                    sg.popup_auto_close('Please set all the parameters in '
                                        'case of no time delay set it as "0"',
                                        keep_on_top=True)
                    self.window_menu.close()

            if event == 'Clear':
                for key_argument in self.window_menu.ReturnValuesDictionary.keys():
                    self.window_menu[key_argument].update('')

#        if not enable_window and enabler_close_window:
#                graph.delete_figure(figure_id)
            self.window_menu.close()
# End of the class


def get_window_dialog(menu):
    layout_menu = {
        'Transfer Function': [[sg.T("Fill the parameters:", font=('arial', 12))],
                              [sg.T("You should specify the"
                                    " coefficients in descending"
                                    " order of powers of s. e.g 1,2,3"
                                    " for s+2s^2+3s^3",
                                    font=('arial', 8))],
                              [sg.T('Numerator Coefficients', size=(20, 1)),
                               sg.In(key='-N_COEFF-'),
                               ],
                              [sg.T('Denominator Coefficients', size=(20, 1)),
                               sg.In(key='-D_COEFF-')
                               ],
                              [sg.Button('Clear'),
                               sg.Button('Cancel'),
                               sg.Button('Apply'),
                               ]
                              ],
        'Feedback': [[sg.InputOptionMenu(('Negative',
                                          'Positive',
                                          'No Feedback'
                                          ),
                                         key='-FEEDBACK-')
                      ],
                     # TODO include the option of a transfer function as feedback
                     [sg.Button('Apply'),
                      sg.Button('Cancel'),
                      ]
                     ],

        'Time Delay': [[sg.T('Time delay in sec', font=('arial', 12)),
                        sg.In(key='-TIME_DELAY-')],
                       [sg.Button('Clear'),
                        sg.Button('Cancel'),
                        sg.Button('Apply'),
                        ]
                       ],
        'Plot': [[sg.T('Time of the simulation in sec', font=('arial', 12)),
                  sg.In(key='-TIME_STOP-')],
                 [sg.Button('Clear'),
                  sg.Button('Cancel'),
                  sg.Button('Apply')]
                 ],
    }
    return sg.Window(f'{menu} menu', layout_menu[menu], keep_on_top=True)


def get_option_window(layout_select):
    return sg.Window("ControlPython",
                     layout_select, resizable=True,
                     element_justification='center',
                     finalize=True)


def get_order_graphs(graph):
    # TODO variables should be changed
    list_of_fig_total = []
    sum_of_lists = 0
    for row in range(0, canvas_y):
        list_of_fig_row = []
        for column in range(0, canvas_x):
            figure = graph.get_figures_at_location((column, row))
            graph.bring_figure_to_front(figure)
            if figure != ():
                list_of_fig_row.append(figure[0])
                # Todo include logg
        if list_of_fig_row:
            list_of_fig_row = list(dict.fromkeys(list_of_fig_row))

            if sum_of_lists != sum(list_of_fig_row):
                list_of_fig_total.append(list_of_fig_row)

            sum_of_lists = sum(list_of_fig_row)

    return list_of_fig_total


def get_order_op(dictionary_operations, list_order_fig):
    total_num_systems = []
    largest = 0
    total_dict_ordered = OrderedDict(dictionary_operations)

    for list_order in list_order_fig:
        if len(list_order) > largest:
            for operation in list_order:
                if operation != 1:
                    total_num_systems = list_order
            largest = len(list_order)
    try:
        for order in total_num_systems:
            total_dict_ordered.move_to_end(order)

    except KeyError:
        print(f'The {total_dict_ordered} does not have one key from {total_num_systems}')

    return total_dict_ordered
