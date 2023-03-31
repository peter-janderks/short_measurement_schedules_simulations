from circuits.double_measurement_surface_code import DoubleMeasurementSurfaceCode
from circuits.circuit_builder import CircuitBuilder


class DoubleMeasurementSurfaceCodeMock(DoubleMeasurementSurfaceCode):
    def __init__(self, distance, p_idling=0, p_1=0, p_2=0, p_m=0, p_prep=0):
        self.builder = CircuitBuilder(p_idling, p_1, p_2, p_m, p_prep)
        self.distance = distance
        self.circ = self.builder.circ


def test_create_t0():
    d3rsc = DoubleMeasurementSurfaceCodeMock(3)
    (data_qubits, X_face_ancilla, X_face_flags, Z_face_ancilla, Z_face_flags, X_left_boundary_ancilla, X_left_boundary_flags,
     X_right_boundary_ancilla, X_right_boundary_flags, Z_top_boundary_ancilla, Z_top_boundary_flags, Z_bottom_boundary_ancilla, Z_bottom_boundary_flags) = d3rsc.create_t0()

    assert data_qubits == {(0, 2): 0, (1, 1): 1, (2, 0): 2, (1, 3): 3, (2, 2)                           : 4, (3, 1): 5, (2, 4): 6, (3, 3): 7, (4, 2): 8}
    assert X_face_ancilla == {(2, 1): 9, (2, 3): 11}
    assert X_face_flags == {(2.5, 0.5): 10, (2.5, 2.5): 12}
    assert Z_face_ancilla == {(1, 2): 13, (3, 2): 15}
    assert Z_face_flags == {(1.5, 1.5): 14, (3.5, 1.5): 16}
    assert X_left_boundary_ancilla == {(0, 1): 17}
    assert X_left_boundary_flags == {(0.5, 0.5): 18}
    assert X_right_boundary_ancilla == {(4, 3): 19}
    assert X_right_boundary_flags == {(4.5, 2.5): 20}
    assert Z_top_boundary_ancilla == {(1, 4): 23}
    assert Z_top_boundary_flags == {(1.5, 3.5): 24}
    assert Z_bottom_boundary_ancilla == {(3, 0): 21}
    assert Z_bottom_boundary_flags == {(3.5, -0.5): 22}

    assert d3rsc.circ.num_qubits == 9 + 4 + 4 + 4 + 4

    d5rsc = DoubleMeasurementSurfaceCodeMock(5)
    d5rsc.create_t0()
    assert d5rsc.circ.num_qubits == 25 + 24 + 24


def test_build_d3_circ():
    d3rsc = DoubleMeasurementSurfaceCode(3, 0.1, 0.12, 0.13, 0.14, 0.15)
    assert d3rsc.builder.circ.num_detectors == 48
    print(d3rsc.builder.circ)
    print(d3rsc.builder.circ.detector_error_model(approximate_disjoint_errors=True, decompose_errors=True))
    d5doublesurfacecode = DoubleMeasurementSurfaceCode(5, 0.1, 0.12, 0.13, 0.14, 0.15)
    assert d5doublesurfacecode.builder.circ.num_detectors == 240

    # print(d3rsc.builder.circ.detector_error_model(approximate_disjoint_errors=True, decompose_errors=True))
    # d5 = 240


test_build_d3_circ()
