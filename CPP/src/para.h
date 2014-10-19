#include <boost/program_options.hpp>
#include <iostream>
#include <fstream>


#ifndef PARAMETER_H
#define PARAMETER_H


#define N_COORDS 3
#define N_DIMS 6


namespace bpo = boost::program_options;


struct Range {
	double min, max;
	size_t N;
};


class Parameter {
public:
// Control parameters

// Field parameters
	size_t time;
	// Fields
	std::string Bx, By, Bz, Ex, Ey, Ez;
	// system dimensions
	double Lx, Ly, Lz;
	// number of grid points
	size_t nx, ny, nz;
	size_t rsize;
	// Field data source
	std::string source;
	std::string field_path;
	// Field time range
	size_t ftb, fte, fts;
	// plot background
	std::string plot;

// Tracer parameters
	// number of particles
	size_t Np;
	// time begin, end, step
	double tb, te, ts;
	// output filename
	std::string outf;
	// initial particle data file
	std::string pi_file;
	// initial position
	double r[N_COORDS];
	// initial velocity range
	Range vxR, vyR, vzR;
	size_t nvxyz;
	// scaling factors (obsolete)
	// double rfac, vfac;

	void Update();
	void Show_Info();
	void Process_Range(Range &, const std::string &);
	void Process_Tuple(size_t, double *, const std::string &);
	inline bool Neq(double, double) const; 
	bool Check_LANL_Info_File() const;
	void Dump_Conf_Para(bpo::variables_map &);
	void Split(const std::string &, const char, std::vector<std::string> &);
};


#endif /* PARAMETER_H */
