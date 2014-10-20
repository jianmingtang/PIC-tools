#include <cmath>
#include "field.h"


/**
 *  Constructor
 */
EMField::EMField(const Parameter &p) {

	qom = -1.;
//	qom = 1./25;
	nxC = 1;
	nyC = p.ny / 2;
	nzC = p.nz / 2;
	LxR = p.Lx / (p.nx - 1);
	LyR = p.Ly / p.ny;
	LzR = p.Lz / (p.nz - 1);
	rsize = p.rsize;
	field_path = p.field_path;
	dataf[iBX] = p.Bx; dataf[iBY] = p.By; dataf[iBZ] = p.Bz;
	dataf[iEX] = p.Ex; dataf[iEY] = p.Ey; dataf[iEZ] = p.Ez;

	for (size_t i = 0; i < N_OF_FIELDS; ++i) {
		Fa_[i] = Array2D<float>(p.nz, p.nx);
		Fb_[i] = Array2D<float>(p.nz, p.nx);
	}

	if (p.source == "LANL")
		Update_Ptr = & EMField::Update_LANL;
	if (p.source == "NASA")
		Update_Ptr = & EMField::Update_NASA;

	Get_F_Ptr = & EMField::Get_E;
	if (p.plot == "Bx") Get_F_Ptr = & EMField::Get_Bx;
	if (p.plot == "By") Get_F_Ptr = & EMField::Get_By;
	if (p.plot == "Bz") Get_F_Ptr = & EMField::Get_Bz;
	if (p.plot == "B")  Get_F_Ptr = & EMField::Get_B;
	if (p.plot == "Ex") Get_F_Ptr = & EMField::Get_Ex;
	if (p.plot == "Ey") Get_F_Ptr = & EMField::Get_Ey;
	if (p.plot == "Ez") Get_F_Ptr = & EMField::Get_Ez;
//	if (p.plot == "E")  Get_F_Ptr = & EMField::Get_E;
}

/**
 *  Destructor
 */
EMField::~EMField() {
}

/**
 *  Update fields at two time slices
 */
void EMField::Update(int ta, int tb) {
	this->ta = ta;
	this->tb = tb;
	(this->*Update_Ptr)(ta, tb);
} 

void EMField::Update_LANL(int ta, int tb) {
	Read_From_LANL_File(ta, Fa_);
	Read_From_LANL_File(tb, Fb_);
}

void EMField::Update_NASA(int ta, int tb) {
	Read_From_NASA_File(ta, Fa_);
	Read_From_NASA_File(tb, Fb_);
}

/**
 *  Read one time slice from LANL files
 */
