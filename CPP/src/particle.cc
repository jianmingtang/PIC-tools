#include "particle.h"

Particle::Particle(const Parameter &p) {
	Np = p.Np;
	data = std::vector<double>(p.Np * N_DIMS);
	f = std::vector<double>(p.Np * N_DIMS);
}

Particle::Particle(const Parameter &p, double *x) {
	Np = p.Np;
	data = std::vector<double>(p.Np * N_DIMS);
	f = std::vector<double>(p.Np * N_DIMS);
	for (size_t i = 0; i < p.Np; ++i) {
		for (size_t j = 0; j < N_COORDS; ++j)
			data[i*N_DIMS+j] = x[i*N_DIMS+j] * p.rfac;
		for (size_t j = N_COORDS; j < N_DIMS; ++j)
			data[i*N_DIMS+j] = x[i*N_DIMS+j] * p.vfac;
	}
}
