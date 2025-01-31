from functools import lru_cache

import numpy as np
from scipy.stats import norm
from aleatory.processes.base_analytical import SPAnalytical
from aleatory.utils.utils import check_positive_number, get_times


def _fgn_auto_covariance(hurst, n):
    ns_2h = np.arange(n + 1) ** (2 * hurst)
    return np.insert((ns_2h[:-2] - 2 * ns_2h[1:-1] + ns_2h[2:]) / 2, 0, 1)


def _fgn_dh_sqrt_eigenvalues(hurst, n):
    return np.fft.irfft(_fgn_auto_covariance(hurst, n))[:n] ** 0.5


class fBM(SPAnalytical):

    def __init__(self, hurst=0.5, T=1.0, rng=None):
        super().__init__(T=T, rng=rng)
        self.hurst = hurst
        self.name = f"Fractional Brownian Motion $X = B_{{{self.hurst}}}(t)$"
        self._auto_covariance_function = lru_cache(1)(_fgn_auto_covariance)
        self._dh_sqrt_eigenvalues = lru_cache(1)(_fgn_dh_sqrt_eigenvalues)
        self.times = None

    def _davies_harte_algorithm(self, n):
        """
        Generate a fractional Gaussian noise using the Davies Harte algorithm.
        Davies, Robert B., and D. S. Harte. "Tests for Hurst effect."
        https://robertnz.net/pdf/hursteffect.pdf
        """

        # For scaling to interval [0, T]
        increment = self.T / n
        scale = increment**self.hurst

        # If H = 0.5, then generate a standard Brownian motion, otherwise
        # proceed with the Davies Harte method
        if self.hurst == 0.5:
            return self.rng.normal(scale=scale, size=n)
        else:
            # Generate  more fGns to use power-of-two FFTs for speed.
            m = 2 ** (n - 2).bit_length() + 1
            sqrt_eigenvalues = self._dh_sqrt_eigenvalues(self.hurst, m)

            # irfft results will be normalized by (2(m-1))**(3/2) but we only
            # want to normalize by 2(m-1)**(1/2).
            scale *= 2 ** (1 / 2) * (m - 1)

            w = self.rng.normal(scale=scale, size=2 * m).view(complex)
            w[0] = w[0].real * 2 ** (1 / 2)
            w[-1] = w[-1].real * 2 ** (1 / 2)

            # Resulting z is fft of sequence w.
            return np.fft.irfft(sqrt_eigenvalues * w)[:n]

    def _sample_fractional_brownian_motion(self, n):
        fgn = self._davies_harte_algorithm(n)
        fbm = fgn.cumsum()
        fbm = np.insert(fbm, [0], 0)
        return fbm

    def sample(self, n):

        check_positive_number(n)
        self.n = n
        self.times = get_times(self.T, self.n)
        sample = self._sample_fractional_brownian_motion(n - 1)
        return sample

    def _process_expectation(self, times=None):
        if times is None:
            times = self.times
        return 0.0 * times

    def get_marginal(self, t):
        s = np.sqrt(t ** (2.0 * self.hurst))
        marginal = norm(loc=0.0, scale=s)
        return marginal


# if __name__ == "__main__":
#
#     import matplotlib.pyplot as plt
#
#     qs = "https://raw.githubusercontent.com/quantgirluk/matplotlib-stylesheets/main/quant-pastel-light.mplstyle"
#     plt.style.use(qs)
#
#     p1 = fBM(T=10.0)
#     p2 = fBM(hurst=0.25, T=10.0)
#     p3 = fBM(hurst=0.75, T=10.0)
#     p4 = fBM(hurst=0.15, T=10.0)
#
#     for p, cm in [
#         (p1, "twilight"),
#         (p2, "Purples"),
#         (p3, "PuOr"),
#         (p4, "Blues"),
#     ]:
#
#         p.draw(
#             n=1000,
#             N=300,
#             figsize=(12, 7),
#             style=qs,
#             colormap=cm,
#             #     # orientation="vertical",
#         )
# p.plot(
#     n=1000,
#     N=5,
#     figsize=(12, 7),
#     style=qs,
#     # colormap=cm,
#     # orientation="vertical",
#     # mode="steps+points",
#     # envelope=False,
# )

# p.plot(N=10, n=100)
