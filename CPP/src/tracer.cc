#include <iostream>
#include <cmath>
#include "tracer.h"
#include "config.h"
#ifdef HAVE_PYTHON
	#include "pyplot.h"
#endif
#ifdef HAVE_ODEINT_HPP
	#include <boost/numeric/odeint/integrate/integrate.hpp>
#endif


#define iRx 0
#define iRy 1
#define iRz 2
#define iVx 3
#define iVy 4
#define iVz 5


#ifdef HAVE_ODEINT_HPP
	using namespace boost::numeric;
#endif


ParticleTracer::ParticleTracer(EMField &f, const Particle &pi,
		const Parameter &p) {
	this->field = &f;
	this->Np = p.Np;
	pt.push_back(pi);
}

void ParticleTracer::Run(const Parameter &p) {
#ifdef HAVE_PYTHON
	PyPlot bgplot(p);
#endif
	Particle a;
	double t = p.tb, dt = p.ts;
	double *x, *y;
	size_t j = 0;
	bool stop = false;
	int dir;

	int ib, ie, is;

	if (p.ts > 0) {
		dir = 1;
		ib = floor((p.tb - p.ftb) / p.fts) * p.fts + p.ftb;
	} else {
		dir = -1;
		ib = ceil((p.tb - p.ftb) / p.fts) * p.fts + p.ftb;
	}
	is = p.fts * dir;

	for (int i = ib; (p.ftb<=i)&&(i<=p.fte) ; i += is) {
		field->Update(i,i + is);
		std::cout << i << std::endl;
#ifdef HAVE_PYTHON
		bgplot.Update_Data(*field);
		bgplot.Plot();
#endif
		while ((t-i) * (t-i-is) <= 0) {
//			std::cout << t << " ";
			a = Particle(p);
			pt.push_back(a);
			field->Set_Time(t);
			Move_One_Time_Step(dt, &(pt[j][0]),
				&(pt[j+1][0]), &pt[j].f[0]);
/*
			for (size_t k=0; k<p.Np; k++) {
				x = &(pt[j+1][k*6]);
				y = &(pt[j][k*6]);
				if (x[0] < 0 || x[0] > 320 || abs(x[2]) > 63) {
					for (size_t l =0; l <6;l++)
						x[l] = y[l];
				}
			}
*/
			j++;
			t += dt;
			if ((t-p.tb)*(t-p.te)>0) {
				stop = true;
				break;
			}
		}
		if (stop) break;
	}
	std::cout << "\nNumber of time steps: " << pt.size() << std::endl;
} 

void ParticleTracer::Write(const Parameter &p) {
	unsigned int ibuf;
	float fbuf;
	std::fstream ofs(p.outf.c_str());
#ifdef DEBUG
	std::string debugf = p.outf + "_txt";
	std::ofstream ofsd(debugf.c_str());
#endif
	if (ofs) {
		ofs.close();
		std::string ans;
		std::cout << "File " << p.outf << " exist. Overwrite (y/n)? ";
		std::cin >> ans;
		if (ans != "y" && ans != "Y")
			throw std::invalid_argument("Data not saved!!!");
		else {
			ofs.open(p.outf.c_str(), std::ios::out | 
				std::ios::trunc|std::ios::binary);
		}
	} else {
		ofs.open(p.outf.c_str(), std::ios::out|std::ios::binary);
	}

	ofs << p.Np << " " << pt.size() << "\n";
/*
	ibuf = p.Np;
	ofs.write((char*)&ibuf, sizeof(ibuf));
	ibuf = pt.size();
	ofs.write((char*)&ibuf, sizeof(ibuf));
*/
	for (size_t i = 0; i < pt.size(); ++i) {
		for (size_t j = 0; j < p.Np; ++j) {
/*
			for (size_t k = 0; k < N_COORDS; ++k) {
				ofs << pt[i][j*N_DIMS+k]/p.rfac << " ";
			}
			for (size_t k = N_COORDS; k < N_DIMS; ++k) {
				ofs << pt[i][j*N_DIMS+k]/p.vfac << " ";
			}
*/
// switch to de scale
			for (size_t k = 0; k < N_DIMS; ++k) {
				fbuf = pt[i][j * N_DIMS + k];
#ifdef DEBUG
				ofsd << fbuf << " ";
#endif
				ofs.write((char*)&fbuf, sizeof(fbuf));
			}
		}
#ifdef DEBUG
		ofsd << "\n";
#endif
	}
	ofs.close();
	std::cout << "Data saved to " << p.outf << ".\n";
#ifdef DEBUG
	ofsd.close();
	std::cout << "Data saved to " << debugf << ".\n";
#endif
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
		xo[j+iVx] = vxm + (uy*f[iBZ]-uz*f[iBY])*dt/(hm+1) + f[iEX]*dt2;
		xo[j+iVy] = vym + (uz*f[iBX]-ux*f[iBZ])*dt/(hm+1) + f[iEY]*dt2;
		xo[j+iVz] = vzm + (ux*f[iBY]-uy*f[iBX])*dt/(hm+1) + f[iEZ]*dt2;
		xo[j+iRx] = xi[j+iRx] + xo[j+iVx] * dt;
		xo[j+iRy] = xi[j+iRy] + xo[j+iVy] * dt;
		xo[j+iRz] = xi[j+iRz] + xo[j+iVz] * dt;
	}
}
