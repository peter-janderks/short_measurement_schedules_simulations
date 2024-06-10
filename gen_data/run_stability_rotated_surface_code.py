import math
import stim
import sinter
import matplotlib.pyplot as plt
from circuits.stability_rotated_surface_code import StabilityRotatedSurfaceCode
import numpy as np


def get_normal_data(diameters, rounds, error_probabilities, measurement_noise_factor):
    samples_normal = sinter.collect(
        num_workers=10,
        max_shots=10_000_000,
        max_errors=1000,
        tasks=generate_SD6_tasks(
            diameters, rounds, error_probabilities, measurement_noise_factor),
        decoders=["pymatching"],
        save_resume_filepath=f"../INSERT_FILE_NAME_HERE",
        print_progress=True,
    )

    samples_normal = sinter.collect(
        num_workers=10,
        max_shots=10_000_000,
        max_errors=1000,
        tasks=generate_SI1000_tasks(diameters, rounds, error_probabilities),
        decoders=["pymatching"],
        save_resume_filepath=f"../INSERT_FILE_NAME_HERE",
        print_progress=True,
    )


def generate_SD6_tasks(diameters, rounds, error_probabilities, measurement_noise_factor):
    for diameter in diameters:
        #        for n_rounds in rounds:
        for p in error_probabilities:
            yield sinter.Task(
                # get it for the stim example
                circuit=StabilityRotatedSurfaceCode(diameter, diameter, p, 0,  p,
                                                    p, p*measurement_noise_factor, p).builder.circ,
                json_metadata={"p": p, "diameter": diameter, "code": "rotated_surface_code",
                               "noise_model": "SD6_" + str(measurement_noise_factor), "rounds": diameter}
            )


def generate_SI1000_tasks(diameters, rounds, error_probabilities):
    for diameter in diameters:
        for p in error_probabilities:
            yield sinter.Task(
                # get it for the stim example
                circuit=StabilityRotatedSurfaceCode(
                    diameter, diameter, p/10, 2*p, p/10, p, 5*p, 2*p).builder.circ,
                json_metadata={"p": p, "diameter": diameter, "code": "rotated_surface_code",
                               'noise_model': "SI1000", "rounds": diameter}
            )


def main():
    diameters = [4, 8, 10, 12, 14]
    rounds = [5, 10, 15]
    error_probabilities = np.linspace(0.0005, 0.005, 21)
    measurement_noise_factors = [1, 5, 10, 20]

    for measurement_noise_factor in measurement_noise_factors:
        get_normal_data(diameters, rounds, error_probabilities,
                        measurement_noise_factor)


if __name__ == "__main__":
    main()
