from matplotlib.colors import to_rgba
from matplotlib import pyplot as plt
import numpy as np

x = np.arange(0, 100, 10)
fig, ax = plt.subplots(1, 1)
ax.plot(x, x**2, marker="o", fillstyle='full',
        markerfacecolor=to_rgba("r", .4), markeredgecolor="k")
fig.savefig("testplot.pdf")
