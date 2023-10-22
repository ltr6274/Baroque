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
from qiskit_ibm_provider import IBMProvider
from qiskit import QuantumCircuit, Aer
from qiskit.converters import circuit_to_dag, dag_to_circuit
from qiskit.compiler import transpile
from qiskit import qasm3
import HERR

# Python Imports
import sys
import os.path
import shutil
import json
import getopt
from pathlib import Path

# BAROQUE Imports
import BAROQUE_Metrics as Metrics
import BAROQUE_IBM_Interface as IbmInterface
import BAROQUE_Common_Constants as CommConst
import BAROQUE_Herr_Wrapper as HerrWrap

HELP_MSG = "Welcome to Baroque!\n" \
           "Here's how you use it:\n" \
           "\tAdd Baroque to your global path for ease of use.\n" \
           "\tHere's the generic outline of a Baroque command:\n\n" \
           "\tBaroque -i [input_file] -c [compare_file] -o [output_file] -b [backend] -r [routing_algorithm] " \
           "--<metric_test>\n\n" \
           "\tOut of all the arguments there, only input file and backend are necessary.\n" \
           "\tHowever, most arguments can have default values be specified.\n\n" \
           "Additional Commands:\n" \
           "\tYou can use any of these commands after the 'Baroque' keyword:\n" \
           "\t--set_default_<something> <value>\n" \
           "\t\tThis is how you set default values.\n" \
           "\t\tWhere <something> is replaced by input_file, compare_file, output_file, backend, or routing.\n" \
           "\t--show_defaults\n" \
           "\t\tThis will print all defaults you have set.\n" \
           "\t--reset_all\n" \
           "\t\tThis will reset all default values you have set.\n" \
           "\t--set_API_key <key>\n" \
           "\t\tUse this to set the API key you will use for using IBMQ simulators and machines.\n\n" \
           "Available Metrics: \n" \
           "\t--metricCountGate=<gate string>\n" \
           "\t\tCount the occurrences of a specific gate.\n" \
           "\t--metricDiffGate=<gate string>\n" \
           "\t\tFind the difference in occurrences of a specific between two circuits.\n" \
           "\t--metricDiffDepth\n" \
           "\t\tFind the difference in depth between two circuits.\n" \
           "\t--metricCircuitDepth\n" \
           "\t\tFind the depth of the circuit.\n" \
           "\t--metricRaw\n" \
           "\t\tDisplay raw data about the simulation.\n" \
           "\t\n" \
           "\t(gate strings have been defined as per IBM standards)\n" \
           "\nGood luck :3"

# metric strings
COUNT_GATE = "count_gate"
DIFF_GATE = "diff_gate"
DIFF_DEPTH = "diff_depth"
CIRCUIT_DEPTH = "circuit_depth"
RAW = "raw"


# TODO handle more than one input circuit (2)
# TODO implement all the metrics available
#


def show_defaults(user_pref):
    """
    Prints out the json defaults. Specific to this json.
    """
    print("DEFAULTS:")
    print("\tInput File:\t" + user_pref['DEFAULT_INPUT_FILE'])
    print("\tCompare File:\t" + user_pref['DEFAULT_COMPARE_FILE'])
    print("\tOutput File:\t" + user_pref['DEFAULT_OUTPUT_FILE'])
    print("\tBackend:\t" + user_pref['DEFAULT_BACKEND'])
    print("\tRouting:\t" + user_pref['DEFAULT_ROUTING'])


