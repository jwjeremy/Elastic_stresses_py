# Definitions of objects used in this project

import collections
from . import conversion_math
from Tectonic_Utils.geodesy import fault_vector_functions

Params = collections.namedtuple('Params', [
    'config_file', 'input_file', 'aftershocks',
    'disp_points_file', 'strain_file',
    'strike_num_receivers',
    'dip_num_receivers',
    'fixed_rake',
    'mu', 'lame1', 'B', 'alpha',
    'plot_stress', 'plot_grd_disp', 'outdir']);

Faults_object = collections.namedtuple('Faults_object', [
    'xstart', 'xfinish',
    'ystart', 'yfinish',
    'Kode', 'zerolon', 'zerolat',
    'rtlat', 'reverse', 'tensile', 'potency',
    'strike', 'dipangle', 'rake',
    'top', 'bottom', 'comment',
    'R', 'R2', 'W', 'L', 'strike_unit_vector', 'dip_unit_vector', 'plane_normal']);
# rtlat, reverse, tensile are in units of meters
# See constructor below for the creating of this object.  We usually don't call this object directly.

Input_object = collections.namedtuple('Input_object', [
    'PR1', 'FRIC', 'depth',
    'start_gridx', 'finish_gridx',
    'start_gridy', 'finish_gridy',
    'xinc', 'yinc',
    'minlon', 'maxlon',
    'zerolon',
    'minlat', 'maxlat',
    'zerolat',
    'source_object',
    'receiver_object', 'receiver_horiz_profile'])
# source_object = a list of Faults (pycoulomb format), with the same zerolon/zerolat as the overall system
# receiver_object = a list of Faults (pycoulomb format), with the same zerolon/zerolat as the overall system

Receiver_Horiz_Profile = collections.namedtuple('Receiver_Horiz_Profile', [
    'depth_km', 'strike', 'dip', 'rake', 'centerlon', 'centerlat', 'lon1d', 'lat1d',
    'width', 'length', 'inc', 'shape'])

Out_object = collections.namedtuple('Out_object', [
    'x', 'y',
    'x2d', 'y2d', 'u_disp', 'v_disp', 'w_disp',
    'zerolon', 'zerolat',
    'model_disp_points', 'strains',
    'source_object', 'receiver_object',
    'receiver_normal', 'receiver_shear', 'receiver_coulomb', 'receiver_profile']);

Displacement_points = collections.namedtuple('Disp_Points', [
    'lon', 'lat',
    'dE_obs', 'dN_obs', 'dU_obs',
    'Se_obs', 'Sn_obs', 'Su_obs',
    'name', 'starttime', 'endtime', 'refframe', 'meas_type'], defaults=(None,) * 13);
# Disp_points are now lists of individual disp_point elements
# Displacements in meters
# Might want to ensure that -180 < lon < 180 in the future


def construct_pycoulomb_fault(xstart, xfinish, ystart, yfinish, rtlat, reverse, tensile, potency, strike, dipangle,
                              rake, zerolon, zerolat, top, bottom, Kode=100, comment=None):
    """
    Like a constructor for this named tuple.
    You pass the required input parameters, and the remaining parameters are filled in.
    While keeping the interface simple,
    we are pre-computing some geometry parameters ONCE for each fault, for performance reasons.
    """
    if bottom < top:
        raise ValueError("Error! Provided bad fault- top depth (%f km) below bottom depth (%f km)" % (top, bottom) )
    R, R2 = conversion_math.get_R_from_strike(strike);
    L = fault_vector_functions.get_strike_length(xstart, xfinish, ystart, yfinish);
    W = fault_vector_functions.get_downdip_width(top, bottom, dipangle);
    strike_unit_vector = fault_vector_functions.get_strike_vector(strike);  # 3d vector in horizontal plane.
    dip_unit_vector = fault_vector_functions.get_dip_vector(strike, dipangle);  # a 3d vector.
    plane_normal = fault_vector_functions.get_plane_normal(strike, dipangle);  # a 3d vector.

    one_source = Faults_object(xstart=xstart, xfinish=xfinish, ystart=ystart, yfinish=yfinish,
                               Kode=Kode, rtlat=rtlat, reverse=reverse, tensile=tensile,
                               potency=potency, strike=strike, zerolon=zerolon, zerolat=zerolat,
                               dipangle=dipangle, rake=rake, top=top, bottom=bottom, comment=comment,
                               R=R, R2=R2, W=W, L=L,
                               strike_unit_vector=strike_unit_vector, dip_unit_vector=dip_unit_vector,
                               plane_normal=plane_normal);
    return one_source;
