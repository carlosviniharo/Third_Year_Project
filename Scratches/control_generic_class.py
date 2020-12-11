#from control import *
from matplotlib import pyplot as plt
from control.matlab import *
from control import feedback
import argparse as arg
import os


class GetControlGraphs:
    """
        This Class contains the methods and instances for the plotting of
        a Control System
    """
    def __init__(self, gain, time_constant, stop_time, feedback_tf= None):
        self.dc_gain = gain
        self.time_cons = time_constant
        self.stp_time = stop_time
        self.feedback_tf = feedback_tf
       # time in four decimals

#gain = int(input("Enter gain\n"))
#time_constant = float(input("Enter time constan\n"))
#stop_time = int(input("Enter the stop time\n"))
#unit_step = tf(1,[1])

    def get_transfer_function(self):
        sys = TransferFunction(1*self.dc_gain, [1*self.time_cons,1])
        if self.feedback_tf is None:
            sys_feedback = sys
        elif self.feedback_tf == 1:
            sys_feedback = feedback(sys, sign=-1)
        else:
            sys_feedback = feedback(sys, self.feedback_tf, sign= -1)

        return sys_feedback


def get_plots(sys, stop_time):
    plot_arguments = []
    time_limit = [(steps + 1) / 100000 for steps in range(0, int(stop_time * 100000))]
    if type(sys) is not list:
        sys = [sys]

    # Unpack the transfer function and packing the y_out and t_s points from step signal object
    for index_plot, in_tf_sys in enumerate(sys):
        y_out, t_s = step(in_tf_sys, T=time_limit)
        plot_arguments.append(t_s.T)
        plot_arguments.append(y_out.T)


    # Notice that the first object in the list will be the main tramnfer function
    # Bode plot for the system
    plt.figure(index_plot+2)
    plt.title('Bode Plot')
    mag, phase, om = bode(sys[0], logspace(-2, 5), Plot=True)
    plt.show(block=False)

    # Nyquist plot for the system
    plt.figure(index_plot+3)
    plt.title('Nyquist plot')
    nyquist(sys[0], logspace(-2, 2))
    plt.show(block=False)

    # Root lcous plot for the system
    rlocus(sys[0])

    # Step response of the system
    plt.figure(1)
    plt.title('Step Response')
    plt.plot(*plot_arguments)
    plt.show(block=False)

    if 'PYCONTROL_TEST_EXAMPLES' not in os.environ:
        plt.show()


def get_time_delay(time_delay, sys):
    """
    This function  gives an approximation of a time delay in a transfer function
    using pade approximant
    :param time_delay: int time of the delay
    :param sys: obt control class (array) transfer function to apply the delay
    :return:
    """
    delay = pade(time_delay, 15)
    delay_tf = tf(delay[0], delay[1])
    final = sys * delay_tf
    return final


#plt.figure(2)
#x_out, t_u_s = step(unit_step)
#plt.plot(t_u_s.T, x_out.T)
