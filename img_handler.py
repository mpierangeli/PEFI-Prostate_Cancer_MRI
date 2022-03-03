import pydicom
from pydicom.pixel_data_handlers.util import apply_modality_lut,apply_voi_lut
import matplotlib.pyplot as plt
from skimage import exposure
import numpy as np

filePath = 'PROSTATA_1.MR.0001.0015.2021.12.22.13.14.21.169473.39474333.ima'

with pydicom.dcmread(filePath) as full_dicom: #forma correcta de abrir el archivo "context manager"
    img = full_dicom.pixel_array

#img_255 = exposure.rescale_intensity(img,in_range="image",out_range=(0,255)) # ver si in_range deberian los valores min y max que podrían tener una imágen saliente del resonador y no los de la imágen particular.
#img_bis = apply_voi_lut(img, full_dicom) # no estoy seguro si va o no
""" print(img_bis.min())
print(full_dicom)
plt.subplot(1,2,1)
plt.imshow(img,cmap="magma")
plt.subplot(1,2,2)
plt.imshow(img_bis,cmap="magma")
plt.show() """
""" plt.imsave("test.jpeg",img_255,cmap="gray")
r_img = plt.imread("test.jpeg")
plt.imshow(r_img)
plt.show() """

""" #para obtener la trafo de Fourier
ft = np.fft.ifftshift(img)
ft = np.fft.fft2(ft)
ft = np.fft.fftshift(ft)
plt.subplot(1,2,1)
plt.imshow(np.log(abs(ft)),cmap="gray")
#plt.show()
#para obtener la imagen original
ift = np.fft.ifftshift(ft)
ift = np.fft.ifft2(ift)
ift = np.fft.fftshift(ift)
ift = ift.real
plt.subplot(1,2,2)
plt.imshow(ift,cmap="gray")
plt.show() """
