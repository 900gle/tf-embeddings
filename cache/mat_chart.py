import matplotlib.pyplot as plt
import numpy as np

# Fixing random state for reproducibility
np.random.seed(19680801)

x, y = np.random.randn(2, 100)
fig, [ax1, ax2, ax3] = plt.subplots(3, 1, sharex=True)

print(x)
ax1.xcorr(x, y, usevlines=True, maxlags=50, normed=True, lw=2)
ax1.grid(True)
ax1.set_title('Cross-correlation (xcorr)')


print(x)
ax2.acorr(x, usevlines=True, normed=True, maxlags=50, lw=2)
ax2.grid(True)
ax2.set_title('Auto-correlation (acorr)')

ax3.acorr(x, usevlines=True, normed=True, maxlags=50, lw=2)
ax3.grid(True)
ax3.set_title('Auto-correlation (acorr)')

plt.show()