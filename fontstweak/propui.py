# -*- coding: utf-8 -*-
# propui.py
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
from gi.repository import Easyfc
from gi.repository import GObject
from gi.repository import Gtk

class FontsTweakPropUI:

    def __init__(self, config, builder, parent):
        self.__initialized = False

        self.config = config
        self.parent_window = parent
        self.remove_button = builder.get_object('remove-font')
        self.pages = builder.get_object('notebook-properties-pages')
        self.selector = builder.get_object('treeview-selection')
        self.view = builder.get_object('treeview-prop-fonts-list')
        self.view.append_column(Gtk.TreeViewColumn(None, Gtk.CellRendererText(), text=0))
        self.view_list = builder.get_object('fonts-list')
        self.check_subpixel_rendering = builder.get_object('checkbutton-subpixel-rendering')
        self.check_embedded_bitmap = builder.get_object('checkbutton-embedded-bitmap')
        self.combobox_subpixel_rendering = builder.get_object('combobox-subpixel-rendering')
        self.combobox_hintstyle = builder.get_object('combobox-hintstyle')
        self.radio_no_hinting = builder.get_object('radiobutton-no-hinting')
        self.radio_hinting = builder.get_object('radiobutton-hinting')
        self.radio_autohinting = builder.get_object('radiobutton-autohinting')

        self.listobj = Gtk.ListStore(GObject.TYPE_STRING)
        for f in Easyfc.Font.get_list(None, None, False):
            iter = self.listobj.append()
            self.listobj.set_value(iter, 0, f)

        chooser_builder = FontsTweakUtil.create_builder('chooser.ui')
        chooser_builder.connect_signals(ChooserUI(chooser_builder, self.listobj, self.on_treemodel_filter))
        self.chooser = chooser_builder.get_object('chooser-dialog')
        self.chooser.set_transient_for(self.parent_window)
        self.chooser_view = chooser_builder.get_object('treeview')
        self.chooser_selector = chooser_builder.get_object('treeview-selection')
        self.chooser_view.append_column(Gtk.TreeViewColumn(None, Gtk.CellRendererText(), text=0))

        self.on_treeview_selection_changed(self.selector)

        self.__initialized = True

    def on_treemodel_filter(self, model, iter, filter):
        patterns = filter.get_text().split(' ')
        if len(patterns) == 1 and patterns[0] == '':
            return True
        n = model.get_value(iter, 0)
        for p in patterns:
            if re.search(p, n, re.I):
                return True

        return False

    def on_treeview_selection_changed(self, widget):
        model, iter = widget.get_selected()
        if iter == None:
            self.pages.set_current_page(1)
            self.remove_button.set_sensitive(False)
        else:
            font = model.get_value(iter, 0)
            for f in self.config.get_fonts():
                if f.get_family() == font:
                    x = f.get_subpixel_rendering()
                    if x != Easyfc.FontSubpixelRender.NONE:
                        self.check_subpixel_rendering.set_active(True)
                        self.combobox_subpixel_rendering.set_active(x - 1)
                    else:
                        self.check_subpixel_rendering.set_active(False)
                        self.combobox_subpixel_rendering.set_active(0)
                    self.check_embedded_bitmap.set_active(f.get_embedded_bitmap())
                    h = f.get_hinting()
                    ah = f.get_autohinting()
                    style = f.get_hintstyle()
                    if style == Easyfc.FontHintstyle.UNKNOWN:
                        style = Easyfc.FontHintstyle.NONE
                    if not h and not ah:
                        self.radio_no_hinting.set_active(True)
                    elif h and not ah:
                        self.radio_hinting.set_active(True)
                    elif not h and ah:
                        self.radio_autohinting.set_active(True)
                    self.combobox_hintstyle.set_active(style - 1)
            self.pages.set_current_page(0)
            self.remove_button.set_sensitive(True)

    def on_add_font_clicked(self, widget):
        self.chooser.show_all()
        resid = self.chooser.run()
        self.chooser.hide()
        if resid == Gtk.ResponseType.CANCEL:
            return
        model, iter = self.chooser_selector.get_selected()
        if iter == None:
            return
        font = model.get_value(iter, 0)
        iter = self.add_font(font)
        if iter == None:
            print "%s has already been added." % font
        else:
            model = self.view.get_model()
            path = model.get_path(iter)
            self.view.set_cursor(path, None, False)

    def on_remove_font_clicked(self, widget):
        model, iter = self.selector.get_selected()
        if iter == None:
            return
        font = model.get_value(iter, 0)
        self.config.remove_font(font)
        try:
            self.config.save()
        except gi._glib.GError, e:
            if e.domain != 'ezfc-error-quark' and e.code != 6:
                raise
            else:
                print "%s: %s" % (sys.argv[0], e)
        model.remove(iter)
        self.on_treeview_selection_changed(self.selector)

    def on_checkbutton_subpixel_rendering_toggled(self, widget):
        mode = Easyfc.FontSubpixelRender.UNKNOWN
        if widget.get_active():
            self.combobox_subpixel_rendering.set_sensitive(True)
            model = self.combobox_subpixel_rendering.get_model()
            iter = self.combobox_subpixel_rendering.get_active_iter()
            mode = model.get_value(iter, 1)
        else:
            self.combobox_subpixel_rendering.set_sensitive(False)
            mode = Easyfc.FontSubpixelRender.NONE
        self.__apply_changes(lambda o: o.set_subpixel_rendering(mode))

    def on_checkbutton_embedded_bitmap_toggled(self, widget):
        self.__apply_changes(lambda o: o.set_embedded_bitmap(widget.get_active()))

    def on_radiobutton_no_hinting_toggled(self, widget):
        if not widget.get_active():
            return
        self.__apply_changes(lambda o: o.set_hinting(False) == o.set_autohinting(False))

    def on_radiobutton_hinting_toggled(self, widget):
        if not widget.get_active():
            return
        self.__apply_changes(lambda o: o.set_hinting(True) == o.set_autohinting(False))

    def on_radiobutton_autohinting_toggled(self, widget):
        self.combobox_hintstyle.set_sensitive(widget.get_active())
        if not widget.get_active():
            return
        cb = (lambda o: o.set_hinting(False) == o.set_autohinting(True))
        self.__apply_changes(cb)
        self.on_combobox_hintstyle_changed(self.combobox_hintstyle)

    def on_combobox_subpixel_rendering_changed(self, widget):
        model = widget.get_model()
        iter = widget.get_active_iter()
        if iter == None:
            return
        rgba = model.get_value(iter, 1)
        self.__apply_changes(lambda o: o.set_subpixel_rendering(rgba))

    def on_combobox_hintstyle_changed(self, widget):
        model = widget.get_model()
        iter = widget.get_active_iter()
        if iter == None:
            return
        hintstyle = model.get_value(iter, 1)
        self.__apply_changes(lambda o: o.set_hintstyle(hintstyle))

    def __apply_changes(self, cb, *args):
        model, iter = self.selector.get_selected()
        if iter == None:
            return
        font = model.get_value(iter, 0)
        for f in self.config.get_fonts():
            if f.get_family() == font:
                cb(f, *args)
                break
        try:
            self.config.save()
        except gi._glib.GError, e:
            if e.domain != 'ezfc-error-quark' and e.code != 6:
                raise
            else:
                print "%s: %s" % (sys.argv[0], e)

    def add_font(self, font):
        retval = True
        model = self.view.get_model()
        iter = model.get_iter_first()
        while iter != None:
            f = model.get_value(iter, 0)
            if f == font:
                retval = False
                break
            iter = model.iter_next(iter)
        if retval == True:
            iter = model.append()
            model.set_value(iter, 0, font)
            o = Easyfc.Font()
            o.set_family(font)
            self.config.add_font(o)
        else:
            iter = None
        return iter
