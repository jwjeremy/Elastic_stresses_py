"""Functions to take a slip distribution and make a map. """

import numpy as np
import pygmt
import os
from ..fault_slip_object import fault_slip_object
from .. import utilities


def unpack_disp_points(disp_points):
    """
    Unpack all displacement points.
    Also unpack any displacement points that have vertical data
    """
    lon = np.array([x.lon for x in disp_points]);
    lat = np.array([x.lat for x in disp_points]);
    disp_x = np.array([x.dE_obs for x in disp_points]);
    disp_y = np.array([x.dN_obs for x in disp_points]);
    disp_z = np.array([x.dU_obs for x in disp_points]);
    lon_vert = np.array([x.lon for x in disp_points if ~np.isnan(x.dU_obs)]);
    lat_vert = np.array([x.lat for x in disp_points if ~np.isnan(x.dU_obs)]);
    disp_z_vert = np.array([x.dU_obs for x in disp_points if ~np.isnan(x.dU_obs)]);
    return [lon, lat, disp_x, disp_y, disp_z, lon_vert, lat_vert, disp_z_vert];


def unpack_horiz_disp_points_for_vectors(disp_points):
    """Unpack any displacement points that have horizontal data; will be plotted as vectors"""
    lon_horiz = np.array([x.lon for x in disp_points if ~np.isnan(x.dE_obs)]);
    lat_horiz = np.array([x.lat for x in disp_points if ~np.isnan(x.dE_obs)]);
    disp_x_horiz = np.array([x.dE_obs for x in disp_points if ~np.isnan(x.dE_obs)]);
    disp_y_horiz = np.array([x.dN_obs for x in disp_points if ~np.isnan(x.dE_obs)]);
    return [lon_horiz, lat_horiz, disp_x_horiz, disp_y_horiz];


def write_patch_edges_for_plotting(fault_dict_list, colorby='slip'):
    """
    Plot the full patches and the surface traces of a collection of rectangular faults.  Can colorcode by slip.
    """
    fault_slip_object.write_gmt_fault_file(fault_dict_list, 'tmp.txt', colorcode=colorby, verbose=False);
    fault_slip_object.write_gmt_surface_trace(fault_dict_list, 'tmp2.txt', verbose=False);
    return "tmp.txt", "tmp2.txt";


