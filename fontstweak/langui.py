# -*- coding: utf-8 -*-
# langui.py
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
import os.path
import re
from chooserui import ChooserUI
from util import FontsTweakUtil
from gi.repository import GObject
from gi.repository import Gtk

class FontsTweakLangUI:

    def __init__(self, builder, parent):
        self.__changed = False
        self.parent_window = parent
        self.remove_button = builder.get_object('remove-lang-order')
        self.up_button = builder.get_object('move-up-order')
        self.down_button = builder.get_object('move-down-order')
        self.selector = builder.get_object('treeview-selection')
        self.view = builder.get_object('treeview-lang-order-list')
        self.view.append_column(Gtk.TreeViewColumn(None, Gtk.CellRendererText(), text=0))
        self.view_list = builder.get_object('order-lang-list')

        self.listobj = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING)

        self.langlist = FontsTweakUtil.get_language_list(False)
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

        self.load()

        self.on_treeview_selection_changed(self.selector)

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

    def on_treeview_selection_changed(self, widget):
        model, iter = widget.get_selected()
        if iter == None:
            self.remove_button.set_sensitive(False)
            self.up_button.set_sensitive(False)
            self.down_button.set_sensitive(False)
        else:
            self.remove_button.set_sensitive(True)
            if model.iter_previous(iter) == None:
                self.up_button.set_sensitive(False)
            else:
                self.up_button.set_sensitive(True)
            if model.iter_next(iter) == None:
                self.down_button.set_sensitive(False)
            else:
                self.down_button.set_sensitive(True)
        if self.__changed == True:
            self.save()

    def on_add_lang_order_clicked(self, widget):
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
            self.__changed = True
            self.view.set_cursor(path, None, False)

    def on_remove_lang_order_clicked(self, widget):
        model, iter = self.selector.get_selected()
        if iter == None:
            return
        model.remove(iter)
        self.__changed = True
        self.on_treeview_selection_changed(self.selector)

    def on_move_up_order_clicked(self, widget):
        model, iter = self.selector.get_selected()
        piter = model.iter_previous(iter)
        if piter == None:
            return
        n, t = model.get(iter, 0, 1)
        niter = model.insert_before(piter)
        model.set_value(niter, 0, n)
        model.set_value(niter, 1, t)
        model.remove(iter)
        self.__changed = True
        path = model.get_path(niter)
        self.view.set_cursor(path, None, False)

    def on_move_down_order_clicked(self, widget):
        model, iter = self.selector.get_selected()
        niter = model.iter_next(iter)
        if niter == None:
            return
        n, t = model.get(iter, 0, 1)
        newiter = model.insert_after(niter)
        model.set_value(newiter, 0, n)
        model.set_value(newiter, 1, t)
        model.remove(iter)
        self.__changed = True
        path = model.get_path(newiter)
        self.view.set_cursor(path, None, False)

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

    def __get_i18nfilename(self):
        homedir = os.path.expanduser('~')
        i18nfile = os.path.join(homedir, '.i18n')

        return i18nfile

    def __get_i18nfile(self):
        i18nfile = self.__get_i18nfilename()
        content = []
        found = False
        if os.path.isfile(i18nfile):
            f = open(i18nfile, 'r')
            content = f.readlines()
            f.close

        return content

    def load(self):
        content = self.__get_i18nfile()
        l = None
        for line in content:
            if re.search(r'^FC_LANG=', line):
                l = re.sub(r'^FC_LANG=(.*)$', r'\1', line).rstrip('\n')
        model = self.view.get_model()
        model.clear()
        if l != None:
            for tag in l.split(':'):
                for lang in self.langlist.keys():
                    if re.search(r'^%s' % tag, lang):
                        iter = model.append()
                        model.set_value(iter, 0, self.langlist[lang])
                        model.set_value(iter, 1, lang)

    def save(self):
        l = []
        model = self.view.get_model()
        iter = model.get_iter_first()
        while iter != None:
            t = model.get_value(iter, 1)
            l.append(re.sub(r'([^\.].*)\..*$', r'\1', t))
            iter = model.iter_next(iter)
        line = ':'.join(l)

        content = self.__get_i18nfile()
        found = False
        i = 0
        while i < len(content):
            if re.search(r'^FC_LANG=', content[i]):
                if len(line) > 0:
                    content[i] = re.sub(r'^(FC_LANG=).*$', r'\1%s' % line, content[i])
                else:
                    del(content[i])
                    i -= 1
                found = True
            i += 1

        if not found:
            if len(line) == 0:
                return
            content.append('FC_LANG=%s' % line)

        f = open(self.__get_i18nfilename(), 'w')
        f.writelines(content)
        f.close()

        self.__changed = False
