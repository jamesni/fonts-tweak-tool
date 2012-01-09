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
from gi.repository import Gtk
from gi.repository import GObject
	
__all__ = (
	    "FontsTweakTool",
          )

class FontsTweakTool:
    def destroy(self, args):
        Gtk.main_quit()
   
    def selectClicked(self, *args):
	#Get the lang from the list of languages
        rc = self.langView.get_selection().get_selected()
        if rc:
            model, iter = rc
            defaultLang =  self.langStore.get_value(iter, 0)
            sysfontacm = self.langStore.get_value(iter, 1)
            sysfont = self.langStore.get_value(iter, 2)
            fullName = self.langStore.get_value(iter, 3)
	
     	list_iter = self.lang_list.append()
        self.lang_list.set(list_iter, 0, "en_US.UTF-8")
        self.lang_list.set(list_iter, 1, "iso01")
        #self.lang_list.set_value(iter, 2, 'lat0-sun16')
        #self.lang_list.set_value(iter, 3, 'English (USA)')
	
        column = Gtk.TreeViewColumn(None, Gtk.CellRendererText(), text=3)
	self.lang_view.append_column(column)
 
    def closeClicked(self, *args):
	Gtk.main_quit()

    def addlangClicked(self, *args):
        lang_dialog = Gtk.Dialog() 	
        self.toplevel = Gtk.VBox()
        self.langStore = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING,
                                       GObject.TYPE_STRING, GObject.TYPE_STRING)
        self.title = Gtk.Label("Language Selection")
            
        iter = self.langStore.append()
        self.langStore.set_value(iter, 0, 'en_US.UTF-8')
        self.langStore.set_value(iter, 1, 'iso01')
        self.langStore.set_value(iter, 2, 'lat0-sun16')
        self.langStore.set_value(iter, 3, 'English (USA)')

        self.langView = Gtk.TreeView(self.langStore)
        self.col = Gtk.TreeViewColumn(None, Gtk.CellRendererText(), text=3)
        self.langView.append_column(self.col)
        self.langView.set_property("headers-visible", False)
	content = lang_dialog.get_content_area()
	content.add(self.langView)
	
	self.bb = Gtk.HButtonBox()
        self.bb.set_layout(Gtk.ButtonBoxStyle.END)
        self.bb.set_spacing(12)

        action = lang_dialog.get_action_area()
        self.okButton = Gtk.Button('Select')
        self.okButton.connect("clicked", self.selectClicked)
        action.add(self.okButton)
	lang_dialog.show_all()    
 
    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file("fontstools.ui") 
        self.window = builder.get_object("dialog1")
        self.window.connect("destroy", self.destroy)
	self.window.set_title("fonts-tweak-tool")
        self.window.set_size_request(640, 480)        
	
	self.lang_view = builder.get_object("treeview1")
	self.lang_list = builder.get_object("lang_list")
	
	self.close_button = builder.get_object("button2")
	self.close_button.connect("clicked", self.closeClicked)
  
	self.addlang_button = builder.get_object("add-lang")
        self.addlang_button.connect("clicked", self.addlangClicked)

def main(argv):
    tool = FontsTweakTool()
    tool.window.show_all()
    Gtk.main()
