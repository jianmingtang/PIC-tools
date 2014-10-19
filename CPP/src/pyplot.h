#include "Python.h"
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include "numpy/arrayobject.h"
#include "para.h"
#include "field.h"


#ifndef PYTHON_PLOT_H
#define PYTHON_PLOT_H


class PyPlot {
private:
	size_t nx, ny;
	std::vector<double> A;
	PyObject *pName, *pModule, *pDict, *pFunc, *pFuncCB, *pArgs, *pGraph;
public:
	PyPlot(const Parameter &);
	~PyPlot();
	void Update_Data(const EMField &);
	void Plot();
};


#endif /* PYTHON_PLOT_H */
