#include "particle.h"

Particle::Particle(const Parameter &p) {
	data = std::vector<double>(p.Np * N_DIMS);
	f = std::vector<double>(p.Np * N_DIMS);
}

Particle::Particle(const Parameter &p, const double *x) {
	data = std::vector<double>(p.Np * N_DIMS);
	f = std::vector<double>(p.Np * N_DIMS);
	for (size_t i = 0; i < p.Np; ++i) {
		for (size_t j = 0; j < N_DIMS; ++j)
			data[i*N_DIMS+j] = x[i*N_DIMS+j];
/*
		for (size_t j = 0; j < N_COORDS; ++j)
			data[i*N_DIMS+j] = x[i*N_DIMS+j] * p.rfac;
		for (size_t j = N_COORDS; j < N_DIMS; ++j)
			data[i*N_DIMS+j] = x[i*N_DIMS+j] * p.vfac;
*/
	}
}

/**
 *  Set up a set of particles according to the vx, vy, vz ranges.
 */
void Particle::Set_Up_Uniform(const Parameter &p) {
	size_t i, j, k;
	double vx, vy, vz;
	double vxR = p.vxR.max - p.vxR.min;
	double vyR = p.vyR.max - p.vyR.min;
	double vzR = p.vzR.max - p.vzR.min;
	size_t vxS = p.vxR.N - 1;
	size_t vyS = p.vyR.N - 1;
	size_t vzS = p.vzR.N - 1;

	f = std::vector<double>(p.Np * N_DIMS);

	for (i = 0; i < p.vxR.N; ++i) {
		vx = p.vxR.min + vxR * i / vxS;
		for (j = 0; j < p.vyR.N; ++j) {
			vy = p.vyR.min + vyR * j / vyS;
			for (k = 0; k < p.vzR.N; ++k) {
				vz = p.vzR.min + vzR * k / vzS;
				data.push_back(p.r[0]);
				data.push_back(p.r[1]);
				data.push_back(p.r[2]);
				data.push_back(vx);
				data.push_back(vy);
				data.push_back(vz);
/*
				data.push_back(p.r[0] * p.rfac);
				data.push_back(p.r[1] * p.rfac);
				data.push_back(p.r[2] * p.rfac);
				data.push_back(vx * p.vfac);
				data.push_back(vy * p.vfac);
				data.push_back(vz * p.vfac);
*/
			}
		}
	}
}