void EMField::Read_From_LANL_File(int t, Array2D<float> *F) {
// Two additonal parameters (4 bytes each) at the end of each time slice
	size_t skip = (rsize + 2) * DATA_SIZE * (t - 1);
	std::string fname, err;

	for (size_t i = 0; i < N_OF_FIELDS; ++i) {
		std::string fname = field_path + "/" + dataf[i]; 
		std::ifstream ifs(fname.c_str(), std::ios::binary);
		if (!ifs) {
			err = "File " + fname + " not found!"; 
			throw std::invalid_argument(err);
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
void EMField::Read_From_NASA_File(int t, Array2D<float> *F) {
	size_t i;
	static size_t skip = (rsize * 4 * 3 + 8) * DATA_SIZE;
	char buf[9];
	std::string fname, err;

	sprintf(buf, "%05d.dat", t);
	fname = field_path + "/fields-" + buf;
	std::ifstream ifs(fname.c_str(), std::ios::binary);
	if (!ifs) {
		err = "File " + fname + " not found!"; 
		throw std::invalid_argument(err);
	} else {
		ifs.seekg(skip, ifs.beg);
		for (i = 0; i < N_OF_FIELDS; ++i)
			ifs.read((char*)F[i][0], rsize * DATA_SIZE);  
		ifs.close();
	}
}

void EMField::Set_Time(double t) {
	wfa = (tb - t) / (tb - ta);
	wfb = (t - ta) / (tb - ta);
}

void EMField::Get(double *f, double *r) const {

	double fa[N_OF_FIELDS], fb[N_OF_FIELDS];

	Get_fab(fa, r, Fa_);
	Get_fab(fb, r, Fb_);
	for (unsigned int i = 0; i < N_OF_FIELDS; ++i) {
		f[i] = fa[i] * wfa + fb[i] * wfb;
		f[i] = f[i] * qom;
	}
}

inline double EMField::scaleX(double x) const {
	return x / LxR + nxC;
}

inline double EMField::scaleZ(double z) const {
	return z / LzR + nzC;
}

inline unsigned int EMField::iX(double x) const {
	return floor(x / LxR + nxC);
}

inline unsigned int EMField::iZ(double z) const {
	return floor(z / LzR + nzC);
}

void EMField::Get_fab(double *f, double *r, const Array2D<float> *F) const {

	unsigned int ix, iz, j;
	double fx, fz;
// weighting factors for bilinear interpolation
	double wmm, wmp, wpm, wpp;

	fx = scaleX(r[0]);
	fz = scaleZ(r[2]);
	ix = floor(fx);
	iz = floor(fz);
	assert (ix >= 1 && ix < 999);
	assert (iz >= 1 && iz < 799);
	fx -= ix;
	fz -= iz;	
	wmm = (1.-fx) * (1.-fz);
	wpm = fx * (1.-fz);
	wmp = (1.-fx) * fz;
	wpp = fx * fz;
	assert(wmm>0);
	assert(wpm>0);
	assert(wmp>0);
	assert(wpp>0);
/*
// approx 1
	for (j = 0; j < N_OF_FIELDS; ++j) {
		std::cout << F[j][iz][ix] << ", ";
	}
	std::cout << std::endl;
// approx 2
	for (j = 0; j < N_OF_FIELDS; ++j) {
		std::cout << F[j][iz+1][ix+1] << ", ";
	}
	std::cout << std::endl;
// approx 3
	for (j = 0; j < N_OF_FIELDS; ++j) {
		f[j] = (wmm * F[j][iz][ix]   +
			wpm * F[j][iz][ix+1] +
			wmp * F[j][iz+1][ix] +
			wpp * F[j][iz+1][ix+1]);
	}
*/
// approx 4
// bilinear interpolation
	f[iBX] = (wmm * (F[iBX][iz-1][ix]   + F[iBX][iz][ix]    ) +
		  wpm * (F[iBX][iz-1][ix+1] + F[iBX][iz][ix+1]  ) +
		  wmp * (F[iBX][iz][ix]     + F[iBX][iz+1][ix]  ) +
		  wpp * (F[iBX][iz][ix+1]   + F[iBX][iz+1][ix+1]) ) * 0.5;
	f[iBY] = (wmm * (F[iBY][iz-1][ix-1] + F[iBY][iz][ix-1]  +
			 F[iBY][iz-1][ix]   + F[iBY][iz][ix]     ) +
		  wpm * (F[iBY][iz-1][ix]   + F[iBY][iz][ix]    +
			 F[iBY][iz-1][ix+1] + F[iBY][iz][ix+1]   ) +
		  wmp * (F[iBY][iz][ix-1]   + F[iBY][iz+1][ix-1]+
			 F[iBY][iz][ix]     + F[iBY][iz+1][ix]   ) +
		  wpp * (F[iBY][iz][ix]     + F[iBY][iz+1][ix]  +
			 F[iBY][iz][ix+1]   + F[iBY][iz+1][ix+1] ) ) * 0.25;
	f[iBZ] = (wmm * (F[iBZ][iz][ix-1]   + F[iBZ][iz][ix]    ) +
		  wpm * (F[iBZ][iz][ix]     + F[iBZ][iz][ix+1]  ) +
		  wmp * (F[iBZ][iz+1][ix-1] + F[iBZ][iz+1][ix]  ) +
		  wpp * (F[iBZ][iz+1][ix]   + F[iBZ][iz+1][ix+1]) ) * 0.5;
	f[iEX] = (wmm * (F[iEX][iz][ix-1]   + F[iEX][iz][ix]    ) +
		  wpm * (F[iEX][iz][ix]     + F[iEX][iz][ix+1]  ) +
		  wmp * (F[iEX][iz+1][ix-1] + F[iEX][iz+1][ix]  ) +
		  wpp * (F[iEX][iz+1][ix]   + F[iEX][iz+1][ix+1]) ) * 0.5;
	f[iEY] = (wmm * F[iEY][iz][ix]   +
		  wpm * F[iEY][iz][ix+1] +
		  wmp * F[iEY][iz+1][ix] +
		  wpp * F[iEY][iz+1][ix+1]);
	f[iEZ] = (wmm * (F[iEZ][iz-1][ix]   + F[iEZ][iz][ix]    ) +
		  wpm * (F[iEZ][iz-1][ix+1] + F[iEZ][iz][ix+1]  ) +
		  wmp * (F[iEZ][iz][ix]     + F[iEZ][iz+1][ix]  ) +
		  wpp * (F[iEZ][iz][ix+1]   + F[iEZ][iz+1][ix+1]) ) * 0.5;
}

double EMField::Get_Bx(unsigned int i) const {
	return Fa_[iBX][0][i];
}
double EMField::Get_By(unsigned int i) const {
	return Fa_[iBY][0][i];
}
double EMField::Get_Bz(unsigned int i) const {
	return Fa_[iBZ][0][i];
}
double EMField::Get_B(unsigned int i) const {
	return sqrt((double)Fa_[iBX][0][i] * Fa_[iBX][0][i]
		+ Fa_[iBY][0][i] * Fa_[iBY][0][i]
		+ Fa_[iBZ][0][i] * Fa_[iBZ][0][i]);
}
double EMField::Get_Ex(unsigned int i) const {
	return Fa_[iEX][0][i];
}
double EMField::Get_Ey(unsigned int i) const {
	return Fa_[iEY][0][i];
}
double EMField::Get_Ez(unsigned int i) const {
	return Fa_[iEZ][0][i];
}
double EMField::Get_E(unsigned int i) const {
	return sqrt((double)Fa_[iEX][0][i] * Fa_[iEX][0][i]
		+ Fa_[iEY][0][i] * Fa_[iEY][0][i]
		+ Fa_[iEZ][0][i] * Fa_[iEZ][0][i]);
}
