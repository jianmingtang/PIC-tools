/*
    picpt: Particle in Cell Particle Tracing

    Copyright (C) 2014  Jian-Ming Tang <jian.ming.tang@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include <fstream>
#include <iostream>
#include <string>
#include <cstdlib>
#include <boost/program_options.hpp>
#include "config.h"
#include "para.h"
#include "field.h"
#include "particle.h"
#include "tracer.h"

#define PROGRAM_NAME "picpt"

namespace bpo = boost::program_options;

int main(int argc, char *argv[]) {

	Parameter para;

	std::vector<std::string> sublist;
	std::string conffile;
	std::string vxR, vyR, vzR, ri;

	bpo::variables_map vm;
	bpo::options_description cOpt("Control options");
	bpo::options_description fOpt("Field options");
	bpo::options_description tOpt("Tracer options");
	bpo::options_description allOpt;
	bpo::options_description confOpt;

	cOpt.add_options()
	("help,h", "print this help message")
	("config,c", bpo::value<std::string>(&conffile),
		"configuration file (required)")
	("dump", "print out simulation parameters")
#ifdef HAVE_PYTHON
	("plot-B", "plot the magnetic field")
	("plot-Bx", "plot the x component of the magnetic field")
	("plot-By", "plot the y component of the magnetic field")
	("plot-Bz", "plot the z component of the magnetic field")
	("plot-E", "plot the electric field")
	("plot-Ex", "plot the x component of the electric field")
	("plot-Ey", "plot the y component of the electric field")
	("plot-Ez", "plot the z component of the electric field")
#endif
	;
	fOpt.add_options()
	("source", bpo::value<std::string>(&para.source),
		"data source")
	("field-path", bpo::value<std::string>(&para.field_path),
		"Search path for field data")
	("time", bpo::value<size_t>(&para.time)->
		default_value(1), "Time slice")
	("Bx", bpo::value<std::string>(&para.Bx), "Bx data file")
	("By", bpo::value<std::string>(&para.By), "By data file")
	("Bz", bpo::value<std::string>(&para.Bz), "Bz data file")
	("Ex", bpo::value<std::string>(&para.Ex), "Ex data file")
	("Ey", bpo::value<std::string>(&para.Ey), "Ey data file")
	("Ez", bpo::value<std::string>(&para.Ez), "Ez data file")
	("Lx", bpo::value<double>(&para.Lx), "Lx/de")
	("Ly", bpo::value<double>(&para.Ly), "Ly/de")
	("Lz", bpo::value<double>(&para.Lz), "Lz/de")
	("nx", bpo::value<size_t>(&para.nx), "nx")
	("ny", bpo::value<size_t>(&para.ny), "ny")
	("nz", bpo::value<size_t>(&para.nz), "nz")
	("ftb", bpo::value<size_t>(&para.ftb)->
		default_value(0), "field time begin")
	("fte", bpo::value<size_t>(&para.fte)->
		default_value(0), "field time end")
	("fts", bpo::value<size_t>(&para.fts)->
		default_value(0), "field time step")
	;
	tOpt.add_options()
	("pi-file", bpo::value<std::string>(&para.pi_file),
		"Initial particle set")
	("Np", bpo::value<size_t>(&para.Np)->
		default_value(1), "number of particles")
	("tb", bpo::value<double>(&para.tb), "time begin")
	("te", bpo::value<double>(&para.te), "time end")
	("ts", bpo::value<double>(&para.ts)->
		default_value(-0.05,"-0.05"), "time step")
	("vx", bpo::value<std::string>(&vxR), "Vx range")
	("vy", bpo::value<std::string>(&vyR), "Vy range")
	("vz", bpo::value<std::string>(&vzR), "Vz range")
	("ri", bpo::value<std::string>(&ri), "start position")
	("output,o", bpo::value<std::string>(&para.outf)->
		default_value("./out.dat"), "Output file for particle trace")
	;
	allOpt.add(cOpt).add(fOpt).add(tOpt);
	confOpt.add(fOpt).add(tOpt);

// Verify input parameters
	try {
		bpo::store(bpo::parse_command_line(argc, argv, allOpt), vm);
		bpo::notify(vm);

		if (vm.count("help")) {
			std::cout << PACKAGE_STRING << "\n";
			std::cout << "\nUsage: " << PROGRAM_NAME
				<< " [options]\n";
			std::cout << allOpt <<"\n";
			return EXIT_SUCCESS;
		}

		std::ifstream ifs(conffile.c_str());
		if (!ifs) {
			std::cout << PACKAGE_STRING << "\n\n";
			std::cout << "Missing configuration file. ";
			std::cout << "Use -h for help.\n";
			return EXIT_FAILURE;
		} else {
			bpo::store(bpo::parse_config_file(ifs, confOpt), vm);
			bpo::notify(vm);
		}	
	} catch (const std::exception& e) {
		std::cerr << e.what() << std::endl;
		return EXIT_FAILURE;
	}

	if ((para.source == "LANL") && (!para.Check_LANL_Info_File()))
		return EXIT_FAILURE;

// Process input parameters
	if (vm.count("plot-Bx")) para.plot = "Bx";
	if (vm.count("plot-By")) para.plot = "By";
	if (vm.count("plot-Bz")) para.plot = "Bz";
	if (vm.count("plot-B")) para.plot = "B";
	if (vm.count("plot-Ex")) para.plot = "Ex";
	if (vm.count("plot-Ey")) para.plot = "Ey";
	if (vm.count("plot-Ez")) para.plot = "Ez";
	if (vm.count("plot-E")) para.plot = "E";
	try {
		if (vm.count("vx")) {
			para.Process_Range(para.vxR, vxR);
		} else {
			para.Process_Range(para.vxR, "0,0,0");
		}
		if (vm.count("vy")) {
			para.Process_Range(para.vyR, vyR);
		} else {
			para.Process_Range(para.vyR, "0,0,0");
		}
		if (vm.count("vz")) {
			para.Process_Range(para.vzR, vzR);
		} else {
			para.Process_Range(para.vzR, "0,0,0");
		}
		if (vm.count("ri")) {
			para.Process_Tuple(3, para.r, ri);
		} else {
			para.Process_Tuple(3, para.r, "0,0,0");
		}

		para.Update();
	}
	catch (const std::exception& err) {
		std::cerr << err.what() << std::endl;
		return EXIT_FAILURE;
	}


	if (vm.count("dump")) {
		para.Dump_Conf_Para(vm);
		return EXIT_SUCCESS;
	}

	para.Show_Info();

// EM fields
	EMField field(para);

// initial particle set
	Particle pi;

	if (para.nvxyz) {
		pi.Set_Up_Uniform(para);
	} else {
		const double x[N_DIMS]={para.r[0],para.r[1],para.r[2],0,0,0};
		pi = Particle(para, x);
	}

	ParticleTracer tracer(field, pi, para);
	try {
		tracer.Run(para);
		tracer.Write(para);
	}
	catch (const std::exception& err) {
		std::cerr << err.what() << std::endl;
		return EXIT_FAILURE;
	}

	return EXIT_SUCCESS;
}