def run_metrics(metric_queue, circuit1, circuit2, quantum_container, backend_object):
    """
    Take the list of metric strings and run each metric on circuit 1 and optional circuit 2.
    Format the results into a string to return.
    """
    result = ""
    for metric_str in metric_queue:
        metric_arg = metric_str.split()
        arg_num = len(metric_arg) - 1
        metric = metric_arg[0]
        if metric == COUNT_GATE:
            if arg_num != 1:
                result += "ERROR: --metricCountGate requires 1 argument. Refer to --help or -h.\n"
            else:
                result += "Count Gate(" + metric_arg[1] + "): "
                result += str(Metrics.metricCountGate(circuit1, metric_arg[1]))
                result += "\n"
        elif metric == DIFF_GATE:
            if arg_num != 1 or circuit2 is None:
                result += "ERROR: --metricDiffGate requires 1 argument and a compare_file specified. Refer to --help " \
                          "or -h.\n"
            else:
                result += "Difference (Compare - Input) Gate Count(" + metric_arg[1] + "): "
                result += str(Metrics.metricDiffGate(circuit1, circuit2, metric_arg[1]))
                result += "\n"
        elif metric == DIFF_DEPTH:
            if circuit2 is None:
                result += "ERROR: --metricDiffDepth requires a compare_file specified Refer to --help " \
                          "or -h.\n"
            else:
                result += "Difference (Compare - Input) in Circuit Depth: "
                result += str(Metrics.metricDiffDepth(circuit1, circuit2))
                result += "\n"
        elif metric == CIRCUIT_DEPTH:
            result += "Circuit Depth: "
            result += str(Metrics.metricCircuitDepth(circuit1))
            result += "\n"
        elif metric == RAW:
            result += "Raw data:"
            result += str(Metrics.metricRawResults(1028, circuit1, quantum_container.noise_model, backend_object))
            result += "\n"

    return result


