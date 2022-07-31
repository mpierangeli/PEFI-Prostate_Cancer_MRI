import numpy as np
import matplotlib.pyplot as plt

h = 100
w = 100
center = [int(h/2),int(w/2)]
radius = 20

Y, X = np.ogrid[:h, :w]
dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)

mask = dist_from_center <= radius

plt.imshow(mask)
plt.show()