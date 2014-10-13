#include "Python.h"
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include "numpy/arrayobject.h"

#ifndef PYTHON_PLOT_H
#define PYTHON_PLOT_H


class PyPlot {
private:
	PyObject *pName, *pModule, *pDict, *pFunc, *pFuncCB, *pArgs, *pGraph;

public:
	PyPlot();
	~PyPlot();
	void Plot(double*, int, int);
};


#endif /* PYTHON_PLOT_H */
