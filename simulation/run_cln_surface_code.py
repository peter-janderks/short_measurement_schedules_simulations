import math
import stim
import sinter
import matplotlib.pyplot as plt
from circuits.cln_short_surface_code import ShortSurfaceCode
from circuits.rsc_surface_code import create_surface_code
import numpy as np

# add idling error option...


def get_short_data(distances, error_probabilities, p_I):
    samples_short = sinter.collect(
        num_workers=10,
        max_shots=20_000_000,
        max_errors=100,
        tasks=generate_short_tasks(distances, error_probabilities, p_I),
        decoders=["pymatching"],
        save_resume_filepath=f"../data/new_short_surface_code_p_I_{p_I}.csv",
        print_progress=True,
    )


def generate_short_tasks(distances, error_probabilities, p_I):
    for d in distances:
        for p in error_probabilities:

            yield sinter.Task(
                circuit=ShortSurfaceCode(d, d, p_I * p, p, p, p, p).circ,
                json_metadata={
                    "p": p,
                    "d": d,
                    "code": "short_surface_code",
                    "p_I": p_I,
                },
            )


def get_normal_data(distances, error_probabilities, p_I):
    samples_normal = sinter.collect(
        num_workers=10,
        max_shots=20_000_000,
        max_errors=100,
        tasks=generate_normal_tasks(distances, error_probabilities, p_I),
        decoders=["pymatching"],
        save_resume_filepath=f"../data/new_surface_code_p_I_{p_I}.csv",
        print_progress=True,
    )


def generate_normal_tasks(distances, error_probabilities, p_I):
    for d in distances:
        for p in error_probabilities:

            yield sinter.Task(
                # get it for the stim example
                circuit=create_surface_code(d, d, p_I * p, p, p, p, p),
                json_metadata={"p": p, "d": d, "code": "surface_code", "p_I": p_I},
            )


USED_NOISE_VALUES = [
    0.0001,
    0.0002,
    0.0003,
    0.0005,
    0.0007,
    0.0010,
    0.0015,
    0.0020,
    0.0030,
    0.0050,
    0.0070,
    0.0100,
    0.0150,
    0.0200,
    0.0300,
]


def main():

    data_to_collect = dict()
    data_to_collect["1"] = {
        #    (3, 5): USED_NOISE_VALUES,
        #     (7, 9): USED_NOISE_VALUES[3:],
        (7,): [0.0002],
        #     (11): USED_NOISE_VALUES[6:],
    }
    data_to_collect["0.75"] = {
        #        (3, 5): USED_NOISE_VALUES,
        #        (7, 9): USED_NOISE_VALUES[3:],
        #    (11, 13): USED_NOISE_VALUES[5:],
        (7,): [0.0002],
    }
    data_to_collect["0.5"] = {
        #        (3, 5): USED_NOISE_VALUES[1:],
        #        (7, 9): USED_NOISE_VALUES[4:],
        #    (11, 13): USED_NOISE_VALUES[6:],
        (7,): [0.0003],
    }
    data_to_collect["0.25"] = {
        #        (3, 5): USED_NOISE_VALUES[1:],
        #        (7, 9): USED_NOISE_VALUES[4:],
        #    (11, 13): USED_NOISE_VALUES[6:],
        (7,): [0.0002, 0.0003],
    }
    data_to_collect["0.1"] = {
        #        (3, 5): USED_NOISE_VALUES[2:],
        #        (7, 9): USED_NOISE_VALUES[5:],
        #    (11, 13): USED_NOISE_VALUES[7:],
        (7,): [0.0005],
    }

    data_to_collect["0.05"] = {
        #        (3, 5): USED_NOISE_VALUES[2:],
        #        (7, 9): USED_NOISE_VALUES[5:],
        #    (11, 13): USED_NOISE_VALUES[7:],
        (5, 7): [0.0003, 0.0005],
    }

    # Collect the samples (takes a few minutes).
    for p_I in data_to_collect.keys():
        for distances, error_probabilities in data_to_collect[p_I].items():
            print(distances, error_probabilities)

            get_short_data(list(distances), list(error_probabilities), float(p_I))
            get_normal_data(list(distances), list(error_probabilities), float(p_I))


if __name__ == "__main__":
    main()
