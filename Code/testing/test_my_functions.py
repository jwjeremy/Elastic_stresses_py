# Testing code

import numpy as np 
import conversion_math


def test_strike(deltax, deltay, answer):
	strike = conversion_math.get_strike(deltax, deltay);
	print("Computed strike is : %.1f ; Correct strike is %.1f degrees" % (strike, answer) );
	return;

def test_rake(ss, ds, answer):
	rake=conversion_math.get_rake(ss,ds);
	print("Computed rake is : %.1f ; Correct rake is %.1f degrees" % (rake, answer) )
	return;

def test_plane_normal(strike, dip, answer):
	print("given strike/dip are: %f %f "  % (strike, dip) )
	plane_normal=conversion_math.get_plane_normal(strike, dip);
	print("Computed plane normal is: ")
	print(plane_normal);
	print("Expected answer is %s\n" % answer);
	return;

if __name__=="__main__":
	test_strike(1, 0.0, 90);  
	test_strike(-1, 0.0, 270); 
	test_strike(0.0, -1.0, 180); 
	angle = -160;
	test_strike(np.cos(np.deg2rad(angle)), np.sin(np.deg2rad(angle)), 250);

	test_plane_normal(0, 0, '[0, 0, 1]');
	test_plane_normal(90, 89, '[0, -1, verysmall]');
	test_plane_normal(270, 89, '[0, 1, verysmall]');
	test_plane_normal(0, 1, '[verysmall, 0, 1]');
	test_plane_normal(180, 1, '[-verysmall, 0, 1]');



# Testing wells and coppersmith code. 
import wells_and_coppersmith as wc 

length=45.47;
width=14.4;
m=6.8;
fault_type='SS';

length=wc.RLD_from_M(m, fault_type);
print(length);

width=wc.RW_from_M(m, fault_type);
print(width);

slip=wc.rectangular_slip(length*1000, width*1000, m);
print(slip);

m2=wc.get_magnitude(length*1000, width*1000, slip);
print(m2)
