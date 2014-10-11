#include <cmath>
#include <iostream>
#include "field.h"

EMField::EMField(const Parameter &p) {

	rsize = p.rsize;
// Two additonal parameters (4 bytes each) at the end of each time slice

	unsigned int i;
	std::string dataf[6] = { p.Bx, p.By, p.Bz, p.Ex, p.Ey, p.Ez };

	if (p.source == "LANL") {
		skip = (rsize + 2) * DATA_SIZE * (p.time - 1);

		for (i = 0; i < N_OF_FIELDS; ++i) {
			std::string fp = p.field_path + "/" + dataf[i]; 
			_F[i] = new float [rsize];
			Read_From_File(fp, i);
		}
	}
	if (p.source == "NASA") {
//		std::string fname(p.time);
		std::string fp = p.field_path + "/fields-01750.dat"; 
		skip = (rsize * 4 * 3 + 8) * DATA_SIZE;
		for (i = 0; i < N_OF_FIELDS; ++i) {
			_F[i] = new float [rsize];
			Read_From_File(fp, i);
			skip += rsize * DATA_SIZE;
		}
	}
}


/**
 *  Deallocate EM Field.
 *  We need to be careful with this since we have not defined
 *  a deep copy constructor.
 */
EMField::~EMField() {
	unsigned int i;
	for (i = 0; i < N_OF_FIELDS; ++i) {
		delete [] _F[i];
	}
}

void EMField::Read_From_File(std::string fp, unsigned int i) {
	std::ifstream ifs(fp.c_str(), std::ios::binary);
	if (!ifs) {
		std::cerr << "File " << fp << " not found!\n"; 
	} else {
		ifs.seekg(skip, ifs.beg);
		ifs.read((char*)_F[i], rsize * DATA_SIZE);  
	}
	ifs.close();
}

double EMField::Get_Bx(unsigned int i) const {
	return (double)_F[0][i];
}
double EMField::Get_By(unsigned int i) const {
	return (double)_F[1][i];
}
double EMField::Get_Bz(unsigned int i) const {
	return (double)_F[2][i];
}
double EMField::Get_B(unsigned int i) const {
	return sqrt((double)_F[0][i]*_F[0][i]+_F[1][i]*_F[1][i]+_F[2][i]*_F[2][i]);
}
double EMField::Get_Ex(unsigned int i) const {
	return (double)_F[3][i];
}
double EMField::Get_Ey(unsigned int i) const {
	return (double)_F[4][i];
}
double EMField::Get_Ez(unsigned int i) const {
	return (double)_F[5][i];
}
double EMField::Get_E(unsigned int i) const {
	return sqrt((double)_F[3][i]*_F[3][i]+_F[4][i]*_F[4][i]+_F[5][i]*_F[5][i]);
}
