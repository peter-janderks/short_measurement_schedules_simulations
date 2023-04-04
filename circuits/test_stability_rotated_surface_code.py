from circuits.stability_rotated_surface_code import StabilityRotatedSurfaceCode
from circuits.circuit_builder import CircuitBuilder
import stim


class StabilityRotatedSurfaceCodeMock(StabilityRotatedSurfaceCode):
    def __init__(self, diameter, distance, p_idling=0, p_resonator_idling=0, p_1=0, p_2=0, p_m=0, p_prep=0):
        self.builder = CircuitBuilder(p_idling, p_resonator_idling, p_1, p_2, p_m, p_prep)
        self.diameter = diameter
        self.circ = self.builder.circ


def test_create_t0():
    d3rsc = StabilityRotatedSurfaceCodeMock(4, 3)
    data_qubits, X_face_ancilla, Z_face_ancilla, X_left_boundary_ancilla, X_right_boundary_ancilla, X_top_boundary_ancilla, X_bottom_boundary_ancilla = d3rsc.create_t0()
    assert data_qubits == {(0, 3): 0, (1, 2): 1, (2, 1): 2, (3, 0): 3, (1, 4): 4, (2, 3): 5, (3, 2): 6, (4, 1)
                            : 7, (2, 5): 8, (3, 4): 9, (4, 3): 10, (5, 2): 11, (3, 6): 12, (4, 5): 13, (5, 4): 14, (6, 3): 15}
    assert X_face_ancilla == {(2, 2): 16, (2, 4): 17, (4, 2): 18, (4, 4): 19}
    assert Z_face_ancilla == {(1, 3): 20, (3, 1): 21, (3, 3): 22, (3, 5): 23, (5, 3): 24}
    assert X_left_boundary_ancilla == {(0, 2): 25, (2, 0): 26}
    assert X_top_boundary_ancilla == {(0, 4): 27, (2, 6): 28}
    assert X_right_boundary_ancilla == {(4, 6): 30, (6, 4): 29}
    assert X_bottom_boundary_ancilla == {(4, 0): 31, (6, 2): 32}

    assert d3rsc.circ.num_qubits == 16+4+5+2+2+2+2

    d5rsc = StabilityRotatedSurfaceCodeMock(6, 3)
    data_qubits, X_face_ancilla, Z_face_ancilla, X_left_boundary_ancilla, X_right_boundary_ancilla, X_top_boundary_ancilla, X_bottom_boundary_ancilla = d5rsc.create_t0()

    assert d5rsc.circ.num_qubits == 6*6 + 13 + 12 + 3 + 3 + 3 + 3


def test_distance_of_circuit():
    for diameter in [4, 6, 8]:
        for distance in [3, 5, 10, 15]:
            rsc = StabilityRotatedSurfaceCode(diameter, distance, 0.1, 0.11, 0.12, 0.13, 0.14, 0.15)
            assert len(rsc.builder.circ.detector_error_model(approximate_disjoint_errors=True,
                                                             decompose_errors=True).shortest_graphlike_error()) == distance
