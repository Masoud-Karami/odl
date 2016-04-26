# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 10:48:55 2016

@author: jonasadler
"""

from odl.discr import uniform_discr_frompartition, uniform_partition
import numpy as np
try:
    from skimage.transform import radon, iradon
    SCIKIT_IMAGE_AVAILABLE = True
except ImportError:
    SCIKIT_IMAGE_AVAILABLE = False

__all__ = ('scikit_radon_forward', 'scikit_radon_back_projector',
           'SCIKIT_IMAGE_AVAILABLE')


def scikit_theta(geometry):
    """Calculate angles in degrees with ODL scikit conventions."""
    return np.asarray(geometry.motion_grid).squeeze() * 180.0 / np.pi - 90


def scikit_sinogram_space(geometry, volume_space, sinogram_space):
    """Create a range adapted to the scikit radon geometry."""

    padded_size = int(np.ceil(volume_space.shape[0] * np.sqrt(2)))
    det_width = volume_space.domain.extent()[0] * np.sqrt(2)
    scikit_detector_part = uniform_partition(-det_width/2.0 - 0.142,
                                             det_width/2.0,
                                             padded_size)

    scikit_range_part = geometry.motion_partition.insert(1,
                                                         scikit_detector_part)

    scikit_range = uniform_discr_frompartition(scikit_range_part,
                                               interp=sinogram_space.interp,
                                               dtype=sinogram_space.dtype)

    return scikit_range


def clamped_interpolation(scikit_range, sinogram):
    """Interpolate in a possibly smaller space

    Sets all points that would be outside ofthe domain to match the boundary
    values.
    """
    min_x = scikit_range.domain.min()[1]
    max_x = scikit_range.domain.max()[1]

    def interpolation_wrapper(x):
        x = (x[0], np.maximum(min_x, np.minimum(max_x, x[1])))

        return sinogram.interpolation(x)
    return interpolation_wrapper


def scikit_radon_forward(volume, geometry, range, out=None):
    """Calculate forward projection using scikit

    Parameters
    ----------
    volume : DiscreteLpVector
        The volume to project
    geometry : Geometry
        The projection geometry to use
    range : DiscreteLp
        range of this projection (sinogram space)
    out : range element, optional
        An element in range that the result should be written to

    Returns
    -------
    sinogram : range element
        The sinogram given by the projection
    """

    # Check basic requirements. Fully checking should be in wrapper
    assert volume.shape[0] == volume.shape[1]

    theta = scikit_theta(geometry)
    scikit_range = scikit_sinogram_space(geometry, volume.space, range)

    sinogram = scikit_range.element(radon(volume.asarray(), theta=theta).T)

    if out is None:
        out = range.element()

    out.sampling(clamped_interpolation(scikit_range, sinogram))

    scale = volume.space.cell_sides[0]

    out *= scale

    return out


def scikit_radon_back_projector(sinogram, geometry, range, out=None):
    """Calculate forward projection using scikit

    Parameters
    ----------
    sinogram : DiscreteLpVector
        The sinogram (projections) to backproject
    geometry : Geometry
        The projection geometry to use
    range : DiscreteLp
        range of this projection (volume space)
    out : range element, optional
        An element in range that the result should be written to

    Returns
    -------
    sinogram : range element
        The sinogram given by the projection
    """
    theta = scikit_theta(geometry)
    scikit_range = scikit_sinogram_space(geometry, range, sinogram.space)

    scikit_sinogram = scikit_range.element()
    scikit_sinogram.sampling(clamped_interpolation(range, sinogram))

    if out is None:
        out = range.element()
    else:
        # Only do asserts here since these are backend functions
        assert out in range

    out[:] = iradon(scikit_sinogram.asarray().T, theta,
                    output_size=range.shape[0], filter=None)

    # Empirical value, gives correct scaling
    scale = 4.0
    out *= scale

    return out
