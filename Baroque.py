"""
BAROQUE - Blueprint for Assembling Runtime Operations for Quantum Experiments

Author - Harrison Barnes, Lucas Romero
College - Rochester Institute of Technology, Kate Gleason College of Engineering
Email - hjjbarnes@gmail.com lucasr2125@gmail.com

BAROQUE provides a basic structure for researchers, scientists, and engineers to add a quantum assembly file, generate
a QISKIT circuit, fetch a specific IBMQ API backend for a device, transpiles it, and runs it. Allows room for users to
edit and tailor it to their needs
"""

# Qiskit Imports
import networkx as nx
from qiskit_aer import AerSimulator, AerProvider
from qiskit_ibm_provider import IBMProvider
import qiskit_aer
from qiskit import QuantumCircuit, Aer
from qiskit.converters import circuit_to_dag, dag_to_circuit
from qiskit.compiler import transpile
from qiskit import qasm3

import BAROQUE_Metrics
import HERR

# Python Imports
import sys
import os.path
import shutil
import json
import getopt
from pathlib import Path
from queue import Queue

# BAROQUE Imports
import BAROQUE_Metrics as Metrics
import BAROQUE_IBM_Interface as IbmInterface
from Print_Metrics import *
import BAROQUE_Common_Constants as CommConst
import BAROQUE_Herr_Wrapper as HerrWrap


class Reference:
    """
    Just to get circuits by reference.
    """

    def __init__(self, val, name=""):
        self._val = val
        self._name = name

    def get_name(self):
        return self._name

    def get(self):
        return self._val

    def set(self, val, name=""):
        self._val = val
        self._name = name

    def isEmpty(self):
        if self._val is None or self._val == "":
            return True
        return False


# References to settings to keep track of everywhere.
_input_circuit = Reference(None)
_compare_circuit = Reference(None)
_ibmq_api_key = Reference(None)
_input_file = Reference(None)
_compare_file = Reference(None)
_output_file = Reference(None)
_backend_str_input = Reference(None)
_backend_str_compare = Reference(None)
_routing_algorithm_input = Reference(None)
_routing_algorithm_compare = Reference(None)
_quantum_container_input = Reference(None)
_quantum_container_compare = Reference(None)
_backend_input = Reference(None)
_backend_compare = Reference(None)
_show_backends = Reference(False)


