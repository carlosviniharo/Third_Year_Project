import unittest
from control_generic_class import *
from control import *
from robustcontrol import InternalDelay
import controlpython_window_gui as cp_gui
import PySimpleGUI as sg
import warnings
import logger_settings as log_set


class MyTestCase(unittest.TestCase):
    @ classmethod
    def setUpClass(cls):
        cls.test_graph, cls.examples = get_test_graph()
        cls.my_logger = log_set.get_logger('controlpython')

    def setUp(cls):
        cls.control_python = GetControlTransferFunction()
        cls.test_tf = tf([1], [1, 2, 3])
        cls.parameters_transfer = ([1], [1, 2, 3])
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
        warnings.filterwarnings("ignore", category=UserWarning)

    def tearDown(cls):
        cls.control_python = None

    @classmethod
    def tearDownClass(cls):
        cls.test_graph = None

    def test_get_internal_delay(self):
        internal_transfer_function = self.control_python.get_internal_delay(self.test_tf)
        self.control_python.feedback_tf = -1
        internal_transfer_function_feedb = self.control_python.get_internal_delay(self.test_tf)
        self.assertIsInstance(internal_transfer_function, InternalDelay.InternalDelay)
        self.assertNotEqual(internal_transfer_function, internal_transfer_function_feedb)
        self.my_logger.debug(f"test_get_internal_delay: PASS")

    def test_add_transfer_function(self):
        test_tf_in = self.control_python.get_internal_delay(self.test_tf)
        result_control = self.control_python.add_transfer_fuction(self.parameters_transfer, self.test_tf)
        result_control_param = self.control_python.add_transfer_fuction(self.parameters_transfer)
        result_internal = self.control_python.add_transfer_fuction(self.parameters_transfer, test_tf_in)
        self.assertIsInstance(result_control, xferfcn.TransferFunction)
        self.assertIsInstance(result_control_param, xferfcn.TransferFunction)
        self.assertIsInstance(result_internal, InternalDelay.InternalDelay)
        self.my_logger.debug("test_add_transfer_function: PASS")

    def test_get_negative_feedback(self):
        self.control_python.feedback_tf = -1
        n_feedback_tf = self.control_python.get_feedback(self.test_tf)
        self.control_python.feedback_tf = 1
        p_feedback_tf = self.control_python.get_feedback(self.test_tf)
        self.assertNotEqual(n_feedback_tf, p_feedback_tf)
        self.assertIsInstance(n_feedback_tf, xferfcn.TransferFunction)
        self.my_logger.debug("test_get_negative_feedback: PASS")

    def test_get_time_delay_pade(self):
        # The order of the pade approximant is 3 but in the simulator the number is 30
        self.control_python.internal_delay_t = 10
        pade_test = self.control_python.get_time_delay_pade(self.test_tf, 3)
        pade_calculated = tf([-1, 1.2, -0.6, 0.12],
                             [1, 3.2, 6, 4.92, 2.04, 0.36])
        self.control_python.internal_delay_t = 0.1
        pade_test_2 = self.control_python.get_time_delay_pade(self.test_tf, 3)
        pade_calculated_2 = tf([-1, 120, -6000, 120000],
                               [1, 1.2200e+02, 6.2430e+03, 1.3236e+05, 2.5800e+05, 3.6000e+05])
        self.assertIsNone(np.testing.assert_almost_equal(
            pade_test.den, pade_calculated.den))
        self.assertIsNone(np.testing.assert_almost_equal(
            pade_test.num, pade_calculated.num))
        self.control_python.internal_delay_t = 0.1

        self.assertIsNone(np.testing.assert_almost_equal(
            pade_test_2.den, pade_calculated_2.den))
        self.assertIsNone(np.testing.assert_almost_equal(
            pade_test_2.num, pade_calculated_2.num))
        self.my_logger.debug("test_get_time_delay_pade: PASS")

    def test_evaluate_time_delays_plane(self):
        # Case : only Transfer Function
        test_tf_no_time_delay = self.control_python.evaluate_time_delays(self.test_tf)
        figs = list(map(test_tf_no_time_delay.figure, test_tf_no_time_delay.get_fignums()))
        self.assertEqual(4, len(figs))
        test_tf_no_time_delay.close("all")
        self.my_logger.debug("test_evaluate_time_delays_plane: PASS")

    def test_evaluate_time_delays_case_1(self):
        # Case : Transfer Function and Feedback
        self.control_python.feedback_tf = -1
        test_tf_time_delay = self.control_python.evaluate_time_delays(self.test_tf)
        figs = list(map(test_tf_time_delay.figure, test_tf_time_delay.get_fignums()))
        self.assertEqual(4, len(figs))
        test_tf_time_delay.close("all")
        self.my_logger.debug("test_evaluate_time_delays_case_1: PASS")

    def test_evaluate_time_delays_case_2(self):
        # Case : Transfer Function and Time Delay
        self.control_python.time_delay = 5
        test_tf_time_delay = self.control_python.evaluate_time_delays(self.test_tf)
        figs = list(map(test_tf_time_delay.figure, test_tf_time_delay.get_fignums()))
        self.assertEqual(4, len(figs))
        test_tf_time_delay.close("all")
        self.my_logger.debug("test_evaluate_time_delays_case_2: PASS")

    def test_evaluate_time_delays_case_3(self):
        # Case : Transfer Function, Time Delay and Feedback
        self.control_python.feedback_tf = -1
        self.control_python.internal_delay_t = 5
        test_tf_time_delay = self.control_python.evaluate_time_delays(self.test_tf)
        figs = list(map(test_tf_time_delay.figure, test_tf_time_delay.get_fignums()))
        self.assertEqual(1, len(figs))
        test_tf_time_delay.close("all")
        self.my_logger.debug("test_evaluate_time_delays_case_3: PASS")

    def test_evaluate_time_delays_case_4(self):
        # Case : Transfer Function, Feedback and Time Delay.
        self.control_python.feedback_tf = -1
        self.control_python.time_delay = 5
        test_tf_time_delay = self.control_python.evaluate_time_delays(self.test_tf)
        figs = list(map(test_tf_time_delay.figure, test_tf_time_delay.get_fignums()))
        self.assertEqual(4, len(figs))
        test_tf_time_delay.close("all")
        self.my_logger.debug("test_evaluate_time_delays_case_4: PASS")

    def test_evaluate_time_delays_case_5(self):
        # Case : Transfer Function,Time Delay, Feedback and Time Delay.
        self.control_python.feedback_tf = -1
        self.control_python.time_delay = 5
        self.control_python.internal_delay_t = 5
        test_tf_time_delay = self.control_python.evaluate_time_delays(self.test_tf)
        figs = list(map(test_tf_time_delay.figure, test_tf_time_delay.get_fignums()))
        self.assertEqual(1, len(figs))
        test_tf_time_delay.close("all")
        self.my_logger.debug("test_evaluate_time_delays_case_5: PASS")

    def test_evaluate_time_delays_case_6(self):
        # Case : Transfer Function,Time Delay, Feedback, Time Delay and ....
        self.control_python.feedback_tf = -1
        self.control_python.enable_time_delay = True
        self.control_python.internal_delay_t = 5
        self.test_tf = self.control_python.get_internal_delay(self.test_tf)
        test_tf_time_delay = self.control_python.evaluate_time_delays(self.test_tf)
        figs = list(map(test_tf_time_delay.figure, test_tf_time_delay.get_fignums()))
        self.assertEqual(1, len(figs))
        test_tf_time_delay.close("all")
        self.my_logger.debug("test_evaluate_time_delays_case_6: PASS")

    def test_get_plots(self):
        self.test_tf_in = self.control_python.get_internal_delay(self.test_tf)
        self.assertRaises(TypeError, self.control_python.get_plots, self.test_tf_in)
        self.my_logger.debug("test_get_plots: PASS")

    def test_get_plot_internal_delay(self):
        self.assertRaises(AttributeError, self.control_python.get_plot_internal_delay, self.test_tf)
        self.my_logger.debug("test_get_plot_internal_delay: PASS")

    def test_get_order_op(self):
        test_list_order = {'test_one': [[1], [123, 167, 87], [123, 167, 87, 65], [123, 167, 87],
                                        [123, 167]],
                           'test_two': [[1], [12, 578], [12, 578, 384, 867, 145], [578, 384, 867, 145],
                                        [384, 867, 145], [867, 145]],
                           'test_tree': [[2, 4], [2, 4, 589, 908, 768, 89], [4, 589, 908, 768, 89],
                                         [908, 768, 89]]
                           }
        order_list = [[123, 167, 87, 65], [12, 578, 384, 867, 145], [2, 4, 589, 908, 768, 89]]
        dictionary_operations = ({87: ('Transfer Function', ([1.0], [1.0, 5.0])), 65: ('Feedback', '-1'),
                                  123: ('Time Delay', '5'), 167: ('Plot', '4')},
                                 {12: ('Time Delay', '4'), 145: ('Transfer Function', ([1.0], [1.0])),
                                  578: ('Feedback', '-1'), 384: ('Time Delay', '5'), 867: ('Plot', '45')},
                                 {2: ('Transfer Function', ([1.0], [1.0, 5.0])), 4: ('Feedback', '-1'),
                                  89: ('Time Delay', '5'), 589: ('Plot', '4'),
                                  768: ('Transfer Function', ([1.0], [1.0])), 908: ('Feedback', '-1')}
                                 )
        for index, order_test in enumerate(test_list_order.values()):
            ordered_dic_test = cp_gui.get_order_op(dictionary_operations[index], order_test)
            self.assertEqual(list(ordered_dic_test.keys()), order_list[index])
        self.my_logger.debug("test_get_order_op: PASS")

    def test_get_order_graphs(self):
        order_test = cp_gui.get_order_graphs(self.test_graph)
        self.assertIn(self.examples, order_test)
        self.my_logger.debug("test_get_order_graphs: PASS")


def get_test_graph():
    layout = [[sg.Graph(canvas_size=(400, 400),
                        graph_bottom_left=(0, 0),
                        graph_top_right=(400, 400),
                        background_color='white',
                        key='graph')]]

    window = sg.Window('Graph test', layout, auto_close=True,
                       finalize=True)
    graph = window['graph']         # type: sg.Graph
    circle = graph.draw_circle((200, 200), 25, fill_color='Blue', line_color='')
    point = graph.draw_point((226, 200), 10, color='red')
    oval = graph.draw_oval((100, 225), (175, 175), fill_color='purple', line_color='purple')
    rectangle = graph.draw_rectangle((10, 250), (100, 100), line_color='purple')
    line = graph.draw_line((236, 200), (350, 50))
    poly = graph.draw_polygon([(300, 50), (300, 0), (350, 250), (400, 250)], fill_color='green')
    return graph, [rectangle, oval, circle, point, line, poly]


if __name__ == '__main__':
    unittest.main()
