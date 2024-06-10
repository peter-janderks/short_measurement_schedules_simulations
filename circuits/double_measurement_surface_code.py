import stim
# import stimcirq
from circuits.circuit_builder import CircuitBuilder


class DoubleMeasurementSurfaceCode(object):
    def __init__(self, distance, p_idling, p_resonator_idling, p_1, p_2, p_m, p_prep, rounds=0, ft_version=True):
        self.builder = CircuitBuilder(float(p_idling), float(p_resonator_idling),
                                      float(p_1), float(p_2), float(p_m), float(p_prep))
        self.distance = int(distance)
        (self.data_qubits,
         self.builder.X_face_ancilla,
         self.builder.X_face_flags,
         self.builder.Z_face_ancilla,
         self.builder.Z_face_flags,
         self.builder.X_left_boundary_ancilla,
         self.builder.X_left_boundary_flags,
         self.builder.X_right_boundary_ancilla,
         self.builder.X_right_boundary_flags,
         self.builder.Z_top_boundary_ancilla,
         self.builder.Z_top_boundary_flags,
         self.builder.Z_bottom_boundary_ancilla,
         self.builder.Z_bottom_boundary_flags) = self.create_t0()

        self.builder.ancilla_qubits_ind_to_coord.update(
            {ind: coord for coord, ind in self.builder.X_face_ancilla.items()})
        self.builder.ancilla_qubits_ind_to_coord.update(
            {ind: coord for coord, ind in self.builder.X_face_flags.items()})
        self.builder.ancilla_qubits_ind_to_coord.update(
            {ind: coord for coord, ind in self.builder.Z_face_ancilla.items()})
        self.builder.ancilla_qubits_ind_to_coord.update(
            {ind: coord for coord, ind in self.builder.Z_face_flags.items()})
        self.builder.ancilla_qubits_ind_to_coord.update(
            {ind: coord for coord, ind in self.builder.X_left_boundary_ancilla.items()})
        self.builder.ancilla_qubits_ind_to_coord.update(
            {ind: coord for coord, ind in self.builder.X_left_boundary_flags.items()})
        self.builder.ancilla_qubits_ind_to_coord.update(
            {ind: coord for coord, ind in self.builder.X_right_boundary_ancilla.items()})
        self.builder.ancilla_qubits_ind_to_coord.update(
            {ind: coord for coord, ind in self.builder.X_right_boundary_flags.items()})
        self.builder.ancilla_qubits_ind_to_coord.update(
            {ind: coord for coord, ind in self.builder.Z_top_boundary_ancilla.items()})
        self.builder.ancilla_qubits_ind_to_coord.update(
            {ind: coord for coord, ind in self.builder.Z_top_boundary_flags.items()})
        self.builder.ancilla_qubits_ind_to_coord.update(
            {ind: coord for coord, ind in self.builder.Z_bottom_boundary_ancilla.items()})
        self.builder.ancilla_qubits_ind_to_coord.update(
            {ind: coord for coord, ind in self.builder.Z_bottom_boundary_flags.items()})

        all_qubits = (
            set(self.data_qubits.values())
            | set(self.builder.X_face_ancilla.values())
            | set(self.builder.X_face_flags.values())
            | set(self.builder.Z_face_ancilla.values())
            | set(self.builder.Z_face_flags.values())
            | set(self.builder.X_left_boundary_ancilla.values())
            | set(self.builder.X_left_boundary_flags.values())
            | set(self.builder.X_right_boundary_ancilla.values())
            | set(self.builder.X_right_boundary_flags.values())
            | set(self.builder.Z_top_boundary_ancilla.values())
            | set(self.builder.Z_top_boundary_flags.values())
            | set(self.builder.Z_bottom_boundary_ancilla.values())
            | set(self.builder.Z_bottom_boundary_flags.values())
        )

        self.ancilla_qubits_without_flags_dict = (self.builder.X_face_ancilla | self.builder.Z_face_ancilla | self.builder.X_left_boundary_ancilla | self.builder.X_right_boundary_ancilla | self.builder.Z_top_boundary_ancilla |
                                                  self.builder.Z_bottom_boundary_ancilla)
        self.flag_qubit_dict = (self.builder.X_face_flags | self.builder.Z_face_flags | self.builder.X_right_boundary_flags | self.builder.X_left_boundary_flags |
                                self.builder.Z_top_boundary_flags | self.builder.Z_bottom_boundary_flags)

        self.ancilla_qubit_dict = (self.ancilla_qubits_without_flags_dict | self.flag_qubit_dict)
        self.build_six_layers(all_qubits)
        self.first_time_measuring_ancillas(all_qubits)
        self.builder.idling_noise(self.builder.idling_qubits)
        self.builder.resonator_idling_noise(self.builder.idling_qubits)
        self.initialize_ancilla_qubits()

        starting_circ = self.builder.circ.copy()
        self.builder.circ = stim.Circuit()
        self.build_six_layers(all_qubits)
        self.measure_ancilla_qubits(0, all_qubits)
        self.builder.idling_noise(self.builder.idling_qubits)
        self.builder.resonator_idling_noise(self.builder.idling_qubits)
        self.initialize_ancilla_qubits()
        self.builder.circ = starting_circ + self.builder.circ

        if distance > 3 and rounds != 0:
            starting_circ = self.builder.circ.copy()
            self.builder.circ = stim.Circuit()
            self.build_six_layers(all_qubits)
            self.measure_ancilla_qubits(0, all_qubits)
            self.builder.idling_noise(self.builder.idling_qubits)
            self.builder.resonator_idling_noise(self.builder.idling_qubits)
            self.initialize_ancilla_qubits()
            self.builder.circ = starting_circ + (self.distance-3)*self.builder.circ

        else:
            starting_circ = self.builder.circ.copy()
            self.builder.circ = stim.Circuit()
            self.build_six_layers(all_qubits)
            self.measure_ancilla_qubits(0, all_qubits)
            self.builder.idling_noise(self.builder.idling_qubits)
            self.builder.resonator_idling_noise(self.builder.idling_qubits)
            self.initialize_ancilla_qubits()
            self.builder.circ = starting_circ + (int(rounds)-3)*self.builder.circ

        self.build_six_layers(all_qubits)
        self.measure_ancilla_qubits(1, all_qubits)
        self.measure_data_qubits(1, all_qubits)

    def build_six_layers(self, all_qubits):
        self.builder.build_layer(self.l0, all_qubits)
        self.builder.build_layer(self.l1, all_qubits)
        self.builder.build_layer(self.l2, all_qubits)
        self.builder.build_layer(self.l3, all_qubits)
        self.builder.build_layer(self.l4, all_qubits)
        self.builder.build_layer(self.l5, all_qubits)
        self.builder.build_layer(self.l6, all_qubits)

    def create_t0(self):
        data_qubits = self.create_data_qubits()
        X_face_ancilla, X_face_flags, index = self.create_X_face_ancilla()
        Z_face_ancilla, Z_face_flags, index = self.create_Z_face_ancilla(index)
        X_left_boundary_ancilla, X_left_boundary_flags, X_right_boundary_ancilla, X_right_boundary_flags, index = self.create_X_boundary(
            index)
        Z_top_boundary_ancilla, Z_top_boundary_flags,  Z_bottom_boundary_ancilla, Z_bottom_boundary_flags, index = self.create_Z_boundary(
            index)

        initialized_qubits = list(data_qubits.values())
        initialized_qubits.extend(list(X_face_ancilla.values()))
        initialized_qubits.extend(list(X_face_flags.values()))
        initialized_qubits.extend(list(Z_face_ancilla.values()))
        initialized_qubits.extend(list(Z_face_flags.values()))
        initialized_qubits.extend(list(X_left_boundary_ancilla.values()))
        initialized_qubits.extend(list(X_left_boundary_flags.values()))
        initialized_qubits.extend(list(X_right_boundary_ancilla.values()))
        initialized_qubits.extend(list(X_right_boundary_flags.values()))
        initialized_qubits.extend(list(Z_top_boundary_ancilla.values()))
        initialized_qubits.extend(list(Z_top_boundary_flags.values()))
        initialized_qubits.extend(list(Z_bottom_boundary_ancilla.values()))
        initialized_qubits.extend(list(Z_bottom_boundary_flags.values()))
        self.builder.p_prep_noise(initialized_qubits)
        return (
            data_qubits,
            X_face_ancilla,
            X_face_flags,
            Z_face_ancilla,
            Z_face_flags,
            X_left_boundary_ancilla,
            X_left_boundary_flags,
            X_right_boundary_ancilla,
            X_right_boundary_flags,
            Z_top_boundary_ancilla,
            Z_top_boundary_flags,
            Z_bottom_boundary_ancilla,
            Z_bottom_boundary_flags,
        )

    def build_same_round_detectors(self, z_cor):
        for ancilla_coords, ancilla_index in self.ancilla_qubits_without_flags_dict.items():
            flag_ancilla_index = self.flag_qubit_dict[ancilla_coords[0]+0.5, ancilla_coords[1]-0.5]
            self.builder.circ.append("DETECTOR", [stim.target_rec(self.builder.measurement_order[ancilla_index]),
                                     stim.target_rec(self.builder.measurement_order[flag_ancilla_index])],
                                     (ancilla_coords[0], ancilla_coords[1], z_cor))

    def build_first_round_detectors(self, q_indexes_measure, z_cor=0):
        self.builder.update_measurement_order(q_indexes_measure)
        for measurement_number, ancilla_index in enumerate(q_indexes_measure):
            x_cord, y_cord = self.builder.ancilla_qubits_ind_to_coord[ancilla_index]
            self.builder.circ.append("DETECTOR", stim.target_rec(
                measurement_number-len(q_indexes_measure)), (x_cord, y_cord, z_cor))

    def build_ancilla_detector(self, z_cor):
        for m_index, (q_coords, q_index) in enumerate(self.ancilla_qubit_dict.items()):

            x_cor, y_cor = q_coords[0], q_coords[1]
            if x_cor % 1 == 0:
                f_index = self.flag_qubit_dict[x_cor + 0.5, y_cor - 0.5]
                self.builder.circ.append(
                    "DETECTOR",
                    [
                        stim.target_rec(m_index - len(self.ancilla_qubit_dict)),
                        stim.target_rec(
                            self.builder.measurement_order[f_index]
                            - len(self.ancilla_qubit_dict)
                        ),
                    ],
                    (x_cor, y_cor, z_cor)
                )

    def measure_ancilla_qubits(self, z_cor, all_qubits):
        self.builder.idling_qubits = all_qubits.copy()
        self.builder.M(list(self.ancilla_qubit_dict.values()))
        self.build_ancilla_detector(z_cor)
        self.builder.update_measurement_order(list(self.ancilla_qubit_dict.values()))
        self.build_same_round_detectors(z_cor)

    def initialize_ancilla_qubits(self):
        self.builder.circ.append("TICK")
        for q in self.ancilla_qubit_dict.values():
            self.builder.circ.append("R", q)
        self.builder.p_prep_noise(self.ancilla_qubit_dict.values())
        self.builder.idling_noise(self.data_qubits.values())
        self.builder.resonator_idling_noise(self.data_qubits.values())
        self.builder.circ.append("TICK")

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
        self.z_bound_detector_bottom(list(self.builder.Z_bottom_boundary_ancilla.values()),
                                     list(self.builder.Z_bottom_boundary_ancilla.keys()), z_cor)

        self.z_bound_detector_top(
            list(self.builder.Z_top_boundary_ancilla.values()),
            list(self.builder.Z_top_boundary_ancilla.keys()), z_cor
        )

        self.add_logical_observable()

    def add_logical_observable(self):

        starting_x, starting_y = 0, self.distance - 1
        measurement_for_observable = []
        for i in range(0, self.distance, 1):
            measurement_for_observable.append(
                stim.target_rec(
                    self.builder.measurement_order[
                        self.data_qubits[starting_x + i, starting_y - i]
                    ]
                )
            )
        self.builder.circ.append("OBSERVABLE_INCLUDE", measurement_for_observable, 0)

    def l0(self):
        for qubit in self.builder.X_face_ancilla.values():
            self.builder.H(qubit)

        for qubit in self.builder.X_face_flags.values():
            self.builder.H(qubit)

        for qubit in self.builder.X_left_boundary_ancilla.values():
            self.builder.H(qubit)

        for qubit in self.builder.X_left_boundary_flags.values():
            self.builder.H(qubit)

        for qubit in self.builder.X_right_boundary_ancilla.values():
            self.builder.H(qubit)

        for qubit in self.builder.X_right_boundary_flags.values():
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

        for coords, q_index in self.builder.Z_top_boundary_ancilla.items():
            self.builder.cnot(
                self.data_qubits[coords[0] + 1, coords[1]], q_index
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

        for coords, q_index in self.builder.Z_top_boundary_ancilla.items():
            self.builder.cnot(self.data_qubits[coords[0], coords[1] - 1], q_index)

    def l3(self):
        for coords, q_index in self.builder.X_face_ancilla.items():
            self.builder.cnot(q_index, self.data_qubits[coords[0], coords[1] - 1])

        for coords, q_index in self.builder.Z_face_ancilla.items():
            self.builder.cnot(self.data_qubits[coords[0], coords[1] + 1], q_index)

        for coords, q_index in self.builder.Z_bottom_boundary_ancilla.items():
            self.builder.cnot(self.data_qubits[coords[0], coords[1] + 1], q_index)

        for coords, q_index in self.builder.X_right_boundary_ancilla.items():
            self.builder.cnot(q_index, self.data_qubits[coords[0], coords[1] - 1])

    def l4(self):
        for coords, q_index in self.builder.X_face_ancilla.items():
            self.builder.cnot(q_index, self.data_qubits[coords[0] - 1, coords[1]])

        for coords, q_index in self.builder.Z_face_ancilla.items():
            self.builder.cnot(self.data_qubits[coords[0] - 1, coords[1]], q_index)

        for coords, q_index in self.builder.Z_bottom_boundary_ancilla.items():
            self.builder.cnot(
                self.data_qubits[coords[0] - 1, coords[1]],
                q_index,
            )

        for coords, q_index in self.builder.X_right_boundary_ancilla.items():
            self.builder.cnot(q_index, self.data_qubits[coords[0] - 1, coords[1]])

    def l5(self):
        for coords, q_index in self.builder.X_face_ancilla.items():
            self.builder.cnot(self.builder.X_face_flags[coords[0]+0.5, coords[1]-0.5], q_index)

        for coords, q_index in self.builder.X_left_boundary_ancilla.items():
            self.builder.cnot(self.builder.X_left_boundary_flags[coords[0]+0.5, coords[1]-0.5], q_index)

        for coords, q_index in self.builder.Z_top_boundary_ancilla.items():
            self.builder.cnot(q_index, self.builder.Z_top_boundary_flags[coords[0]+0.5, coords[1]-0.5])

        for coords, q_index in self.builder.Z_face_ancilla.items():
            self.builder.cnot(q_index, self.builder.Z_face_flags[coords[0]+0.5, coords[1]-0.5])

        for coords, q_index in self.builder.X_right_boundary_ancilla.items():
            self.builder.cnot(self.builder.X_right_boundary_flags[coords[0]+0.5, coords[1]-0.5], q_index)

        for coords, q_index in self.builder.Z_bottom_boundary_ancilla.items():
            self.builder.cnot(q_index, self.builder.Z_bottom_boundary_flags[coords[0]+0.5, coords[1]-0.5])

    def l6(self):
        for qubit in self.builder.X_face_ancilla.values():
            self.builder.H(qubit)

        for qubit in self.builder.X_face_flags.values():
            self.builder.H(qubit)

        for qubit in self.builder.X_left_boundary_ancilla.values():
            self.builder.H(qubit)

        for qubit in self.builder.X_left_boundary_flags.values():
            self.builder.H(qubit)

        for qubit in self.builder.X_right_boundary_ancilla.values():
            self.builder.H(qubit)

        for qubit in self.builder.X_right_boundary_flags.values():
            self.builder.H(qubit)

    def first_time_measuring_ancillas(self, all_qubits):
        self.builder.idling_qubits = all_qubits.copy()
        qubits_to_measure = list(self.builder.X_face_ancilla.values())
        qubits_to_measure.extend(list(self.builder.X_face_flags.values()))
        qubits_to_measure.extend(list(self.builder.X_left_boundary_ancilla.values()))
        qubits_to_measure.extend(list(self.builder.X_left_boundary_flags.values()))
        qubits_to_measure.extend(list(self.builder.X_right_boundary_ancilla.values()))
        qubits_to_measure.extend(list(self.builder.X_right_boundary_flags.values()))
        qubits_to_measure.extend(list(self.builder.Z_face_flags.values()))
        qubits_to_measure.extend(list(self.builder.Z_top_boundary_flags.values()))
        qubits_to_measure.extend(list(self.builder.Z_bottom_boundary_flags.values()))

        self.builder.M(qubits_to_measure)
        self.builder.update_measurement_order(qubits_to_measure)

        qubits_to_measure_deterministic = list(self.builder.Z_face_ancilla.values())
        qubits_to_measure_deterministic.extend(
            list(self.builder.Z_top_boundary_ancilla.values())
        )
        qubits_to_measure_deterministic.extend(
            list(self.builder.Z_bottom_boundary_ancilla.values())
        )
        self.builder.M(qubits_to_measure_deterministic)
        self.build_first_round_detectors(qubits_to_measure_deterministic, 0)

        self.build_same_round_detectors(0)
        self.builder.idling_noise(self.builder.idling_qubits)
        self.builder.resonator_idling_noise(self.builder.idling_qubits)

        self.builder.circ.append("TICK")
        for q in self.ancilla_qubit_dict.values():
            self.builder.circ.append("R", q)
        self.builder.p_prep_noise(self.ancilla_qubit_dict.values())
        self.builder.idling_noise(self.data_qubits.values())
        self.builder.circ.append("TICK")

    def create_Z_face_ancilla(self, index):
        face_ancilla_qubits = dict()
        Z_face_flags = dict()
        starting_x, starting_y = (1, self.distance - 1)
        even = False
        for i in range(0, self.distance-1):
            for j in range(0, self.distance - 1, 2):
                self.builder.circ.append(
                    "QUBIT_COORDS", index, [starting_x + j, starting_y - j]
                )
                face_ancilla_qubits[starting_x + j, starting_y - j] = index
                Z_face_flags[starting_x + j + 0.5, starting_y - j - 0.5] = index + 1
                index += 2
            if even:
                starting_x += 0
                even = False
                starting_y += 2
            else:
                starting_x += 2
                even = True
                starting_y += 0
        self.builder.circ.append("R", face_ancilla_qubits.values())
        self.builder.circ.append("R", Z_face_flags.values())
        return (face_ancilla_qubits, Z_face_flags, index)

    def create_X_face_ancilla(self):
        index = self.distance**2
        X_face_ancilla_qubits = dict()
        X_face_flags = dict()
        starting_x, starting_y = (2, self.distance-2)
        even = True
        for i in range(0, self.distance-1):
            for j in range(0, self.distance - 1, 2):
                self.builder.circ.append(
                    "QUBIT_COORDS", index, [starting_x + j, starting_y - j]
                )
                X_face_ancilla_qubits[starting_x + j, starting_y - j] = index
                X_face_flags[starting_x+j+0.5, starting_y - j - 0.5] = index + 1
                index += 2
            if even:
                starting_x += 0
                even = False
                starting_y += 2
            else:
                starting_x += 2
                even = True
                starting_y += 0
        self.builder.circ.append("R", X_face_ancilla_qubits.values())
        self.builder.circ.append("R", X_face_flags.values())
        return (X_face_ancilla_qubits, X_face_flags, index)

    def create_X_boundary(self, index):
        X_left_boundary_ancilla_qubits = dict()
        X_left_boundary_flags = dict()
        X_right_boundary_ancilla_qubits = dict()
        X_right_boundary_flags = dict()
        starting_x, starting_y = (0, self.distance - 2)
        for i in range(0, self.distance - 1, 2):
            self.builder.circ.append(
                "QUBIT_COORDS", index, [starting_x + i, starting_y - i]
            )
            X_left_boundary_ancilla_qubits[starting_x + i, starting_y - i] = index
            X_left_boundary_flags[starting_x + i +
                                  0.5, starting_y-i-0.5] = index + 1
            index += 2

        starting_x, starting_y = ((self.distance - 1) * 2, self.distance)
        for i in range(0, self.distance - 1, 2):
            self.builder.circ.append(
                "QUBIT_COORDS", index, [starting_x - i, starting_y + i]
            )
            X_right_boundary_ancilla_qubits[starting_x - i, starting_y + i] = index
            X_right_boundary_flags[starting_x-i +
                                   0.5, starting_y+i-0.5] = index + 1
            index += 2

        self.builder.circ.append("R", X_left_boundary_ancilla_qubits.values())
        self.builder.circ.append("R", X_right_boundary_ancilla_qubits.values())
        self.builder.circ.append("R", X_left_boundary_flags.values())
        self.builder.circ.append("R", X_right_boundary_flags.values())
        return (X_left_boundary_ancilla_qubits, X_left_boundary_flags, X_right_boundary_ancilla_qubits, X_right_boundary_flags, index)

    def create_data_qubits(self):
        starting_x, starting_y = (0, self.distance - 1)
        index = 0
        data_qubits = dict()
        for i in range(self.distance):
            for j in range(self.distance):
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

    def create_Z_boundary(self, index):
        bottom_boundary_ancilla_qubits = dict()
        bottom_boundary_flags = dict()
        starting_x, starting_y = (self.distance, 0)
        for i in range(0, self.distance - 1, 2):
            self.builder.circ.append(
                "QUBIT_COORDS", index, [starting_x + i, starting_y + i]
            )
            bottom_boundary_ancilla_qubits[starting_x + i, starting_y + i] = index
            bottom_boundary_flags[starting_x+i +
                                  0.5, starting_y+i-0.5] = index + 1

            index += 2

        top_boundary_ancilla_qubits = dict()
        top_boundary_flags = dict()
        starting_x, starting_y = (1, self.distance + 1)
        for i in range(0, self.distance - 1, 2):
            self.builder.circ.append(
                "QUBIT_COORDS", index, [starting_x + i, starting_y + i]
            )
            top_boundary_ancilla_qubits[starting_x + i, starting_y + i] = index
            top_boundary_flags[starting_x+i+0.5, starting_y+i-0.5] = index + 1
            index += 2
        self.builder.circ.append("R", top_boundary_ancilla_qubits.values())
        self.builder.circ.append("R", top_boundary_flags.values())
        self.builder.circ.append("R", bottom_boundary_ancilla_qubits.values())
        self.builder.circ.append("R", bottom_boundary_flags.values())
        return (top_boundary_ancilla_qubits, top_boundary_flags, bottom_boundary_ancilla_qubits, bottom_boundary_flags, index)

