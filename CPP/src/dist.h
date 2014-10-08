#include "para.h"
#include "particle.h"

#ifndef DISTRIBUTION_H
#define DISTRIBUTION_H

class Distribution {
public:
	Distribution(const Parameter &);
private:
	std::vector<Particle> f;
};

#endif /* DISTRIBUTION_H */
