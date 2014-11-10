#include "config.h"
#ifdef HAVE_PYTHON

#include "pyplot.h"


PyPlot::PyPlot(const Parameter &p) : nx(p.nz), ny(p.nx) {
	A = std::vector<double> (p.rsize);

	Py_Initialize();
	PyRun_SimpleString("import pylab");
	pName = PyString_FromString ("pylab");
	pModule = PyImport_Import (pName);
}

PyPlot::~PyPlot() {
	Py_Finalize();
}

void PyPlot::Update_Data(const EMField &f) {
	 for (size_t i = 0; i < nx * ny; ++i)
		A[i] = f.Get_F(i);
}

void PyPlot::Plot()
{
	PyObject *py_array;
	npy_intp dims[2] = { nx, ny };

/*
	pDict = PyModule_GetDict(pModule);
	pFunc = PyDict_GetItemString (pDict, "pcolormesh");
	pFuncCB = PyDict_GetItemString (pDict, "colorbar");
*/
	pFunc = PyObject_GetAttrString (pModule, "pcolormesh");
	pFuncCB = PyObject_GetAttrString (pModule, "colorbar");

	_import_array ();
	py_array = PyArray_SimpleNewFromData(2, dims, NPY_DOUBLE, &A[0]);

	pArgs = PyTuple_New (1);
	PyTuple_SetItem (pArgs, 0, py_array);
	pGraph = PyObject_CallObject (pFunc, pArgs);

	pArgs = PyTuple_New (1);
	PyTuple_SetItem (pArgs, 0, pGraph);
	PyObject_CallObject (pFuncCB, pArgs);

	PyRun_SimpleString("pylab.axis('tight')");
	PyRun_SimpleString("pylab.ion()");
//	PyRun_SimpleString("pylab.show()");
}

#endif
