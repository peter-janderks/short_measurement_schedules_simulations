import stim


class CircuitBuilder(object):
    def __init__(self, p_idling, p_resonator_idling, p_1, p_2, p_m, p_prep):
        """_summary_

        Args:
            p_idling: _description_
            p_resonator_idling: _description_
            p_1: _description_
            p_2: _description_
            m: _description_
            p_prep: _description_
        """
        self.circ = stim.Circuit()
        self.measurement_order = dict()
        self.ancilla_qubits_ind_to_coord = dict()

        self.p_idling, self.p_resonator_idling, self.p_1, self.p_2, self.p_m, self.p_prep = (
            p_idling,
            p_resonator_idling,
            p_1,
            p_2,
            p_m,
            p_prep,
        )

    def build_layer(self, layer, all_qubits):
        self.p1_qubits = set()
        self.p2_qubits = []
        self.measurement_qubits = []
        self.idling_qubits = all_qubits.copy()
        layer()
        self.add_noise(self.p1_qubits, self.idling_qubits, self.p2_qubits)

    def H(self, qubits: int | list):
        if isinstance(qubits, int):
            qubits = [qubits]

        for qubit in qubits:
            self.circ.append("H", qubit)
            self.idling_qubits.remove(qubit)
            self.p1_qubits.add(qubit)

    def cnot(self, q_cont, q_target):
        self.circ.append("CNOT", [q_cont, q_target])
        self.idling_qubits.remove(q_cont)
        self.idling_qubits.remove(q_target)
        self.p2_qubits.append([q_cont, q_target])

    def add_noise(self, p1_qubits, pI_qubits, p2_qubits):
        self.circ.append("TICK")
        if p1_qubits != set():
            self.p1_noise(p1_qubits)
        if p2_qubits != []:
            self.p2_noise(p2_qubits)
        if pI_qubits != ():
            self.idling_noise(pI_qubits)

    def p1_noise(self, qubits):
        if self.p_1 > 0:
            self.circ.append("PAULI_CHANNEL_1", [q for q in qubits], (self.p_1/3, self.p_1/3, self.p_1/3))

    def idling_noise(self, qubits):
        if self.p_idling > 0:
            self.circ.append("PAULI_CHANNEL_1", [q for q in qubits],
                             (self.p_idling/3, self.p_idling/3, self.p_idling/3))

    def resonator_idling_noise(self, qubits):
        if self.p_resonator_idling > 0:
            self.circ.append("PAULI_CHANNEL_1", [q for q in qubits],
                             (self.p_resonator_idling/3, self.p_resonator_idling/3, self.p_resonator_idling/3))

    def p2_noise(self, qubit_pairs):
        if self.p_2 > 0:
            for pair in qubit_pairs:
                self.circ.append("PAULI_CHANNEL_2", pair, tuple(self.p_2/15 for _ in range(15)))

    def p_prep_noise(self, qubits):
        if self.p_prep > 0:
            self.circ.append("X_ERROR", [q for q in qubits], (self.p_prep))

    def m_noise(self, qubits):
        if self.p_m > 0:
            self.circ.append("X_ERROR", [q for q in qubits], self.p_m)

    def M(self, qubits):
        self.m_noise(qubits)
        for qubit in qubits:
            self.circ.append("M", qubit)
        for qubit in qubits:
            self.idling_qubits.remove(qubit)

    def update_measurement_order(self, measured_qubits):
        for q_index in self.measurement_order.keys():
            self.measurement_order[q_index] -= len(measured_qubits)
        m_index = 0

        for q_index in measured_qubits:
            self.measurement_order[q_index] = -1 * len(measured_qubits) + m_index
            m_index += 1