def main(argv):
    """
    Main function of Baroque. Made up of Initialization, IBM API Access, Circuit Creation, Transpilation
    and Simulation, and the Analysis sections.
    """
    """
    Initialization

    Start of main function. Declare and assign necessary variables.
    See if needed json file is found, if not make a new one to save preferences. Then read from it.
    Handle argv to update the metric queue and json file.
    """
    src_dir = os.path.dirname(Path(__file__))
    pref_dir = os.path.join(src_dir, 'preferences')
    if not os.path.isfile(os.path.join(pref_dir, 'user_pref.json')):
        shutil.copy(os.path.join(pref_dir, 'user_pref_template.json'), os.path.join(pref_dir, 'user_pref.json'))
    f = open(os.path.join(pref_dir, 'user_pref.json'), 'r')
    user_pref = json.load(f)
    f.close()

    # Get all default values from json
    _ibmq_api_key.set(user_pref['API_KEY'])  # REQUIRED for hardware. Check IBMQ profile settings for it.
    _input_file.set(user_pref['DEFAULT_INPUT_FILE'])
    _compare_file.set(user_pref['DEFAULT_COMPARE_FILE'])
    _output_file.set(user_pref['DEFAULT_OUTPUT_FILE'])
    _backend_str_input.set(user_pref['DEFAULT_BACKEND_INPUT'])
    _backend_str_compare.set(user_pref['DEFAULT_BACKEND_COMPARE'])
    _routing_algorithm_input.set(user_pref['DEFAULT_ROUTING_INPUT'])
    _routing_algorithm_compare.set(user_pref['DEFAULT_ROUTING_COMPARE'])

    # metric queue where each item is a tuple (function, args)
    metric_queue = Queue()

    metric_queue, user_pref = handle_argv(argv, metric_queue, user_pref)

    # Update the json file with preferences
    with open(os.path.join(pref_dir, 'user_pref.json'), 'w') as json_out:
        json.dump(user_pref, json_out)
    json_out.close()

    compare_exists = False
    if _compare_file.get() != "":
        if _backend_str_compare.get() == "":
            print("WARNING: You've specified a compare file but no compare backend. Using input backend... \n")
            _backend_str_compare.set(_backend_str_input.get())
        compare_exists = True

    # if there is no input or backend then no need to continue past show_backends
    cont_metrics = True

    if _input_file.get() == "":
        print("WARNING: No input file has been set.\n")
        cont_metrics = False
    if _backend_str_input.get() == "":
        print("WARNING: No backend has been set.\n")
        cont_metrics = False
    if _ibmq_api_key.get() == "":
        print("ERROR: Your IBMQ API Key has not been set.\n")
        return

    """
    IBM API Access Section
    Log in to IBM and obtain backend dating using BAROQUE's IbmqInterfaceContainer class
    """
    provider = IBMProvider(token=_ibmq_api_key.get())  # specifically for ibm
    aer_sim = AerSimulator()
    backend_list = [backend.name for backend in provider.backends()]
    backend_list += aer_sim.available_methods()
    backend_list += [backend.name for backend in AerProvider().backends() if not isinstance(backend, AerSimulator)]

    if _show_backends.get():
        show_available_backends(provider, aer_sim)
        _show_backends.set(False)

    if not cont_metrics:
        return

    if not no_valid_backend_check(backend_list, _backend_str_compare.get(), _backend_str_input.get()):
        show_available_backends(provider, aer_sim)
        return

    _quantum_container_input.set(IbmInterface.IbmqInterfaceContainer(provider, _backend_str_input.get()))
    if compare_exists:
        _quantum_container_compare.set(IbmInterface.IbmqInterfaceContainer(provider, _backend_str_compare.get()))

    """
    Circuit Creation Section
    
    Convert qasm files to circuits 1 and (optional) 2
    """

    # Creates QuantumCircuit from .qasm file specified by the user
    _input_circuit.set(qasm3.load(_input_file.get()), _input_file.get())

    if _compare_file.get() != "":
        _compare_circuit.set(qasm3.load(_compare_file.get()), _compare_file.get())
    else:
        _compare_circuit.set(None, "")

    # Some routing algorithms require a DAG. Generate this here
    circuit_DAG = circuit_to_dag(_input_circuit.get())

    """
    Transpile & Sim Section
    
    Transpile the circuit prior to simulating the circuit. Perform optimization, routing, decomposition, etc.
    Create a simulation object to perform metrics and evaluation
    """

    """
    # Transpile the circuit using qiskit transpile().
    if routing_algorithm == CommConst.ROUTING_HERR:  # Transpile HERR using BAROQUE wrapper
        transpiled_circuit = HerrWrap.transpileUsingHerr(circuit, quantum_container.coupling_list,
                                                         quantum_container.coupling_map,
                                                         quantum_container.cx_error_map,
                                                         quantum_container.basis_gates)
    else:  # Transpile non-Herr routing algorithms normally
        transpiled_circuit = transpile(circuit, Aer.get_backend(CommConst.AER_QASM_SIM),
                                       coupling_map=quantum_container.coupling_map,
                                       basis_gates=quantum_container.basis_gates,
                                       routing_method=routing_algorithm,
                                       layout_method=CommConst.LAYOUT_TRIVIAL)
    """

    # TODO Make a runtime protocol for every backend
    # Retrieve the backend simulator information from Aer

    _backend_input.set(_quantum_container_input.get().backend)
    if compare_exists:
        _backend_compare.set(_quantum_container_compare.get().backend)

    """
    Analysis Section
    
    Call run_metrics() to run all metric tests in queue
    """

    results = run_metrics(metric_queue)

    """
    Output section
    
    Output to a file or to the console
    """
    out_string = ""

    # Add header information for the test's output data
    out_string += ("Test Files: {input} {compare}\n".format(input=_input_file.get(), compare=_compare_file.get()))
    out_string += ("Device: {backend}\n".format(backend=_backend_str_input.get()))
    out_string += results

    if _output_file.get() != "":
        try:
            with open(_output_file.get(), "w") as out_stream:
                out_stream.write(out_string)
            out_stream.close()
        except OSError:
            print("Error opening specified output file. Printing to console...")
            print(out_string)
    else:
        print(out_string)


