NULL =
AUTOMAKE_OPTIONS =	\
	dist-bzip2	\
	$(NULL)
SUBDIRS =		\
	data		\
	fontstweak	\
	po		\
	$(NULL)
EXTRA_DIST =			\
	$(desktop_in_files)	\
	$(bin_SCRIPTS)		\
	setup.py		\
	$(NULL)
MAINTAINERCLEANFILES =		\
	$(srcdir)/INSTALL	\
	$(srcdir)/aclocal.m4	\
	$(srcdir)/autoscan.log	\
	$(srcdir)/compile	\
	$(srcdir)/config.guess	\
	$(srcdir)/config.sub	\
	$(srcdir)/install-sh	\
	$(srcdir)/ltmain.sh	\
	$(srcdir)/missing	\
	$(srcdir)/mkinstalldirs	\
	$(srcdir)/ChangeLog	\
	`find "$(srcdir)" -type f -name Makefile.in -print`	\
	$(NULL)
DISTCLEANFILES =		\
	$(desktop_DATA)		\
	$(NULL)
CLEANFILES =			\
	$(desktop_DATA)		\
	$(NULL)

##
desktopdir = $(datadir)/applications
desktop_in_files =			\
	fonts-tweak-tool.desktop.in	\
	$(NULL)
desktop_DATA = $(desktop_in_files:.desktop.in=.desktop)
@INTLTOOL_DESKTOP_RULE@

##
bin_SCRIPTS =			\
	fonts-tweak-tool	\
	$(NULL)

##
all-local:
	$(PYTHON) $(top_srcdir)/setup.py build

##
install-exec-local:
	$(PYTHON) $(top_srcdir)/setup.py install --root=$(DESTDIR) --prefix=$(prefix)

##
uninstall-local:
	rm -f $(DESTDIR)/$(pythondir)/fonts_tweak_tool*.egg-info

##
clean-local:
	-$(PYTHON) setup.py clean --all

##
ChangeLog: $(srcdir)/ChangeLog
$(srcdir)/ChangeLog:
	$(AM_VN_GEN) if test -d "$(srcdir)/.git"; then	\
	 (GIT_DIR=$(top_srcdir)/.git ./missing --run	\
	  git log --stat) | fmt --split-only > $@.tmp	\
	 && mv -f $@.tmp $@				\
	 || ($(RM) $@.tmp;				\
	     echo Failed to generate ChangeLog.  your ChangeLog may be outdatged >&2;	\
	     (test -f $@ || echo git-log is required to genereate this file >> $@));	\
	 else						\
	   test -f $@ || 				\
	   (echo A git checkout and git-log is required to genereate ChangeLog >&2 &&	\
	    echo A git checkout and git-log is required to genereate this file >> $@);	\
	fi

.PHONY: $(srcdir)/ChangeLog

-include $(top_srcdir)/git.mk
