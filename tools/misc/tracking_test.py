import xarray as xr
import numpy as np
import cv2
from scipy.ndimage import label, center_of_mass

def track_ships_from_netcdf(file_path):
    # Load the dataset
    ds = xr.open_dataset(file_path)

    # Extract variables
    scan_mean = ds['scan_mean']
    lon = ds['lon']
    lat = ds['lat']
    time = ds['time']

    # Prepare output dictionary
    ship_positions_by_time = {}

    # Loop over each time slice
    for t_index in range(scan_mean.sizes['time']):
        # Extract the image for the current time slice
        image = scan_mean.isel(time=t_index).values

        # Normalize and convert to 8-bit grayscale
        image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(image, (5, 5), 0)

        # Apply thresholding to isolate bright spots
        _, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)

        # Label connected components
        labeled_array, num_features = label(thresh)

        # Get centroids of labeled regions
        centroids = center_of_mass(thresh, labeled_array, range(1, num_features + 1))

        # Convert pixel coordinates to lon/lat
        ship_coords = []
        for y, x in centroids:
            # Round to nearest integer indices
            y_idx = int(round(y))
            x_idx = int(round(x))
            if 0 <= y_idx < lat.shape[0] and 0 <= x_idx < lon.shape[1]:
                ship_coords.append((float(lon[y_idx, x_idx]), float(lat[y_idx, x_idx])))

        # Store results indexed by time
        ship_positions_by_time[str(time[t_index].values)] = ship_coords

    return ship_positions_by_time

# Example usage:
# file_path = "radar_data.nc"
# results = track_ships_from_netcdf(file_path)
# print(results)

