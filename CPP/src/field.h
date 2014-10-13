#include "array2D.h"
#include "para.h"

#ifndef EMFIELD_H
#define EMFIELD_H

#define DATA_SIZE 4
#define N_OF_FIELDS 6


/**
 *   This class stores the EM field data
 */
class EMField {
public:
	EMField(const Parameter &);
	~EMField();

	void (EMField::*Update_Ptr)(int, int);
	void Update(int, int);

	void Update_LANL(int, int);
	void Update_NASA(int, int);
// get fields at any point
	double* Get_Fa(const double [3]);

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
	unsigned int rsize;
	std::string field_path, dataf[6];

	Array2D<float> F_[N_OF_FIELDS];
	Array2D<float> Fa_[N_OF_FIELDS];
	Array2D<float> Fb_[N_OF_FIELDS];

	void Read_From_NASA_File(int, Array2D<float> []);
	void Read_From_LANL_File(int, Array2D<float> []);

//friend void pyplot (const EMField &, int, int, int);
};


#endif /* EMFIELD_H */