def map_source_slip_distribution(fault_dict_list, outfile, disp_points=(), region=None,
                                 scale_arrow=(1.0, 0.010, "10 mm"), v_labeling_interval=None, fault_traces=None,
                                 fault_traces_from_dict=None, title="", plot_slip_colorbar=True):
    """
    Plot a map of slip distribution from fault_dict_list, a general format for slip distributions.
    In order to use this function with other formats, like intxt or slippy, convert to the internal fault dict first.

    :param fault_dict_list: list of fault_dict objects
    :param outfile: string, name of file
    :param disp_points: list of disp_point objects
    :param region: tuple of 4 numbers, (W, E, S, N)
    :param scale_arrow: tuple of 3 numbers
    :param v_labeling_interval: float
    :param fault_traces: list of [lons, lats] for plotting fault trace
    :param fault_traces_from_dict: a list of fault_dict objects that will be used for updip fault traces
    :param title: string
    :param plot_slip_colorbar: bool, whether to show a color bar for fault slip
    """
    print("Plotting outfile %s " % outfile);
    proj = "M7i"
    if not region:  # automatically determine the region
        if len(fault_dict_list) == 0:
            raise ValueError("Error! Cannot automatically determine map region because no fault patches provided.");
        buffer_deg = 0.15
        minlon, maxlon, minlat, maxlat = fault_slip_object.get_four_corners_lon_lat_multiple(fault_dict_list);
        region = [minlon-buffer_deg, maxlon+buffer_deg, minlat-buffer_deg, maxlat+buffer_deg];
    fig = pygmt.Figure();
    fig_width_deg = region[1] - region[0];
    fig.basemap(region=region, projection=proj, frame="+t\"" + title + "\"");
    fig.coast(shorelines="1.0p,black", region=region, borders="1", projection=proj, frame=str(fig_width_deg/5));
    fig.coast(region=region, projection=proj, borders='2', shorelines='0.5p,black', water='lightblue');

    # Drawing fault slip with a color scale.
    fault_colors = [_i["slip"] for _i in fault_dict_list];
    [cmap_opts, cbar_opts] = utilities.define_colorbar_series(fault_colors);
    if len(fault_colors) > 0:
        pygmt.makecpt(cmap="devon", series=str(cmap_opts[0])+"/"+str(cmap_opts[1])+"/"+str(cmap_opts[2]),
                      truncate="0/1", background="o", reverse=True, output="mycpt.cpt");  # slip divided into 100
    # Write the source patches
    file1, file2 = write_patch_edges_for_plotting(fault_dict_list, colorby='slip');   # write the source patches
    fig.plot(data=file1, pen="0.2p,black", color="+z", cmap="mycpt.cpt");
    fig.plot(data=file2, pen="0.6p,black");   # shallow edges
    os.remove(file1); os.remove(file2);
    fig.coast(region=region, projection=proj, borders='2', shorelines='0.5p,black', map_scale="jBL+o0.7c/1c+w25");
    if fault_dict_list:
        if plot_slip_colorbar:
            fig.colorbar(position="jBr+w3.5i/0.2i+o2.5c/1.5c+h", cmap="mycpt.cpt",
                         truncate=str(cbar_opts[0]) + "/" + str(cbar_opts[1]),
                         frame=["x" + str(cbar_opts[2]), "y+L\"Slip(m)\""]);

    if len(disp_points) > 0:
        [lon, lat, _, _, disp_z, lon_vert, lat_vert, disp_z_vert] = unpack_disp_points(disp_points);
        [lon_horiz, lat_horiz, disp_x_horiz, disp_y_horiz] = unpack_horiz_disp_points_for_vectors(disp_points);
        fig.plot(x=lon, y=lat, style='s0.07i', color='blue', pen="thin,black");
        if sum(~np.isnan(disp_z)) > 0:  # display vertical data if it's provided
            [v_cmap_opts, v_cbar_opts] = utilities.define_colorbar_series(disp_z_vert, tol=0.0001,
                                                                          v_labeling_interval=v_labeling_interval);
            series_str = str(v_cmap_opts[0])+"/" + str(v_cmap_opts[1]) + "/" + str(v_cmap_opts[2])
            pygmt.makecpt(cmap="roma", series=series_str, background="o", output="vert.cpt");
            fig.plot(x=lon_vert, y=lat_vert, style='c0.3c', color=disp_z_vert, cmap='vert.cpt', pen="thin,black");
            truncate_str = str(v_cbar_opts[0]) + "/" + str(v_cbar_opts[1]),
            fig.colorbar(position="JCR+w4.0i+v+o0.7i/0i", cmap="vert.cpt", truncate=truncate_str,
                         frame=["x"+str(v_cbar_opts[2]), "y+L\"Vert Disp(m)\""]);
        if sum(~np.isnan(disp_x_horiz) > 0):
            scale = scale_arrow[0] * (1/scale_arrow[1]);  # empirical scaling for convenient display
            fig.plot(x=lon_horiz, y=lat_horiz, style='v0.2c+e+gblack+h0+p1p,black+z'+str(scale),
                     direction=[disp_x_horiz, disp_y_horiz], pen="thin,black");
            fig.plot(x=[region[0]+0.30], y=[region[2]+1.05],  style='v0.2c+e+gblack+h0+p1p,black+z'+str(scale),
                     direction=[[scale_arrow[1]], [0]],  pen="thin,black");  # scale vector
            fig.text(x=[region[0]+0.45], y=[region[2]+1.15], text=scale_arrow[2],
                     font='14p,Helvetica,black');  # scale label

    # Optional lines you can draw on the plot
    if fault_traces:
        for item in fault_traces:
            fig.plot(x=item[0], y=item[1], pen="thickest,darkred");

    # Draw the updip trace of each fault segment
    if fault_traces_from_dict:
        for item in fault_dict_list:
            lons, lats = fault_slip_object.get_updip_corners_lon_lat(item);
            fig.plot(x=lons, y=lats, pen="thickest,darkred");

    fig.savefig(outfile);
    return;


