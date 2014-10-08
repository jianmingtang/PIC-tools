#include <boost/program_options.hpp>
#include <iostream>
#include <fstream>

#ifndef PARAMETER_H
#define PARAMETER_H

namespace bpo = boost::program_options;

class ParaPIC {
public:
	unsigned int time_slice;
	std::string Bx, By, Bz, Ex, Ey, Ez;
	double Lx, Ly, Lz;
	unsigned int nx, ny, nz;
};

class ParaPT {
public:
	unsigned int Np, step;
	std::string output_path;
	void Read_From_File();
};

class Parameter: public ParaPT, public ParaPIC {
public:
	std::string origin;
	unsigned int rsize;
	std::string field_path, pdist_path;

	void Update();	
	bool Check_LANL_Info_File() const;
	void Dump_Conf_Para(bpo::variables_map &);

	Parameter() {}
	~Parameter() {}
//	Parameter(int argc, char *argv[]) : ParaBPO(argc,argv) {}

private:

	void Read_From_File();

};


#endif /* PARAMETER_H */
