from PIL import Image
import numpy as np
import matplotlib.pyplot as plt


an_image = Image.open("sector_map_v21_mask_v2.png")

image = np.asarray(an_image)


mask = (image[:,:,0] == 0)*(image[:,:,1] == 0)*(image[:,:,2] == 20)

new_img = image.copy()
new_img[mask] = [255,255,0]
    
plt.imshow(new_img)
plt.show()