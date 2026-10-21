"""Small, general Matplotlib commands: choose your data, labels and layout.

    chart = plot(times, {"Left": left, "Right": right}, ylabel="Distance (m)")
    chart.save("distance.png")
    show()

For several panels, use figure(rows=2) and chart.plot(...) for each panel.
This module never reads sensors or advances simulation.
"""

from collections.abc import Mapping
from pathlib import Path

import numpy as np

OUTPUT = Path(__file__).resolve().parents[1] / "outputs"


def _series(x, y, labels):
    x = np.asarray(x, dtype=float)
    if x.ndim != 1 or not len(x):
        raise ValueError("x must be a nonempty 1D array")
    if isinstance(y, Mapping):
        if not y:
            raise ValueError("y must contain at least one series")
        if labels is None:
            labels = list(y)
        columns = [np.asarray(column, dtype=float) for column in y.values()]
        if any(column.shape != x.shape for column in columns):
            raise ValueError("each y series must have the same length as x")
        y = np.column_stack(columns)
    else:
        y = np.asarray(y, dtype=float)
        if y.ndim == 1:
            y = y[:, None]
    if y.ndim != 2 or y.shape[0] != len(x) or y.shape[1] == 0:
        raise ValueError("y must have shape (samples,) or (samples, series)")
    if isinstance(labels, str):
        labels = [labels]
    if labels is not None:
        labels = list(labels)
        if len(labels) != y.shape[1]:
            raise ValueError("labels must match the number of y series")
    elif y.shape[1] > 1:
        labels = [f"Series {i+1}" for i in range(y.shape[1])]
    return (np.where(np.isfinite(x), x, np.nan),
            np.where(np.isfinite(y), y, np.nan), labels)


class _Figure:
    def __init__(self, rows, cols, title, xlabel):
        if any(isinstance(n, bool) or not isinstance(n, int) or n < 1 for n in (rows, cols)):
            raise ValueError("rows and cols must be positive integers")
        import matplotlib.pyplot as plt

        size = (10 if cols == 1 else 6 * cols, 3 * rows if rows > 1 else 4.5)
        self.figure = plt.figure(figsize=size, layout="constrained")
        self._rows, self._cols, self._xlabel = rows, cols, xlabel
        self._axes = {}
        if title:
            self.figure.suptitle(title)

    def plot(self, x, y, *, labels=None, title=None, xlabel=None, ylabel="",
             panel=None, polar=False, equal=False, style="-", **options):
        """Draw one/many series; panel=1 selects the first panel for overlays.

        y accepts a 1D list, a [samples, series] array, or a label-to-series dict.
        polar=True interprets x as radians and y as radius.
        style and options go to Matplotlib, e.g. style=".", color="red".
        """
        if "label" in options:
            if labels is not None:
                raise ValueError("use labels or label, not both")
            labels = options.pop("label")
        x, values, names = _series(x, y, labels)
        total = self._rows * self._cols
        if panel is None:
            panel = next((i for i in range(1, total+1) if i not in self._axes), None)
            if panel is None:
                raise ValueError("all panels are used; select panel=1 to add more lines")
        if isinstance(panel, bool) or not isinstance(panel, int) or not 1 <= panel <= total:
            raise ValueError(f"panel must be between 1 and {total}")
        axis = self._axes.get(panel)
        if axis is None:
            axis = self.figure.add_subplot(self._rows, self._cols, panel,
                                           projection="polar" if polar else None)
            self._axes[panel] = axis
        elif (axis.name == "polar") != polar:
            raise ValueError("a panel cannot mix polar and Cartesian plots")
        for index in range(values.shape[1]):
            name = names[index] if names is not None else None
            axis.plot(x, values[:, index], style, label=name, **options)
        if title is not None:
            axis.set_title(title)
        if xlabel is not None:
            axis.set_xlabel(xlabel)
        elif self._xlabel and not axis.get_xlabel():
            axis.set_xlabel(self._xlabel)
        if ylabel:
            axis.set_ylabel(ylabel)
        if equal:
            axis.set_aspect("equal", adjustable="box")
        axis.grid(alpha=0.3)
        if axis.get_legend_handles_labels()[1]:
            axis.legend()
        return self

    def save(self, filename="plot.png"):
        """Save relative paths under outputs/; return the written Path."""
        path = Path(filename)
        if not path.is_absolute():
            path = OUTPUT / path
        path.parent.mkdir(parents=True, exist_ok=True)
        self.figure.savefig(path, dpi=160)
        print(f"Saved: {path}")
        return path


def figure(rows=1, cols=1, *, title=None, xlabel=""):
    """Prepare a chart; each plot() uses the next panel unless panel is given."""
    return _Figure(rows, cols, title, xlabel)


def plot(x, y, **options):
    """Draw a single chart using the same inputs/options as chart.plot()."""
    return figure().plot(x, y, **options)


def show():
    """Open all prepared graphs. Does not read sensors or run physics."""
    import matplotlib.pyplot as plt

    plt.show()


__all__ = ["figure", "plot", "show"]
