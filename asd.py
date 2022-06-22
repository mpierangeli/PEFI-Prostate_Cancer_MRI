from PIL import Image
import numpy as np
import matplotlib.pyplot as plt


an_image = Image.open("asd.png")

image = np.asarray(an_image)

print(image)
