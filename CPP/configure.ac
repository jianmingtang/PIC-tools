AC_INIT([picpt], [0.1.0], [jmtang@mailaps.org])
AC_CANONICAL_HOST
AM_INIT_AUTOMAKE([-Wall -Werror foreign])
AM_CONFIG_HEADER(config.h)
AC_SUBST(VERSION)
AM_MAINTAINER_MODE

AC_PROG_CXX
AM_PATH_PYTHON([2.6])

AC_CHECK_LIB(boost_program_options,main,,AC_MSG_ERROR([libboost_program_options is required]))

AC_CHECK_LIB(python$PYTHON_VERSION,Py_Initialize,,AC_MSG_ERROR([libpython is required]))

PyHeader=/usr/include/python$PYTHON_VERSION/Python.h
AC_CHECK_HEADER($PyHeader, CXXFLAGS+=" -I/usr/include/python$PYTHON_VERSION",
	AC_MSG_ERROR([Python.h is required]),)
AC_CHECK_HEADER(numpy/arrayobject.h,,AC_MSG_ERROR([numpy is required]),
	[#include<$PyHeader>])


AC_SUBST(CXXFLAGS)
AC_CONFIG_FILES([Makefile src/Makefile])
AC_OUTPUT


