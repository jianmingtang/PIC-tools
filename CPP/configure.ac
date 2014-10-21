AC_INIT([picpt], [0.1.0], [jmtang@mailaps.org])
AC_CANONICAL_HOST
AM_INIT_AUTOMAKE([-Wall -Werror foreign])
AM_CONFIG_HEADER(config.h)
AC_SUBST(VERSION)
AC_CONFIG_MACRO_DIR(m4)
AM_MAINTAINER_MODE

AC_PROG_CXX
AC_PROG_CPP
AC_LANG(C++)

AC_CHECK_LIB(boost_program_options,main,,
	AC_MSG_ERROR([libboost_program_options is required]))
boost=/usr/include/boost/numeric
#AC_CHECK_HEADER($boost/odeint/integrate/integrate.hpp,,,)
AC_CHECK_HEADER($boost/odeint.hpp,
	AC_DEFINE(HAVE_ODEINT_HPP,1,"Define to 1 if exists"),,)

AC_MSG_CHECKING([for Python Matplotlib support])
AC_ARG_ENABLE(python, AC_HELP_STRING([--disable-python],
        [disable python (default is enable)]), python=disabled, python=enabled)
AC_MSG_RESULT($python)
if test "$python" = "enabled"; then
        ACX_PYTHON
fi

AC_SUBST(CXXFLAGS)
AC_CONFIG_FILES([Makefile src/Makefile])
AC_OUTPUT


