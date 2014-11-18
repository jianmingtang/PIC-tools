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

AC_ARG_ENABLE(debug, AC_HELP_STRING([--enable-debug],
        [enable debug (default is disable)]),
	AC_DEFINE(DEBUG,1,"Define to 1 if debug mode"),)

AC_MSG_CHECKING([for boost odeint support])
AC_ARG_ENABLE(odeint, AC_HELP_STRING([--enable-odeint],
        [enable odeint (default is disable)]), odeint=enabled, odeint=disabled)
AC_MSG_RESULT($odeint)
if test "$odeint" = "enabled"; then
	boost=/usr/include/boost/numeric
	#AC_CHECK_HEADER($boost/odeint/integrate/integrate.hpp,,,)
	AC_CHECK_HEADER($boost/odeint.hpp,
		AC_DEFINE(HAVE_ODEINT_HPP,1,"Define to 1 if exists"),,)
fi

AC_MSG_CHECKING([for Python numpy and matplotlib support])
AC_ARG_ENABLE(python, AC_HELP_STRING([--enable-python],
        [enable python (default is disable)]), python=enabled, python=disabled)
AC_MSG_RESULT($python)
if test "$python" = "enabled"; then
        ACX_PYTHON
fi

AM_OPTIONS_WXCONFIG
reqwx=3.0.0
AM_PATH_WXCONFIG($reqwx, wxWin=1)
if test "$wxWin" != 1; then
	AC_MSG_ERROR([
		wxWidgets must be installed on your system.
 
		Please check that wx-config is in path, the directory
		where wxWidgets libraries are installed (returned by
		'wx-config --libs' or 'wx-config --static --libs' command)
		is in LD_LIBRARY_PATH or equivalent variable and
		wxWidgets version is $reqwx or above.
		])
fi
 
CPPFLAGS="$CPPFLAGS $WX_CPPFLAGS"
LIBS="$LIBS $WX_LIBS"


AC_SUBST(CPPFLAGS)
AC_CONFIG_FILES([Makefile src/Makefile])
AC_OUTPUT


