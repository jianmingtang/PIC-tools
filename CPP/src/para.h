#include <boost/program_options.hpp>
#include <iostream>
#include <fstream>

#ifndef PARAMETER_H
#define PARAMETER_H

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
	std::string output_path;

	std::string source;
	unsigned int rsize;
	std::string field_path, pdist_path;

	void Update();	
	bool Check_LANL_Info_File() const;
	void Dump_Conf_Para(bpo::variables_map &);

	Parameter() {}
	~Parameter() {}

private:

};


#endif /* PARAMETER_H */
