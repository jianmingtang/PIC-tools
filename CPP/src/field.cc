#include <cmath>
#include <iostream>
#include <cstdio>
#include "field.h"


#define IBX 0
#define IBY 1
#define IBZ 2
#define IEX 3
#define IEY 4
#define IEZ 5


/**
 *  Destructor
 */
EMField::~EMField() {
}

/**
 *  Constructor
 */
EMField::EMField(const Parameter &p) {

	rsize = p.rsize;
	field_path = p.field_path;
	dataf[IBX] = p.Bx; dataf[IBY] = p.By; dataf[IBZ] = p.Bz;
	dataf[IEX] = p.Ex; dataf[IEY] = p.Ey; dataf[IEZ] = p.Ez;

	unsigned int i;
	for (i = 0; i < N_OF_FIELDS; ++i) {
		F_[i] = Array2D<float>(p.nz, p.nx);
		Fa_[i] = Array2D<float>(p.nz, p.nx);
		Fb_[i] = Array2D<float>(p.nz, p.nx);
	}

	if (p.source == "LANL") {
		Update_Ptr = & EMField::Update_LANL;
	}
	if (p.source == "NASA") {
		Update_Ptr = & EMField::Update_NASA;
	}
}

/**
 *  Update fields at two time slices
 */
void EMField::Update(int ta, int tb) {
	(this->*Update_Ptr)(ta, tb);
} 

void EMField::Update_LANL(int ta, int tb) {
	Read_From_LANL_File(ta, F_);
	Read_From_LANL_File(ta, Fa_);
	Read_From_LANL_File(tb, Fb_);
}

void EMField::Update_NASA(int ta, int tb) {
	Read_From_NASA_File(ta, F_);
	Read_From_NASA_File(ta, Fa_);
	Read_From_NASA_File(tb, Fb_);
}

/**
 *  Read one time slice from LANL files
 */
void EMField::Read_From_LANL_File(int t, Array2D<float> F[]) {
	unsigned int i;
// Two additonal parameters (4 bytes each) at the end of each time slice
	unsigned int skip = (rsize + 2) * DATA_SIZE * (t - 1);
	std::string fname;

	for (i = 0; i < N_OF_FIELDS; ++i) {
		std::string fname = field_path + "/" + dataf[i]; 
		std::ifstream ifs(fname.c_str(), std::ios::binary);
		if (!ifs) {
			std::cerr << "File " << fname << " not found!\n"; 
		} else {
			ifs.seekg(skip, ifs.beg);
			ifs.read((char*)F[i][0], rsize * DATA_SIZE);  
			ifs.close();
		}
	}
}

/**
 *  Read one time slice from a NASA file
 */
void EMField::Read_From_NASA_File(int t, Array2D<float> F[]) {
	unsigned int i;
	static unsigned int skip = (rsize * 4 * 3 + 8) * DATA_SIZE;
	char buf[9];
	std::string fname;

	sprintf(buf, "%05d.dat", t);
	fname = field_path + "/fields-" + buf;
	std::ifstream ifs(fname.c_str(), std::ios::binary);
	if (!ifs) {
		std::cerr << "File " << fname << " not found!\n"; 
	} else {
		ifs.seekg(skip, ifs.beg);
		for (i = 0; i < N_OF_FIELDS; ++i)
			ifs.read((char*)F[i][0], rsize * DATA_SIZE);  
		ifs.close();
	}
}

