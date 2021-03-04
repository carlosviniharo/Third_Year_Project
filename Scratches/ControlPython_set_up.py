import argparse as arg
# internal packages
from control_generic_class import *


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
    parser.add_argument("-g", "--dc_gain", dest="dc_gain", type=int, default=1,
                        help="DC gain K "
                        )
    parser.add_argument("-fb", "--feedback", dest="feedback",
                        help=" Feedback's Transfer function", required=False, type=int, default=None
                        )
    parser.add_argument("-d", "--damping_ratio", dest="damping_ratio", type=float, default=1,
                        help="Damping ratio of the system ζ"
                        )
    parser.add_argument("-f", "--natural_frequency", dest="natural_frequency", type=float, default=1,
                        help="Natural Frequency of the system ω"
                        )
    parser.add_argument("-den", "--denominator", dest="denominator_coeff", type=str, default='1',
                        help="row vector of denominator coefficients"
                        )
    parser.add_argument("-num", "--numerator", dest="numerator_coeff", type=str, default='1',
                        help="row vector of numerator coefficients"
                        )
    parser.add_argument("-td", "--time_delay", dest="time_delay", type=float, default=0,
                        help="Time delay in seconds"
                        )
    parser.add_argument("-id", "--internal_time_delay", dest="internal_time_delay", type=float, default=0,
                        help="Internal delay in the system in seconds"
                        )
    return parser.parse_args()


if __name__ in "__main__":
    args = get_args()
    gain = args.dc_gain
    time_constant = args.time_constant
    stop_time = args.sys_tf
    natural_frequency = args.natural_frequency
    damping_ratio = args.damping_ratio
    denominator_coeff = args.denominator_coeff
    numerator_coeff = args.numerator_coeff
    feedback_tf = args.feedback
    time_delay = args.time_delay
    internal_time_delay = args.internal_time_delay

    system_tf = GetControlTransferFunction(gain, time_constant, stop_time, natural_frequency,
                                           damping_ratio, denominator_coeff, numerator_coeff, feedback_tf,
                                           internal_time_delay)

    if args.first_order:
        sys_tf = system_tf._get_first_order_transfer_function()
        system_tf.evaluate_time_delays(sys_tf)

    elif args.second_order:
        sys_tf = system_tf._get_second_order_transfer_function()
        system_tf.evaluate_time_delays(sys_tf)

    elif args.transfer_function:
        # TODO Create an exception for non causal systems
        sys_tf = system_tf._get_generic_transfer_function()
        system_tf.evaluate_time_delays(sys_tf)
