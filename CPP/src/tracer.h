#include <vector>
#include "para.h"
#include "field.h"
#include "particle.h"

#ifndef PARTICLE_TRACE_H
#define PARTICLE_TRACE_H


class ParticleTracer {
public:
	ParticleTracer(EMField &, const Particle &, const Parameter &);

	void Run(const Parameter &);
	void Write(const Parameter &);

private:
	unsigned int Np;
//	double rfac, vfac;
	EMField *field;
	std::vector<Particle> pt;

	void Move_One_Time_Step(double, double *, double *, double *);
};

#endif /* PARTICLE_TRACE_H */
