import GPS
import getpass
import re
import os
from gi.repository import Gtk, GLib, Gdk, GObject

messages_file="peereview.gnat"
category="Peereview"
subject_id=0

class CloseWindow(Gtk.Window):
   def __init__(self, filename, line, subject_ids):

      # Class attributes
      self.filename = filename
      self.line = line

      # Create window instance
      Gtk.Window.__init__(self, title="Close comment")
      
      # Find parent
      msg_win = GPS.MDI.get("Messages").pywidget().get_toplevel()
      if isinstance(msg_win, Gtk.Window):
         self.set_transient_for(msg_win)
      self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)

      # Create list box
      grid = Gtk.Grid()
      self.add(grid)

      # Add comment label
      label = Gtk.Label("Remove comment")
      grid.add(label)

      # Create combo to select the subject to answer
      store = Gtk.ListStore(str);
      for subject in subject_ids:
         store.append(["#%d" % subject])
      self.combo = Gtk.ComboBox.new_with_model(store)
      renderer_text = Gtk.CellRendererText()
      self.combo.pack_start(renderer_text, True)
      self.combo.add_attribute(renderer_text, "text", 0)
      self.combo.set_active(0)
      grid.attach_next_to(self.combo, label, Gtk.PositionType.RIGHT, 2, 1)
      
      # Add comment label
      buttonAdd = Gtk.Button("_Remove", use_underline=True)
      buttonAdd.connect("clicked", self.on_add_clicked)
      grid.attach_next_to(buttonAdd, label, Gtk.PositionType.BOTTOM, 2,1)

      buttonCancel = Gtk.Button("_Cancel", use_underline=True)
      buttonCancel.connect("clicked", self.on_close_clicked)
      grid.attach_next_to(buttonCancel, buttonAdd, Gtk.PositionType.RIGHT, 1, 1)


   def on_add_clicked(self, button):
     # Get subject id from combo box
      subject = ""
      tree_iter = self.combo.get_active_iter()
      if tree_iter != None:
         model = self.combo.get_model()
         subject = model[tree_iter][0]

      # Confirm with your to delete
      if not GPS.MDI.yes_no_dialog("Are you certain to delete comment %s?" % subject):
         return

      # Open comments file
      lines = []
      with open(messages_file, "r+") as f:
         lines = f.readlines()

      # Line index of subject
      start_idxs = [i for i in range(len(lines)) if "%s:" % (subject) in lines[i]]
      start_idx = start_idxs[0] if start_idxs is not None and len(start_idxs) > 0 else 0
      
      # Line index of next subject
      insert_idxs = [i for i in range(start_idx+1, len(lines)) if re.search(' #\d+:', lines[i]) is not None]
      end_idx = insert_idxs[0] if insert_idxs is not None and len(insert_idxs) > 0 else len(lines)

      # Update file
      with open(messages_file, "w") as f:
         for idx in range(len(lines)):
            if idx not in range(start_idx, end_idx):
               f.write(lines[idx])
 
      # Find element with subject and remove it
      locations_subject=[i for i in GPS.Message.list() if subject in i.get_text()]
      if len(locations_subject) > 0:
         locations_subject[0].remove() 
    
      self.destroy()


   def on_close_clicked(self, button):
      self.destroy()


