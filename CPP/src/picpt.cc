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
#include "pyplot.h"

#define PROGRAM_NAME "picpt"

namespace bpo = boost::program_options;

int main(int argc, char *argv[]) {

	Parameter para;

	std::vector<std::string> sublist;
	std::string conffile, vx, vy, vz, ri;

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
	;
	tOpt.add_options()
	("Np", bpo::value<size_t>(&para.Np)->
		default_value(1), "number of particles")
	("ts", bpo::value<double>(&para.ts)->
		default_value(-0.05), "time step")
	("vx", bpo::value<std::string>(&vx), "Vx range")
	("vy", bpo::value<std::string>(&vy), "Vy range")
	("vz", bpo::value<std::string>(&vz), "Vz range")
	("ri", bpo::value<std::string>(&ri), "start position")
	("steps", bpo::value<size_t>(&para.step), "number of steps")
	("output,o", bpo::value<std::string>(&para.outf)->
		default_value("./out.dat"), "Output file for particle trace")
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

	if (vm.count("vx")) {
		para.Split(vx, ',', sublist);
		para.vx[0] = atof(sublist[0].c_str());
		para.vx[1] = atof(sublist[1].c_str());
		para.nvx = atoi(sublist[2].c_str());
	} else
		para.nvx = 0;
	if (vm.count("vy")) {
		para.Split(vy, ',', sublist);
		para.vy[0] = atof(sublist[0].c_str());
		para.vy[1] = atof(sublist[1].c_str());
		para.nvy = atoi(sublist[2].c_str());
	} else
		para.nvy = 0;
	if (vm.count("vz")) {
		para.Split(vz, ',', sublist);
		para.vz[0] = atof(sublist[0].c_str());
		para.vz[1] = atof(sublist[1].c_str());
		para.nvz = atoi(sublist[2].c_str());
	} else
		para.nvz = 0;
	if (vm.count("ri")) {
		para.Split(ri, ',', sublist);
		para.r[0] = atof(sublist[0].c_str());
		para.r[1] = atof(sublist[1].c_str());
		para.r[2] = atof(sublist[2].c_str());
	} else {
		para.r[0] = 32; para.r[1] = 0; para.r[2] = -0.32;
	}
	std::cout << para.r[0] << std::endl;
	std::cout << para.r[1] << std::endl;
	std::cout << para.r[2] << std::endl;
	

	para.Update();

	if (vm.count("dump")) {
		para.Dump_Conf_Para(vm);
		return EXIT_SUCCESS;
	}

	if ((para.source == "LANL") && (!para.Check_LANL_Info_File()))
		return EXIT_FAILURE;

// Load EM fields from file
	EMField field(para);

	Particle pi;

	if (para.nvxyz) {
		pi.Set_Up_Uniform(para);
	} else {
		const double x[N_DIMS]={para.r[0],para.r[1],para.r[2],0,-3.5,0};
		pi = Particle(para, x);
	}

	ParticleTracer pt(field, pi, para);
	try {
		pt.Run(1750,1250,para);
	} catch (const std::exception& err) {
		std::cerr << err.what() << std::endl;
		return EXIT_FAILURE;
	}

	try {
		pt.Write(para.outf, para);
	} catch (const std::exception& err) {
		std::cerr << err.what() << std::endl;
		return EXIT_FAILURE;
	}

	return EXIT_SUCCESS;
}
