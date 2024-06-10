from circuits.stability_double_measurement_surface_code import StabilityDoubleMeasurementSurfaceCode
from circuits.circuit_builder import CircuitBuilder
import stim


class StabilityDoubleMeasurementSurfaceCodeMock(StabilityDoubleMeasurementSurfaceCode):
    def __init__(self, diameter, distance, p_idling=0, p_resonator_idling=0, p_1=0, p_2=0, p_m=0, p_prep=0):
        self.builder = CircuitBuilder(p_idling, p_resonator_idling, p_1, p_2, p_m, p_prep)
        self.diameter = diameter
        self.circ = self.builder.circ


def test_create_t0():
    d3rsc = StabilityDoubleMeasurementSurfaceCodeMock(4, 3)
    (data_qubits, X_face_ancilla, X_face_flags, Z_face_ancilla, Z_face_flags, X_left_boundary_ancilla, X_left_boundary_flags,
     X_top_boundary_ancilla, X_top_boundary_flags, X_right_boundary_ancilla, X_right_boundary_flags, X_bottom_boundary_ancilla, X_bottom_boundary_flags) = d3rsc.create_t0()
    assert data_qubits == {(0, 3): 0, (1, 2): 1, (2, 1): 2, (3, 0): 3, (1, 4): 4, (2, 3): 5, (3, 2): 6, (4, 1)
                            : 7, (2, 5): 8, (3, 4): 9, (4, 3): 10, (5, 2): 11, (3, 6): 12, (4, 5): 13, (5, 4): 14, (6, 3): 15}
    # add the double ancilla?

    assert X_face_ancilla == {(2, 2): 16, (2, 4): 18, (4, 2): 20, (4, 4): 22}
    assert X_face_flags == {(2.5, 1.5): 17, (2.5, 3.5): 19, (4.5, 1.5): 21, (4.5, 3.5): 23}
    assert Z_face_ancilla == {(1, 3): 24, (3, 1): 26, (3, 3): 28, (3, 5): 30, (5, 3): 32}
    assert Z_face_flags == {(1.5, 2.5): 25, (3.5, 0.5): 27, (3.5, 2.5): 29, (3.5, 4.5): 31, (5.5, 2.5): 33}

    assert X_left_boundary_ancilla == {(0, 2): 34, (2, 0): 36}
    assert X_left_boundary_flags == {(0.5, 1.5): 35, (2.5, -0.5): 37}

    assert X_top_boundary_ancilla == {(0, 4): 38, (2, 6): 40}
    assert X_top_boundary_flags == {(0.5, 3.5): 39, (2.5, 5.5): 41}

    print(X_right_boundary_flags)
    assert X_right_boundary_ancilla == {(4, 6): 44, (6, 4): 42}
    assert X_right_boundary_flags == {(4.5, 5.5): 45, (6.5, 3.5): 43}

    print(X_bottom_boundary_ancilla)
    assert X_bottom_boundary_ancilla == {(4, 0): 46, (6, 2): 48}
    assert X_bottom_boundary_flags == {(4.5, -0.5): 47, (6.5, 1.5): 49}

    # calculate again!
    # assert d3rsc.circ.num_qubits == 16+4+5+2+2+2+2

    #d5rsc = StabilityRotatedSurfaceCodeMock(6, 3)
    #data_qubits, X_face_ancilla, Z_face_ancilla, X_left_boundary_ancilla, X_right_boundary_ancilla, X_top_boundary_ancilla, X_bottom_boundary_ancilla = d5rsc.create_t0()

    #assert d5rsc.circ.num_qubits == 6*6 + 13 + 12 + 3 + 3 + 3 + 3





def test_distance_of_circuit():
    for diameter in [4, 6, 8]:
        for distance in [3, 5, 10, 15]:
            dmsc = StabilityDoubleMeasurementSurfaceCode(diameter, distance, 0.1, 0.11, 0.12, 0.13, 0.14, 0.15)
            assert len(dmsc.builder.circ.detector_error_model(approximate_disjoint_errors=True,
                                                             decompose_errors=True).shortest_graphlike_error()) == distance
