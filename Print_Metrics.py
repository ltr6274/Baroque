"""
File: Print_Metrics.py
Author: Lucas Romero
Email: lucasr2125@gmail.com

Description: Use as a wrapper for BAROQUE_Metrics.py to check function inputs and print results.
Assumes that all circuit files exist (should have checked them before they get here).
"""
import qiskit

import BAROQUE_Common_Constants as Consts
import BAROQUE_Metrics as Metrics

# Use to format the results for each metric
METRIC_OUT = ("\nMetric:\t{metricDesc}\n"
              "Gate:\t{gateName}\n"
              "Result Note:\t{resultNote}\n"
              "Result:\t{result}\n")

# Use to format the errors for each metric
METRIC_ERROR = "\nERROR - {metricName}: {errorNote}\n"


def printMetricDiffGate(circuit_a, circuit_b, gate_string):
    """
    Print the output or input error for metricDiffGate.
    :param circuit_a: Reference to a circuit being compared
    :param circuit_b: Reference to a circuit being compared
    :param gate_string: a string representation of the gate provided by Qiskit
    :return: A string of the output
    """
    if gate_string not in Consts.valid_gate_strings:
        error = METRIC_ERROR.format(metricName="metricDiffGate", errorNote="Invalid gate string chosen.")
        return error
    if circuit_b is None:
        error = METRIC_ERROR.format(metricName="metricDiffGate", errorNote="Compare circuit must be defined.")
        return error
    result = str(Metrics.metricDiffGate(circuit_a.get(), circuit_b.get(), gate_string))

    resultNote = "({compName}) {compCnt} - ({inputName}) {impCnt}"
    resultNote = resultNote.format(compName=circuit_b.get_name(),
                                   compCnt=displayCount(circuit_b, gate_string),
                                   inputName=circuit_a.get_name(),
                                   impCnt=displayCount(circuit_a, gate_string))

    out = METRIC_OUT.format(metricDesc="Difference in Gate Occurrences",
                            gateName=gate_string,
                            resultNote=resultNote,
                            result=result)
    return out


def printMetricCountGate(circuit_a, circuit_b, gate_string):
    """
    Count the occurrences of a specified gate in the circuit.
    :param circuit_a: The Reference to a circuit whose gates are being counted
    :param circuit_b: The Reference to a circuit whose gates are being counted (can be None)
    :param gate_string: The gate we want to count occurrences of
    :return: A string of the output
    """
    if gate_string not in Consts.valid_gate_strings:
        error = METRIC_ERROR.format(metricName="metricCountGate", errorNote="Invalid gate string chosen.")
        return error

    result_for_a = str(Metrics.metricCountGate(circuit_a.get(), gate_string))

    if circuit_b.get() is None:
        result_for_b = None
    else:
        result_for_b = str(Metrics.metricCountGate(circuit_b.get(), gate_string))
    out = METRIC_OUT.format(metricDesc="Count of Gate Occurrences",
                            gateName=gate_string,
                            resultNote=circuit_a.get_name(),
                            result=result_for_a)
    if result_for_b is not None:
        out += METRIC_OUT.format(metricDesc="Count of Gate Occurrences",
                                 gateName=gate_string,
                                 resultNote=circuit_b.get_name(),
                                 result=result_for_b)
    return out


def printMetricRatioGate(circuit_a, circuit_b, gate_string):
    """
    Get the ratio of gate counts for two circuits.
    :param circuit_a: Reference to circuit whose gate count goes in denominator.
    :param circuit_b: Reference to circuit whose gate count goes in numerator.
    :param gate_string: Gate string whose occurrences is being ratioed.
    :return: The output as a string.
    """
    if gate_string not in Consts.valid_gate_strings:
        error = METRIC_ERROR.format(metricName="metricRatioGate", errorNote="Invalid gate string chosen.")
        return error
    if circuit_b is None:
        error = METRIC_ERROR.format(metricName="metricRatioGate", errorNote="Compare circuit must be defined.")
        return error
    result = str(Metrics.metricRatioGate(circuit_a.get(), circuit_b.get(), gate_string))

    resultNote = "({compName}) {compCnt} / ({inputName}) {impCnt}"
    resultNote = resultNote.format(compName=circuit_b.get_name(),
                                   compCnt=displayCount(circuit_b, gate_string),
                                   inputName=circuit_a.get_name(),
                                   impCnt=displayCount(circuit_a, gate_string))

    out = METRIC_OUT.format(metricDesc="Ratio of Gate Occurrences",
                            gateName=gate_string,
                            resultNote=resultNote,
                            result=result)
    return out