def plot_data_model_residual(outfile, disp_points, model_disp_points, resid_disp_points, region,
                             scale_arrow, fault_dict_list=(), v_labeling_interval=None, rms=None):
    """
    Plot data, model, residual vectors
    """
    print("Plotting outfile %s " % outfile);
    fig = pygmt.Figure();
    proj = 'M3.2i'
    point_size = 0.15  # for vertical symbol
    numrows, numcols = 1, 3;
    with fig.subplot(nrows=numrows, ncols=numcols, figsize=("12i", "12i"), frame="lrtb"):
        # Data
        with fig.set_panel(panel=0):
            fig.basemap(region=region, projection=proj, frame=["WeSn", "2.0"]);
            fig.coast(region=region, projection=proj, borders='2', shorelines='1.0p,black', water='lightblue');
            [_, _, _, _, disp_z, lon_vert, lat_vert, disp_z_vert] = unpack_disp_points(disp_points);
            [lon_horiz, lat_horiz, dispx_horiz, dispy_horiz] = unpack_horiz_disp_points_for_vectors(disp_points);

            if sum(~np.isnan(disp_z)) > 0:  # display vertical data if it's provided
                [cmap_opts, cbar_opts] = utilities.define_colorbar_series(disp_z_vert,
                                                                          v_labeling_interval=v_labeling_interval);
                series_str = str(cmap_opts[0]) + "/" + str(cmap_opts[1]) + "/" + str(cmap_opts[2]);
                pygmt.makecpt(cmap="roma", series=series_str, background="o", output="vert.cpt");
                fig.plot(x=lon_vert, y=lat_vert, projection=proj, style='c'+str(point_size)+'c', color=disp_z_vert,
                         cmap='vert.cpt', pen="0.1p,black");

            scale = scale_arrow[0] * (1/scale_arrow[1]);  # empirical scaling for convenient display
            fig.plot(x=lon_horiz, y=lat_horiz, projection=proj, style='v0.12c+e+gblack+h0+p0.1p,black+z'+str(scale),
                     direction=[dispx_horiz, dispy_horiz], pen="0.1p,black");
            fig.plot(x=[region[0]+0.30], y=[region[2]+1.05], projection=proj,
                     style='v0.2c+e+gblack+h0+p1p,black+z'+str(scale),
                     direction=[[scale_arrow[1]], [0]],  pen="thin,black");  # scale vector
            fig.text(x=[region[0]+0.85], y=[region[2]+1.25], projection=proj, text=scale_arrow[2]+' data');  # label
            fig.text(position="TL", projection=proj, font="18p,Helvetica,black", fill="white", offset='j0.1/0.1',
                     text='A) Data');

        # Model
        with fig.set_panel(panel=1):
            fig.basemap(region=region, projection=proj, frame=["WeSn", "2.0"]);
            fig.coast(region=region, projection=proj, borders='2', shorelines='1.0p,black', water='lightblue');
            [_, _, _, _, disp_z, lon_vert, lat_vert, disp_z_vert] = unpack_disp_points(model_disp_points);
            [lon_horiz, lat_horiz, dispx_horiz, dispy_horiz] = unpack_horiz_disp_points_for_vectors(model_disp_points);

            file1, file2 = write_patch_edges_for_plotting(fault_dict_list, colorby='None');
            fig.plot(data=file1, pen="0.2p,black", color="white");  # annotate the rectangular fault patches
            fig.plot(data=file2, pen="0.6p,black", projection=proj);  # annotate shallow edges of rect. fault patches
            os.remove(file1); os.remove(file2);

            if sum(~np.isnan(disp_z)) > 0:  # display vertical data if it's provided
                fig.plot(x=lon_vert, y=lat_vert, projection=proj, style='c'+str(point_size)+'c', color=disp_z_vert,
                         cmap='vert.cpt', pen="0.1p,black");

            scale = scale_arrow[0] * (1/scale_arrow[1]);  # empirical scaling for convenient display
            fig.plot(x=lon_horiz, y=lat_horiz, projection=proj, style='v0.12c+e+gblack+h0+p0.1p,black+z'+str(scale),
                     direction=[dispx_horiz, dispy_horiz], pen="0.1p,black");
            fig.plot(x=[region[0]+0.30], y=[region[2]+1.05], projection=proj,
                     style='v0.2c+e+gblack+h0+p1p,black+z'+str(scale),
                     direction=[[scale_arrow[1]], [0]],  pen="thin,black");  # scale vector
            fig.text(x=[region[0]+0.95], y=[region[2]+1.25], projection=proj, text=scale_arrow[2]+' model');  # label
            fig.text(position="TL", projection=proj, font="18p,Helvetica,black", fill="white", offset='j0.1/0.1',
                     text='B) Model');

        # Residual
        with fig.set_panel(panel=2):
            fig.basemap(region=region, projection=proj, frame=["WeSn", "2.0"]);
            fig.coast(region=region, projection=proj, borders='2', shorelines='1.0p,black', water='lightblue');
            [_, _, _, _, disp_z, lon_vert, lat_vert, disp_z_vert] = unpack_disp_points(resid_disp_points);
            [lon_horiz, lat_horiz, dispx_horiz, dispy_horiz] = unpack_horiz_disp_points_for_vectors(resid_disp_points);

            if sum(~np.isnan(disp_z)) > 0:  # display vertical data if it's provided
                fig.plot(x=lon_vert, y=lat_vert, projection=proj, style='c'+str(point_size)+'c', color=disp_z_vert,
                         cmap='vert.cpt', pen="0.1p,black");
                fig.colorbar(position="JCR+w4.0i+v+o0.4i/0i", projection=proj, cmap="vert.cpt",
                             truncate=str(cbar_opts[0]) + "/" + str(cbar_opts[1]),
                             frame=["x" + str(cbar_opts[2]), "y+L\"Vert Disp(m)\""]);

            scale = scale_arrow[0] * (1/scale_arrow[1]);  # empirical scaling for convenient display
            fig.plot(x=lon_horiz, y=lat_horiz, projection=proj, style='v0.12c+e+gblack+h0+p0.1p,black+z'+str(scale),
                     direction=[dispx_horiz, dispy_horiz], pen="0.1p,black");
            fig.plot(x=[region[0]+0.30], y=[region[2]+1.05], projection=proj,
                     style='v0.2c+e+gblack+h0+p1p,black+z'+str(scale),
                     direction=[[scale_arrow[1]], [0]],  pen="thin,black");  # scale vector
            fig.text(x=[region[0]+0.85], y=[region[2]+1.25], projection=proj, text=scale_arrow[2]+' res');  # label
            fig.text(position="TL", projection=proj, font="18p,Helvetica,black", fill="white", offset='j0.1/0.1',
                     text='C) Residual');
            if rms:
                fig.text(x=[region[0] + 1.20], y=[region[2] + 0.65], projection=proj,
                         text='rms='+str(np.round(rms, 2)) + ' mm');  # label

    fig.savefig(outfile);
    return;
