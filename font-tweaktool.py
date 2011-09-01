import sys
from gi.repository import Gtk
	
class TutorialTextEditor:

    def on_window_destroy(self, widget, data=None):
        Gtk.main_quit()
     
    def __init__(self):
    
        builder = Gtk.Builder()
        builder.add_from_file("fonttools-2.ui") 
        
        self.window = builder.get_object("fonttools")
        builder.connect_signals(self)       
    
if __name__ == "__main__":
    editor = TutorialTextEditor()
    editor.window.show()
    Gtk.main()
