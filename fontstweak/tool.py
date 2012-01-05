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
	
__all__ = (
	    "FontsTweakTool",
          )

class FontsTweakTool:
    def destroy(self, args):
        Gtk.main_quit()
    
    def closeClicked(self, *args):
	Gtk.main_quit()	
     
    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file("fontstools.ui") 
        self.window = builder.get_object("dialog1")
        self.window.connect("destroy", self.destroy)
	self.window.set_title("fonts-tweak-tool")
        self.window.set_size_request(640, 480)        
	
	self.close_button = builder.get_object("button2")
	self.close_button.connect("clicked", self.closeClicked)
   
def main(argv):
    tool = FontsTweakTool()
    tool.window.show_all()
    Gtk.main()
