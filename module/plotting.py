"""Shared MuJoCo 2D chart styling and history rendering."""

import mujoco
import numpy as np


def make_figure(title, labels, colors):
    figure = mujoco.MjvFigure()
    mujoco.mjv_defaultFigure(figure)
    figure.title = title
    figure.xlabel = "Simulation time (s)"
    figure.figurergba[:] = (0.07, 0.09, 0.12, 1)
    figure.panergba[:] = (0.10, 0.13, 0.17, 1)
    figure.gridrgb[:] = (0.25, 0.29, 0.34)
    figure.gridsize[:] = (5, 5)
    figure.flg_extend = 0
    figure.flg_legend = 1
    figure.linewidth = 2
    for index, (label, color) in enumerate(zip(labels, colors)):
        figure.linename[index] = label
        figure.linergb[index] = color
    return figure


def update_history_figure(figure, history, values, padding=0.1):
    times = np.array([sample["time"] for sample in history])
    series = np.array([sample[values] for sample in history])
    figure.linepnt[:] = 0
    figure.flg_barplot = 1
    for index in range(series.shape[1]):
        # Missing returns leave gaps instead of connecting distant samples.
        valid = np.isfinite(series[:-1, index]) & np.isfinite(series[1:, index])
        xy = np.column_stack((times, series[:, index]))
        segments = np.stack((xy[:-1][valid], xy[1:][valid]), axis=1).reshape(-1, 2)
        figure.linepnt[index] = len(segments)
        figure.linedata[index, :2 * len(segments)] = segments.ravel()
    figure.range[0] = (max(0.0, times[-1] - 10.0), max(10.0, times[-1]))
    finite = series[np.isfinite(series)]
    lo, hi = (float(finite.min()), float(finite.max())) if finite.size else (0.0, 1.0)
    margin = max(padding, (hi - lo) * 0.15)
    figure.range[1] = (min(0.0, lo) - margin, max(0.0, hi) + margin)

