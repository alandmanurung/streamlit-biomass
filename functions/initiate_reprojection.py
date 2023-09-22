import pyproj

gcs = pyproj.CRS('EPSG:4326')
psm = pyproj.CRS('EPSG:3857')
project = pyproj.Transformer.from_crs(gcs, psm, always_xy=True).transform