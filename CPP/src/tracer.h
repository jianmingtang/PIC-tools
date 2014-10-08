#include "para.h"
#include "field.h"
#include "dist.h"

#ifndef PARTICLE_TRACER_H
#define PARTICLE_TRACER_H

class ParticleTracer {
public:
	ParticleTracer(const EMField &, const Distribution &,
		const Parameter &);
	~ParticleTracer() {}
private:
};

#endif /* PARTICLE_TRACER_H */
