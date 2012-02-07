#vim:set et sts=4 sw=4:
# -*- encoding: utf-8 -*-
#
# Fonts Tweak Tool
#
# Copyright (c) 2011-2012 Jian Ni <jni@redhat.com>
# Copyright (c) 2012 Red Hat, Inc.
#
#This program is free software: you can redistribute it and/or 
#modify it under the terms of the GNU Lesser General Public 
#License as published by the Free Software Foundation, either
#version 3 of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import string
import gi
from collections import OrderedDict
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import Easyfc

__all__ = (
	    "FontsTweakTool",
          )

alias_names = ['sans-serif', 'serif', 'monospace', 'cursive', 'fantasy']

class LangList:

    def __init__(self, parent):
        self.langlist = OrderedDict()
        self.parent_window = parent
        path = os.path.dirname(os.path.realpath(__file__))
        localefile = os.path.join(path, 'locale-list')
        
        try:
            fd = open(localefile, "r")
        except:
            try:
		fd = open("/usr/share/system-config-language/locale-list", "r")
            except:
                raise RuntimeError, ("Cannot find locale-list")

        while True:
            line = fd.readline()
            if not line:
                break
	    tokens = string.split(line)
            lang = str(tokens[0]).split('.')[0].replace('_', '-')
            self.langlist[lang] = string.join(tokens[3:], ' ')

    def show_dialog(self):
        builder = Gtk.Builder()
        path = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(path, 'fontstools.ui')
        builder.add_from_file(uifile)
        self.dialog = builder.get_object("dialog2")
        self.dialog.set_transient_for(self.parent_window)
        self.langStore = builder.get_object("lang_and_locale_list")

        for l in self.langlist.keys():
            iter = self.langStore.append()
            self.langStore.set_value(iter, 0, l)
            self.langStore.set_value(iter, 1, self.langlist[l])

        self.langView = builder.get_object("lang_view")
        col = Gtk.TreeViewColumn(None, Gtk.CellRendererText(), text=1)
        self.langView.append_column(col)
        self.dialog.show_all()
        self.dialog.run()

    def close_dialog(self):
        self.dialog.destroy()
        self.dialog = None

    def get_selection(self):
        lang = None
        fullName = None
        if self.dialog != None:
            selection = self.langView.get_selection().get_selected()
            if selection:
                model, iter = selection
                lang = self.langStore.get_value(iter, 0)
                fullName = self.langStore.get_value(iter, 1)

        return [lang, fullName]

