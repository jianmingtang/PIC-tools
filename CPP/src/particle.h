#include <vector>
#include "para.h"

#ifndef PARTICLE_H
#define PARTICLE_H

class Particle {
public:
	double q;
	double m;
	unsigned int Np;

	std::vector<double> data;
	std::vector<double*> ptr;

	Particle(const Parameter &);
	Particle(unsigned int);
	Particle(double [], unsigned int);
};

#endif /* PARTICLE_H */
