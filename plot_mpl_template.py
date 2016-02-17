import numpy as np
import matplotlib.pyplot as plt
#references: https://github.com/jakevdp/mpl_tutorial/blob/master/notebooks_raw/02_object_oriented.ipynb

x = np.linspace(0, 10, 1000)
y = np.sin(x)
y2 = np.cos(x)


#style 1
fig2 = plt.figure()  # a new figure window
ax1 = fig2.add_subplot(1, 2, 1)  # specify (nrows, ncols, axnum)
ax2 = fig2.add_subplot(1, 2, 2)  # specify (nrows, ncols, axnum)
ax1.plot(x,y)
ax2.plot(x,y2)
ax1.legend(['sine'])
ax1.set_xlabel("$x$")
ax1.set_ylabel("$\sin(x)$")
ax1.set_title("I like $\pi$")
ax1.set_xlim(-1, 11)
fig2.savefig('plot_mpl_template_style1')


#style 2
#Matplotlib 1.0 (June 2010) added an even nicer subplot interface, plt.subplots. It automates the creation of the figure and subplots.
fig, axes = plt.subplots(2,2,figsize=(12, 6))
axes[0,0].plot(x, y)
axes[0,1].plot(x, y2)
fig.savefig('plot_mpl_template_style2.png')
