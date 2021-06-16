""""
Functions for slippy IO of faults and slip distributions into list of fault_slip_object dictionaries

Format json: basis1, basis2, length(m), width(m), nlength, nwidth, strike, dip, position [lon, lat, dep], penalty
Format slippy: lon lat depth[m] strike[deg] dip[deg] length[m] width[m] left-lateral[m] thrust[m] tensile[m]
"""

import json
from Tectonic_Utils.geodesy import fault_vector_functions


def read_faults_json(infile):
    """
    Read all faults from a json file (just geometry; no slip or rake) into a list of fault dictionaries.
    It has to convert from fault center to fault corner.
    Faults read from JSON have zero slip.

    :param infile: name of input json file
    :type infile: string
    :returns: list of fault dictionaries
    :rtype: list
    """
    fault_list = [];
    config_file = open(infile, 'r')
    config = json.load(config_file);
    for key in config.keys():
        one_fault = {"strike": config[key]["strike"], "dip": config[key]["dip"],
                     "length": config[key]["length"] / 1000.0,
                     "width": config[key]["width"] / 1000.0};
        center_lon = config[key]["position"][0];
        center_lat = config[key]["position"][1];
        x_start, y_start = fault_vector_functions.add_vector_to_point(0, 0, one_fault["length"] / 2,
                                                                      one_fault["strike"] - 180);  # in km
        corner_lon, corner_lat = fault_vector_functions.xy2lonlat(x_start, y_start, center_lon, center_lat);  #
        one_fault["lon"] = corner_lon;
        one_fault["lat"] = corner_lat;
        one_fault["depth"] = -config[key]["position"][2] / 1000;
        one_fault["rake"] = 0;
        one_fault["slip"] = 0;
        one_fault["tensile"] = 0;
        fault_list.append(one_fault);
    return fault_list;


def write_faults_json(faults_list, outfile):
    """
    Writes faults to json as receivers with zero slip

    :param faults_list: list of fault dictionaries
    :type faults_list: list
    :param outfile: name of output json file
    :type outfile: string
    """
    output = {};
    faults = {};
    count = 0;
    for fault in faults_list:
        # Convert the fault (which has top left corner) into a fault with top center coordinate
        corner_lon = fault["lon"]
        corner_lat = fault["lat"]
        x_center, y_center = fault_vector_functions.add_vector_to_point(0, 0, fault["length"] / 2, fault["strike"]);
        center_lon, center_lat = fault_vector_functions.xy2lonlat(x_center, y_center, corner_lon, corner_lat);

        count = count + 1;
        label = "fault" + str(count)
        fault["length"] = fault["length"] * 1000;
        fault["width"] = fault["width"] * 1000;
        fault["basis1"] = [1, 0, 0];
        fault["basis2"] = None;
        fault["Nlength"] = 1;
        fault["Nwidth"] = 1;
        fault["penalty"] = 1;
        fault["position"] = [center_lon, center_lat, fault["depth"]];
        fault.pop("lon");
        fault.pop("lat");
        fault.pop("depth");
        faults[label] = fault;
    output["faults"] = faults;
    output["plotter"] = "gmt";
    with open(outfile, 'w') as ofile:
        json.dump(output, ofile, indent=4);
    return;
