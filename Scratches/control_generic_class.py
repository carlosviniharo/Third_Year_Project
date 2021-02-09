# from control import *
from matplotlib import pyplot as plt
from control.matlab import *
from control import feedback
import numpy as np
import os


class GetControlTransferFunction:
    """
        This Class contains the methods and instances for plotting of
        a Control System.
    """

    def __init__(self, gain=None, time_constant=None, stop_time=None, natural_frequency=None,
                 damping_ratio=None, denominator_coeff=None, numerator_coeff=None, feedback_tf=None):
        self.dc_gain = gain
        self.time_cons = time_constant
        self.stp_time = stop_time
        self.feedback_tf = feedback_tf
        self.natural_frequency = float(natural_frequency)
        self.damping_ratio = float(damping_ratio)
        self.denominator_coeff = [float(deno) for deno in denominator_coeff if deno not in ","]
        self.numerator_coeff = [float(num) for num in numerator_coeff if num not in ","]
        self.sys_neg_feedback = None

    def _get_first_order_transfer_function(self):
        sys_tf = TransferFunction(1 * self.dc_gain, [1 * self.time_cons, 1])
        if self.feedback_tf is not None:
            self.sys_neg_feedback = self.get_negative_feedback(sys_tf)
        return sys_tf

    def _get_second_order_transfer_function(self):
        sys_tf = TransferFunction(self.natural_frequency * self.natural_frequency,
                                  [1, 2 * self.natural_frequency * self.damping_ratio,
                                   self.natural_frequency * self.natural_frequency]
                                  )
        if self.feedback_tf is not None:
            self.sys_neg_feedback = self.get_negative_feedback(sys_tf)
        return sys_tf

    def _get_generic_transfer_function(self):
        sys_tf = TransferFunction(self.numerator_coeff, self.denominator_coeff)
        if self.feedback_tf is not None:
            self.sys_neg_feedback = self.get_negative_feedback(sys_tf)
        return sys_tf

    # TODO include the option of a transfer function feedback
    def get_negative_feedback(self, sys_tf):
        if self.feedback_tf == -1:
            sys_feedback = feedback(sys_tf, sign=-1)
        elif self.feedback_tf == 1:
            sys_feedback = feedback(sys_tf, self.feedback_tf, sign=1)

        return sys_feedback


def get_plots(sys, stop_time, time_delay=0):
    plot_arguments = []
    time_limit = np.linspace(0, stop_time, 50000)
    if type(sys) is not list:
        sys = [sys]

    # Unpack the transfer function and packing the y_out and t_s points from step signal object
    for index_plot, in_tf_sys in enumerate(sys):
        y_out, t_s = step(in_tf_sys, T=time_limit)
        t = [time + time_delay for time in t_s.T]
        y_out = y_out.T.tolist()
        plot_arguments.append(t)
        plot_arguments.append(y_out)
    plot_arguments[1].insert(0, 0)
    plot_arguments[0].insert(0, 0)

    # Notice that the first object in the list will be the main transfer function
    # Bode plot for the system
    plt.figure(index_plot + 2)
    plt.title('Bode Plot')
    mag, phase, om = bode(sys[0], logspace(-2, 5), Plot=True)
    plt.show(block=False)

    # Nyquist plot for the system
    plt.figure(index_plot + 3)
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


def get_time_delay_pade(time_delay, sys):
    """
    This function  gives an approximation of a time delay in a transfer function
    using pade approximant
    :param time_delay: int time of the delay
    :param sys: obj control class (array) transfer function to apply the delay
    :return:
    """
    delay = pade(time_delay, 15)
    delay_tf = tf(delay[0], delay[1])
    final = sys * delay_tf
    return final


def evaluate_time_delay(sys, stop_time, time_delay):
    if time_delay < 0:
        sys.exit('Time delay should be positive integer number in seconds')
    elif time_delay == 0:
        get_plots(sys, stop_time)
    else:
        get_plots(sys, stop_time, time_delay)

