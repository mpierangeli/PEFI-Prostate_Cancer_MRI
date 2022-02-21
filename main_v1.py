import pydicom
import matplotlib.pyplot as plt
import numpy as np

filePath = 'PROSTATA_1.MR.0001.0015.2021.12.22.13.14.21.169473.39474333.ima'
img = pydicom.read_file(filePath)
img = pydicom.dcmread(filePath)
plt.imshow(img.pixel_array,cmap=plt.cm.bone)
plt.show()
img