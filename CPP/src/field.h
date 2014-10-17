#define ARRAY2D_DEBUG
#include "array2D.h"
#include "para.h"

#ifndef EMFIELD_H
#define EMFIELD_H

#define DATA_SIZE 4
#define N_OF_FIELDS 6

#define iBX 0
#define iBY 1
#define iBZ 2
#define iEX 3
#define iEY 4
#define iEZ 5


/**
 *   This class stores the EM field data
 */
class EMField {
public:
	EMField(const Parameter &);
	~EMField();

	void (EMField::*Update_Ptr)(int, int);
	void Update(int, int);

// get fields at any point
	void Set_Time(double);
	void Get(double *, double *) const;

// get fields at the sites
	double Get_Bx(unsigned int) const;
	double Get_By(unsigned int) const;
	double Get_Bz(unsigned int) const;
	double Get_B(unsigned int) const;
	double Get_Ex(unsigned int) const;
	double Get_Ey(unsigned int) const;
	double Get_Ez(unsigned int) const;
	double Get_E(unsigned int) const;

	double (EMField::*Get_F)(unsigned int) const;
        double Get_FF(unsigned int i) const {
		return (this->*Get_F)(i);
	}

private:
	// two time slices and their relative weights
	double ta, tb, wfa, wfb;
	// charge to mass ratio
	double qom;
	// length to grid ratio
	double LxR, LyR, LzR;
	unsigned int nxC, nyC, nzC;
	unsigned int rsize;
	std::string field_path, dataf[6];

	Array2D<float> F_[N_OF_FIELDS];
	Array2D<float> Fa_[N_OF_FIELDS];
	Array2D<float> Fb_[N_OF_FIELDS];

	void Read_From_NASA_File(int, Array2D<float> *);
	void Read_From_LANL_File(int, Array2D<float> *);
	void Update_LANL(int, int);
	void Update_NASA(int, int);

	void Get_fab(double *, double *, const Array2D<float> *) const;

	inline unsigned int iX(double) const;
	inline unsigned int iZ(double) const;
	inline double scaleX(double) const;
	inline double scaleZ(double) const;
//friend void pyplot (const EMField &, int, int, int);
};


#endif /* EMFIELD_H */
