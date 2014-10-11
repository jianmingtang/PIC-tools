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
// get fields at any point
//	double get_B(const double[]);
//	double get_E(const double[]);

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
	unsigned int rsize, skip;
	float *_F[N_OF_FIELDS];

	void Read_From_File(std::string, unsigned int);

//friend void pyplot (const EMField &, int, int, int);
};


#endif /* EMFIELD_H */
