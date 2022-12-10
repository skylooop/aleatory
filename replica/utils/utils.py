from numbers import Number
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import pandas as pd


def get_times(end, n):
    """Generate a linspace from 0 to end for n increments."""
    return np.linspace(0, end, n)


def plot_paths(times, paths, name):
    with plt.style.context('seaborn-whitegrid'):
        for p in paths:
            plt.plot(times, p)
        plt.title(name)
        plt.show()
    return 1


def draw_paths(times, paths, N, expectations,  name,
               marginal =False, marginalT=None,
               envelope=False, lower=None, upper=None):

    if marginal:
        draw_paths_with_marginal(times=times, paths=paths, N=N,expectations=expectations,
                                 name=name, marginalT=marginalT, envelope=envelope, lower=lower, upper=upper)
    else:
        draw_paths_without_marginal(times=times, paths=paths, N=N,expectations=expectations,
                                 name=name, envelope=envelope, lower=lower, upper=upper)

    return 1

def draw_paths_without_marginal(times, paths, N, expectations,  name, envelope=False, lower=None, upper=None):
    with plt.style.context('seaborn-whitegrid'):
        plt.figure(figsize=(48 / 5, 6))
        for i in range(N):
            plt.plot(times, paths[i], '-', lw=1.5)
        plt.plot(times, expectations, '-', lw=1.5, color='black', label='$E[X_t]$')
        if envelope:
            plt.fill_between(times, upper, lower, color='grey', alpha=0.25)
        plt.suptitle(name)
        plt.title('Simulated Paths $X_t, t \in [t_0, T]$')  # Title
        plt.xlabel('t')
        plt.ylabel('X(t)')
        plt.legend()
        plt.show()

        return 1

def draw_paths_with_marginal(times, paths, N, marginalT, expectations, name, envelope=False, lower=None, upper=None):
    with plt.style.context('seaborn-whitegrid'):
        fig = plt.figure(figsize=(12, 6))
        gs = GridSpec(1, 5, figure=fig)
        ax1 = fig.add_subplot(gs[:4])
        ax2 = fig.add_subplot(gs[4:], sharey=ax1)

        last_points = [path[-1] for path in paths]
        cm = plt.cm.get_cmap('RdYlBu_r')
        n_bins = int(np.sqrt(N))

        n, bins, patches = ax2.hist(last_points, n_bins, color='green', orientation='horizontal', density=True)
        bin_centers = 0.5 * (bins[:-1] + bins[1:])
        col = bin_centers - min(bin_centers)  # scale values to interval [0,1]
        col /= max(col)
        for c, p in zip(col, patches):
            plt.setp(p, 'facecolor', cm(c))
        my_bins = pd.cut(last_points, bins=bins, labels=range(len(bins) - 1), include_lowest=True)
        colors = [col[b] for b in my_bins]

        marginal = marginalT
        x = np.linspace(marginal.ppf(0.005), marginal.ppf(0.995), 100)
        ax2.plot(marginal.pdf(x), x, '--', lw=1.75, alpha=0.6, color='blue', label='$X_T$ pdf')
        ax2.axhline(y=marginal.mean(), color='black', lw=1.2, label='$E[X_T]$')
        plt.setp(ax2.get_yticklabels(), visible=False)

        for i in range(N):
            ax1.plot(times, paths[i], '-', lw=1.5, color=cm(colors[i]))

        ax1.plot(times, expectations, '-', lw=1.5, color='black', label='$E[X_t]$')
        if envelope:
            ax1.fill_between(times, upper, lower, alpha=0.25, color='grey')
        fig.suptitle(name, size=14)
        ax1.set_title('Simulated Paths $X_t, t \in [t_0, T]$', size=12)  # Title
        ax2.set_title('$X_T$', size=12)  # Title
        ax1.set_xlabel('t')
        ax1.set_ylabel('X(t)')
        plt.subplots_adjust(wspace=0.025, hspace=0.025)
        ax1.legend()
        ax2.legend()
        plt.show()

    return 1


def check_positive_integer(n, name=""):
    """Ensure that the number is a positive integer."""
    if not isinstance(n, int):
        raise TypeError(f"{name} must be an integer.")
    if n <= 0:
        raise ValueError(f"{name} must be positive.")


def check_numeric(value, name=""):
    """Ensure that the value is numeric."""
    if not isinstance(value, Number):
        raise TypeError(f"{name} value must be a number.")


def check_positive_number(value, name=""):
    """Ensure that the value is a positive number."""
    check_numeric(value, name)
    if value <= 0:
        raise ValueError(f"{name} value must be positive.")


def check_increments(times):
    increments = np.diff(times)
    if np.any([t < 0 for t in times]):
        raise ValueError("Times must be nonnegative.")
    if np.any([t <= 0 for t in increments]):
        raise ValueError("Times must be strictly increasing.")
    return increments


def times_to_increments(times):
    """Ensure a positive, monotonically increasing sequence."""
    return check_increments(times)