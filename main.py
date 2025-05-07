from pathlib import Path
import skeletonkey as sk
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


def load_name_data(file: Path | str) -> list[tuple[str, str, int]]:
    rows = []
    with open(file) as f:
        while (line := f.readline()) != '':
            name, gender, count = line.split(",")
            rows.append((name, gender, int(count),))
    return rows


def find_top_n_longest_lexi_names(
    names: list[tuple[str, str, int]],
    n: int = 5,
    verbose: bool = True,
) -> list[str]:
    lexi_sorted_names = []
    for name, gender, count in names:
        if name.lower() == ''.join(sorted(name.lower())):
            lexi_sorted_names.append((name, gender, count,))

    long_sorted_names = sorted(
        lexi_sorted_names,
        key=lambda row: len(row[0]),
        reverse=True,
    )
    return long_sorted_names[:n]


def plot_sorted_names_with_labels(
    dir_path: str,
    normalize_by_frequency: bool = True,
) -> None:
    years, percents = [], []
    labels = {}

    for file in sorted(Path(dir_path).glob("yob*.txt")):
        year = int(file.stem[3:])
        rows = load_name_data(file)

        population = sum(c for *_, c in rows)

        # compute count or sum of counts for sorted names
        if not normalize_by_frequency:
            count = sum(1 for n, *_ in rows
                        if n.lower() == ''.join(sorted(n.lower())))
        else:
            count = sum(c for n, _, c in rows
                        if n.lower() == ''.join(sorted(n.lower())))

        pct = count / population
        years.append(year)
        percents.append(pct)

        if year % 5 == 0:
            sorted_rows = [(n, c) for n, _, c in rows
                           if n.lower() == ''.join(sorted(n.lower()))]
            if sorted_rows:
                top_name, top_count = max(sorted_rows, key=lambda x: x[1])
                labels[year] = (top_name, top_count / population, pct)

    fig, ax = plt.subplots()
    ax.plot(years, percents, marker='o', linewidth=1)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))

    for yr, (name, pct, overall_pct) in labels.items():
        ax.annotate(
            f"{name}\n{pct:.1%}",
            xy=(yr, overall_pct),
            xytext=(0, 8),
            textcoords='offset points',
            ha='center',
            fontsize=8
        )

    ax.set_xlabel("Year")
    ax.set_ylabel("Percentage of lex. sorted names")
    ax.set_title("Percent of Sorted Names per Year")
    plt.tight_layout()
    plt.show()


@sk.unlock(str(Path(__file__).parent / 'configs/config.yaml'))
def main(cfg):
    name_path = Path(cfg.name_path)

    names = load_name_data(name_path)
    print(find_top_n_longest_lexi_names(names))

    plot_sorted_names_with_labels(
        name_path.parent,
        normalize_by_frequency=True,
    )


if __name__ == "__main__":
    main()