// This should be in grid units
// So that the conversion is done at the beginning and the end of simulation
double* EMField::Get_Fa(const double r[3]) {
	unsigned int ix, iz, j;
	double fx, fz;
	double wmm, wmp, wpm, wpp;
	double F[N_OF_FIELDS];

	ix = (unsigned int)floor(r[0]);
	iz = (unsigned int)floor(r[2]);
	fx = r[0] - ix;
	fz = r[2] - iz;	
	wmm = (1.-fx) * (1.-fz);
	wpm = fx * (1.-fz);
	wmp = (1.-fx) * fz;
	wpp = fx * fz;
// approx 1
	for (j = 0; j < N_OF_FIELDS; ++j) {
		std::cout << Fa_[j][iz][ix] << ", ";
	}
	std::cout << std::endl;
// approx 2
	for (j = 0; j < N_OF_FIELDS; ++j) {
		std::cout << Fa_[j][iz+1][ix+1] << ", ";
	}
	std::cout << std::endl;
// approx 3
	for (j = 0; j < N_OF_FIELDS; ++j) {
		F[j] = (wmm * Fa_[j][iz][ix]   +
			wpm * Fa_[j][iz][ix+1] +
			wmp * Fa_[j][iz+1][ix] +
			wpp * Fa_[j][iz+1][ix+1]);
	}
	for (j = 0; j < N_OF_FIELDS; ++j) {
		std::cout << F[j] << ", ";
	}
	std::cout << std::endl;
// approx 4
	F[IBX] = (wmm * (Fa_[IBX][iz-1][ix] + Fa_[IBX][iz][ix]    ) +
		wpm * (Fa_[IBX][iz-1][ix+1] + Fa_[IBX][iz][ix+1]  ) +
		wmp * (Fa_[IBX][iz][ix]     + Fa_[IBX][iz+1][ix]  ) +
		wpp * (Fa_[IBX][iz][ix+1]   + Fa_[IBX][iz+1][ix+1])) * 0.5;
	F[IBY] = (wmm * (Fa_[IBY][iz-1][ix-1] + Fa_[IBY][iz][ix-1]   +
			Fa_[IBY][iz-1][ix]    + Fa_[IBY][iz][ix]     ) +
		wpm * (Fa_[IBY][iz-1][ix]     + Fa_[IBY][iz][ix]     +
			Fa_[IBY][iz-1][ix+1]  + Fa_[IBY][iz][ix+1]   ) +
		wmp * (Fa_[IBY][iz][ix-1]     + Fa_[IBY][iz+1][ix-1] +
			Fa_[IBY][iz][ix]      + Fa_[IBY][iz+1][ix]   ) +
		wpp * (Fa_[IBY][iz][ix]       + Fa_[IBY][iz+1][ix]   +
			Fa_[IBY][iz][ix+1]    + Fa_[IBY][iz+1][ix+1] )) * 0.25;
	F[IBZ] = (wmm * (Fa_[IBZ][iz][ix-1] + Fa_[IBZ][iz][ix]    ) +
		wpm * (Fa_[IBZ][iz][ix]     + Fa_[IBZ][iz][ix+1]  ) +
		wmp * (Fa_[IBZ][iz+1][ix-1] + Fa_[IBZ][iz+1][ix]  ) +
		wpp * (Fa_[IBZ][iz+1][ix]   + Fa_[IBZ][iz+1][ix+1])) * 0.5;
	F[IEX] = (wmm * (Fa_[IEX][iz][ix-1] + Fa_[IEX][iz][ix]    ) +
		wpm * (Fa_[IEX][iz][ix]     + Fa_[IEX][iz][ix+1]  ) +
		wmp * (Fa_[IEX][iz+1][ix-1] + Fa_[IEX][iz+1][ix]  ) +
		wpp * (Fa_[IEX][iz+1][ix]   + Fa_[IEX][iz+1][ix+1])) * 0.5;
	F[IEY] = (wmm * Fa_[IEY][iz][ix] +
		wpm * Fa_[IEY][iz][ix+1] +
		wmp * Fa_[IEY][iz+1][ix] +
		wpp * Fa_[IEY][iz+1][ix+1]);
	F[IEZ] = (wmm * (Fa_[IEZ][iz-1][ix] + Fa_[IEZ][iz][ix]     ) +
		wpm * (Fa_[IEZ][iz-1][ix+1] + Fa_[IEZ][iz][ix+1]   ) +
		wmp * (Fa_[IEZ][iz][ix]     + Fa_[IEZ][iz+1][ix]   ) +
		wpp * (Fa_[IEZ][iz][ix+1]   + Fa_[IEZ][iz+1][ix+1])) * 0.5;

	for (j = 0; j < N_OF_FIELDS; ++j) {
		std::cout << F[j] << ", ";
	}
	std::cout << std::endl;
}

double EMField::Get_Bx(unsigned int i) const {
	return F_[0][0][i];
}
double EMField::Get_By(unsigned int i) const {
	return F_[1][0][i];
}
double EMField::Get_Bz(unsigned int i) const {
	return F_[2][0][i];
}
double EMField::Get_B(unsigned int i) const {
	return sqrt((double)F_[0][0][i] * F_[0][0][i]
		+ F_[1][0][i] * F_[1][0][i] + F_[2][0][i] * F_[2][0][i]);
}
double EMField::Get_Ex(unsigned int i) const {
	return F_[3][0][i];
}
double EMField::Get_Ey(unsigned int i) const {
	return F_[4][0][i];
}
double EMField::Get_Ez(unsigned int i) const {
	return F_[5][0][i];
}
double EMField::Get_E(unsigned int i) const {
	return sqrt((double)F_[3][0][i] * F_[3][0][i]
		+ F_[4][0][i] * F_[4][0][i] + F_[5][0][i] * F_[5][0][i]);
}
