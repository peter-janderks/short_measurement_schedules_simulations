import math
import stim
import sinter
import matplotlib.pyplot as plt
from circuits.rotated_surface_code import RotatedSurfaceCode
import numpy as np


def get_normal_data(distances, error_probabilities, measurement_noise_factor, rounds=None):

    samples_normal = sinter.collect(
        num_workers=10,
        max_shots=10_000_000,
        max_errors=1000,
        tasks=generate_SD6_tasks(
            distances, error_probabilities, rounds, measurement_noise_factor),
        decoders=["pymatching"],
        save_resume_filepath=f"./data/13_4_memory_data_new/rotated_surface_code.csv",
        print_progress=True,
    )

    samples_normal = sinter.collect(
        num_workers=10,
        max_shots=10_000_000,
        max_errors=1000,
        tasks=generate_SI1000_tasks(distances, error_probabilities, rounds),
        decoders=["pymatching"],
        save_resume_filepath=f"./data/13_4_memory_data_new/rotated_surface_code.csv",
        print_progress=True,
    )


def generate_SD6_tasks(distances, error_probabilities, rounds, measurement_noise_factor):
    for d in distances:
        for p in error_probabilities:
            stim_circuit = RotatedSurfaceCode(
                d, p, 0,  p, p, measurement_noise_factor * p, p, rounds).builder.circ
            circuit_path = "stim_circuits/memory_rotated_surface_code_SD6_d" + \
                str(d) + "_measurement_noise_factor" + \
                str(measurement_noise_factor) + "_p" + str(p) + ".stim"
            stim_circuit.to_file(circuit_path)
            yield sinter.Task(
                # get it for the stim example
                circuit=stim_circuit,
                json_metadata={"p": p, "d": d, "code": "rotated_surface_code",
                               f"noise_model": "SD6_" + str(measurement_noise_factor), "rounds": rounds}
            )


def generate_SI1000_tasks(distances, error_probabilities, rounds):
    for d in distances:
        for p in error_probabilities:
            stim_circuit = RotatedSurfaceCode(
                d, p/10, 2*p, p/10, p, 5*p, 2*p, rounds).builder.circ
            circuit_path = "stim_circuits/memory_rotated_surface_code_SI000_d" + \
                str(d) + "_p" + str(p) + ".stim"
            stim_circuit.to_file(circuit_path)
            yield sinter.Task(
                # get it for the stim example
                circuit=stim_circuit,
                json_metadata={"p": p, "d": d, "code": "rotated_surface_code",
                               'noise_model': "SI1000", "rounds": rounds}
            )


USED_NOISE_VALUES = np.linspace(0.0005, 0.005, 21)


def main():

    data_to_collect = dict()
    data_to_collect = {
        (5, 7, 9, 11, 13, 15): USED_NOISE_VALUES, }
    # Collect the samples (takes a few minutes).
    measurement_noise_factors = [1, 5, 10, 20]
    for distances, error_probabilities in data_to_collect.items():
        for measurement_noise_factor in measurement_noise_factors:
            get_normal_data(list(distances), list(
                error_probabilities), measurement_noise_factor, rounds=0)


if __name__ == "__main__":
    main()
