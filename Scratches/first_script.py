#from control import *
# External packages
from matplotlib import pyplot as plt
from control.matlab import *
import argparse as arg
import os
# internal packages
from control_generic_class import GetControlGraphs as ConGen
import control_generic_class


def get_args():
    # Option parser command line.
    parser = arg.ArgumentParser(description='Control System Examples')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-fo", "--first_order", help="First Order, Second Order, First Order Parallel",
                       action="store_true"
                       )
    group.add_argument("-so", "--second_order", help="First Order, Second Order, First Order Parallel",
                       action="store_true"
                       )
    group.add_argument("-p", "--parallel", help="First Order, Second Order, First Order Parallel",
                       action="store_true"
                       )
    group.add_argument("-tf", "--transfer_function",
                       help="Type directly the Transfer Function of the system.",
                       action="store_true"
                       )
    parser.add_argument("-st", "--stop_time", dest="sys_tf",
                        help="Time to stop the samples", type=float, required=True
                        )
    parser.add_argument("-tc", "--time_constant", dest="time_constant",
                        help="Time constant of the Fist Order System ", type=float, default=1
                        )
    parser.add_argument("-g", "--dc_gain", dest="dc_gain", type=int, default= 1,
                        help="DC gain K "
                        )
    parser.add_argument("-fb", "--feedback", dest="fb_transfer_function",
                        help=" Feedback's Transfer function", required=False, default=None
                        )
    parser.add_argument("-d", "--damping_ratio", dest="damping_ratio", type=float, default= 1,
                        help="Damping ratio of the system ζ"
                        )
    parser.add_argument("-f", "--natural_frequency", dest="natural_frequency", type=float, default= 1,
                        help="Natural Frequency of the system ω"
                        )
    parser.add_argument("-den", "--denominator", dest="tf_denominator", type=list, default=[1],
                        help="row vector of denominator coefficients"
                        )
    parser.add_argument("-num", "--numerator", dest="tf_numerator", type=list, default=[1],
                        help="row vector of numerator coefficients"
                        )
    parser.add_argument("-td", "--time_delay", dest="time_delay", type=float, default= 0,
                        help="Time delay in seconds"
                        )
    return parser.parse_args()


if __name__ in "__main__":
    args = get_args()
    stop_time = args.sys_tf
    time_delay = args.time_delay
    #TODO Include the option of a transfer function for the negative feedback
    if args.first_order:
        feedback = args.fb_transfer_function
        # Systems with negative feedback
        if feedback is not None:
            sys_fo = ConGen(args.dc_gain, args.time_constant, stop_time, int(feedback))
            if time_delay == 0:
                tf_sys = sys_fo.get_transfer_function()
                control_generic_class.get_plots(tf_sys, stop_time)
            elif time_delay < 0:
                sys.exit('Time delay should be positive integer number in seconds')
            else:
                tf_sys = sys_fo.get_transfer_function()
                tf_t_delay = control_generic_class.get_time_delay(time_delay, tf_sys)
                control_generic_class.get_plots([tf_t_delay, tf_sys], stop_time)
        else:
            sys_fo = ConGen(args.dc_gain, args.time_constant, stop_time)
            if time_delay == 0:
                tf_sys = sys_fo.get_transfer_function()
                control_generic_class.get_plots(tf_sys, stop_time)
            elif time_delay < 0:
                sys.exit('Time delay should be positive integer number in seconds')
            else:
                tf_sys = sys_fo.get_transfer_function()
                tf_t_delay = control_generic_class.get_time_delay(time_delay, tf_sys)
                control_generic_class.get_plots([tf_t_delay, tf_sys], stop_time)

    elif args.second_order:
        natural_freq = float(args.natural_frequency)
        damping_ratio = float(args.damping_ratio)
        sys_tf = TransferFunction(natural_freq * natural_freq,
                               [1, 2 * natural_freq * damping_ratio,natural_freq * natural_freq]
        )
        if time_delay < 0:
            sys.exit('Time delay should be positive integer number in seconds')
        elif time_delay != 0:
            tf_t_delay = control_generic_class.get_time_delay(time_delay, sys_tf)
            control_generic_class.get_plots([tf_t_delay, sys_tf], stop_time)
        else:
            control_generic_class.get_plots(sys_tf, stop_time)

    elif args.transfer_function:
        denominatro_coeff = [float(deno) for deno in args.tf_denominator if deno not in ","]
        numerator_coeff = [float(num) for num in args.tf_numerator if num not in ","]
        sys_tf = TransferFunction(numerator_coeff, denominatro_coeff)
        # TODO Create a exception for non causal systems
        """try:
            control_generic_class.get_plots(sys, stop_time)
        except ValueError as exc:
            raise RuntimeError("Cannot simulate the step signal of non-causal systems") from exc"""

        if time_delay < 0:
            sys.exit('Time delay should be positive integer number in seconds')
        elif time_delay != 0:
            tf_t_delay = control_generic_class.get_time_delay(time_delay, sys_tf)
            control_generic_class.get_plots([tf_t_delay, sys_tf], stop_time)
        else:
            control_generic_class.get_plots(sys_tf, stop_time)

