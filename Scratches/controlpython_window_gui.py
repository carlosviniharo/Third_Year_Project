#!/usr/bin/python39
import PySimpleGUI as sg
from control_generic_class import *
from collections import OrderedDict


CANVAS_WORKING_SPACE_X = 800,
CANVAS_WORKING_SPACE_Y = 800,
# Layout for all the windows in the ControlPython's GUI
# Define the window's content
layout_main = [[sg.Text("ControlPython",
                        size=(26, 1),
                        font=('TimesNewRoman', 30),
                        justification='center'),
                ],
               [sg.Image(filename=r'icons/snake.png', size=(300,300))],
               ]
# Define layout for the pade menu of the second window
layout_r = [[sg.T('Choose the operation',
                  enable_events=True)
             ],
            [sg.R('', 1,
                  key='-TRANF_FUNCTION-',
                  enable_events=True),
             sg.B('Transfer function',
                  image_filename=r'icons/High_order.png',
                  image_subsample=4,
                  tooltip='Transfer function',
                  auto_size_button=True)
             ],
            [sg.R('', 1,
                  key='-FEEDBACK-',
                  enable_events=True),
             sg.B('Feedback',
                  image_filename=r'icons/Feedback.png',
                  image_subsample=4,
                  tooltip='Feedback',
                  auto_size_button=True),
             ],
            [sg.R('', 1,
                  key='-TIME_DELAY-',
                  enable_events=True),
             sg.B('Time delay',
                  image_filename=r'icons/Delay.png',
                  image_subsample=4,
                  tooltip='Time delay',
                  auto_size_button=True),
             ],
            [sg.R('', 1,
                  key='-PLOT-',
                  enable_events=True),
             sg.B('Draw plot',
                  image_filename=r'icons/plot.png',
                  image_subsample=4,
                  tooltip='Draw plot',
                  auto_size_button=True)
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
            [sg.B('Erase all', size=(22, 1))],
            [sg.B('Run')],
            ]

# Define layout for the left side of the second window
layout_l = [[sg.Graph(canvas_size=(600, 600),
                      graph_bottom_left=(0, 0),
                      graph_top_right= (800,800),
                      key="-GRAPH-",
                      enable_events=True,
                      background_color='white',
                      drag_submits=True,
                      right_click_menu=[[], ['Erase item']])
             ],
            [sg.Text(key='-INFO-', size=(60, 1))]
            ]

# Define layout of the transfer function menu.


class CreateWindow():

    time_display = 2000

    def __init__(self):

        self.menu = None
        self.window_menu = None
        self.dictionary_arguments_operations = {}

    def get_main_window(self):
        return sg.Window('ControlPython',
                         layout_main,
                         element_justification = 'center',
                         ).read(timeout=self.time_display, close=True)

    def get_second_window(self):
        window_l = sg.Window("Drawing and Moving Stuff Around",
                             layout_l, resizable=True,
                             location=(200, 100),
                             finalize=True)
        window_r = sg.Window("ControlPython Palette",
                             layout_r, keep_on_top=False,
                             default_element_size=(22, 1))
        return window_l,window_r

    def get_menu_options(self, figure_id):
        self.window_menu = get_window_new(self.menu)
        enable_window = True
#      enabler_close_window = True
        while enable_window:
            event, values =  self.window_menu.read()

            if event == sg.WIN_CLOSED or event == 'Cancel':
                self.window_menu.close()
                enable_window = False


            if event == 'Apply':
                if not '' in values.values() and self.menu == 'Transfer Function':
                    # TODO support extra characters in the input or give a exception
                    self.dictionary_arguments_operations[figure_id] = \
                        (self.menu,([float(num) for num in values['-N_COEFF-'].split(' ')],
                         [float(num) for num in values['-D_COEFF-'].split(' ')])
                         )

                if  self.menu == 'Feedback':
                    if values['-FEEDBACK-'] == 'Negative':
                        self.dictionary_arguments_operations[figure_id] = (self.menu, '-1')
                    if values['-FEEDBACK-'] == 'Positive':
                        self.dictionary_arguments_operations[figure_id] = (self.menu, '1')

                if not '' in values.values() and self.menu == 'Time Delay':
                    self.dictionary_arguments_operations[figure_id] = (self.menu, values['-TIME_DELAY-'])

                if not '' in values.values() and self.menu =='Plot':
                    self.dictionary_arguments_operations[figure_id] = (self.menu, values['-TIME_STOP-'])
                
                if '' in values.values() and self.menu != 'Feedback':
                    sg.popup_auto_close('Please set all the parameters in '
                                        'case of no time delay set it as "0"',
                                        keep_on_top=True)
#                enabler_close_window = False

            if event == 'Clear':
                for key_argument in self.window_menu.ReturnValuesDictionary.keys():
                    self.window_menu[key_argument].update('')

#        if not enable_window and enabler_close_window:
#                graph.delete_figure(figure_id)
            self.window_menu.close()


def get_window_new(menu):
    layout_menu = {
        'Transfer Function': [[sg.T("Fill the parameters")],
                              [sg.T('Numerator Coefficients'),
                               sg.In(key='-N_COEFF-'),
                               ],
                              [sg.T('Denominator coefficient'),
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
                     # TODO include the option of a trasnfer function as feedback
                     [sg.Button('Apply'),
                      sg.Button('Cancel'),
                      ]
                     ],

        'Time Delay': [[sg.T('Time delay in sec'),
                        sg.In(key='-TIME_DELAY-')],
                       [sg.Button('Clear'),
                        sg.Button('Cancel'),
                        sg.Button('Apply'),
                        ]
                       ],
        'Plot': [[sg.T('Time stop in sec'),
                  sg.In(key='-TIME_STOP-')],
                 [sg.Button('Clear'),
                  sg.Button('Cancel'),
                  sg.Button('Apply'),]
                 ],
    }
    return sg.Window( f'{menu} menu', layout_menu[menu])

def get_order_graphs(graph):
    # TODO variables should be changed
    list_of_fig_row= []
    list_of_fig = []
    sum_of_lists  = None
    for row in range(1,800):
        for column in range(1,800):
            figure = graph.get_figures_at_location((column, row))
            if figure != ():
                list_of_fig.append(figure[0])
                # Todo include logg
        if list_of_fig != []:
            list_of_fig_col = list(dict.fromkeys(list_of_fig))
            list_of_fig = []

            if sum_of_lists != sum(list_of_fig_col):
                list_of_fig_row.append(list_of_fig_col)
            sum_of_lists = sum(list_of_fig_col)
    return list_of_fig_row

def get_order_op(dictionary_operations, list_order_fig):
    total_num_systems = []
    largest = 0
    total_dict_ordered = OrderedDict(dictionary_operations)
    for list_order in list_order_fig:
        if len(list_order) > largest:
            for operation in list_order:
                if operation != 1 and dictionary_operations[operation][0] == 'Plot':
                    total_num_systems = list_order
            largest = len(list_order)
    try:
        for order in total_num_systems:
            total_dict_ordered.move_to_end(order)

    except KeyError:
        print('Include the icon plot at the end of the simulation')


    return total_dict_ordered
