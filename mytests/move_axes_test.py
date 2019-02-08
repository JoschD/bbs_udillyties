import matplotlib.pyplot as plt

fig1, ax = plt.subplots()
ax.plot(range(10))
ax.remove()

fig2 = plt.figure()
ax.figure=fig2
fig2.axes.append(ax)
fig2.add_axes(ax)

dummy = fig2.add_subplot(111)
ax.set_position(dummy.get_position())
dummy.remove()
plt.close(fig1)

plt.show()