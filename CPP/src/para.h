#include <boost/program_options.hpp>
#include <iostream>
#include <fstream>


#ifndef PARAMETER_H
#define PARAMETER_H


#define N_COORDS 3
#define N_DIMS 6


namespace bpo = boost::program_options;


class Parameter {
public:
	size_t time;
	std::string Bx, By, Bz, Ex, Ey, Ez;
	double Lx, Ly, Lz;
	size_t nx, ny, nz;
	double rfac, vfac;

	size_t Np, step;
	double ts;
	std::string outf;

	std::string source;
	unsigned int rsize;
	std::string field_path, pdist_path;

	double r[N_COORDS];
	double vx[2], vy[2], vz[2];
	size_t nvx, nvy, nvz, nvxyz;

	Parameter() {}

	void Split(const std::string &, const char, std::vector<std::string> &);
	void Update();	
	bool Check_LANL_Info_File() const;
	void Dump_Conf_Para(bpo::variables_map &);
};


#endif /* PARAMETER_H */
