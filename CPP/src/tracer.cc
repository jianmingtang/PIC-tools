#include<iostream>
#include "tracer.h"

#define iRx 0
#define iRy 1
#define iRz 2
#define iVx 3
#define iVy 4
#define iVz 5


ParticleTracer::ParticleTracer(EMField &f, const Particle &pi,
		const Parameter &p) {
	this->field = &f;
	this->Np = pi.Np;
	pt.push_back(pi);
}

void Check_Bounds(double *x) {
}

void ParticleTracer::Run(double ti, double tf, double dt) {
	Particle a(Np);
	double t = ti;
	double *x;
	int j = 0;
	bool stop = false;
	for (int i = 1750; i > 1000; i-=25) {
		field->Update(i,i-25);
		while (t >= i-25) {
			std::cout << t << " \n";
			a = Particle(Np);
			pt.push_back(a);
			field->Set_Time(t);
			Move_One_Time_Step(dt, &pt[j].data[0], &pt[j+1].data[0]);
			x = &pt[j++].data[0];
			if ((abs(x[0]) > 160) || (abs(x[2]) > 64)) {
				stop = true;
				break;
			}
//			Check_Bounds(&pt[j++].data[0]);
			t += dt;
		}
		if (stop) break;
	}
} 

void ParticleTracer::Write(std::string fname, const Parameter &p) {
	std::ofstream ofs(fname.c_str());
	for (unsigned int i = 0; i < pt.size(); ++i) {
		for (unsigned int j = 0; j < Np; ++j) {
			for (unsigned int k = 0; k < 3; ++k)
				ofs << pt[i].data[j*6+k]/p.rfac << " ";
			for (unsigned int k = 3; k < 6; ++k)
				ofs << pt[i].data[j*6+k]/p.vfac << " ";
		}
		ofs << "\n";
	}
	ofs.close();
}

// Boris Procedure
void ParticleTracer::Move_One_Time_Step(double dt, double *xi, double *xo) {

	unsigned int i, j;
	double dt2 = dt/2;
	double f[N_OF_FIELDS];
	double hm, vxm, vym, vzm, ux, uy, uz;

	for (i = 0; i < Np; i++) {
		j = i * 6;
		field->Get(f, &xi[j]);
		hm = (f[iBX]*f[iBX]+f[iBY]*f[iBY] + f[iBZ]*f[iBZ]) * dt2*dt2;
		vxm = (xi[j+iRx] + f[iEX] * dt2);
		vym = (xi[j+iRy] + f[iEY] * dt2);
		vzm = (xi[j+iRz] + f[iEZ] * dt2);
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
