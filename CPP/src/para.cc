#include <sstream>
#include <cmath>
#include "para.h"


void Parameter::Split(const std::string &s,
		const char delim, std::vector<std::string> &sublist) {
	std::stringstream ss(s);
	std::string sub;
	sublist.clear();
	while (std::getline(ss, sub, delim)) {
		sublist.push_back(sub);
	}
}

void Parameter::Process_Range(Range &r, const std::string &s) {
	std::vector<std::string> sublist;

	Split(s, ',', sublist);
	if (sublist.size() != 3) throw
		std::invalid_argument("Invalid range parameters.");
	r.min = atof(sublist[0].c_str());
	r.max = atof(sublist[1].c_str());
	r.N = atoi(sublist[2].c_str());
}

void Parameter::Process_Tuple(size_t N, double *a, const std::string &s) {
	std::vector<std::string> sublist;

	Split(s, ',', sublist);
	if (sublist.size() != 3) throw
		std::invalid_argument("Invalid range parameters.");
	for (size_t i = 0; i < N; ++i)
		a[i] = atof(sublist[i].c_str());
}

void Parameter::Update() {
	std::stringstream ss;

	nvxyz = vxR.N * vyR.N * vzR.N;
	if (nvxyz != 0) Np = nvxyz;

	rsize = nx * nz;
	ss << "pt-r" << r[0] << "_" << r[2] << "-v"
		<< (vxR.max+vxR.min)/2 << "_"
		<< (vyR.max+vyR.min)/2 << "_"
		<< (vzR.max+vzR.min)/2 << "-t"
		<< tb << "_" << te << ".dat";
	outf = ss.str();

// scaling factors (obsolete)
// 25 is the mass ratio
//	rfac = sqrt(25.);
// 0.5 is the wpe/wce
//	vfac = 0.5/sqrt(25.);
}

void Parameter::Show_Info() {
	std::cout << "System dimensions: " << std::endl;
	std::cout << "\tLx: " << Lx << std::endl;
	std::cout << "\tLy: " << Ly << std::endl;
	std::cout << "\tLz: " << Lz << std::endl;
	std::cout << "Grid points: " << std::endl;
	std::cout << "\tnx: " << nx << std::endl;
	std::cout << "\tny: " << ny << std::endl;
	std::cout << "\tnz: " << nz << std::endl;
	std::cout << "Number of particles: " << Np << std::endl;
	std::cout << "Time: " << std::endl;
	std::cout << "\tt: " << tb << " " << te << " " << ts << std::endl;
	std::cout << "\tft: " << ftb << " " << fte << " " << fts << std::endl;
	std::cout << "Initial conditions: " << std::endl;
	std::cout << "\tr: "<< r[0]<<" "<<r[1]<<" "<<r[2]<<std::endl;
	std::cout << "\tvx: "<<vxR.min<<" "<<vxR.max<<" "<<vxR.N<< std::endl;
	std::cout << "\tvy: "<<vyR.min<<" "<<vyR.max<<" "<<vyR.N<< std::endl;
	std::cout << "\tvz: "<<vzR.min<<" "<<vzR.max<<" "<<vzR.N<< std::endl;
}

bool Parameter::Neq(double a, double b) const {
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
		|| Neq(L[0],Lx) || Neq(L[1],Ly) || Neq(L[2],Lz)) {
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


/// Print out simulation parameters.
/** 
 *  This prints out all current simulation parameters and can be used in
 *  an input configuration file.
 */
void Parameter::Dump_Conf_Para (bpo::variables_map &vm) {
	bpo::variables_map::iterator i;
	bpo::variable_value v;
	size_t val_i;
	double val_d;
	std::string val_s;
// needs to exclude control input later
        std::cout << "#\n# This is automatically generated.\n#\n";
	for (i = vm.begin(); i != vm.end(); ++i) {
		std::cout << "\t" << i->first << " = ";
		v = i->second;
		if (!v.empty()) {
			const std::type_info& v_type = v.value().type();
			if (v_type == typeid(size_t)) {
				val_i = v.as<size_t>();
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