def no_valid_backend_check(available, backend1, backend2):
    """
    Check if backend1 or backend2 are in available backends, if not then print an error message and return false.
    :param available: List of IBMQ backend names as well as AerSimulator method names.
    :param backend1: First backend name
    :param backend2: Second backend name
    :return: False if either backend1 or backend2 aren't available.
    """
    one_is_available = False if backend1 is not None and backend1 != "" else True
    two_is_available = False if backend2 is not None and backend2 != "" else True
    all_available = []
    for name in available:
        all_available += [name]
        if backend1 == name:
            one_is_available = True
        if backend2 == name:
            two_is_available = True
    if not (one_is_available and two_is_available):
        print("ERROR: One or both of your selected backends are not available on the active IBMQ API token.\n")
        return False
    return True


def show_available_backends(provider, aer_sim):
    """
    Print a list of available backends to use.
    :param provider: IBMProvider enabled from an APIKey
    :param aer_sim: AerSimulator to get methods from.
    """
    print("Available IBMQ backends:")
    ibmq_backends = provider.backends()
    for backend in ibmq_backends:
        print("\t{backend}".format(backend=backend.name))
    print("Available AerSimulator Methods:")
    aer_backends = aer_sim.available_methods()
    for method in aer_backends:
        print("\t{backend}".format(backend=method))
    print("Available Legacy Simulator Backends:")
    for backend in Aer.backends():
        if not isinstance(backend, AerSimulator):
            print("\t{legacy}".format(legacy=backend.name))
    print()


def show_defaults(user_pref):
    """
    Prints out the json defaults. Specific to this json.
    """
    print("DEFAULTS:")
    print("\tInput File:\t" + user_pref['DEFAULT_INPUT_FILE'])
    print("\tCompare File:\t" + user_pref['DEFAULT_COMPARE_FILE'])
    print("\tOutput File:\t" + user_pref['DEFAULT_OUTPUT_FILE'])
    print("\tInput Backend:\t" + user_pref['DEFAULT_BACKEND_INPUT'])
    print("\tCompare Backend:\t" + user_pref['DEFAULT_BACKEND_COMPARE'])
    print("\tInput Routing:\t" + user_pref['DEFAULT_ROUTING_INPUT'])
    print("\tCompare Routing:\t" + user_pref['DEFAULT_ROUTING_COMPARE'])


