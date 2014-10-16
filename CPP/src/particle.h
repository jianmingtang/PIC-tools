#include <vector>
#include "para.h"


#ifndef PARTICLE_H
#define PARTICLE_H


class Particle {
public:
	double q;
	double m;

	std::vector<double> data;
	std::vector<double> f;

	Particle() {}
	Particle(const Parameter &);
	Particle(const Parameter &, const double *);
	void Set_Up_Uniform(const Parameter &);

	inline double & operator[] (size_t i) { return data[i]; }
};


#endif /* PARTICLE_H */
