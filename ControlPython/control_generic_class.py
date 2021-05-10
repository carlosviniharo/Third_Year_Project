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

    def __init__(self, stop_time=10, denominator_coeff=1, numerator_coeff=1,
                 feedback_tf=None, internal_delay_t=0, time_delay=0):

        # Todo replace default values with None when is sensible.
        self.stp_time = stop_time
        self.feedback_tf = feedback_tf
        self.denominator_coeff = [denominator_coeff]
        self.numerator_coeff = [numerator_coeff]
        self.internal_delay_t = internal_delay_t
        self.time_delay = time_delay
        self.enable_time_delay = False
        self.sys_tem_tf = []


    def add_transfer_fuction(self, parameters, transfer_function= None,):

        if len(parameters[0]) > len(parameters[1]):
            raise ValueError("The model can not be simulated as it is not a causal system"
                             "because the  denominator's order %s is lower "
                             "than the numerator's %s"
                             %(parameters[1], parameters[0]))

        sys_tf = TransferFunction(parameters[0], parameters[1])

        if transfer_function is not None:
            if type(transfer_function) == xferfcn.TransferFunction:
                sys_tf = transfer_function*sys_tf

            else:
                sys_tf = self.get_internal_delay(sys_tf)
                sys_tf = transfer_function.cascade(sys_tf)
        return sys_tf


    def get_internal_delay(self, sys_tf):
        """
        Creates a transfer function for systems that experiment an internal delay
        in a close loop.
   .   :param sys_tf: control object, Transfer function to transform.
        :return:
        """
        if type(sys_tf) == xferfcn.TransferFunction:
            den = (sys_tf.den[0][0]).tolist()
            num = (sys_tf.num[0][0]).tolist()
            sys_tf = tf_id(num, den)
            sys_tf = InternalDelay(sys_tf)

        e = tf_id(1, 1, deadtime=self.internal_delay_t)
        one = InternalDelay(tf_id(1, 1))
        e = InternalDelay(e)
        if self.feedback_tf is not None:
            sys_tf = sys_tf * e / (one + sys_tf * e)
            self.feedback_tf = None
        return sys_tf

    # TODO include the option of a transfer function feedback
    def get_feedback(self, sys_tf):
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
        self.feedback_tf = None

        return sys_feedback

    def get_time_delay_pade(self, sys, order=30):
        """
        This function  gives an approximation of a time delay in a transfer function
        using pade approximant
        :param sys: obj control class (array) transfer function to apply the delay
        :return:
        """
        delay = pade(self.internal_delay_t, order)
        delay_tf = tf(delay[0], delay[1])
        final = sys * delay_tf
        return final

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
            return self.get_plot_internal_delay(sys_tf)

        else:
            return self.get_plots(sys_tf)

    def get_plots(self, sys_tf):
        """
        Creates step response , bode plot, Nyquist and root locus of the system.
        :param sys_tf: control object, resultant transfer function.
        :return: None.
        """

        time_limit = np.linspace(0, self.stp_time, 50000)
        try:
            y_out, t_s = step(sys_tf, T=time_limit)
        except Exception:
            print(f'The transfer function {sys_tf} should be an object of Control Class')
            raise TypeError

        y_out = y_out.T.tolist()
        if self.time_delay:
            t_s = [time + self.time_delay for time in t_s.T]
        if self.internal_delay_t == 0:

            # Root locus plot for the system
            plt.figure('Root Locus')
            rlocus(sys_tf)

            # Nyquist plot for the system
            plt.figure('Nyquist plot')
            #plt.gcf().canvas.set_window_title('Nyquist plot')
            nyquist(sys_tf)
            plt.show(block=False)

            # Bode plot for the system
            plt.figure('Bode Plot')
            mag, phase, om = bode(sys_tf, Plot=True)
            plt.show(block=False)

        # Step response of the system
        plt.figure('Step Response')
        plt.xlabel('Time(s)')
        plt.ylabel('Amplitude')
        plt.grid(True)
        plt.plot(t_s, y_out)
        plt.show(block=False)
        return plt


    def get_plot_internal_delay(self, sys_tf):
        """
        Create the step response plot for the transfer function with internal delay.
        :param sys_tf: control object, resultant transfer function..
        :return: None
        """
        time_limit = np.linspace(0, self.stp_time , 10000)
        y_delay = sys_tf.simulate(lambda t: [1], time_limit)
        if self.time_delay:
            time_limit = [time+self.time_delay for time in time_limit]
        plt.figure('Step Response')
        plt.plot(time_limit , y_delay)
        plt.grid()
        plt.legend([f'Delay={self.internal_delay_t}'])
        return plt
# End class GetControlTransferFunction:

