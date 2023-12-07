"""
BAROQUE - Blueprint for Assembling Runtime Operations for QUantum Experiments

BAROQUE_Common_Constants.py

Author - Harrison Barnes
College - Rochester Institute of Technology, Kate Gleason College of Engineering
Email - hjjbarnes@gmail.com

BAROQUE_Common_Constants.py holds commonly used strings, values, etc. that are used when coding in Qiskit. This allows
programmers to access things like string representations easily without having to navigate IBM Qiskit's documentation

Disclaimer: IBM reserves the right to change representations and add new ones at any time. BAROQUE may not be 100% up
to date. If issues are encountered, access IBM's Quantum website and Qiskit Documentation. Furthermore, Python does not
support non-reassignable constants. Be sure to leave these as be, unless it becomes out of date.

Last Updated (MM/DD/YYYY) - 11/25/2022
"""

# IBM Quantum System Backend Strings
# All IBM quantum systems start with ibmq_ (older) or ibm_ (newer)
# If your account does not have access to a backend, using that backend string will result in an error
# Error will state  " qiskit.providers.exceptions.QiskitBackendNotFoundError: 'No backend matches the criteria' "
# Unlocking access or changing to an account with access will remove this error. This is caused by IBM authentication,
# not by BAROQUE
WASHINGTON_SYS_STR = "ibm_washington"
KYIV_SYS_STR = "ibm_kyiv"
ITHACA_SYS_STR = "ibm_ithaca"
KOLKATA_SYS_STR = "ibmq_kolkata"
MONTREAL_SYS_STR = "ibmq_montreal"
MUMBAI_SYS_STR = "ibmq_mumbai"
CAIRO_SYS_STR = "ibm_cairo"
AUCKLAND_SYS_STR = "ibm_auckland"
HANOI_SYS_STR = "ibm_hanoi"
GENEVA_SYS_STR = "ibm_geneva"
TORONTO_SYS_STR = "ibmq_toronto"
PEEKSKILL_SYS_STR = "ibm_peekskill"
GUADALUPE_SYS_STR = "ibmq_guadalupe"
PERTH_SYS_STR = "ibm_perth"
LAGOS_SYS_STR = "ibm_lagos"
NAIROBI_SYS_STR = "ibm_nairobi"
OSLO_SYS_STR = "ibm_oslo"
JAKARTA_SYS_STR = "ibmq_jakarta"
MANILA_SYS_STR = "ibmq_manila"
QUITO_SYS_STR = "ibmq_quito"
BELEM_SYS_STR = "ibmq_belem"
LIMA_SYS_STR = "ibmq_lima"

hardware = {WASHINGTON_SYS_STR, KYIV_SYS_STR, ITHACA_SYS_STR, KOLKATA_SYS_STR, MONTREAL_SYS_STR, MUMBAI_SYS_STR, CAIRO_SYS_STR,
            AUCKLAND_SYS_STR, HANOI_SYS_STR,GENEVA_SYS_STR, TORONTO_SYS_STR, PEEKSKILL_SYS_STR, GUADALUPE_SYS_STR,
            PERTH_SYS_STR, LAGOS_SYS_STR, NAIROBI_SYS_STR, OSLO_SYS_STR, JAKARTA_SYS_STR, MANILA_SYS_STR,
            QUITO_SYS_STR, BELEM_SYS_STR, LIMA_SYS_STR}

# IBM Quantum Simulator Backend Strings
STABILIZER_SIM = "simulator_stabilizer"
MPS_SIM = "simulator_mps"
EXT_STABILIZER_SIM = "simulator_extended_stabilizer"
QASM_SIM = "ibmq_qasm_simulator"
STATEVECTOR_SIM = "simulator_statevector"
AER_SIM = "aer_simulator"
AER_QASM_SIM = "qasm_simulator"

simulators = {STABILIZER_SIM, MPS_SIM, EXT_STABILIZER_SIM, QASM_SIM, STATEVECTOR_SIM, AER_SIM, AER_QASM_SIM}
# IBM Qiskit Gate String Representations for Common Gates
# Below gates are the common IBM system basis gates
CONTROL_NOT_GATE = "cx"
CONTROL_X_GATE = "cx"
SQRT_X_GATE = "sx"
IDENTITY_GATE = "id"
ROTATION_Z_GATE = "rz"
PAULI_X_GATE = "x"
RESET_GATE = "reset"
MEASURE_GATE = "measure"

valid_gate_strings = {CONTROL_NOT_GATE, CONTROL_X_GATE, SQRT_X_GATE, IDENTITY_GATE, ROTATION_Z_GATE,PAULI_X_GATE, RESET_GATE, MEASURE_GATE}

# Routing Methods
ROUTING_BASIC = "basic"
ROUTING_SABRE = "sabre"
ROUTING_LOOKAHEAD = "lookahead"
ROUTING_STOCHASTIC = "stochastic"
ROUTING_HERR = "herr"

# Layout Methods
LAYOUT_TRIVIAL = "trivial"
