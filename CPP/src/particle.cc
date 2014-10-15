#include "particle.h"

Particle::Particle(const Parameter &p) {
	Np = 1;
	data = std::vector<double>(6);
	data[0] = 32. * p.rfac;
	data[1] = 0. * p.rfac;
	data[2] = -0.32 * p.rfac;
	data[3] = 0. * p.vfac;
	data[4] = -3.5 * p.vfac;
	data[5] = 0. * p.vfac;
}

Particle::Particle(unsigned int N) {
	Np = N;
	data = std::vector<double>(N*6);
}

Particle::Particle(double x[], unsigned int N) {
	Np = N;
	data = std::vector<double>(N*6);
	for (unsigned int i = 0; i < N * 6; ++i)
		data[i] = x[i];
}
