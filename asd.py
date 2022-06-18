from PIL import Image
import numpy as np
import matplotlib.pyplot as plt


an_image = Image.open("t2.jpg")

image_sequence = an_image.getdata()
image_array = np.array(image_sequence)

#print(np.histogram(image_array.T[0],255))

plt.hist(image_array.T[2],bins=255,log=True)
plt.show()