class FontsTweakTool:

    def selectionChanged(self, *args):
        selection = self.lang_view.get_selection()
        model, iter = selection.get_selected()
        if iter == None:
            self.note_book.set_current_page(1)
            self.removelang_button.set_sensitive(False)
        else:
            lang = model.get_value(iter, 1)
            for n in alias_names:
                self.render_combobox(lang, n)
            self.note_book.set_current_page(0)
            self.removelang_button.set_sensitive(True)

    def add_language(self, desc, lang):
        retval = True
        model = self.lang_view.get_model()
        iter = model.get_iter_first()
        while iter != None:
            n, l = model.get(iter, 0, 1)
            if l == lang:
                retval = False
                break
            iter = model.iter_next(iter)
        if retval == True:
            iter = self.lang_list.append()
            self.lang_list.set_value(iter, 0, desc)
            self.lang_list.set_value(iter, 1, lang)
        else:
            iter = None

        return iter

    def addlangClicked(self, *args):
        response = self.languages.show_dialog()

        if response != Gtk.ResponseType.CANCEL:
            lang, desc = self.languages.get_selection()
            iter = self.add_language(desc, lang)
            if iter == None:
                print "%s has already been added.\n" % lang
            else:
                model = self.lang_view.get_model()
                path = model.get_path(iter)
                self.lang_view.set_cursor(path, None, False)

        self.languages.close_dialog()

    def removelangClicked(self, *args):
        selection = self.lang_view.get_selection()
        model, iter = selection.get_selected()
        if iter != None:
            lang = model.get(iter, 1)[0]
            self.lang_list.remove(iter)
            self.note_book.set_current_page(1)
            self.removelang_button.set_sensitive(False)
            self.config.remove_aliases(lang)

    def fontChanged(self, combobox, *args):
        if self.__initialized == False:
            return
        selection = self.lang_view.get_selection()
        model, iter = selection.get_selected()
        if iter != None:
            lang = model.get(iter, 1)[0]
            model = combobox.get_model()
            iter = combobox.get_active_iter()
            if iter != None:
                font = model.get(iter, 0)[0]
                iter = model.get_iter_first()
                alias = model.get(iter, 0)[0]
                self.config.remove_alias(lang, alias)
                a = Easyfc.Alias.new(alias)
                try:
                    a.set_font(font)
                    self.config.add_alias(lang, a)
                except gi._glib.GError:
                    pass

    def closeClicked(self, *args):
	Gtk.main_quit()

    def applyClicked(self, *args):
        self.config.save()
        Gtk.main_quit()

    def render_combobox(self, lang, alias):
        if self.fontslist.has_key(lang) == False:
            self.fontslist[lang] = {}
        if self.fontslist[lang].has_key(alias) == False:
            self.fontslist[lang][alias] = Easyfc.get_fonts_list(lang, alias)
        self.lists[alias].clear()
        self.lists[alias].append([alias])
        for f in self.fontslist[lang][alias]:
	    self.lists[alias].append([unicode(f, "utf8")])
        fn = None
        for a in self.config.get_aliases(lang):
            if a.get_name() == alias:
                fn = a.get_font()
                break
        if fn != None:
            model = self.combobox[alias].get_model()
            iter = model.get_iter_first()
            while iter != None:
                f = model.get(iter, 0)[0]
                if f == unicode(fn, "utf8"):
                    self.combobox[alias].set_active_iter(iter)
                    break
                iter = model.iter_next(iter)
        else:
            self.combobox[alias].set_active(0)

    def __init__(self):
        self.__initialized = False
        builder = Gtk.Builder()
        path = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(path, 'fontstools.ui')
	builder.add_from_file(uifile) 
        self.window = builder.get_object("dialog1")
        self.window.connect("destroy", Gtk.main_quit)
	self.window.set_title("fonts-tweak-tool")
        self.window.set_size_request(640, 480)        
	
	self.scrollwindow = builder.get_object("scrolledwindow1")
	self.scrollwindow.set_min_content_width(200)
	self.lang_view = builder.get_object("treeview1")
        self.lang_list = builder.get_object("lang_list")
        column = Gtk.TreeViewColumn(None, Gtk.CellRendererText(), text=0)
	self.lang_view.append_column(column)

	self.note_book = builder.get_object("notebook1")
	self.note_book.set_current_page(1)

        self.fontslist = {}

        self.combobox = {}
	self.combobox['sans-serif'] = builder.get_object("sans_combobox")
	self.combobox['serif'] = builder.get_object("serif_combobox")
	self.combobox['monospace'] = builder.get_object("monospace_combobox")
	self.combobox['cursive'] = builder.get_object("cursive_combobox")
	self.combobox['fantasy'] = builder.get_object("fantasy_combobox")

        for f in alias_names:
            renderer_text = Gtk.CellRendererText()
            self.combobox[f].pack_start(renderer_text, True)
            self.combobox[f].add_attribute(renderer_text, "text", 0)
            self.combobox[f].connect('changed', self.fontChanged)

        self.lists = {}
        self.lists['sans-serif'] = builder.get_object("sans_fonts_list")
	self.lists['serif'] = builder.get_object("serif_fonts_list")
	self.lists['monospace'] = builder.get_object("monospace_fonts_list")
	self.lists['cursive'] = builder.get_object("cursive_fonts_list")
	self.lists['fantasy'] = builder.get_object("fantasy_fonts_list")

	self.close_button = builder.get_object("button2")
	self.close_button.connect("clicked", self.closeClicked)
  
	self.addlang_button = builder.get_object("add-lang")
        self.addlang_button.connect("clicked", self.addlangClicked)

        self.removelang_button = builder.get_object("remove-lang")
        self.removelang_button.connect("clicked", self.removelangClicked)
        self.removelang_button.set_sensitive(False)
	
	self.apply_button = builder.get_object("button1")
	self.apply_button.connect("clicked", self.applyClicked)

        selection = self.lang_view.get_selection()
        selection.connect("changed", self.selectionChanged)

        self.languages = LangList(self.window)
        self.data = {}

	Easyfc.init()

        self.config = Easyfc.Config()
        self.config.set_name("fontstweak")
        try:
            self.config.load()
        except gi._glib.GError, e:
            if e.domain != 'ezfc-error-quark' or e.code != 7:
                raise

        for l in self.config.get_language_list():
            # XXX: need to take care of the KeyError exception?
            desc = self.languages.langlist[l]
            self.add_language(desc, l)
            for a in self.config.get_aliases(l):
                an = a.get_name()
                self.render_combobox(l, an)

        self.__initialized = True

def main(argv):
    tool = FontsTweakTool()
    tool.window.show_all()
    Gtk.main()
