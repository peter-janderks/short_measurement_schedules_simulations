import stim
import sinter
import matplotlib.pyplot as plt
from rep_code import create_rep_code


def generate_example_tasks():
    for d in [3]:
        for p in [0.001, 0.0025, 0.005, 0.0075, 0.01]:
            yield sinter.Task(
                circuit=create_rep_code(True, True, True, True, p),
                json_metadata={"p": p, "d": d},
            )


def main():
    # Collect the samples (takes a few minutes).
    samples = sinter.collect(
        num_workers=4,
        max_shots=100_000,
        max_errors=100,
        tasks=generate_example_tasks(),
        decoders=["pymatching"],
    )

    # Print samples as CSV data.
    print(sinter.CSV_HEADER)
    for sample in samples:
        print(sample.to_csv_line())

    # Render a matplotlib plot of the data.
    fig, ax = plt.subplots(1, 1)
    sinter.plot_error_rate(
        ax=ax,
        stats=samples,
        group_func=lambda stat: f"Rotated Surface Code d={stat.json_metadata['d']}",
        x_func=lambda stat: stat.json_metadata["p"],
    )
    ax.loglog()
    ax.set_ylim(1e-5, 1)
    ax.grid()
    ax.set_title("Logical Error Rate vs Physical Error Rate")
    ax.set_ylabel("Logical Error Probability (per shot)")
    ax.set_xlabel("Physical Error Rate")
    ax.legend()

    # Save to file and also open in a window.
    fig.savefig("plot.png")
    plt.show()


if __name__ == "__main__":
    main()
