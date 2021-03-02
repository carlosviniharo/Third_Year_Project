import PySimpleGUI as sg
from control_generic_class import *
import sys
import os

sg.theme('SystemDefaultForReal')

# Define the window's content
layout_main = [[sg.Text("Chosse the case")],
               [sg.Button('First Order', image_filename=r'icons/first_order.png'),
                sg.Button(button_text='Second Order',image_filename=r'icons/second_order.png'),
                sg.Button(button_text='Higer Order',image_filename=r'icons/High_order.png'),
                sg.Button('Quit')],
               ]
"""
layout_menu_options = [[sg.Text("Chosse the case")],
                       [sg.Input(key= '-INPUT-')],
                       [sg.Text(size = (40, 1), key= '-OUTPUT-')],
                       [sg.Button('OK'), sg.Button('Quit'), sg.Button('Remain')],
                       ]
                       """
# Create the window
window = sg.Window('ControlPython', layout_main, resizable=True).Finalize()

# Display and interact with the window using an Event loop
while True:
    event, values = window.read()
    # See if user wants to quit or windows was close
    if event == 'First Order':
        system_tf = GetControlTransferFunction(10, 1.5, 10)
    #if args.first_order:
        time_delay = 0
        sys_tf = system_tf._get_first_order_transfer_function()
        system_tf.evaluate_time_delays(sys_tf, time_delay)

    if event == sg.WIN_CLOSED or event == 'Quit':
        break
    if event == 'Remain':
        pass

    # Output a message to the window
    #window[ '-OUTPUT-'].update(f'Hello {values["-INPUT-"]} ! Thanks for traying PySimpleGUI')
# Finish by removing from the screen
window.close()
