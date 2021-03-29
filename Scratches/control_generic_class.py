from collections import defaultdict
from control import *
from matplotlib import pyplot as plt
from control.matlab import *
from control import feedback
from robustcontrol.utils import InternalDelay
from robustcontrol.utils import tf as tf_id
import numpy as np
import sys


class GetControlTransferFunction:
    """
        This Class analyzes and convert the information of the system into "s" domain transfer function. There can be
        three cases First Order, Second Order and High Order. For each cases it can be done
        manipulations such as Feedback or  Time Delay.
    """

    def __init__(self, dictionary_transfer_function, gain=1, time_constant=1, stop_time=10, natural_frequency=1,
                 damping_ratio=1, denominator_coeff=1, numerator_coeff=1, feedback_tf=None,
                 internal_delay_t=0, time_delay=0):
        """
        :param gain: int, The gain of a first oder system.
        :param time_constant: float, Time required to reach 63% of the signal(seconds).
        :param stop_time: float, Duration of the simulation.
        :param natural_frequency: float, Frequency of the system where the vibrations are higher
        :param damping_ratio: float, Ratio at which the system will decrease the vibrations.
        :param denominator_coeff: list, Coefficients of the denominator in the transfer function.
        :param numerator_coeff: list, Coefficients of the denominator in the transfer function.
        :param feedback_tf: int, Feedback of a close loop system. Can be -1 or 1.
        :param internal_delay_t:  float, quantity of time that the system experiments internally
        :param time_delay: float, float, quantity of time that  the system experiments
        """
        # Todo replace default values with None when is sensible.
        self.dc_gain = gain
        self.time_cons = time_constant
        self.stp_time = stop_time
        self.feedback_tf = feedback_tf
        self.natural_frequency = natural_frequency
        self.damping_ratio = damping_ratio
        self.denominator_coeff = [denominator_coeff]
        self.numerator_coeff = [numerator_coeff]
        self.internal_delay_t = internal_delay_t
        self.time_delay = time_delay
        self.enable_time_delay = False
        self.dictionary_arguments_gui = dictionary_transfer_function
        self.sys_tem_tf = []
        self.dictionary_single_system = defaultdict(list)


    def _get_first_order_transfer_function(self):
        """
        Digest the information of a first order system and creates their transfer function
        :return: control object
        """
        sys_tf = TransferFunction(1 * self.dc_gain, [1 * self.time_cons, 1])
        if all([self.feedback_tf is not None, self.internal_delay_t == 0]):
            sys_tf = self.get_negative_feedback(sys_tf)
        return sys_tf

    def _get_second_order_transfer_function(self):
        """
       Digest the information of a second order system and creates their transfer function
       :return: control object
       """
        sys_tf = TransferFunction(self.natural_frequency * self.natural_frequency,
                                  [1, 2 * self.natural_frequency * self.damping_ratio,
                                   self.natural_frequency * self.natural_frequency]
                                  )
        if all([self.feedback_tf is not None, self.internal_delay_t == 0]):
            sys_tf = self.get_negative_feedback(sys_tf)
        return sys_tf

    def _get_generic_transfer_function(self, general_trans_function):
        """
       Creates a transfer function for systems higher tha second order.
       :return: control object
       """
        sys_tf =general_trans_function
        if all([self.feedback_tf is not None, self.internal_delay_t == 0]):
            sys_tf = self.get_negative_feedback(sys_tf)
        return sys_tf

    def add_transfer_fuction(self, parameters, inter_delay, transfer_function= None,):

        sys_tf = TransferFunction(parameters[0], parameters[1])

        if transfer_function is not None:
            try:
                sys_tf = transfer_function.cascade(transfer_function)
            except:
                sys_tf = transfer_function*sys_tf
        return sys_tf


    def _get_internal_delay(self, sys_tf):
        """
        Creates a transfer function for systems that experiment an internal delay
        in a close loop.
        :param num: list, Coefficients of the numerator in the transfer function.
        :param den: list, Coefficients of the denominator in the transfer function.
        :return:
        """
        den = (sys_tf.den[0][0]).tolist()
        num = (sys_tf.num[0][0]).tolist()

        sys_tf = tf_id(num, den)
        e = tf_id(1, 1, deadtime=self.internal_delay_t)
        one = InternalDelay(tf_id(1, 1))
        sys_tf = InternalDelay(sys_tf)
        e = InternalDelay(e)
        if self.feedback_tf is not None:
            sys_tf = sys_tf * e / (one + sys_tf * e)
        return sys_tf

    # TODO include the option of a transfer function feedback
    def get_negative_feedback(self, sys_tf):
        """
        Calculates the transfer function of a close loop
        :param sys_tf: control object, Transfer function to transform.
        :return: control object, Result transfer function
        """
        sys_feedback = None
        if self.feedback_tf == -1:
            sys_feedback = feedback(sys_tf, sign=-1)
        elif self.feedback_tf == 1:
            sys_feedback = feedback(sys_tf, self.feedback_tf, sign=1)

        return sys_feedback

    def evaluate_time_delays(self, sys_tf):
        """
        Insert the time delay in the resultant transfer function and call the plots
        function of the script.
        :param sys_tf:  Control object or robustcontrol object, transfer function to digest.
        :return:  None
        """
        if self.internal_delay_t < 0 or self.time_delay < 0:
            # TODO Improve exit traceback
            print('Internal delay should be positive integer number in causal systems')
            sys.exit(1)
        if self.enable_time_delay:
            get_plot_internal_delay(sys_tf, self.stp_time, self.internal_delay_t,self.time_delay)
        elif self.time_delay != 0:
                get_plots(sys_tf, self.stp_time, self.time_delay)

        else:
            get_plots(sys_tf, self.stp_time)


# End class GetControlTransferFunction:


def get_plots(sys_tf, stop_time, time_delay=0):
    """
    Creates step response , bode plot, Nyquist and root locus of the system.
    :param sys_tf: control object, resultant transfer function.
    :param stop_time: int, Total time for the plot
    :param time_delay: float, quantity of time that  the system experiments
    :return: None.
    """
    plot_arguments = []
    time_limit = np.linspace(0, stop_time, 50000)
    y_out, t_s = step(sys_tf, T=time_limit)
    t = [time + time_delay for time in t_s.T]
    y_out = y_out.T.tolist()
    plot_arguments.append(t)
    plot_arguments.append(y_out)
    plot_arguments[1].insert(0, 0)
    plot_arguments[0].insert(0, 0)

    # Root locus plot for the system
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

    plt.show()


def get_plot_internal_delay(sys_tf, stop_time, internal_delay_t, time_delay):
    """
    Create the step response plot for the transfer function with internal delay.
    :param sys_tf: control object, resultant transfer function.
    :param stop_time: int, Total time for the plot
    :param internal_delay_t: float, quantity of time that  the system experiments internally.
    :return: None
    """
    time_limit = np.linspace(0, stop_time, 10000)
    y_delay = sys_tf.simulate(lambda t: [1], time_limit)
    plt.plot(time_limit, y_delay)
    plt.grid()
    plt.legend([f'Delay={internal_delay_t}'])
    plt.show()

