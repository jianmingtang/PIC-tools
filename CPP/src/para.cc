#include <cmath>
#include "para.h"


bool neq(double a, double b) {
	if (fabs(a-b) > 1.e-3) return true;
	else return false;
}

/**
 *  Perform a consistency check on system sizes if a LANL info file is present.
 *  The LANL binary info file contains two records with 3 numbers each.
 */
bool Parameter::Check_LANL_Info_File() const {
	int buf;
	unsigned int n[3];
	float L[3];
	std::string fp = field_path + "/info";
        std::ifstream ifs(fp.c_str(), std::ios::binary);
        if (!ifs) {
		std::cerr << "LANL info file not found!\n"; 
	} else {
		ifs.read((char*)&buf, sizeof(int));
		ifs.read((char*)&n[0], sizeof(int)*3);
		ifs.read((char*)&buf, sizeof(int));
		ifs.read((char*)&buf, sizeof(int));
		ifs.read((char*)&L[0], sizeof(float)*3);
		ifs.read((char*)&buf, sizeof(int));
	}
	ifs.close();
	if ((n[0] != nx) || (n[1] != ny) || (n[2] != nz)
		|| neq(L[0],Lx) || neq(L[1],Ly) || neq(L[2],Lz)) {
		std::cerr << "Inconsistent LANL PIC parameters!\n";
		std::cerr << "Parameters from LANL info file:\n";
		std::cerr << "\tnx = " << n[0] << "\n";
		std::cerr << "\tny = " << n[1] << "\n";
		std::cerr << "\tnz = " << n[2] << "\n";
		std::cerr << "\tLx = " << L[0] << "\n";
		std::cerr << "\tLy = " << L[1] << "\n";
		std::cerr << "\tLz = " << L[2] << "\n";
		return false;
	} else {
		return true;
	}
}

void Parameter::Update() {
	rsize = nx * nz;
	rfac = sqrt(25.);
	vfac = 0.5/sqrt(25.);
}


/// Print out simulation parameters.
/** 
 *  This prints out all current simulation parameters and can be used in
 *  an input configuration file.
 */
void Parameter::Dump_Conf_Para (bpo::variables_map &vm) {
	bpo::variables_map::iterator i;
	bpo::variable_value v;
	unsigned int val_i;
	double val_d;
	std::string val_s;
// needs to exclude control input later
        std::cout << "#\n# This is automatically generated.\n#\n";
	for (i = vm.begin(); i != vm.end(); ++i) {
		std::cout << "\t" << i->first << " = ";
		v = i->second;
		if (!v.empty()) {
			const std::type_info& v_type = v.value().type();
			if (v_type == typeid(unsigned int)) {
				val_i = v.as<unsigned int>();
				std::cout << val_i << "\n";
			} else if (v_type == typeid(double)) {
				val_d = v.as<double>();
				std::cout << val_d << "\n";
			} else if (v_type == typeid(std::string)) {
				val_s = v.as<std::string>();
				std::cout << val_s << "\n";
			}
		} else {
			std::cout << "\n";
		}
	}
}