def printMetricDiffDepth(circuit_a, circuit_b, basis_gates_a=None, basis_gates_b=None):
    """
    Get the difference in depths for two circuits.
    :param circuit_a: The first reference to a circuit whose depth is being counted.
    :param circuit_b: The second reference to a circuit whose depth is being counted.
    :param basis_gates_a: TODO should be able to implement different basis gates
    :param basis_gates_b: TODO should be able to implement different basis gates
    :return: A string of the output.
    """
    if circuit_b is None:
        error = METRIC_ERROR.format(metricName="metricDiffDepth", errorNote="Compare circuit must be defined.")
        return error
    result = str(Metrics.metricDiffDepth(circuit_a.get(), circuit_b.get()))
    resultNote = "({compName} in {basis_b}) {compCnt} - ({inputName} in {basis_a}) {impCnt}"
    resultNote = resultNote.format(compName=circuit_b.get_name(),
                                   basis_b=str(basis_gates_b if basis_gates_b is not ("" or None) else "Default Gates"),
                                   compCnt=displayDepth(circuit_b, basis_gates_b),
                                   inputName=circuit_a.get_name(),
                                   basis_a=str(basis_gates_a if basis_gates_a is not ("" or None) else "Default Gates"),
                                   impCnt=displayDepth(circuit_a, basis_gates_a))

    out = METRIC_OUT.format(metricDesc="Difference in Circuit Depth",
                            gateName="",
                            resultNote=resultNote,
                            result=result)
    return out


def printMetricCircuitDepth(circuit_a, circuit_b, basis_gates_a=None, basis_gates_b=None):
    """
    Get the circuit depths for circuit_a and an optional circuit_b
    :param circuit_a: Ref to circuit that we want to get depth of.
    :param circuit_b: Ref to circuit that we want to get depth of (optional).
    :param basis_gates_a: TODO should be able to implement different basis gates
    :param basis_gates_b: TODO should be able to implement different basis gates
    :return: A string of the output
    """
    result_for_a = str(Metrics.metricCircuitDepth(circuit_a.get(), basis_gates_a))

    if circuit_b.get() is None:
        result_for_b = None
    else:
        result_for_b = str(Metrics.metricCircuitDepth(circuit_b.get(), basis_gates_b))
    result_note = "{circName} in {basis}"
    result_note_a = result_note.format(circName=circuit_a.get_name(),
                                       basis=str(
                                           basis_gates_a if basis_gates_a is not ("" or None) else "Default Gates"))
    out = METRIC_OUT.format(metricDesc="Circuit Depth",
                            gateName="",
                            resultNote=result_note_a,
                            result=result_for_a)
    if result_for_b is not None:
        result_note_b = result_note.format(circName=circuit_b.get_name(),
                                           basis=str(
                                               basis_gates_b if basis_gates_b is not ("" or None) else "Default Gates"))
        out += METRIC_OUT.format(metricDesc="Circuit Depth",
                                 gateName=str(basis_gates_b),
                                 resultNote=result_note_b,
                                 result=result_for_b)
    return out


def printMetricRatioDepth(circuit_a, circuit_b, basis_gates_a=None, basis_gates_b=None):
    """
    Get the ratio of depth between two circuits.
    :param circuit_a: A ref to a circuit whose depth is measured
    :param circuit_b: A ref to a circuit whose depth is measured
    :param basis_gates_a: Optional basis gates to measure depth for circuit_a
    :param basis_gates_b: Optional basis gates to measure depth for circuit_b
    :return: A string of the output.
    """
    if circuit_b is None:
        error = METRIC_ERROR.format(metricName="metricRatioGate", errorNote="Compare circuit must be defined.")
        return error
    result = str(Metrics.metricRatioDepth(circuit_a.get(), circuit_b.get(), basis_gates_a, basis_gates_b))

    resultNote = "({compName} in {basis_b}) {compCnt} / ({inputName} in {basis_a}) {impCnt}"
    resultNote = resultNote.format(compName=circuit_b.get_name(),
                                   basis_b=str(basis_gates_b if basis_gates_b is not ("" or None) else "Default Gates"),
                                   compCnt=displayDepth(circuit_b, basis_gates_b),
                                   inputName=circuit_a.get_name(),
                                   basis_a=str(basis_gates_a if basis_gates_a is not ("" or None) else "Default Gates"),
                                   impCnt=displayDepth(circuit_a, basis_gates_a))

    out = METRIC_OUT.format(metricDesc="Ratio of Circuit Depths",
                            gateName="",
                            resultNote=resultNote,
                            result=result)
    return out


def printMetricRaw(quantum_container, circuit, backend):
    """
    Get the output for the metricRawResults.
    :param quantum_container: A reference to an IbmqInterfaceContainer whose config is being run.
    :param circuit: The circuit being run on simulator.
    :param backend: The backend object that is being run on.
    :return: A string of the output.
    """
    if circuit.get() is None:
        return ""
    container = quantum_container.get()
    if container is None:
        return ""
    out = Metrics.metricRawResults(1024, circuit.get(), container.noise_model, backend.get())

    try:
        counts = out.get_counts()
    except qiskit.QiskitError:
        counts = None
    result = "\n{name} Raw Results\n{out}\nCounts:\n{counts}\n".format(name=circuit.get_name(), out=out,
                                                                       counts=counts if counts else "None")
    return result


def displayCount(circuit, gate_string):
    """
    Display the number of gate string occurrences.
    :param circuit: Reference to circuit we are counting gates of
    :param gate_string: Gate string we are counting occurences of
    :return: string of output
    """
    result = str(Metrics.metricCountGate(circuit.get(), gate_string))
    return result


def displayDepth(circuit, basis_gates=None):
    """
    Display the circuit's depth.
    :param circuit: A reference to the circuit whose depth is needed.
    :param basis_gates: Optional basis gates to measure depth in
    :return: A string of the circuit's depth.
    """
    result = str(Metrics.metricCircuitDepth(circuit.get(), basis_gates))
    return result
