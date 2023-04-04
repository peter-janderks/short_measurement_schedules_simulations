import stim
# import stimcirq
from circuits.circuit_builder import CircuitBuilder


class StabilityRotatedSurfaceCode(object):
    def __init__(self, diameter, rounds, p_idling, p_resonator_idling, p_1, p_2, p_m, p_prep):
        self.builder = CircuitBuilder(float(p_idling), float(p_resonator_idling),
                                      float(p_1), float(p_2), float(p_m), float(p_prep))
        self.diameter = int(diameter)
        (self.data_qubits,
         self.builder.X_face_ancilla,
         self.builder.Z_face_ancilla,
         self.builder.X_left_boundary_ancilla,
         self.builder.X_right_boundary_ancilla,
         self.builder.X_top_boundary_ancilla,
         self.builder.X_bottom_boundary_ancilla) = self.create_t0()

        self.builder.ancilla_qubits_ind_to_coord.update(
            {ind: coord for coord, ind in self.builder.X_face_ancilla.items()})
        self.builder.ancilla_qubits_ind_to_coord.update(
            {ind: coord for coord, ind in self.builder.Z_face_ancilla.items()})
        self.builder.ancilla_qubits_ind_to_coord.update(
            {ind: coord for coord, ind in self.builder.X_left_boundary_ancilla.items()})
        self.builder.ancilla_qubits_ind_to_coord.update(
            {ind: coord for coord, ind in self.builder.X_right_boundary_ancilla.items()})
        self.builder.ancilla_qubits_ind_to_coord.update(
            {ind: coord for coord, ind in self.builder.X_top_boundary_ancilla.items()})
        self.builder.ancilla_qubits_ind_to_coord.update(
            {ind: coord for coord, ind in self.builder.X_bottom_boundary_ancilla.items()})

        all_qubits = (
            set(self.data_qubits.values())
            | set(self.builder.X_face_ancilla.values())
            | set(self.builder.Z_face_ancilla.values())
            | set(self.builder.X_left_boundary_ancilla.values())
            | set(self.builder.X_right_boundary_ancilla.values())
            | set(self.builder.X_top_boundary_ancilla.values())
            | set(self.builder.X_bottom_boundary_ancilla.values())
        )

        self.ancilla_qubits = (
            set(self.builder.X_face_ancilla.values())
            | set(self.builder.Z_face_ancilla.values())
            | set(self.builder.X_left_boundary_ancilla.values())
            | set(self.builder.X_right_boundary_ancilla.values())
            | set(self.builder.X_top_boundary_ancilla.values())
            | set(self.builder.X_bottom_boundary_ancilla.values())
        )

        self.build_five_layers(all_qubits)
        self.first_time_measuring_ancillas(all_qubits)
        self.builder.idling_noise(self.builder.idling_qubits)
        self.builder.resonator_idling_noise(self.builder.idling_qubits)
        self.initialize_ancilla_qubits()

        starting_circ = self.builder.circ.copy()
        self.builder.circ = stim.Circuit()
        self.build_five_layers(all_qubits)
        self.measure_ancilla_qubits(0, all_qubits)
        self.builder.idling_noise(self.builder.idling_qubits)
        self.builder.resonator_idling_noise(self.builder.idling_qubits)
        self.initialize_ancilla_qubits()

        self.builder.circ = starting_circ + self.builder.circ

        if rounds > 3:
            starting_circ = self.builder.circ.copy()
            self.builder.circ = stim.Circuit()
            self.build_five_layers(all_qubits)
            self.measure_ancilla_qubits(0, all_qubits)
            self.builder.idling_noise(self.builder.idling_qubits)
            self.builder.resonator_idling_noise(self.builder.idling_qubits)
            self.initialize_ancilla_qubits()
            self.builder.circ = starting_circ + (rounds-3)*self.builder.circ

        self.build_five_layers(all_qubits)
        self.measure_ancilla_qubits(1, all_qubits)
        self.measure_data_qubits(1, all_qubits)

    def build_five_layers(self, all_qubits):
        self.builder.build_layer(self.l0, all_qubits)
        self.builder.build_layer(self.l1, all_qubits)
        self.builder.build_layer(self.l2, all_qubits)
        self.builder.build_layer(self.l3, all_qubits)
        self.builder.build_layer(self.l4, all_qubits)
        self.builder.build_layer(self.l5, all_qubits)

    def create_t0(self):
        data_qubits = self.create_data_qubits()
        X_face_ancilla, index = self.create_X_face_ancilla()
        Z_face_ancilla, index = self.create_Z_face_ancilla(index)
        X_left_boundary_ancilla, X_right_boundary_ancilla, X_top_boundary_ancilla, X_bottom_boundary_ancilla, index = self.create_X_boundary(
            index)
        initialized_qubits = list(data_qubits.values())
        initialized_qubits.extend(list(X_face_ancilla.values()))
        initialized_qubits.extend(list(Z_face_ancilla.values()))
        initialized_qubits.extend(list(X_left_boundary_ancilla.values()))
        initialized_qubits.extend(list(X_right_boundary_ancilla.values()))
        initialized_qubits.extend(list(X_top_boundary_ancilla.values()))
        initialized_qubits.extend(list(X_bottom_boundary_ancilla.values()))
        self.builder.p_prep_noise(initialized_qubits)
        return (
            data_qubits,
            X_face_ancilla,
            Z_face_ancilla,
            X_left_boundary_ancilla,
            X_right_boundary_ancilla,
            X_top_boundary_ancilla,
            X_bottom_boundary_ancilla,
        )

    def build_first_round_detectors(self, q_indexes_measure, z_cor=0):
        self.builder.update_measurement_order(q_indexes_measure)
        for measurement_number, ancilla_index in enumerate(q_indexes_measure):
            x_cord, y_cord = self.builder.ancilla_qubits_ind_to_coord[ancilla_index]
            self.builder.circ.append("DETECTOR", stim.target_rec(
                measurement_number-len(q_indexes_measure)), (x_cord, y_cord, z_cor))

    def build_ancilla_detector(self, ancilla_qubit_indexes, z_cor):
        #        list(ancilla_qubit_indexes).sort()
        for m_index, q_index in enumerate(ancilla_qubit_indexes):
            x_cor, y_cor = self.builder.ancilla_qubits_ind_to_coord[q_index]
            self.builder.circ.append(
                "DETECTOR",
                [
                    stim.target_rec(m_index - len(ancilla_qubit_indexes)),
                    stim.target_rec(
                        self.builder.measurement_order[q_index]
                        - len(ancilla_qubit_indexes)
                    ),
                ],
                (x_cor, y_cor, z_cor)
            )

    def measure_ancilla_qubits(self, z_cor, all_qubits):
        self.builder.idling_qubits = all_qubits.copy()

        qubits_to_measure_deterministic = list(self.ancilla_qubits)
        self.builder.M(qubits_to_measure_deterministic)
        self.build_ancilla_detector(qubits_to_measure_deterministic, z_cor)
        self.builder.update_measurement_order(qubits_to_measure_deterministic)

    def initialize_ancilla_qubits(self):
        self.builder.circ.append("TICK")
        for q in self.ancilla_qubits:
            self.builder.circ.append("R", q)
        self.builder.p_prep_noise(self.ancilla_qubits)
        self.builder.idling_noise(self.data_qubits.values())
        self.builder.resonator_idling_noise(qubits=self.data_qubits.values())
        self.builder.circ.append("TICK")

    def x_bound_detector(self, x_bound_coords, z_cor):
        for coords in x_bound_coords:
            self.builder.circ.append(
                "DETECTOR",
                [
                    stim.target_rec(
                        self.builder.measurement_order[
                            self.builder.H1_X_boundary_ancilla[coords]
                        ]
                    ),
                    stim.target_rec(
                        self.builder.measurement_order[
                            self.data_qubits[coords[0] + 1, coords[1]]
                        ]
                    ),
                    stim.target_rec(
                        self.builder.measurement_order[
                            self.data_qubits[coords[0], coords[1] + 1]
                        ]
                    ),
                ],
                (coords[0], coords[1], z_cor)
            )

    def z_bound_detector_top(self, q_indexes_z_faces, coords_list, z_cor):

        for cor_index, q_index in enumerate(q_indexes_z_faces):
            coords = coords_list[cor_index]
            self.builder.circ.append(
                "DETECTOR",
                [
                    stim.target_rec(self.builder.measurement_order[q_index]),
                    stim.target_rec(
                        self.builder.measurement_order[
                            self.data_qubits[coords[0], coords[1]-1]
                        ]
                    ),
                    stim.target_rec(
                        self.builder.measurement_order[
                            self.data_qubits[coords[0]+1, coords[1]]
                        ]
                    ),
                ],
                (coords[0], coords[1], z_cor)
            )

    def z_bound_detector_bottom(self, q_indexes_z_faces, coords_list, z_cor):

        for cor_index, q_index in enumerate(q_indexes_z_faces):
            coords = coords_list[cor_index]
            self.builder.circ.append(
                "DETECTOR",
                [
                    stim.target_rec(self.builder.measurement_order[q_index]),
                    stim.target_rec(
                        self.builder.measurement_order[
                            self.data_qubits[coords[0] - 1, coords[1]]
                        ]
                    ),
                    stim.target_rec(
                        self.builder.measurement_order[
                            self.data_qubits[coords[0], coords[1] + 1]
                        ]
                    ),
                ],
                (coords[0], coords[1], z_cor)
            )

    def x_face_detector(self, x_face_coords, z_cor):
        for coords in x_face_coords:
            self.builder.circ.append(
                "DETECTOR",
                [
                    stim.target_rec(
                        self.builder.measurement_order[
                            self.builder.H1_X_face_ancilla[coords]
                        ]
                    ),
                    stim.target_rec(
                        self.builder.measurement_order[
                            self.data_qubits[coords[0] - 1, coords[1]]
                        ]
                    ),
                    stim.target_rec(
                        self.builder.measurement_order[
                            self.data_qubits[coords[0], coords[1] + 1]
                        ]
                    ),
                    stim.target_rec(
                        self.builder.measurement_order[
                            self.data_qubits[coords[0], coords[1] - 1]
                        ]
                    ),
                    stim.target_rec(
                        self.builder.measurement_order[
                            self.data_qubits[coords[0] + 1, coords[1]]
                        ]
                    ),
                ],
                (coords[0], coords[1], z_cor)
            )

    def z_face_detector(self, q_indexes_z_faces, coords_list, z_cor):
        for cor_index, q_index in enumerate(q_indexes_z_faces):
            coords = coords_list[cor_index]
            self.builder.circ.append(
                "DETECTOR",
                [
                    stim.target_rec(self.builder.measurement_order[q_index]),
                    stim.target_rec(
                        self.builder.measurement_order[
                            self.data_qubits[coords[0] - 1, coords[1]]
                        ]
                    ),
                    stim.target_rec(
                        self.builder.measurement_order[
                            self.data_qubits[coords[0], coords[1] + 1]
                        ]
                    ),
                    stim.target_rec(
                        self.builder.measurement_order[
                            self.data_qubits[coords[0], coords[1] - 1]
                        ]
                    ),
                    stim.target_rec(
                        self.builder.measurement_order[
                            self.data_qubits[coords[0] + 1, coords[1]]
                        ]
                    ),
                ],
                (coords[0], coords[1], z_cor)
            )

    def measure_data_qubits(self, z_cor, all_qubits):
        # measure data qubits and build detectors
        self.builder.M(self.data_qubits.values())
        self.builder.update_measurement_order(self.data_qubits.values())

        self.z_face_detector(list(self.builder.Z_face_ancilla.values()),
                             list(self.builder.Z_face_ancilla.keys()), z_cor)
        self.add_logical_observable()

    def add_logical_observable(self):

        # this needs to be all X ancilla? yes should be x ancilla
        X_ancilla = list(self.builder.X_face_ancilla.values())
        X_ancilla.extend(list(self.builder.X_left_boundary_ancilla.values()))
        X_ancilla.extend(list(self.builder.X_right_boundary_ancilla.values()))
        X_ancilla.extend(list(self.builder.X_top_boundary_ancilla.values()))
        X_ancilla.extend(list(self.builder.X_bottom_boundary_ancilla.values()))

        measurement_for_observable = []
        for qubit in X_ancilla:
            measurement_for_observable.append(
                stim.target_rec(
                    self.builder.measurement_order[
                        qubit
                    ]
                )
            )
        self.builder.circ.append("OBSERVABLE_INCLUDE", measurement_for_observable, 0)

    def l0(self):
        for qubit in self.builder.X_face_ancilla.values():
            self.builder.H(qubit)

        for qubit in self.builder.X_left_boundary_ancilla.values():
            self.builder.H(qubit)

        for qubit in self.builder.X_right_boundary_ancilla.values():
            self.builder.H(qubit)

        for qubit in self.builder.X_top_boundary_ancilla.values():
            self.builder.H(qubit)

        for qubit in self.builder.X_bottom_boundary_ancilla.values():
            self.builder.H(qubit)

    def l1(self):
        for coords, q_index in self.builder.X_face_ancilla.items():
            self.builder.cnot(
                q_index,
                self.data_qubits[coords[0] + 1, coords[1]],
            )

        for coords, q_index in self.builder.X_left_boundary_ancilla.items():
            self.builder.cnot(
                q_index,
                self.data_qubits[coords[0] + 1, coords[1]],
            )

        for coords, q_index in self.builder.X_top_boundary_ancilla.items():
            self.builder.cnot(
                q_index,
                self.data_qubits[coords[0] + 1, coords[1]]
            )

        for coords, q_index in self.builder.Z_face_ancilla.items():
            self.builder.cnot(self.data_qubits[coords[0] + 1, coords[1]], q_index)

    def l2(self):
        for coords, q_index in self.builder.X_face_ancilla.items():
            self.builder.cnot(
                q_index,
                self.data_qubits[coords[0], coords[1] + 1],
            )

        for coords, q_index in self.builder.Z_face_ancilla.items():
            self.builder.cnot(self.data_qubits[coords[0], coords[1] - 1], q_index)

        for coords, q_index in self.builder.X_left_boundary_ancilla.items():
            self.builder.cnot(q_index, self.data_qubits[coords[0], coords[1] + 1])

        for coords, q_index in self.builder.X_bottom_boundary_ancilla.items():
            self.builder.cnot(q_index, self.data_qubits[coords[0], coords[1] + 1])

    def l3(self):
        for coords, q_index in self.builder.X_face_ancilla.items():
            self.builder.cnot(q_index, self.data_qubits[coords[0], coords[1] - 1])

        for coords, q_index in self.builder.Z_face_ancilla.items():
            self.builder.cnot(self.data_qubits[coords[0], coords[1] + 1], q_index)

        for coords, q_index in self.builder.X_top_boundary_ancilla.items():
            self.builder.cnot(q_index, self.data_qubits[coords[0], coords[1] - 1])

        for coords, q_index in self.builder.X_right_boundary_ancilla.items():
            self.builder.cnot(q_index, self.data_qubits[coords[0], coords[1] - 1])

    def l4(self):
        for coords, q_index in self.builder.X_face_ancilla.items():
            self.builder.cnot(q_index, self.data_qubits[coords[0] - 1, coords[1]])

        for coords, q_index in self.builder.Z_face_ancilla.items():
            self.builder.cnot(self.data_qubits[coords[0] - 1, coords[1]], q_index)

        for coords, q_index in self.builder.X_bottom_boundary_ancilla.items():
            self.builder.cnot(
                q_index,
                self.data_qubits[coords[0] - 1, coords[1]],
            )

        for coords, q_index in self.builder.X_right_boundary_ancilla.items():
            self.builder.cnot(q_index, self.data_qubits[coords[0] - 1, coords[1]])

    def l5(self):
        for qubit in self.builder.X_face_ancilla.values():
            self.builder.H(qubit)

        for qubit in self.builder.X_left_boundary_ancilla.values():
            self.builder.H(qubit)

        for qubit in self.builder.X_right_boundary_ancilla.values():
            self.builder.H(qubit)

        for qubit in self.builder.X_top_boundary_ancilla.values():
            self.builder.H(qubit)

        for qubit in self.builder.X_bottom_boundary_ancilla.values():
            self.builder.H(qubit)

    def first_time_measuring_ancillas(self, all_qubits):
        self.builder.idling_qubits = all_qubits.copy()
        qubits_to_measure = list(self.builder.X_face_ancilla.values())
        qubits_to_measure.extend(list(self.builder.X_left_boundary_ancilla.values()))
        qubits_to_measure.extend(list(self.builder.X_right_boundary_ancilla.values()))
        qubits_to_measure.extend(list(self.builder.X_top_boundary_ancilla.values()))
        qubits_to_measure.extend(list(self.builder.X_bottom_boundary_ancilla.values()))
        self.builder.M(qubits_to_measure)
        self.builder.update_measurement_order(qubits_to_measure)

        qubits_to_measure_deterministic = list(self.builder.Z_face_ancilla.values())
        self.builder.M(qubits_to_measure_deterministic)
        self.build_first_round_detectors(qubits_to_measure_deterministic, 0)
        self.builder.idling_noise(self.builder.idling_qubits)

        self.builder.circ.append("TICK")
        for q in self.ancilla_qubits:
            self.builder.circ.append("R", q)
        self.builder.p_prep_noise(self.ancilla_qubits)
        self.builder.idling_noise(self.data_qubits.values())
        self.builder.circ.append("TICK")

    def create_Z_face_ancilla(self, index):
        face_ancilla_qubits = dict()
        starting_x, starting_y = (1, self.diameter - 1)
        even = False
        for i in range(0, self.diameter-1):
            if even:
                for j in range(0, self.diameter - 2, 2):
                    self.builder.circ.append(
                        "QUBIT_COORDS", index, [starting_x + j, starting_y - j]
                    )
                    face_ancilla_qubits[starting_x + j, starting_y - j] = index
                    index += 1
            else:
                for j in range(0, self.diameter - 1, 2):
                    self.builder.circ.append(
                        "QUBIT_COORDS", index, [starting_x + j, starting_y - j]
                    )
                    face_ancilla_qubits[starting_x + j, starting_y - j] = index
                    index += 1
            if even:
                starting_x += 0
                even = False
                starting_y += 2
            else:
                starting_x += 2
                even = True
                starting_y += 0
        self.builder.circ.append("R", face_ancilla_qubits.values())

        return (face_ancilla_qubits, index)

    def create_X_face_ancilla(self):
        index = self.diameter**2
        X_face_ancilla_qubits = dict()
        starting_x, starting_y = (2, self.diameter-2)
        even = True
        for i in range(0, self.diameter-1):
            if even:
                for j in range(0, self.diameter - 2, 2):
                    self.builder.circ.append(
                        "QUBIT_COORDS", index, [starting_x + j, starting_y - j]
                    )
                    X_face_ancilla_qubits[starting_x + j, starting_y - j] = index
                    index += 1
            else:
                for j in range(0, self.diameter - 1, 2):
                    self.builder.circ.append(
                        "QUBIT_COORDS", index, [starting_x + j, starting_y - j]
                    )
                    X_face_ancilla_qubits[starting_x + j, starting_y - j] = index
                    index += 1
            if even:
                starting_x += 0
                even = False
                starting_y += 2
            else:
                starting_x += 2
                even = True
                starting_y += 0
        self.builder.circ.append("R", X_face_ancilla_qubits.values())

        return (X_face_ancilla_qubits, index)

    def create_X_boundary(self, index):
        X_left_boundary_ancilla_qubits = dict()
        X_top_boundary_ancilla_qubits = dict()
        X_right_boundary_ancilla_qubits = dict()
        X_bottom_boundary_ancilla_qubits = dict()
        starting_x, starting_y = (0, self.diameter - 2)
        for i in range(0, self.diameter - 1, 2):
            self.builder.circ.append(
                "QUBIT_COORDS", index, [starting_x + i, starting_y - i]
            )
            X_left_boundary_ancilla_qubits[starting_x + i, starting_y - i] = index
            index += 1

        starting_x, starting_y = (0, self.diameter)
        for i in range(0, self.diameter - 1, 2):
            self.builder.circ.append(
                "QUBIT_COORDS", index, [starting_x + i, starting_y + i]
            )
            X_top_boundary_ancilla_qubits[starting_x + i, starting_y + i] = index
            index += 1

        starting_x, starting_y = ((self.diameter - 1) * 2, self.diameter)
        for i in range(0, self.diameter - 1, 2):
            self.builder.circ.append(
                "QUBIT_COORDS", index, [starting_x - i, starting_y + i]
            )
            X_right_boundary_ancilla_qubits[starting_x - i, starting_y + i] = index
            index += 1

        starting_x, starting_y = (self.diameter, 0)
        for i in range(0, self.diameter - 1, 2):
            self.builder.circ.append(
                "QUBIT_COORDS", index, [starting_x + i, starting_y + i]
            )
            X_bottom_boundary_ancilla_qubits[starting_x + i, starting_y + i] = index
            index += 1

        self.builder.circ.append("R", X_top_boundary_ancilla_qubits.values())
        self.builder.circ.append("R", X_bottom_boundary_ancilla_qubits.values())
        self.builder.circ.append("R", X_left_boundary_ancilla_qubits.values())
        self.builder.circ.append("R", X_right_boundary_ancilla_qubits.values())
        return (X_left_boundary_ancilla_qubits, X_right_boundary_ancilla_qubits, X_top_boundary_ancilla_qubits, X_bottom_boundary_ancilla_qubits, index)

    def create_data_qubits(self):
        starting_x, starting_y = (0, self.diameter - 1)
        index = 0
        data_qubits = dict()
        for i in range(self.diameter):
            for j in range(self.diameter):
                coords = (starting_x + j, starting_y - j)
                self.builder.circ.append(
                    "QUBIT_COORDS", index, [starting_x + j, starting_y - j]
                )
                data_qubits[starting_x + j, starting_y - j] = index
                index += 1
            starting_x += 1
            starting_y += 1
        self.builder.circ.append("R", data_qubits.values())
        return data_qubits


if __name__ == "__main__":
    """
    surface_code_circuit = stim.Circuit.generated(
    "surface_code:rotated_memory_z",
    rounds=9,
    diameter=3,
    after_clifford_depolarization=0.001,
    after_reset_flip_probability=0.001,
    before_measure_flip_probability=0.001,
    before_round_data_depolarization=0.001)
    """

    shortsurfacecode = ShortSurfaceCode(3, 3, 0.1, 0.1, 0.1, 0.1, 0.1)
    print(shortsurfacecode.circ)
    """
    print(
        stimcirq.stim_circuit_to_cirq_circuit(shortsurfacecode.circ[50:]),
        file=open("circ.txt", "w"),
    )
    print(
        stimcirq.stim_circuit_to_cirq_circuit(shortsurfacecode.circ),
        file=open("full_circ.txt", "w"),
    )
    """
#    print(shortsurfacecode.circ)
#    print(len(shortsurfacecode.circ.shortest_graphlike_error()))
