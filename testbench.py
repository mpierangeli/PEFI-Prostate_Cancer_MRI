import pydicom
import pydicom_seg
import SimpleITK as sitk

dcm = pydicom.dcmread('1-1.dcm')

reader = pydicom_seg.SegmentReader()
result = reader.read(dcm)

for segment_number in result.available_segments:
    image_data = result.segment_data(segment_number)  # directly available
    image = result.segment_image(segment_number)  # lazy construction
    sitk.WriteImage(image, f'segmentation-{segment_number}.nrrd', True)