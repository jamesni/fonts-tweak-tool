dnl Process this file with autoconf to produce a configure script.
AC_PREREQ(2.62)
AC_INIT([fonts-tweak-tool], 0.0.6, [http://github.com/jamesni/fonts-tweak-tool/issues])

AM_INIT_AUTOMAKE
AM_MAINTAINER_MODE

AC_PROG_LIBTOOL
AC_PROG_INTLTOOL

AM_PATH_PYTHON

dnl ======================================================================
dnl gettext stuff
dnl ======================================================================
GETTEXT_PACKAGE=$PACKAGE
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE, "$GETTEXT_PACKAGE", [Gettext package])

AM_GLIB_GNU_GETTEXT

dnl ======================================================================
dnl output
dnl ======================================================================
AC_CONFIG_COMMANDS([chmod-scripts],
	[chmod 0755 fonts-tweak-tool])
AC_CONFIG_FILES([
	Makefile
	data/Makefile
	fontstweak/Makefile
	po/Makefile.in
	setup.py
])
AC_OUTPUT
