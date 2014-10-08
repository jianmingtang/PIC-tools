#include <cmath>
#include <iostream>
#include "field.h"

EMField::EMField(const Parameter &p) {

	rsize = p.nx * p.nz;
// Two additonal parameters (4 bytes each) at the end of each time slice
	skip = (rsize + 2) * DATA_SIZE * (p.time_slice - 1);
	std::string dataf[6] = { p.Bx, p.By, p.Bz, p.Ex, p.Ey, p.Ez };

	unsigned int i;
	for (i = 0; i < N_OF_FIELDS; ++i) {
		std::string fp = p.field_path + "/" + dataf[i]; 
		_F[i] = new float [rsize];
		Read_From_File(fp, i);
	}
}


/**
 *  Deallocate EM Field.
 *  We need to be careful with this since we have not defined a copy constructor.
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

double EMField::get_Bx(unsigned int i) {
	return (double)_F[0][i];
}
double EMField::get_By(unsigned int i) {
	return (double)_F[1][i];
}
double EMField::get_Bz(unsigned int i) {
	return (double)_F[2][i];
}
double EMField::get_B(unsigned int i) const {
	return sqrt((double)_F[0][i]*_F[0][i]+_F[1][i]*_F[1][i]+_F[2][i]*_F[2][i]);
}
double EMField::get_Ex(unsigned int i) {
	return (double)_F[3][i];
}
double EMField::get_Ey(unsigned int i) {
	return (double)_F[4][i];
}
double EMField::get_Ez(unsigned int i) {
	return (double)_F[5][i];
}
double EMField::get_E(unsigned int i) const {
	return sqrt((double)_F[3][i]*_F[3][i]+_F[4][i]*_F[4][i]+_F[5][i]*_F[5][i]);
}
