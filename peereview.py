import GPS
import re
import os

## The following line is the usual way to make pygobject visible
from gi.repository import Gtk, GLib, Gdk, GObject

messages_file="peereview.gnat"
category="Peereview"
subject_id=1

class AnswerWindow(Gtk.Window):
   def __init__(self, filename, line, subject_ids):

      # Class attributes
      self.filename = filename
      self.line = line

      # Create window instance
      Gtk.Window.__init__(self, title="Answer comment")
      self.set_border_width(10)

      # Create list box
      grid = Gtk.Grid()
      self.add(grid)

      # Add comment label
      label = Gtk.Label("Choose comment", xalign=0)     
      grid.add(label)
      
      # Create combo to select the subject to answer
      self.combo = Gtk.ComboBoxText()
      for subject in subject_ids:
         self.combo.append_text("#%d" % subject)
      grid.attach_next_to(label, self.combo, Gtk.PositionType.RIGHT, 1, 1)

      # Add comment label
      label2 = Gtk.Label("Answer", xalign=0)     
      grid.attach_next_to(label, label2, Gtk.PositionType.BOTTOM, 3, 1)
 
      # Add comment label
      self.text_entry = Gtk.Entry()     
      grid.attach_next_to(label2, self.text_entry, Gtk.PositionType.BOTTOM, 3, 3)
 
      # Add comment label
      buttonAdd = Gtk.Button("_Add", use_underline=True)
      buttonAdd.connect("clicked", self.on_add_clicked)
      grid.attach_next_to(self.text_entry, buttonAdd, Gtk.PositionType.BOTTOM, 1,1)

      buttonCancel = Gtk.Button("_Cancel", use_underline=True)
      buttonCancel.connect("clicked", self.on_close_clicked)
      grid.attach_next_to(buttonAdd, buttonCancel, Gtk.PositionType.RIGHT, 1, 1)

   def on_add_clicked(self, button):
      subject = self.combo.get_active_text()
      
      with open(messages_file, "r+") as f:
         lines = f.readlines()
         
         # Line index of subject
         line_idx = [i for i in range(len(lines)) if "%s:" % (subject) in lines[i]]
         
         # Check if there's already another answer
         insert_idxs = [i for i in range(line_dix[0]+1, len(lines)) if re.search(' #\d+:', lines[i]) is not None]
         insert_idx = insert_idxs[0] if insert_idxs is not None and len(insert_idxs) > 0 else line_idx[0]+1

         # Insert line in opened file
         lines.insert(insert_idx, "%s:%s: %s:%s %s" % (self.filename, self.line, self.filename, self.line, self.text_entry.get_text()))
         
         # Update file
         for line in lines:
            messages_file.write(line) 
      Gtk.main_quit()

   def on_close_clicked(self, button):
      Gtk.main_quit()

def add_message(filename, line):

   # Increment subject id
   global subject_id
   subject_id = subject_id + 1

   # Request message to enter
   title = "Comment #%d at [%s:%s]" % (subject_id, filename, line)
   message=GPS.MDI.input_dialog(title, "Comment")
   
   # Create the message pattern to open in Locations window
   entry = "%s:%s: #%s:%s" % (filename, line, subject_id, message)

   # Append new message in file
   with open(messages_file, "a") as comment:
      comment.write("%s\n" % entry)

   # Clear Peereview locations
   GPS.Locations.remove_category(category)

   # Reload file to add all comments
   for comment in open(messages_file):
      GPS.Locations.parse(comment.rstrip('\n'), category)
   
def answer (filename, line):
   win = AnswerWindow(filename, line, get_subjects(filename, line))
   win.show_all()
   Gtk.main()


def get_subjects (filename, line):
   # Get all lines from reference file
   with open(messages_file, 'r') as input_file:
      lines="".join(input_file.readlines())

      # Get all ids from that file in the given line
      pattern='''%s:%s: #(\d+)''' % (filename, line)
      subjects = re.findall(pattern, lines)

   # Return an unique list with all subjects
   return list(set([int(item) for item in subjects]))

def clean_messages ():
   open(messages_file, 'w').close()

def close_subject (filename, line):
   # TODO - REQUEST USER FOR SUBJECT ID
   # Get subjects in that particular line
   subjects=get_subjects(filename, line)

   message=GPS.MDI.input_dialog("Chose subject to close", ["#%d" % num for num in subjects])
   # Create pattern to look for in a line to look for the subject to delete
   subject_pattern="%s:%d: #%d" % (filename, line, subject_id)

   # Open temporary file that will hold everything
   # but the subject at hand
   with open(".temp", 'w') as temp_file:
      for line in open(messages_file):
         if subject_pattern not in line:
            temp_file.write(line)

   # Rename temporary file to the original
   os.rename(".temp", messages_file)


def load():
   global subject_id

   # Load file into the Locations view
   with open(messages_file, "r") as msg_file:
      GPS.Locations.parse("".join(msg_file.readlines()), category) 

   # Update maximum subject id
   subject_id = max(get_subjects('''.*''', '''\d+'''))

