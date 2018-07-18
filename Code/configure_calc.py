# Configures a stress calculation 

import collections

Params = collections.namedtuple('Params',
	['input_file','strike_num_receivers','dip_num_receivers','fixed_rake','mu','lame1','alpha','outdir']);


def configure_stress_calculation():
	# input_file = "../Inputs/Example-2CSZ_LL.inp";
	input_file = "../Inputs/simplest_receiver.inp";
	outdir="../Outputs/simple_"
	strike_num_receivers = 10;  # in the strike direction
	dip_num_receivers = 10;  # in the dip direction. how many sub-faults do you want? 

	mu = 30e9; # 30 GPa for shear modulus
	lame1 = 30e9;  # This is LAMDA, but I'm not using Lamda as a variable name. 
	alpha = (lame1+mu)/(lame1+2*mu);  # a parameter for the Okada functions. It is (lamda+mu)/(lamda+2*mu): 2.0/3.0 for simplest case.  See documentation for DC3D.f

	fixed_rake = 0; # on receiver faults, we need to specify the rake globally if we're using .inp format. 90=reverse. 
	# No effect if you're using .inr format. 

	MyParams = Params(input_file=input_file, strike_num_receivers=strike_num_receivers, dip_num_receivers=dip_num_receivers, fixed_rake=fixed_rake, mu=mu, lame1=lame1, alpha=alpha, outdir=outdir);
	return MyParams;