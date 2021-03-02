from control import *
from matplotlib import pyplot as plt
from control.matlab import *
from control import feedback
from robustcontrol.utils import InternalDelay
from robustcontrol.utils import tf as tf_id
import numpy as np
import sys
import os


class GetControlTransferFunction:
    """
        This Class contains the methods and instances for plotting
        a Control System.
    """

    def __init__(self, gain=None, time_constant=None, stop_time=None, natural_frequency=None,
                 damping_ratio=None, denominator_coeff=None, numerator_coeff=None, feedback_tf=None, internal_delay_t=None):
        self.dc_gain = gain
        self.time_cons = time_constant
        self.stp_time = stop_time
        self.feedback_tf = feedback_tf
        self.natural_frequency = float(natural_frequency)
        self.damping_ratio = float(damping_ratio)

        # Todo Check the type of the variables that coming from the GUI
        # self.denominator_coeff = [float(deno) for deno in denominator_coeff.split(',')]
        # self.numerator_coeff = [float(num) for num in numerator_coeff.split(',')]

        self.denominator_coeff = denominator_coeff
        self.numerator_coeff = numerator_coeff
        self.sys_neg_feedback = None
        self.internal_delay_t = internal_delay_t

    def _get_first_order_transfer_function(self):
        sys_tf = TransferFunction(1 * self.dc_gain, [1 * self.time_cons, 1])
        if all([self.feedback_tf is not None, self.internal_delay_t ==0]):
            sys_tf = self.get_negative_feedback(sys_tf)
        return sys_tf

    def _get_second_order_transfer_function(self):
        sys_tf = TransferFunction(self.natural_frequency * self.natural_frequency,
                                  [1, 2 * self.natural_frequency * self.damping_ratio,
                                   self.natural_frequency * self.natural_frequency]
                                  )
        if all([self.feedback_tf is not None, self.internal_delay_t ==0]):
            sys_tf = self.get_negative_feedback(sys_tf)
        return sys_tf

    def _get_generic_transfer_function(self):
        sys_tf = TransferFunction(self.numerator_coeff, self.denominator_coeff)
        if all([self.feedback_tf is not None, self.internal_delay_t ==0]):
            sys_tf = self.get_negative_feedback(sys_tf)
        return sys_tf

    def _get_internal_delay(self, num, den):
        sys_tf = tf_id(den, num)
        e = tf_id(1, 1, deadtime=self.internal_delay_t)
        one = InternalDelay(tf_id(1, 1))
        sys_tf = InternalDelay(sys_tf)
        e = InternalDelay(e)
        if self.feedback_tf is not None:
            sys_tf = sys_tf * e / (one + sys_tf * e)
        return sys_tf

    # TODO include the option of a transfer function feedback
    def get_negative_feedback(self, sys_tf):
        sys_feedback = None
        if self.feedback_tf == -1:
            sys_feedback = feedback(sys_tf, sign=-1)
        elif self.feedback_tf == 1:
            sys_feedback = feedback(sys_tf, self.feedback_tf, sign=1)

        return sys_feedback

    def evaluate_time_delays(self, sys_tf, time_delay):
        if self.internal_delay_t < 0:
            # Improve exit traceback
            print('Internal delay should be positive integer number in causal systems')
            sys.exit(1)
        elif self.internal_delay_t == 0:
            if time_delay < 0:
                print('Time delay should be positive integer number in seconds')
                sys.exit(1)
            elif time_delay == 0:
                get_plots(sys_tf, self.stp_time)
            else:
                get_plots(sys_tf, self.stp_time, time_delay)
        else:
            den = (sys_tf.den[0][0]).tolist()
            num = (sys_tf.num[0][0]).tolist()
            sys_tf = self._get_internal_delay(den, num)
            get_plot_internal_delay(sys_tf, self.stp_time, self.internal_delay_t)
# End class GetControlTransferFunction:


def get_plots(sys_tf, stop_time, time_delay=0):
    plot_arguments = []
    time_limit = np.linspace(0, stop_time, 50000)
    #if type(sys_tf) is not list:
        #sys_tf = [sys_tf]

    # Unpack the transfer function and packing the y_out and t_s points from step signal object
    #for index_plot, in_tf_sys in enumerate(sys_tf):
    y_out, t_s = step(sys_tf, T=time_limit)
    t = [time + time_delay for time in t_s.T]
    y_out = y_out.T.tolist()
    plot_arguments.append(t)
    plot_arguments.append(y_out)
    plot_arguments[1].insert(0, 0)
    plot_arguments[0].insert(0, 0)

    # Notice that the first object in the list will be the main transfer function


    # Root lcous plot for the system
    rlocus(sys_tf)

    # Nyquist plot for the system
    plt.figure(2)
    plt.gcf().canvas.set_window_title('Nyquist plot')
    nyquist(sys_tf, logspace(-2, 2))
    plt.show(block=False)

    # Bode plot for the system
    plt.figure(3)
    plt.gcf().canvas.set_window_title('Bode Plot')
    mag, phase, om = bode(sys_tf, logspace(-2, 5), Plot=True)
    plt.show(block=False)

    # Step response of the system
    plt.figure(4)
    plt.gcf().canvas.set_window_title('Step Response')
    plt.xlabel('Time(s)')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.plot(t, y_out)
    plt.show(block=False)

    if 'PYCONTROL_TEST_EXAMPLES' not in os.environ:
        plt.show()


def get_plot_internal_delay(sys_tf, stop_time, internal_delay_t):
    time_limit = np.linspace(0, stop_time, 10000)
    y_delay = sys_tf.simulate(lambda t: [1], time_limit)
    plt.plot(time_limit, y_delay)
    plt.grid()
    plt.legend([f'Delay={internal_delay_t}'])
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