def handle_argv(argv, metric_queue, user_pref, ibmq_api_key, input_file, compare_file, output_file, routing_algorithm):
    """
    Handle the user arguments, update the metric_queue and user preferences
    argv - list of strings passed into main
    metric_queue - list of strings meant to be inputted metrics
    user_pref - loaded in json struct
    """

    try:
        opts, trailing_args = getopt.getopt(argv, "i:c:o:b:r:h",
                                            ["input_file=",
                                             "output_file=",
                                             "compare_file=",
                                             "backend=",
                                             "routing=",
                                             "set_API_key=",
                                             "set_default_input_file=",
                                             "set_default_output_file=",
                                             "set_default_backend=",
                                             "set_default_routing=",
                                             "reset_all",
                                             "show_defaults",
                                             "metricCountGate=",
                                             "metricDiffGate=",
                                             "metricDiffDepth",
                                             "metricCircuitDepth",
                                             # "metricAccuracy",
                                             # "metricStatevectorNorm",
                                             # "metricExpectedStatevector",
                                             # "metricRoutingTime",
                                             # "metricTranspilationTime",
                                             "metricRaw",
                                             "help"])
    except getopt.GetoptError:
        print("Error reading in getopt arguments.")
        return

    for opt, arg in opts:
        if opt in ['-i', '--input_file']:
            input_file = arg
        if opt in ['-c', '--compare_file']:
            compare_file = arg
        if opt in ['-o', '--output_file']:
            output_file = arg
        if opt in ['-b', '--backend']:
            backend_str = arg
        if opt in ['-r', '--routing']:
            routing_algorithm = arg
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
        if opt == "--set_default_backend":
            user_pref['DEFAULT_BACKEND'] = arg
        if opt == "--set_default_routing":
            user_pref['DEFAULT_ROUTING'] = arg
        if opt == "--reset_all":
            user_pref['DEFAULT_INPUT_FILE'] = ""
            user_pref['DEFAULT_OUTPUT_FILE'] = ""
            user_pref['DEFAULT_BACKEND'] = ""
            user_pref['DEFAULT_ROUTING'] = ""
        if opt == "--show_defaults":
            show_defaults(user_pref)
        if opt == "--metricCountGate":
            metric_queue.append(COUNT_GATE + " " + arg)
        if opt == "--metricDiffGate":
            metric_queue.append(DIFF_GATE + " " + arg)
        if opt == "--metricDiffDepth":
            metric_queue.append(DIFF_DEPTH)
        if opt == "--metricCircuitDepth":
            metric_queue.append(CIRCUIT_DEPTH)
        if opt == "--metricRaw":
            metric_queue.append(RAW)
    return metric_queue, user_pref, ibmq_api_key, input_file, compare_file, output_file, routing_algorithm


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

    # TODO make API key not necessary ? do it on local simulator

    # Get all default values from json
    ibmq_api_key = user_pref['API_KEY']  # REQUIRED for hardware. Check IBMQ profile settings for it.
    input_file = user_pref['DEFAULT_INPUT_FILE']
    compare_file = user_pref['DEFAULT_COMPARE_FILE']
    output_file = user_pref['DEFAULT_OUTPUT_FILE']
    backend_str = user_pref['DEFAULT_BACKEND']
    routing_algorithm = user_pref['DEFAULT_ROUTING']
    metric_queue = []  # list of metrics the user wants to run

    metric_queue, user_pref, ibmq_api_key, input_file, compare_file, output_file, routing_algorithm = handle_argv(argv,
                                                                                                                  metric_queue,
                                                                                                                  user_pref,
                                                                                                                  ibmq_api_key,
                                                                                                                  input_file,
                                                                                                                  compare_file,
                                                                                                                  output_file,
                                                                                                                  routing_algorithm)

    # Update the json file with preferences
    with open(os.path.join(pref_dir, 'user_pref.json'), 'w') as json_out:
        json.dump(user_pref, json_out)
    json_out.close()

    if input_file == "" or backend_str == "":
        return
    if ibmq_api_key == "":
        print("WARNING: Your IBMQ API Key has not been set.")

    """
    IBM API Access Section
    Log in to IBM and obtain backend dating using BAROQUE's IbmqInterfaceContainer class
    """

    quantum_container = IbmInterface.IbmqInterfaceContainer(ibmq_api_key, backend_str)

    """
    Circuit Creation Section
    
    Convert qasm files to circuits 1 and (optional) 2
    """

    # Creates QuantumCircuit from .qasm file specified by the user
    circuit1 = qasm3.load(input_file)

    if compare_file != "":
        circuit2 = qasm3.load(compare_file)
    else:
        circuit2 = None

    # Some routing algorithms require a DAG. Generate this here
    circuit_DAG = circuit_to_dag(circuit1)

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
    provider = IBMProvider(token=ibmq_api_key)  # specifically for ibm
    simulation = provider.get_backend(backend_str)

    """
    Analysis Section
    
    Call run_metrics() to run all metric tests in queue
    """

    results = run_metrics(metric_queue, circuit1, circuit2, quantum_container, simulation)

    """
    Output section
    
    Output to a file or to the console
    """
    out_string = ""

    # Add header information for the test's output data
    out_string += ("Test File: " + input_file + "\n")
    out_string += ("Device: " + backend_str + "\n\n")
    out_string += results

    if output_file != "":
        try:
            with open(output_file, "w") as out_stream:
                out_stream.write(out_string)
            out_stream.close()
        except OSError:
            print("Error opening specified output file. Printing to console...")
            print(out_string)
    else:
        print(out_string)


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


def checkRequiredOptions():
    return True


"""
Function - usage

Prints the usage string for the BAROQUE getopt terminal format
If getopt is not used, this function can be removed
"""


def usage():
    print(HELP_MSG)


"""
Function - exitBAROQUE
Inputs: cause_code - code denoting the cause of the exit condition
Outputs: none, exits program
    
Prints the relevant error message and exits with the cause_code
If no exit codes are needed, this function can be removed
"""


def exitBAROQUE(cause_code):
    print("Sample function. Put exit codes here if wanted...\n")
    print("Exiting BAROQUE code...\n")
    sys.exit(cause_code)


if __name__ == "__main__":
    print(sys.argv)
    main(sys.argv[1:])