def handle_argv(argv, metric_queue, user_pref):
    """
    Take in the arguments, update the metrics queue and user preferences as necessary.
    :param argv: The arguments inputted by the user, starting after the program title
    :param metric_queue: Queue of metrics -> (printMetricFunctionName, (args for that func))
    :param user_pref: Loaded in json struct we can update.
    :return: The updated metric_queue and updated user preferences.
    """

    try:
        opts, trailing_args = getopt.getopt(argv, "i:c:o:b:r:h",
                                            ["input_file=",
                                             "output_file=",
                                             "compare_file=",
                                             "backend=",
                                             "backend_input=",
                                             "backend_compare=",
                                             "routing=",
                                             "routing_input=",
                                             "routing_compare=",
                                             "set_API_key=",
                                             "set_default_input_file=",
                                             "set_default_output_file=",
                                             "set_default_backend_input=",
                                             "set_default_backend_compare=",
                                             "set_default_routing_input=",
                                             "set_default_routing_compare=",
                                             "reset_all",
                                             "show_defaults",
                                             "metricCountGate=",
                                             "metricRatioGate=",
                                             "metricDiffGate=",
                                             "metricDiffDepth",
                                             "metricRatioDepth",
                                             "metricCircuitDepth",
                                             # "metricAccuracy",
                                             # "metricStatevectorNorm",
                                             # "metricExpectedStatevector",
                                             # "metricRoutingTime",
                                             # "metricTranspilationTime",
                                             "metricRaw",
                                             "available_backends",
                                             "help"])
    except getopt.GetoptError:
        print("Error reading in getopt arguments.")
        return

    for opt, arg in opts:
        if opt in ['-i', '--input_file']:
            _input_file.set(arg)
        if opt in ['-c', '--compare_file']:
            _compare_file.set(arg)
        if opt in ['-o', '--output_file']:
            _output_file.set(arg)
        if opt in ['-b', '--backend_input', '--backend']:
            _backend_str_input.set(arg)
        if opt in ['--backend_compare']:
            _backend_str_compare.set(arg)
        if opt in ['-r', '--routing_input', '--routing']:
            _routing_algorithm_input.set(arg)
        if opt in ['--routing_compare']:
            _routing_algorithm_compare.set(arg)
        if opt in ['-h', '--help']:
            usage()
        if opt == "--set_API_key":
            user_pref['API_KEY'] = arg
        if opt == "--set_default_input_file":
            user_pref['DEFAULT_INPUT_FILE'] = arg
        if opt == "--set_default_compare_file":
            user_pref['DEFAULT_COMPARE_FILE'] = arg
        if opt == "--set_default_output_file":
            user_pref['DEFAULT_OUTPUT_FILE'] = arg
        if opt == "--set_default_backend_input":
            user_pref['DEFAULT_BACKEND_INPUT'] = arg
        if opt == "--set_default_backend_compare":
            user_pref['DEFAULT_BACKEND_COMPARE'] = arg
        if opt == "--set_default_routing_input":
            user_pref['DEFAULT_ROUTING_INPUT'] = arg
        if opt == "--set_default_routing_compare":
            user_pref['DEFAULT_ROUTING_COMPARE'] = arg
        if opt == "--reset_all":
            user_pref['DEFAULT_INPUT_FILE'] = ""
            user_pref['DEFAULT_OUTPUT_FILE'] = ""
            user_pref['DEFAULT_BACKEND_INPUT'] = ""
            user_pref['DEFAULT_BACKEND_COMPARE'] = ""
            user_pref['DEFAULT_ROUTING_INPUT'] = ""
            user_pref['DEFAULT_ROUTING_COMPARE'] = ""
        if opt == "--show_defaults":
            show_defaults(user_pref)
        if opt == "--metricCountGate":
            metric_queue.put((printMetricCountGate, (_input_circuit, _compare_circuit, arg)))
        if opt == "--metricDiffGate":
            metric_queue.put((printMetricDiffGate, (_input_circuit, _compare_circuit, arg)))
        if opt == "--metricRatioGate":
            metric_queue.put((printMetricRatioGate, (_input_circuit, _compare_circuit, arg)))
        if opt == "--metricDiffDepth":
            metric_queue.put((printMetricDiffDepth, (_input_circuit, _compare_circuit)))
        if opt == "--metricCircuitDepth":
            metric_queue.put((printMetricCircuitDepth, (_input_circuit, _compare_circuit)))
        if opt == "--metricRatioDepth":
            metric_queue.put((printMetricRatioDepth, (_input_circuit, _compare_circuit)))
        if opt == "--metricRaw":
            metric_queue.put((printMetricRaw, (_quantum_container_input, _input_circuit, _backend_input)))
            metric_queue.put((printMetricRaw, (_quantum_container_compare, _compare_circuit, _backend_compare)))
        if opt == "--available_backends":
            _show_backends.set(True)
    return metric_queue, user_pref


def run_metrics(metric_queue):
    """
    Run every metric in metric queue.
    :param metric_queue: Queue of tuple (function call, (args))
    :return: string of all output
    """
    out = ""
    while not metric_queue.empty():
        current_metric, args = metric_queue.get()
        out += current_metric(*args)
    return out


def checkRequiredOptions():
    """
    Function - checkRequiredOptions
    Inputs:
        put required inputs here if using getopt

    Outputs: True if all valid, False otherwise

    checkRequiredOptions performs validation on the getopt arguments to ensure that they are:
        1. present
        2. correct format
    Note that not all issues are checked here, only getopt-input related ones

    If getopt is not used, this function can be removed
    """
    return True


def usage():
    """
    Prints the usage string for the BAROQUE getopt terminal format.
    """
    src_dir = os.path.dirname(Path(__file__))
    with open(os.path.join(src_dir, 'help.txt'), 'r') as f:
        file_content = f.read()
        print(file_content)


def exitBAROQUE(cause_code):
    """
    Function - exitBAROQUE
    Inputs: cause_code - code denoting the cause of the exit condition
    Outputs: none, exits program

    Prints the relevant error message and exits with the cause_code
    If no exit codes are needed, this function can be removed
    """
    print("Sample function. Put exit codes here if wanted...\n")
    print("Exiting BAROQUE code...\n")
    sys.exit(cause_code)


if __name__ == "__main__":
    print(sys.argv)
    main(sys.argv[1:])
