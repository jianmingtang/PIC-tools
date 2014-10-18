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

void Particle::Set_Up_Uniform(const Parameter &p) {
	size_t i, j, k;
	double vx, vy, vz;

	f = std::vector<double>(p.Np * N_DIMS);

	for (i = 0; i < p.nvx; ++i) {
		vx = p.vx[0]+(p.vx[1]-p.vx[0])*i/(p.nvx-1);
		for (j = 0; j < p.nvy; ++j) {
			vy = p.vy[0]+(p.vy[1]-p.vy[0])*j/(p.nvy-1);
			for (k = 0; k < p.nvz; ++k) {
				vz = p.vz[0]+(p.vz[1]-p.vz[0])*k/(p.nvz-1);
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

	std::cout << p.Np << " " << data.size() << std::endl;
}
