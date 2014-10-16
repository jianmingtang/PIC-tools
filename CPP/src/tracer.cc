#include <iostream>
#include <boost/numeric/odeint/integrate/integrate.hpp>
#include "tracer.h"


#define iRx 0
#define iRy 1
#define iRz 2
#define iVx 3
#define iVy 4
#define iVz 5


using namespace boost::numeric;


ParticleTracer::ParticleTracer(EMField &f, const Particle &pi,
		const Parameter &p) {
	this->field = &f;
	this->Np = p.Np;
	pt.push_back(pi);
}

void Check_Bounds(double *x) {
}

void ParticleTracer::Run(double ti, double tf, const Parameter &p) {
	Particle a;
	double t = ti, dt = p.ts;
	double *x;
	int j = 0;
	bool stop = false;
	for (int i = 1750; i > 1250; i-=25) {
		field->Update(i,i-25);
		while (t >= i-25) {
			std::cout << t << " \n";
			a = Particle(p);
			pt.push_back(a);
			field->Set_Time(t);
			Move_One_Time_Step(dt, &(pt[j][0]),
				&(pt[j+1][0]), &pt[j].f[0]);
			x = &(pt[j++][0]);
			if (x[0] < 0 || x[0] > 320 || abs(x[2]) > 64) {
				stop = true;
				break;
			}
//			Check_Bounds(&pt[j++].data[0]);
			t += dt;
		}
		if (stop) break;
	}
	std::cout << pt.size() << std::endl;
} 

void ParticleTracer::Write(std::string fname, const Parameter &p) {
	std::fstream ofs(fname.c_str());
	if (ofs) {
		ofs.close();
		std::string ans;
		std::cout << "File " << fname << " exist. Overwrite (y/n)? ";
		std::cin >> ans;
		if (ans != "y" && ans != "Y")
			throw std::invalid_argument("Data not saved!!!");
		else
			ofs.open(fname.c_str(), std::ios::out|std::ios::trunc);

	} else
		ofs.open(fname.c_str(), std::ios::out);

	for (size_t i = 0; i < pt.size(); ++i) {
		for (size_t j = 0; j < p.Np; ++j) {
			for (size_t k = 0; k < N_COORDS; ++k) {
				ofs << pt[i][j*N_DIMS+k]/p.rfac << " ";
			}
			for (size_t k = N_COORDS; k < N_DIMS; ++k)
				ofs << pt[i][j*N_DIMS+k]/p.vfac << " ";
		}
		ofs << "\n";
	}
	ofs.close();
	std::cout << "Data saved to " << fname << ".\n";
}

// Boris Procedure
void ParticleTracer::Move_One_Time_Step(double dt, double *xi,
		double *xo, double *f) {

	size_t i, j;
	double dt2 = dt/2;
//	double f[N_OF_FIELDS];
	double hm, vxm, vym, vzm, ux, uy, uz;

	for (i = 0; i < Np; i++) {
		j = i * N_DIMS;
		field->Get(f, &xi[j]);
		hm = (f[iBX]*f[iBX]+f[iBY]*f[iBY] + f[iBZ]*f[iBZ]) * dt2*dt2;
		vxm = (xi[j+iVx] + f[iEX] * dt2);
		vym = (xi[j+iVy] + f[iEY] * dt2);
		vzm = (xi[j+iVz] + f[iEZ] * dt2);
		ux = vxm + (vym * f[iBZ] - vzm * f[iBY]) * dt2;
		uy = vym + (vzm * f[iBX] - vxm * f[iBZ]) * dt2;
		uz = vzm + (vxm * f[iBY] - vym * f[iBX]) * dt2;
		xo[j+iVx] = vxm + (uy*f[iBZ]-uz*f[iBY])*dt/(1+hm) + f[iEX]*dt2;
		xo[j+iVy] = vym + (uz*f[iBX]-ux*f[iBZ])*dt/(1+hm) + f[iEY]*dt2;
		xo[j+iVz] = vzm + (ux*f[iBY]-uy*f[iBX])*dt/(1+hm) + f[iEZ]*dt2;
		xo[j+iRx] = xi[j+iRx] + xo[j+iVx] * dt;
		xo[j+iRy] = xi[j+iRy] + xo[j+iVy] * dt;
		xo[j+iRz] = xi[j+iRz] + xo[j+iVz] * dt;
	}
}
