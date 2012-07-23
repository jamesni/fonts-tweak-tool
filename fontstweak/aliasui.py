# -*- coding: utf-8 -*-
# aliasui.py
# Copyright (C) 2012 Red Hat, Inc.
#
# Authors:
#   Akira TAGOH  <tagoh@redhat.com>
#
# This library is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gi
import re
import sys
from chooserui import ChooserUI
from util import FontsTweakUtil
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Easyfc
from xml.sax.saxutils import quoteattr
from xml.sax.saxutils import escape

def N_(s):
    return s

class FontsTweakAliasUI:

    alias_names = ['sans-serif', 'serif', 'monospace', 'cursive', 'fantasy']
    sample_text = N_('The quick brown fox jumps over the lazy dog. 1234567890')

    def __init__(self, config, builder, parent):
        self.__initialized = False

        self.config = config
        self.parent_window = parent
        self.remove_button = builder.get_object('toolbutton-remove-alias-lang')
        self.pages = builder.get_object('notebook-aliases-pages')
        self.selector = builder.get_object('treeview-selection')
        self.view = builder.get_object('treeview-alias-lang-list')
        self.view.append_column(Gtk.TreeViewColumn(None, Gtk.CellRendererText(), text=0))
        self.view_list = builder.get_object('alias-lang-list')
        self.filter = builder.get_object('checkbutton-filter')
        self.comboboxes = {}
        self.labels = {}
        self.lists = {}
        self.fonts = {}
        for f in self.alias_names:
            self.comboboxes[f] = builder.get_object('combobox-' + f)
            self.lists[f] = builder.get_object(f + '-fonts-list')
            self.labels[f] = builder.get_object('label-sample-' + f)

        self.listobj = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING)

        self.langlist = FontsTweakUtil.get_language_list(True)
        for l in self.langlist.keys():
            iter = self.listobj.append()
            self.listobj.set_value(iter, 0, l)
            self.listobj.set_value(iter, 1, self.langlist[l])

        chooser_builder = FontsTweakUtil.create_builder('chooser.ui')
        chooser_builder.connect_signals(ChooserUI(chooser_builder, self.listobj, self.on_treemodel_filter))
        self.chooser = chooser_builder.get_object('chooser-dialog')
        self.chooser.set_transient_for(self.parent_window)
        self.chooser_view = chooser_builder.get_object('treeview')
        self.chooser_selector = chooser_builder.get_object('treeview-selection')
        self.chooser_view.append_column(Gtk.TreeViewColumn(None, Gtk.CellRendererText(), text=1))

        for l in self.config.get_language_list():
            if not self.langlist.has_key(l):
                print "%s is an unknown language tag. ignoring." % l
                continue
            desc = self.langlist[l]
            self.add_language(desc, l)
            for a in self.config.get_aliases(l):
                an = a.get_name()
                self.__render_combobox(l, an)

        self.on_treeview_selection_changed(self.selector)

        self.__initialized = True

    def __font_changed(self, widget, alias):
        if self.__initialized == False:
            return
        model, iter = self.selector.get_selected()
        if iter != None:
            lang = model.get_value(iter, 1)
            model = widget.get_model()
            iter = widget.get_active_iter()
            if iter != None:
                font = model.get_value(iter, 0)
                self.config.remove_alias(lang, alias)
                a = Easyfc.Alias.new(alias)
                try:
                    a.set_font(font)
                    self.config.add_alias(lang, a)
                except gi._glib.GError:
                    pass
                try:
                    self.config.save()
                except gi._glib.GError, e:
                    if e.domain != 'ezfc-error-quark' and e.code != 6:
                        raise
                    else:
                        print "%s: %s" % (sys.argv[0], e)
                self.__render_label(widget, lang)

    def on_treemodel_filter(self, model, iter, filter):
        patterns = filter.get_text().split(' ')
        if len(patterns) == 1 and patterns[0] == '':
            return True
        t, n = model.get(iter, 0, 1)
        for p in patterns:
            if re.search(p, n, re.I):
                return True
            if re.search(p, t, re.I):
                return True

        return False

    def on_checkbutton_filter_toggled(self, widget):
        self.on_treeview_selection_changed(self.selector)

    def on_combobox_sans_serif_changed(self, widget, *args):
        self.__font_changed(widget, 'sans-serif')

    def on_combobox_serif_changed(self, widget, *args):
        self.__font_changed(widget, 'serif')

    def on_combobox_monospace_changed(self, widget, *args):
        self.__font_changed(widget, 'monospace')
        pass

    def on_combobox_cursive_changed(self, widget, *args):
        self.__font_changed(widget, 'cursive')
        pass

    def on_combobox_fantasy_changed(self, widget, *args):
        self.__font_changed(widget, 'fantasy')

    def on_treeview_selection_changed(self, widget, *args):
        model, iter = widget.get_selected()
        if iter == None:
            self.pages.set_current_page(1)
            self.remove_button.set_sensitive(False)
        else:
            lang = model.get_value(iter, 1)
            for n in self.alias_names:
                self.__render_combobox(lang, n)
            self.pages.set_current_page(0)
            self.remove_button.set_sensitive(True)

    def on_toolbutton_add_alias_lang_clicked(self, widget):
        self.chooser.show_all()
        resid = self.chooser.run()
        self.chooser.hide()
        if resid == Gtk.ResponseType.CANCEL:
            return
        model, iter = self.chooser_selector.get_selected()
        if iter == None:
            return
        tag, name = model.get(iter, 0, 1)
        iter = self.add_language(name, tag)
        if iter == None:
            print "%s has already been added." % tag
        else:
            model = self.view.get_model()
            path = model.get_path(iter)
            self.view.set_cursor(path, None, False)

    def on_toolbutton_remove_alias_lang_clicked(self, widget):
        model, iter = self.selector.get_selected()
        if iter == None:
            return
        lang = model.get_value(iter, 1)
        model.remove(iter)
        self.config.remove_aliases(lang)
        try:
            self.config.save()
        except gi._glib.GError, e:
            if e.domain != 'ezfc-error-quark' and e.code != 6:
                raise
            else:
                print "%s: %s" % (sys.argv[0], e)
        self.on_treeview_selection_changed(self.selector)

    def add_language(self, name, tag):
        retval = True
        model = self.view.get_model()
        iter = model.get_iter_first()
        while iter != None:
            n, t = model.get(iter, 0, 1)
            if t == tag:
                retval = False
                break
            iter = model.iter_next(iter)
        if retval == True:
            iter = model.append()
            model.set_value(iter, 0, name)
            model.set_value(iter, 1, tag)
        else:
            iter = None
        return iter

    def __render_combobox(self, lang, alias):
        if self.fonts.has_key(lang) == False:
            self.fonts[lang] = {}
        if self.filter.get_active():
            kalias = None
        else:
            kalias = alias
        if self.fonts[lang].has_key(kalias) == False:
            self.fonts[lang][kalias] = Easyfc.Font.get_list(lang, kalias, False)
        if len(self.fonts[lang][kalias]) == 0:
            # fontconfig seems not supporting the namelang object
            self.fonts[lang][kalias] = Easyfc.Font.get_list(lang, kalias, True)
        self.lists[alias].clear()
        self.lists[alias].append([alias])
        for f in self.fonts[lang][kalias]:
            self.lists[alias].append([f])
        fn = None
        for a in self.config.get_aliases(lang):
            if a.get_name() == alias:
                fn = a.get_font()
                break
        if fn != None:
            model = self.comboboxes[alias].get_model()
            iter = model.get_iter_first()
            while iter != None:
                f = unicode(model.get_value(iter, 0), "utf8")
                if type(fn) is not unicode:
                    fontname = unicode(fn, "utf8")
                if f == fontname:
                    self.comboboxes[alias].set_active_iter(iter)
                    break
                iter = model.iter_next(iter)
        else:
            self.comboboxes[alias].set_active(0)
        self.__render_label(self.comboboxes[alias], lang)

    def __render_label(self, combobox, lang):
        model = combobox.get_model()
        iter = combobox.get_active_iter()
        if iter != None:
            font = model.get_value(iter, 0)
            # Work around for PyGObject versions 3.0.3 and 3.1.0,
            # which decode strings in Gtk.TreeModel when retrieval.
            # This behavior was reverted in 3.1.1:
            # http://git.gnome.org/browse/pygobject/commit/?id=0285e107
            if type(font) is not unicode:
                font = unicode(font, "utf8")
            iter = model.get_iter_first()
            alias = model.get_value(iter, 0)
            self.labels[alias].set_markup(
                "<span font_family=%s font_size=\"small\">%s</span>" % (
                    quoteattr(font),
                    escape(FontsTweakUtil.translate_text(self.sample_text, lang))))
