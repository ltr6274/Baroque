"""
File: Print_Metrics.py
Author: Lucas Romero
Email: lucasr2125@gmail.com

Description: Use as a wrapper for BAROQUE_Metrics.py to check function inputs and print results.
Assumes that all circuit files exist (should have checked them before they get here).
"""

import BAROQUE_Common_Constants as Consts
import BAROQUE_Metrics as Metrics

# Use to format the results for each metric
METRIC_OUT = ("Metric:\t{metricDesc}\n"
              "Gate:\t{gateName}\n"
              "Result Note:\t{resultNote}\n"
              "Result:\t{result}\n")


# Use to format the errors for each metric
METRIC_ERROR = "ERROR - {metricName}: {errorNote}\n"


def printMetricDiffGate(circuit_a, circuit_b, gate_string):
    """
    Print the output or input error for metricDiffGate.
    :param circuit_a: Qiskit Quantum Circuit being compared
    :param circuit_b: Qiskit Quantum Circuit being compared
    :param gate_string: a string representation of the gate provided by Qiskit.
    """
    if gate_string not in Consts.valid_gate_strings:
        error = METRIC_ERROR.format(metricName="metricDiffGate", errorNote="Invalid gate string chosen.")
        print(error)
        return
    if circuit_b is None:
        error = METRIC_ERROR.format(metricName="metricDiffGate", errorNote="Compare circuit must be defined.")
        print(error)
    result = str(Metrics.metricDiffGate(circuit_a, circuit_b, gate_string))
    out = METRIC_OUT.format(metricDesc="Difference in Gate Occurrences",
                            gateName=gate_string,
                            resultNote="Compare - Input",
                            result=result)
    print(out)