class AnswerWindow(Gtk.Window):
   def __init__(self, filename, line, subject_ids):

      # Class attributes
      self.filename = filename
      self.line = line

      # Create window instance
      Gtk.Window.__init__(self, title="Answer comment")
      
      # Find parent
      msg_win = GPS.MDI.get("Messages").pywidget().get_toplevel()
      if isinstance(msg_win, Gtk.Window):
         self.set_transient_for(msg_win)
      self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
      

      # Create list box
      grid = Gtk.Grid()
      self.add(grid)

      # Add comment label
      label = Gtk.Label("Comment")
      grid.add(label)

      # Create combo to select the subject to answer
      store = Gtk.ListStore(str);
      for subject in subject_ids:
         store.append(["#%d" % subject])
      self.combo = Gtk.ComboBox.new_with_model(store)
      renderer_text = Gtk.CellRendererText()
      self.combo.pack_start(renderer_text, True)
      self.combo.add_attribute(renderer_text, "text", 0)
      self.combo.set_active(0)
      grid.attach_next_to(self.combo, label, Gtk.PositionType.RIGHT, 2, 1)
      
      # Add comment label
      label2 = Gtk.Label("Answer", xalign=0)
      grid.attach_next_to(label2, label, Gtk.PositionType.BOTTOM, 3, 1)
 
      # Add comment label
      self.text_entry = Gtk.Entry()
      self.text_entry.set_size_request(500, 20)
      self.text_entry.set_property("truncate-multiline", True)
      self.text_entry.connect('activate', self.on_add_clicked)
      grid.attach_next_to(self.text_entry, label2, Gtk.PositionType.BOTTOM, 3, 3)
 
      # Add comment label
      buttonAdd = Gtk.Button("_Add", use_underline=True)
      buttonAdd.connect("clicked", self.on_add_clicked)
      grid.attach_next_to(buttonAdd, self.text_entry, Gtk.PositionType.BOTTOM, 2,1)

      buttonCancel = Gtk.Button("_Cancel", use_underline=True)
      buttonCancel.connect("clicked", self.on_close_clicked)
      grid.attach_next_to(buttonCancel, buttonAdd, Gtk.PositionType.RIGHT, 1, 1)


   def on_add_clicked(self, button):
      subject = ""
      tree_iter = self.combo.get_active_iter()
      if tree_iter != None:
         model = self.combo.get_model()
         subject = model[tree_iter][0]
      lines = []
      with open(messages_file, "r+") as f:
         lines = f.readlines()
      # Line index of subject
      line_idx = [i for i in range(len(lines)) if "%s:" % (subject) in lines[i]]
      # Check if there's already another answer
      insert_idxs = [i for i in range(line_idx[0]+1, len(lines)) if re.search(' #\d+:', lines[i]) is not None]
      insert_idx = insert_idxs[0] if insert_idxs is not None and len(insert_idxs) > 0 else len(lines)

      # Insert line in opened file
      lines.insert(insert_idx, "%s:%s: at line %s [%s] %s\n" % (self.filename, self.line, self.line, getpass.getuser(), self.text_entry.get_text()))

      # Update file
      with open(messages_file, "w") as f:
         for line in lines:
            f.write(line)
      # Clear Peereview locations
      GPS.Locations.remove_category(category)

      # Reload file to add all comments
      for comment in open(messages_file, "r"):
         GPS.Locations.parse(output=comment.rstrip('\n'), category=category, highlight_category="Peereview")
      
      self.destroy()


   def on_close_clicked(self, button):
      self.destroy()


def add_message(filename, line):

   # Increment subject id
   global subject_id
   if not os.path.isfile(messages_file):
      open(messages_file, 'w').close()
   if not is_file_wr():
      return
 
   # Request message to enter
   title = "Comment #%d at [%s:%s]" % (subject_id + 1, filename, line)
   message=GPS.MDI.input_dialog(title, "Comment")
   if message is None or len(message) == 0:
      return

   # New subject
   subject_id = subject_id + 1

   # Create the message pattern to open in Locations window
   entry = "%s:%s: #%s:[%s] %s" % (filename, line, subject_id, getpass.getuser(), message[0])

   # Append new message in file
   with open(messages_file, "a") as comment:
      comment.write("%s\n" % entry)

   GPS.Locations.add(category=category, 
                     file=GPS.File(filename), 
                     line=int(line),
                     column=1,
                     message="#%s:[%s] %s" % (subject_id, getpass.getuser(), message[0]),
                     highlight="Peereview")


def reload_file():
   # Clear Peereview locations
   GPS.Locations.remove_category(category)

   # Reload file to add all comments
   for comment in open(messages_file, "r"):
      GPS.Locations.parse(output=comment.rstrip('\n'), category=category, highlight_category="Peereview")

   
def answer(filename, line):
   if not is_file_wr():
      return
    # Show window to user insert its response
   win = AnswerWindow(filename, line, get_subjects(filename, line))
   win.show_all()
   win.text_entry.grab_focus()


def get_subjects(filename, line):
   # Get all lines from reference file
   with open(messages_file, 'r') as input_file:
      lines="".join(input_file.readlines())

      # Get all ids from that file in the given line
      pattern='''%s:%s: #(\d+)''' % (filename, line)
      subjects = re.findall(pattern, lines)

   # Return an unique list with all subjects
   return list(set([int(item) for item in subjects]))


def clean_messages():
   if GPS.MDI.yes_no_dialog("CAUTION: This will remove ALL comments from all files\nDo you confirm?") and is_file_wr():
      open(messages_file, 'w').close()
      GPS.Locations.remove_category(category)


def close_subject(filename, line):
   if not is_file_wr():
      return
    # Show window to user insert its response
   win = CloseWindow(filename, line, get_subjects(filename, line))
   win.show_all()


def is_file_wr(file_name=messages_file):
   if not os.access(file_name, os.W_OK):
      GPS.MDI.dialog("CAUTION: peereview.gnat file is Read-Only.\nPlease change its permission and reload the file.")
      return False
   else:
      return True


def change_filename():
   global messages_file

   new_file = GPS.MDI.file_selector("*.gnat")
   
   if new_file is not None and len(new_file.name()) > 0 and is_file_wr(new_file.name()):
         messages_file = new_file.name()
         load()

def load(name=0):
   global subject_id

   if os.path.isfile(messages_file) and is_file_wr():
      # Load file
      reload_file()

      # Update maximum subject id
      subjects = get_subjects('''.*''', '''\d+''')
      subject_id = max(subjects) if subjects is not None and len(subjects) > 0 else 0

GPS.Hook("desktop_loaded").add(load)
GPS.Editor.register_highlighting(category="Peereview", color="#2f4f4f", speedbar=True)
