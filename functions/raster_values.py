from os.path import join
from .dataset_map import dataset_url
from .initiate_reprojection import gcs, psm, project

import rasterio as rio
from rasterio.mask import mask
from numpy import unique
from shapely.ops import transform

def GetRasterValues(dataset, geom):
     url = dataset_url[dataset]
     geom_psm = transform(project, geom[0])
     geom_area = geom_psm.area * 0.0001
     with rio.open(url) as src:
          out_image, out_transform = mask(src, geom, crop=True)
          n_pixels = out_image.size
          out_image = out_image[out_image > 0]
          arr_unique, arr_counts = unique(out_image, return_counts=True)
          arr_unique = arr_unique + 2000
          arr_counts = arr_counts / n_pixels * geom_area
          return dict(zip(arr_unique, arr_counts))