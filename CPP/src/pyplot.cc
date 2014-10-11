#include "Python.h"
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include "numpy/arrayobject.h"
#include "field.h"


void pyplot(double* A, int x, int y)
{
	PyObject *pName, *pModule, *pDict, *pFunc, *pFuncCB, *pArgs, *pGraph;
	PyObject *py_array;
	npy_intp dims[2] = { x, y };

	Py_Initialize();

	PyRun_SimpleString("import pylab");
	pName = PyString_FromString ("pylab");
	pModule = PyImport_Import (pName);
/*
	pDict = PyModule_GetDict(pModule);
	pFunc = PyDict_GetItemString (pDict, "pcolormesh");
	pFuncCB = PyDict_GetItemString (pDict, "colorbar");
*/
	pFunc = PyObject_GetAttrString (pModule, "pcolormesh");
	pFuncCB = PyObject_GetAttrString (pModule, "colorbar");

	_import_array ();
	py_array = PyArray_SimpleNewFromData(2, dims, NPY_DOUBLE, A);

	pArgs = PyTuple_New (1);
	PyTuple_SetItem (pArgs, 0, py_array);
	pGraph = PyObject_CallObject (pFunc, pArgs);

	pArgs = PyTuple_New (1);
	PyTuple_SetItem (pArgs, 0, pGraph);
	PyObject_CallObject (pFuncCB, pArgs);

	PyRun_SimpleString("pylab.axis('tight')");
	PyRun_SimpleString("pylab.show()");

	Py_Exit(0);
}

