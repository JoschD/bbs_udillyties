import numpy as np
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.gca()
x = np.linspace(0,3,10000)
y = 1e6*np.exp(-x) * (np.sin(10*x)-0.5)
ax.plot(x,y)

fig = plt.figure()
ax = fig.gca()
Y = np.sign(y)*np.log10(np.abs(y))
ax.plot(x,Y,'.')

# yl = [float(l.get_text().replace) for l in ax.get_ymajorticklabels()]
# ax.set_yticklabels(yl)
# yl = get(gca,'ytick');
# set(gca,'yticklabel',sign(yl).*10.^abs(yl))
plt.show()
