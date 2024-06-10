import math
import stim
import sinter
import matplotlib.pyplot as plt
from circuits.double_measurement_surface_code import DoubleMeasurementSurfaceCode
import numpy as np


def get_normal_data(distances, error_probabilities, measurement_noise_factor, rounds):

    samples_normal = sinter.collect(
        num_workers=10,
        max_shots=10_000_000,
        max_errors=1000,
        tasks=generate_SD6_tasks(distances, error_probabilities, rounds, measurement_noise_factor),
        decoders=["pymatching"],
        save_resume_filepath=f"../INSERT_FILE_NAME_HERE",
        print_progress=True,
    )

    samples_normal = sinter.collect(
        num_workers=10,
        max_shots=10_000_000,
        max_errors=1000,
        tasks=generate_SI1000_tasks(distances, error_probabilities, rounds),
        decoders=["pymatching"],
        save_resume_filepath=f"../INSERT_FILE_NAME_HERE",
        print_progress=True,
    )


def generate_SD6_tasks(distances, error_probabilities, rounds, measurement_noise_factor):
    for d in distances:
        for p in error_probabilities:
            yield sinter.Task(
                # get it for the stim example
                circuit=DoubleMeasurementSurfaceCode(
                    d, p, 0,  p, p, measurement_noise_factor*p, p, rounds).builder.circ,
                json_metadata={"p": p, "d": d, "code": "double_measurement_surface_code",
                               "noise_model": "SD6_" + str(measurement_noise_factor), "rounds": rounds}
            )


def generate_SI1000_tasks(distances, error_probabilities, rounds):
    for d in distances:
        for p in error_probabilities:
            yield sinter.Task(
                # get it for the stim example
                circuit=DoubleMeasurementSurfaceCode(d, p/10, 2*p, p/10, p, 5*p, 2*p, rounds).builder.circ,
                json_metadata={"p": p, "d": d, "code": "double_measurement_surface_code",
                               'noise_model': "SI1000", "rounds": rounds}
            )


USED_NOISE_VALUES = np.linspace(0.0005, 0.005, 21)


def main():

    data_to_collect = dict()
    data_to_collect = {
        (5, 7, 9, 11, 13, 15): USED_NOISE_VALUES,
    }
    measurement_noise_factors = [1, 5, 10, 20]

    # Collect the samples (takes a few minutes).
    for distances, error_probabilities in data_to_collect.items():
        for measurement_noise_factor in measurement_noise_factors:
            get_normal_data(list(distances), list(error_probabilities), measurement_noise_factor, 1)


if __name__ == "__main__":
    main()
