#include "para.h"

#ifndef EMFIELD_H
#define EMFIELD_H

#define DATA_SIZE 4
#define N_OF_FIELDS 6

class EMField {
public:
	EMField(const Parameter &);
	~EMField();
// get fields at any point
//	double get_B(const double[]);
//	double get_E(const double[]);

// get fields at the sites
	double get_Bx(unsigned int);
	double get_By(unsigned int);
	double get_Bz(unsigned int);
	double get_B(unsigned int) const;
	double get_Ex(unsigned int);
	double get_Ey(unsigned int);
	double get_Ez(unsigned int);
	double get_E(unsigned int) const;

private:
	unsigned long int rsize, skip;
	float *_F[N_OF_FIELDS];
//	float *Bx, *By, *Bz;

	void Read_From_File(std::string, unsigned int);

friend void pyplot (const EMField &, int, int, int);
};


#endif /* EMFIELD_H */
