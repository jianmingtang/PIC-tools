#ifndef PARTICLE_H
#define PARTICLE_H

class Particle {
public:
	double q;
	double m;
	double x, y, z;
	double vx, vy, vz;

	Particle(double []);
};

#endif /* PARTICLE_H */
