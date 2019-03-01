# Configures a stress calculation 

import coulomb_collections


def configure_stress_calculation():
	aftershocks=''; title='';  disp_points=''; # by default, we don't include an aftershocks file. Format is from NCEDC search. 

	# # PARAMETER SET: THE EXAMPLE
	# input_file = "../Inputs/simplest_receiver.inp";
	# outdir="../Outputs/simple/"

	# PARAMETER SET: THE 2010 EARTHQUAKE
	# input_file = "../Inputs/M6p5.inp";
	# aftershocks="../Inputs/20100110_aftershocks_ncsn.txt";
	# outdir="../Outputs/M6p5/";
	# title="Coulomb Stresses for 2010 M6.5";

	# PARAMETER SET: THE 2014 EARTHQUAKE
	input_file = "../Inputs/M6.8_2014.intxt";
	aftershocks="../Inputs/20140310_aftershocks_ncsn.txt";
	outdir="../Outputs/M6p8/";
	title="Coulomb Stresses for 2014 M6.8";

	# PARAMETER SET: THE 2016 EARTHQUAKE
	# input_file = "../Inputs/M6.6_2016.intxt";
	# outdir="../Outputs/M6p6/"
	# title="Coulomb Stresses for 2016 M6.6";

	strike_num_receivers = 10;  # in the strike direction
	dip_num_receivers = 10;  # in the dip direction. how many sub-faults do you want? 

	mu = 30e9; # 30 GPa for shear modulus
	lame1 = 30e9;  # This is LAMDA, but I'm not using Lamda as a variable name. 
	alpha = (lame1+mu)/(lame1+2*mu);  # a parameter for the Okada functions. It is (lamda+mu)/(lamda+2*mu): 2.0/3.0 for simplest case.  See documentation for DC3D.f

	fixed_rake = 90; # on receiver faults, we need to specify the rake globally if we're using .inp format. 90=reverse. 
	# No effect if you're using .inr or .intxt format. 

	MyParams = coulomb_collections.Params(input_file=input_file, aftershocks=aftershocks, 
		strike_num_receivers=strike_num_receivers, dip_num_receivers=dip_num_receivers, fixed_rake=fixed_rake, 
		mu=mu, lame1=lame1, alpha=alpha, outdir=outdir, title=title);
	return MyParams;