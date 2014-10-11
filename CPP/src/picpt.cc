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
#include <boost/program_options.hpp>
#include "config.h"
#include "para.h"
#include "field.h"
#include "dist.h"
#include "tracer.h"
#include "pyplot.h"

#define PROGRAM_NAME "picpt"

namespace bpo = boost::program_options;

int main(int argc, char *argv[]) {

	Parameter para;

	std::string conffile;
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
	("plot-B", "plot the magnetic field")
	("plot-Bx", "plot the x component of the magnetic field")
	("plot-By", "plot the y component of the magnetic field")
	("plot-Bz", "plot the z component of the magnetic field")
	("plot-E", "plot the electric field")
	("plot-Ex", "plot the x component of the electric field")
	("plot-Ey", "plot the y component of the electric field")
	("plot-Ez", "plot the z component of the electric field")
	;
	fOpt.add_options()
	("source", bpo::value<std::string>(&para.source),
		"data source")
	("field-path", bpo::value<std::string>(&para.field_path),
		"Search path for field data")
	("pdist-path", bpo::value<std::string>(&para.pdist_path),
		"Search path for particle distribution")
	("time", bpo::value<unsigned int>(&para.time)->
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
	("nx", bpo::value<unsigned int>(&para.nx), "nx")
	("ny", bpo::value<unsigned int>(&para.ny), "ny")
	("nz", bpo::value<unsigned int>(&para.nz), "nz")
	;
	tOpt.add_options()
	("Np", bpo::value<unsigned int>(&para.Np), "number of particles")
	("steps", bpo::value<unsigned int>(&para.step), "number of steps")
	;
	allOpt.add(cOpt).add(fOpt).add(tOpt);
	confOpt.add(fOpt).add(tOpt);

	try {
		bpo::store(bpo::parse_command_line(argc, argv, allOpt), vm);
		bpo::notify(vm);

		if (vm.count("help")) {
			std::cout << PACKAGE_STRING << "\n";
			std::cout << "\nUsage: " << PROGRAM_NAME
				<< " [options]\n";
			std::cout << allOpt <<"\n";
			exit(EXIT_SUCCESS);
		}

		std::ifstream ifs(conffile.c_str());
		if (!ifs) {
			std::cout << PACKAGE_STRING << "\n\n";
			std::cout << "Missing configuration file. ";
			std::cout << "Use -h for help.\n";
			exit(EXIT_FAILURE);
		} else {
			bpo::store(bpo::parse_config_file(ifs, confOpt), vm);
			bpo::notify(vm);
		}	
	} catch (const std::exception& e) {
		std::cerr << e.what() << std::endl;
		exit(EXIT_FAILURE);
	}

	para.Update();

	if ((para.source == "LANL") && (!para.Check_LANL_Info_File()))
		exit(EXIT_FAILURE);

// Load EM fields from file
	EMField field(para);

	if (vm.count("dump")) {
		para.Dump_Conf_Para(vm);
		exit(EXIT_SUCCESS);
	}

	bool plot = false;
	if (vm.count("plot-Bx")) {
		plot = true;
		field.Get_F = &EMField::Get_Bx;
	}
	if (vm.count("plot-By")) {
		plot = true;
		field.Get_F = &EMField::Get_By;
	}
	if (vm.count("plot-Bz")) {
		plot = true;
		field.Get_F = &EMField::Get_Bz;
	}
	if (vm.count("plot-Ex")) {
		plot = true;
		field.Get_F = &EMField::Get_Ex;
	}
	if (vm.count("plot-Ey")) {
		plot = true;
		field.Get_F = &EMField::Get_Ey;
	}
	if (vm.count("plot-Ez")) {
		plot = true;
		field.Get_F = &EMField::Get_Ez;
	}
	if (vm.count("plot-B")) {
		plot = true;
		field.Get_F = &EMField::Get_B;
	}
	if (vm.count("plot-E")) {
		plot = true;
		field.Get_F = &EMField::Get_E;
	}
	if (plot) {
		double *A = new double [para.rsize];
		for (unsigned int i = 0; i < para.rsize; ++i)
			A[i] = field.Get_FF(i);	
		pyplot (A, para.nz, para.nx);
		delete [] A;
		exit(EXIT_SUCCESS);
	}

	Distribution distf(para);

	ParticleTracer pt(field,distf,para);
}
