import warnings

import numpy as np
import pyproj


def cartesian_to_polar(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    return np.array([
        (x**2 + y**2) ** 0.5,
        np.atan2(y, x)
    ])


def polar_to_cartesian(radius: np.ndarray, azimuths: np.ndarray, ) -> np.ndarray:
    return np.array([
        radius * np.cos(azimuths),
        radius * np.sin(azimuths)
    ])


def en_to_xy(points_en: np.ndarray, origin_en: np.ndarray) -> np.ndarray:
    """Est-North (EN) to XY mapping

    Parameters
    ----------
    points_en: array (N x 2)
        [[lon0, lat0], ... , [lonN, latN]]
    origin_en: array (2 x 1)

    Returns
    -------

    """
    # Npoints = np.array(points).shape[0]
    if not isinstance(points_en, np.ndarray):
        points_en = np.array(points_en)

    lon0, lat0 = origin_en
    proj = pyproj.Proj(proj="aeqd", lat_0=lat0, lon_0=lon0, datum="WGS84", units="m")

    lons, lats = points_en.T
    x, y = proj(lons, lats)

    return np.array([x, y]).T


def xy_to_en(points_xy: np.ndarray, origin_en: np.ndarray) -> np.ndarray:
    """XY mapping to Est-North (EN)

    Parameters
    ----------
    points_xy: array (N x 2)
        [[x0, y0], ... , [xN, yN]]
    origin_en: array (2 x 1)

    Returns
    -------

    """
    # Npoints = np.array(points).shape[0]
    if not isinstance(points_xy, np.ndarray):
        points_xy = np.array(points_xy)

    lon0, lat0 = origin_en
    proj = pyproj.Proj(proj="aeqd", lat_0=lat0, lon_0=lon0, datum="WGS84", units="m")

    x, y = points_xy.T
    lons, lats = proj(x, y, inverse=True)

    return np.array([lons, lats]).T

