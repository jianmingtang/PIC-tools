#include "Python.h"
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include "numpy/arrayobject.h"
#include "field.h"


void pyplot(const EMField &field, int c, int x, int y)
{
	PyObject *pName, *pModule, *pDict, *pFunc, *pFuncCB, *pArgs, *pGraph;
	PyObject *py_array;
	npy_intp dims[2] = { x, y };

	Py_Initialize();

	PyRun_SimpleString("import pylab");
	pName = PyString_FromString ("pylab");
	pModule = PyImport_Import (pName);
	pDict = PyModule_GetDict(pModule);
//	pFunc1 = PyObject_GetAttrString (pModule, "pcolormesh");
	pFunc = PyDict_GetItemString (pDict, "pcolormesh");
	pFuncCB = PyDict_GetItemString (pDict, "colorbar");
//	pFunc2 = PyObject_GetAttrString (pModule, "colorbar");
//	Py_DECREF(pName);

	_import_array ();
	if (c < N_OF_FIELDS) {
		py_array = PyArray_SimpleNewFromData(2,
			dims, NPY_FLOAT32, field._F[c]);
	} else {
		 double *A = new double [x*y];
		if (c == 10) {
			for (unsigned int i = 0; i < x*y; ++i)
				A[i] = field.get_B(i);
		} else if (c == 11) {
			for (unsigned int i = 0; i < x*y; ++i)
				A[i] = field.get_E(i);
		}
		py_array = PyArray_SimpleNewFromData(2, dims, NPY_DOUBLE, A);
	}
	if (PyCallable_Check (pFunc)) 
	{
		pArgs = PyTuple_New (1);
		PyTuple_SetItem (pArgs, 0, py_array);
		pGraph = PyObject_CallObject (pFunc, pArgs);
		pArgs = PyTuple_New (1);
		PyTuple_SetItem (pArgs, 0, pGraph);
		PyObject_CallObject (pFuncCB, pArgs);
	} else {
		printf ("Function not callable !\n");
	}
	PyRun_SimpleString("pylab.axis('tight')");
	PyRun_SimpleString("pylab.show()");

//	Py_DECREF(py_array);
//	Py_DECREF(pModule);
//	Py_DECREF(pFunc1);
//	Py_DECREF(pFunc2);
//	Py_DECREF(pArgs);
//	Py_Finalize();
	Py_Exit(0);
}

