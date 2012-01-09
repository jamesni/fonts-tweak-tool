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
	
__all__ = (
	    "FontsTweakTool",
          )

class FontsTweakTool:
    def destroy(self, args):
        Gtk.main_quit()
    
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
        rc = self.langView.get_selection().get_selected()
        if rc:
            model, iter = rc
            fullName = self.langStore.get_value(iter, 0)
	
     	list_iter = self.lang_list.append()
       	self.lang_list.set_value(list_iter, 0, fullName)
 
    def closeClicked(self, *args):
	Gtk.main_quit()

    def addlangClicked(self, *args):
        lang_dialog = Gtk.Dialog() 	
        self.toplevel = Gtk.VBox()
        self.langStore = Gtk.ListStore(GObject.TYPE_STRING)
        self.title = Gtk.Label("Language Selection")
            
        lines = self.readTable()
        
	for line in lines:
	    tokens = string.split(line)
            iter = self.langStore.append()
            name = ""
            for token in tokens[3:]:
            	name = name + " " + token
            self.langStore.set_value(iter, 0, name)

        self.langView = Gtk.TreeView(self.langStore)
        self.col = Gtk.TreeViewColumn(None, Gtk.CellRendererText(), text=0)
        self.langView.append_column(self.col)
        self.langView.set_property("headers-visible", False)
	self.langViewSW = Gtk.ScrolledWindow()
        #self.langViewSW.set_policy(Gtk.POLICY_AUTOMATIC, Gtk.POLICY_AUTOMATIC)
        #self.langViewSW.set_shadow_type(Gtk.SHADOW_IN)
        self.langViewSW.add(self.langView)
	content = lang_dialog.get_content_area()
	content.add(self.langViewSW)
	
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
        self.lang_list = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING,
                                       GObject.TYPE_STRING, GObject.TYPE_STRING)
	self.lang_view.set_model(self.lang_list)
        column = Gtk.TreeViewColumn(None, Gtk.CellRendererText(), text=0)
	self.lang_view.append_column(column)
	
	self.close_button = builder.get_object("button2")
	self.close_button.connect("clicked", self.closeClicked)
  
	self.addlang_button = builder.get_object("add-lang")
        self.addlang_button.connect("clicked", self.addlangClicked)

def main(argv):
    tool = FontsTweakTool()
    tool.window.show_all()
    Gtk.main()
