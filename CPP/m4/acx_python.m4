AC_DEFUN([ACX_PYTHON], [
AC_PREREQ(2.60)

dnl Check Python Path and Version
AM_PATH_PYTHON([2.7])

dnl Check Python library
AC_CHECK_LIB(python$PYTHON_VERSION, Py_Initialize, pylib=yes, pylib=no)

dnl Check Python header
PyHeader=/usr/include/python$PYTHON_VERSION/Python.h
AC_CHECK_HEADER($PyHeader, pyinc=yes, pyinc=no,)

dnl Check NumPy header
AC_CHECK_HEADER(numpy/arrayobject.h, numpy=yes, numpy=no,
	[#include<$PyHeader>])

if test $pylib = yes && test $pyinc = yes && test $numpy = yes; then
	AC_DEFINE(HAVE_PYTHON, 1,
		"Define to 1 if you have required Python files")
	CPPFLAGS+=" -I/usr/include/python$PYTHON_VERSION"
	LIBS+=" -lpython$PYTHON_VERSION"
fi
]) dnl ACX_PYTHON
