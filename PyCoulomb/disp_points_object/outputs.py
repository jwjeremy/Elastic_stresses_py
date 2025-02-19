"""
Special output functions for disp_point_objects
More specific than the basic ones listed in io_additionals.py
"""


def write_disp_points_gmt(disp_points, filename, write_meas_type=False):
    """Write disp_points in GMT psvelo format"""
    print("Writing %s " % filename);
    ofile = open(filename, 'w');
    ofile.write("# lon lat dE dN dU Se Sn Su name\n");
    for item in disp_points:
        ofile.write("%f %f %f %f %f " % (item.lon, item.lat, item.dE_obs, item.dN_obs, item.dU_obs) );
        ofile.write("%f %f %f %s " % (item.Se_obs, item.Sn_obs, item.Su_obs, item.name));
        if write_meas_type:
            ofile.write("%s " % item.meas_type);
        ofile.write("\n");
    ofile.close();
    return;
