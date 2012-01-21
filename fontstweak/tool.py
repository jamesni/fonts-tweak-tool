#vim:set et sts=4 sw=4:
#
# Font Tweak Tool
#
# Copyright (c) 2011 Jian Ni <jni@redhat.com>
# Copyright (c) 2011 Red Hat, Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330,
# Boston, MA  02111-1307  USA

import sys
import string
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import Easyfc
	
__all__ = (
	    "FontsTweakTool",
          )

class LangDialog(Gtk.Dialog):
    
    def __init__(self, parent, main_ui):
	dialog = Gtk.Dialog.__init__(self, "Select Language", parent, 0)
        self.main_ui = main_ui
        self.lang_list = self.main_ui.lang_list
	self.toplevel = Gtk.VBox()
        self.langStore = Gtk.ListStore(str, str)
        self.title = Gtk.Label("Language Selection")
            
        lines = self.readTable()
        
	for line in lines:
	    tokens = string.split(line)
            iter = self.langStore.append()
            self.langStore.set_value(iter, 0, tokens[0])
            name = ""
            for token in tokens[3:]:
            	name = name + " " + token
            self.langStore.set_value(iter, 1, name)

        self.langView = Gtk.TreeView(self.langStore)
        self.col = Gtk.TreeViewColumn(None, Gtk.CellRendererText(), text=1)
        self.langView.append_column(self.col)
        self.langView.set_property("headers-visible", False)
	
	lang_view_sw = Gtk.ScrolledWindow()
        lang_view_sw.set_min_content_width(400)
        lang_view_sw.set_min_content_height(400)
        lang_view_sw.add(self.langView)
	content = self.get_content_area()
	content.add(lang_view_sw)

        action = self.get_action_area()
        okButton = Gtk.Button('Select')
        okButton.connect("clicked", self.selectClicked)
	self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)	
        action.add(okButton)
	self.show_all()    
    
    def readTable(self):
        lines = None
        fd = None
        try:
            fd = open("locale-list", "r")
        except:
            try:
                fd = open("/usr/share/system-config-language/locale-list", "r")
            except:
                pass

        if fd:
            lines = fd.readlines()
            fd.close()

        if not lines:
            raise RuntimeError, ("Cannot find locale-list")
        else:
            return lines
    
    def selectClicked(self, *args):
	#Get the lang from the list of languages
        lang = ""
	rc = self.langView.get_selection().get_selected()
        if rc:
            model, iter = rc
            lang = self.langStore.get_value(iter, 0).split('.')[0].replace("_", "-")
            fullName = self.langStore.get_value(iter, 1)
	
        list_iter = self.lang_list.append()
       	self.lang_list.set_value(list_iter, 0, fullName)
	self.main_ui.note_book.set_current_page(0)
	self.main_ui.render_combobox(lang)
        self.destroy()

class FontsTweakTool:
    
    def addlangClicked(self, *args):
        dialog = LangDialog(self.window, self)
        response = dialog.run()

        if response == Gtk.ResponseType.CANCEL:
            dialog.destroy()   
 
    def closeClicked(self, *args):
	Gtk.main_quit()

    def applyClicked(self, *args):
	pass

    def render_combobox(self, lang):
	fonts_store = Gtk.ListStore(str)
	fonts = Easyfc.get_fonts_list(lang, None)
	fonts_store.append([""])
        for f in fonts:
	    fonts_store.append([f])

        self.sans_combobox.set_model(fonts_store)
	self.serif_combobox.set_model(fonts_store)
	self.monospace_combobox.set_model(fonts_store)
	self.cursive_combobox.set_model(fonts_store)
	self.fantasy_combobox.set_model(fonts_store)
	
	renderer_text = Gtk.CellRendererText()
        self.sans_combobox.pack_start(renderer_text, True)
        self.sans_combobox.add_attribute(renderer_text, "text", 0)
        self.serif_combobox.pack_start(renderer_text, True)
        self.serif_combobox.add_attribute(renderer_text, "text", 0)
        self.monospace_combobox.pack_start(renderer_text, True)
        self.monospace_combobox.add_attribute(renderer_text, "text", 0)
        self.cursive_combobox.pack_start(renderer_text, True)
        self.cursive_combobox.add_attribute(renderer_text, "text", 0)
        self.fantasy_combobox.pack_start(renderer_text, True)
        self.fantasy_combobox.add_attribute(renderer_text, "text", 0)
	
    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file("fontstools.ui") 
        self.window = builder.get_object("dialog1")
        self.window.connect("destroy", Gtk.main_quit)
	self.window.set_title("fonts-tweak-tool")
        self.window.set_size_request(640, 480)        
	
	self.scrollwindow = builder.get_object("scrolledwindow1")
	self.scrollwindow.set_min_content_width(200)
	self.lang_view = builder.get_object("treeview1")
        self.lang_list = Gtk.ListStore(GObject.TYPE_STRING)
	self.lang_view.set_model(self.lang_list)
        column = Gtk.TreeViewColumn(None, Gtk.CellRendererText(), text=0)
	self.lang_view.append_column(column)

	self.note_book = builder.get_object("notebook1")
	self.note_book.set_current_page(1)

	self.sans_combobox = builder.get_object("sans_combobox")
	self.serif_combobox = builder.get_object("serif_combobox")
	self.monospace_combobox = builder.get_object("monospace_combobox")
	self.cursive_combobox = builder.get_object("cursive_combobox")
	self.fantasy_combobox = builder.get_object("fantasy_combobox")

	self.close_button = builder.get_object("button2")
	self.close_button.connect("clicked", self.closeClicked)
  
	self.addlang_button = builder.get_object("add-lang")
        self.addlang_button.connect("clicked", self.addlangClicked)
	
	self.apply_button = builder.get_object("button1")
	self.apply_button.connect("clicked", self.applyClicked)

	Easyfc.init()

def main(argv):
    tool = FontsTweakTool()
    tool.window.show_all()
    Gtk.main()
