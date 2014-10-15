#include <vector>
#include "para.h"

#ifndef PARTICLE_H
#define PARTICLE_H

#define N_DIMS 6
#define N_COORDS 3

class Particle {
public:
	double q;
	double m;
	size_t Np;

	std::vector<double> data;
	std::vector<double> f;
	std::vector<double*> ptr;

	Particle(const Parameter &);
	Particle(const Parameter &, double *);

	inline double & operator[] (size_t i) { return data[i]; }
};

#endif /* PARTICLE_H */
