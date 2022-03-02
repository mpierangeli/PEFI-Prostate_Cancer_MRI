import pydicom
import matplotlib.pyplot as plt
from skimage import exposure

filePath = 'PROSTATA_1.MR.0001.0015.2021.12.22.13.14.21.169473.39474333.ima'

with pydicom.dcmread(filePath) as full_dicom: #forma correcta de abrir el archivo "context manager"
    img = full_dicom.pixel_array

img_255 = exposure.rescale_intensity(img,in_range="image",out_range=(0,255)) # ver si in_range deberian los valores min y max que podrían tener una imágen saliente del resonador y no los de la imágen particular.

""" plt.subplot(1,2,1)
plt.imshow(img,cmap="magma")
plt.subplot(1,2,2)
plt.imshow(img_255,cmap="magma")
plt.show() """
plt.imsave("test.jpeg",img_255,cmap="gray")
r_img = plt.imread("test.jpeg")
plt.imshow(r_img)
plt.show()