
from __future__ import division
import cPickle
try :
  import gobject
except ImportError :
  gobject = None
import sys

dict_residue_prop_objects = {}
class coot_extension_gui (object) :
  def __init__ (self, title) :
    import gtk
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    scrolled_win = gtk.ScrolledWindow()
    self.outside_vbox = gtk.VBox(False, 2)
    self.inside_vbox = gtk.VBox(False, 0)
    self.window.set_title(title)
    self.inside_vbox.set_border_width(0)
    self.window.add(self.outside_vbox)
    self.outside_vbox.pack_start(scrolled_win, True, True, 0)
    scrolled_win.add_with_viewport(self.inside_vbox)
    scrolled_win.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

  def finish_window (self) :
    import gtk
    self.outside_vbox.set_border_width(2)
    ok_button = gtk.Button("  Close  ")
    self.outside_vbox.pack_end(ok_button, False, False, 0)
    ok_button.connect("clicked", lambda b: self.destroy_window())
    self.window.connect("delete_event", lambda a, b: self.destroy_window())
    self.window.show_all()

  def destroy_window (self, *args) :
    self.window.destroy()
    self.window = None

  def confirm_data (self, data) :
    for data_key in self.data_keys :
      outlier_list = data.get(data_key)
      if outlier_list is not None and len(outlier_list) > 0 :
        return True
    return False

  def create_property_lists (self, data) :
    import gtk
    for data_key in self.data_keys :
      outlier_list = data[data_key]
      if outlier_list is None or len(outlier_list) == 0 :
        continue
      else :
        frame = gtk.Frame(self.data_titles[data_key])
        vbox = gtk.VBox(False, 2)
        frame.set_border_width(6)
        frame.add(vbox)
        self.add_top_widgets(data_key, vbox)
        self.inside_vbox.pack_start(frame, False, False, 5)
        list_obj = residue_properties_list(
          columns=self.data_names[data_key],
          column_types=self.data_types[data_key],
          rows=outlier_list,
          box=vbox)
        ##save property list frame object
        dict_residue_prop_objects[data_key] = list_obj
# Molprobity result viewer
class coot_molprobity_todo_list_gui (coot_extension_gui) :
  data_keys = [ "clusters","rama", "rota", "cbeta", "probe", "smoc", "cablam",
               "jpred"]
  data_titles = { "clusters"  : "Outlier residue clusters",
                  "rama"  : "Ramachandran outliers",
                  "rota"  : "Rotamer outliers",
                  "cbeta" : "C-beta outliers",
                  "probe" : "Severe clashes",
                  "smoc"  : "Local density fit (SMOC)",
                  "cablam": "Ca geometry (CaBLAM)",
                  "jpred":"SS prediction"}
  data_names = { "clusters"  : ["Chain","Residue","Cluster","Outlier types"],
                 "rama"  : ["Chain", "Residue", "Name", "Score"],
                 "rota"  : ["Chain", "Residue", "Name", "Score"],
                 "cbeta" : ["Chain", "Residue", "Name", "Conf.", "Deviation"],
                 "probe" : ["Atom 1", "Atom 2", "Overlap"],
                 "smoc" : ["Chain", "Residue", "Name", "Score"],
                 "cablam" : ["Chain", "Residue","Name","recommendation","DSSP"],
                 "jpred" : ["Chain", "Residue","Name","predicted SS","current SS"]}
  if (gobject is not None) :
    data_types = {  "clusters" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                             gobject.TYPE_INT, gobject.TYPE_STRING,
                             gobject.TYPE_PYOBJECT],
                    "rama" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                             gobject.TYPE_STRING, gobject.TYPE_FLOAT,
                             gobject.TYPE_PYOBJECT],
                   "rota" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                             gobject.TYPE_STRING, gobject.TYPE_FLOAT,
                             gobject.TYPE_PYOBJECT],
                   "cbeta" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_FLOAT, gobject.TYPE_PYOBJECT],
                   "probe" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_FLOAT, gobject.TYPE_PYOBJECT],
                   "smoc" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_STRING,gobject.TYPE_FLOAT,
                             gobject.TYPE_PYOBJECT],
                   "cablam" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_STRING,gobject.TYPE_STRING,
                             gobject.TYPE_STRING,gobject.TYPE_PYOBJECT],
                   "jpred" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_STRING,gobject.TYPE_STRING,
                             gobject.TYPE_STRING,gobject.TYPE_PYOBJECT]}
  else :
    data_types = dict([ (s, []) for s in ["clusters","rama","rota","cbeta","probe","smoc",
                                          "cablam","jpred"] ])

  def __init__ (self, data_file=None, data=None) :
    assert ([data, data_file].count(None) == 1)
    if (data is None) :
      data = load_pkl(data_file)
    if not self.confirm_data(data) :
      return
    coot_extension_gui.__init__(self, "MolProbity to-do list")
    self.dots_btn = None
    self.dots2_btn = None
    self._overlaps_only = True
    self.window.set_default_size(420, 600)
    self.create_property_lists(data)
    self.finish_window()

  def add_top_widgets (self, data_key, box) :
    import gtk
    if data_key == "probe" :
      hbox = gtk.HBox(False, 2)
      self.dots_btn = gtk.CheckButton("Show Probe dots")
      hbox.pack_start(self.dots_btn, False, False, 5)
      self.dots_btn.connect("toggled", self.toggle_probe_dots)
      self.dots2_btn = gtk.CheckButton("Overlaps only")
      hbox.pack_start(self.dots2_btn, False, False, 5)
      self.dots2_btn.connect("toggled", self.toggle_all_probe_dots)
      self.dots2_btn.set_active(True)
      self.toggle_probe_dots()
      box.pack_start(hbox, False, False, 0)

  def toggle_probe_dots (self, *args) :
    if self.dots_btn is not None :
      show_dots = self.dots_btn.get_active()
      overlaps_only = self.dots2_btn.get_active()
      if show_dots :
        self.dots2_btn.set_sensitive(True)
      else :
        self.dots2_btn.set_sensitive(False)
      show_probe_dots(show_dots, overlaps_only)

  def toggle_all_probe_dots (self, *args) :
    if self.dots2_btn is not None :
      self._overlaps_only = self.dots2_btn.get_active()
      self.toggle_probe_dots()

class rsc_todo_list_gui (coot_extension_gui) :
  data_keys = ["by_res", "by_atom"]
  data_titles = ["Real-space correlation by residue",
                 "Real-space correlation by atom"]
  data_names = {}
  data_types = {}

class residue_properties_list (object) :
  def __init__ (self, columns, column_types, rows, box,
      default_size=(380,200)) :
    assert len(columns) == (len(column_types) - 1)
    if (len(rows) > 0) and (len(rows[0]) != len(column_types)) :
      raise RuntimeError("Wrong number of rows:\n%s" % str(rows[0]))
    import gtk
    ##adding a column type for checkbox (bool) before atom coordinate
    if gobject is not None:
        column_types = column_types[:-1]+[bool]+[column_types[-1]]
    
    self.liststore = gtk.ListStore(*column_types)
    self.listmodel = gtk.TreeModelSort(self.liststore)
    self.listctrl = gtk.TreeView(self.listmodel)
    self.listctrl.column = [None]*len(columns)
    self.listctrl.cell = [None]*len(columns)
    for i, column_label in enumerate(columns) :
      cell = gtk.CellRendererText()
      column = gtk.TreeViewColumn(column_label)
      self.listctrl.append_column(column)
      column.set_sort_column_id(i)
      column.pack_start(cell, True)
      column.set_attributes(cell, text=i)
    ##add a cell for checkbox
    cell1 = gtk.CellRendererToggle()
    cell1.connect ("toggled", self.on_selected_toggled)
    column = gtk.TreeViewColumn('Dealt with',cell1,active=i+1)
    self.listctrl.append_column(column)
    #column.set_sort_column_id(i+1)
    #column.pack_start(cell1, True)
    
    self.listctrl.get_selection().set_mode(gtk.SELECTION_SINGLE)
    for row in rows :
      row = row[:-1] + (False,)+(row[-1],)
      self.listmodel.get_model().append(row)
    self.listctrl.connect("cursor-changed", self.OnChange)
    sw = gtk.ScrolledWindow()
    w, h = default_size
    if len(rows) > 10 :
      sw.set_size_request(w, h)
    else :
      sw.set_size_request(w, 30 + (20 * len(rows)))
    sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    box.pack_start(sw, False, False, 5)
    inside_vbox = gtk.VBox(False, 0)
    sw.add(self.listctrl)

  def OnChange (self, treeview) :
    import coot # import dependency
    selection = self.listctrl.get_selection()
    (model, tree_iter) = selection.get_selected()
    if tree_iter is not None :
      row = model[tree_iter]
      xyz = row[-1]
      if isinstance(xyz, tuple) and len(xyz) == 3 :
        set_rotation_centre(*xyz)
        set_zoom(30)
        graphics_draw()
  ##check box toggle
  def on_selected_toggled(self,renderer,path):
    if path is not None:
      model = self.listmodel.get_model()
      it = model.get_iter(path)
      #set toggle
      model[it][-2] = not model[it][-2]
      #set checkboxes for same residues in other lists
      try:
        chain = model[it][0]
        residue = model[it][1]
        for data_key in dict_residue_prop_objects:
          prop_obj = dict_residue_prop_objects[data_key]
          for row in prop_obj.listmodel.get_model():
            if data_key == 'probe':
              atom1_split = row[0].split()
              atom2_split = row[1].split()
              if atom1_split[0] == chain and atom1_split[1] == residue:
                row[-2] = model[it][-2]
              elif atom2_split[0] == chain and atom2_split[1] == residue:
                row[-2] = model[it][-2]
            elif row[0] == chain and row[1] == residue:
              row[-2] = model[it][-2]
      except IndexError: pass

  def check_chain_residue(self,chain,residue):
      pass
  
def show_probe_dots (show_dots, overlaps_only) :
  import coot # import dependency
  n_objects = number_of_generic_objects()
  sys.stdout.flush()
  if show_dots :
    for object_number in range(n_objects) :
      obj_name = generic_object_name(object_number)
      if overlaps_only and not obj_name in ["small overlap", "bad overlap"] :
        sys.stdout.flush()
        set_display_generic_object(object_number, 0)
      else :
        set_display_generic_object(object_number, 1)
  else :
    sys.stdout.flush()
    for object_number in range(n_objects) :
      set_display_generic_object(object_number, 0)

def load_pkl (file_name) :
  pkl = open(file_name, "rb")
  data = cPickle.load(pkl)
  pkl.close()
  return data
data = {}
data['clusters'] = []
data['rama'] = []
data['rota'] = []
data['jpred'] = []
data['probe'] = [(' B 580  GLN  OE1', ' B1310  NAG  H81', -1.364, (156.453, 202.38, 210.127)), (' B 580  GLN  CD ', ' B1310  NAG  H81', -1.343, (157.125, 201.628, 210.222)), (' B 580  GLN  OE1', ' B1310  NAG  C8 ', -1.08, (155.598, 201.656, 210.751)), (' B 580  GLN  CD ', ' B1310  NAG  C8 ', -0.86, (156.814, 202.647, 211.507)), (' H  66  ARG  NE ', ' H  82B ASN  OD1', -0.7, (188.883, 182.025, 274.115)), (' D   1  NAG  O3 ', ' D   2  NAG  O6 ', -0.611, (201.334, 175.724, 116.482)), (' A 804  GLN  NE2', ' A1303  NAG  O6 ', -0.609, (172.82, 189.022, 146.071)), (' A 563  GLN  O  ', ' A 577  ARG  NH1', -0.602, (231.564, 178.319, 204.93)), (' A 557  LYS  NZ ', ' A 574  ASP  OD2', -0.588, (224.28, 177.894, 194.098)), (' A 905  ARG  NH1', ' A1049  LEU  O  ', -0.578, (191.243, 198.188, 142.006)), (' D   1  NAG  O3 ', ' D   2  NAG  O5 ', -0.571, (201.723, 174.567, 116.317)), (' C 563  GLN  O  ', ' C 577  ARG  NH1', -0.559, (205.711, 243.843, 199.8)), (' A 703  ASN  ND2', ' C 787  GLN  OE1', -0.549, (203.39, 173.001, 148.132)), (' B 498  GLN  OE1', ' B 500  THR  N  ', -0.54, (193.224, 195.839, 250.684)), (' B 342  PHE  CB ', ' B1311  NAG  H82', -0.527, (173.73, 199.034, 233.986)), (' A1019  ARG  NH2', ' B1017  GLU  OE1', -0.525, (198.621, 208.12, 170.97)), (' H  57  LYS  NZ ', ' H  69  ILE  O  ', -0.498, (179.551, 182.226, 261.179)), (' C 115  GLN  NE2', ' C1301  NAG  H82', -0.498, (234.729, 195.087, 234.241)), (' D   1  NAG  O3 ', ' D   1  NAG  O7 ', -0.497, (201.512, 175.627, 118.233)), (' C 738  CYS  SG ', ' C 739  THR  N  ', -0.496, (199.428, 186.211, 193.485)), (' L  52  SER  OG ', ' L  64  GLY  O  ', -0.491, (189.491, 215.751, 252.943)), (' A1307  NAG  O3 ', ' A1307  NAG  O7 ', -0.489, (178.456, 173.188, 167.222)), (' A 189  LEU  N  ', ' A 208  THR  O  ', -0.483, (159.857, 164.863, 197.919)), (' C 804  GLN  NE2', ' C1307  NAG  O6 ', -0.481, (229.996, 179.783, 152.222)), (' J   1  NAG  O3 ', ' J   2  NAG  O6 ', -0.477, (229.088, 208.261, 118.21)), (' B 580  GLN  NE2', ' B1310  NAG  H81', -0.476, (157.495, 202.33, 211.618)), (' B 883  THR HG23', ' C 707  TYR  HB2', -0.468, (222.258, 220.236, 140.363)), (' B 658  ASN  ND2', ' B 660  TYR  OH ', -0.467, (169.925, 226.442, 158.385)), (' B 787  GLN  OE1', ' C 703  ASN  ND2', -0.461, (228.642, 214.915, 148.466)), (' B 405  ASP  OD2', ' B 406  GLU  N  ', -0.459, (195.181, 194.259, 235.236)), (' J   1  NAG  HO3', ' J   2  NAG  HO6', -0.456, (229.692, 208.624, 118.31)), (' B  29  THR  O  ', ' B  62  VAL  N  ', -0.449, (172.834, 243.849, 196.656)), (' C 553  THR  O  ', ' C 586  ASP  N  ', -0.439, (216.619, 238.738, 194.898)), (' B 905  ARG  NH1', ' B1049  LEU  O  ', -0.439, (208.536, 213.416, 142.968)), (' H  70  THR  O  ', ' H  79  VAL  N  ', -0.438, (175.043, 185.415, 264.321)), (' A 641  ASN  ND2', ' A 654  GLU  OE1', -0.432, (195.665, 158.402, 175.846)), (' C 905  ARG  NH1', ' C1049  LEU  O  ', -0.425, (213.12, 190.897, 144.5)), (' B 903  ALA  HB1', ' B 913  GLN  HB2', -0.425, (208.805, 214.673, 131.115)), (' H 113  SER  O  ', ' H 113  SER  OG ', -0.419, (180.21, 186.693, 290.544)), (' C 973  ILE HG23', ' C 980  ILE HG22', -0.411, (209.933, 192.75, 210.539)), (' B1031  GLU  OE2', ' C1039  ARG  NE ', -0.41, (206.486, 202.482, 151.896)), (' B 553  THR  O  ', ' B 586  ASP  N  ', -0.409, (161.436, 199.936, 195.551)), (' B  31  SER  N  ', ' B  60  SER  O  ', -0.402, (175.321, 242.421, 194.549))]
data['cbeta'] = [('L', '  23 ', 'CYS', ' ', 0.30523252641684323, (195.161, 208.695, 261.76200000000006)), ('L', '  49 ', 'TYR', ' ', 0.25097351243034666, (183.07, 206.69500000000005, 254.62000000000003))]
data['cablam'] = [('A', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\n-TT-E', (180.9, 170.3, 210.2)), ('A', '545', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\nSSS--', (218.2, 181.2, 210.7)), ('A', '546', 'LEU', 'check CA trace,carbonyls, peptide', ' \nSS--E', (218.1, 181.2, 206.9)), ('A', '547', 'THR', ' beta sheet', ' \nS--EE', (214.5, 179.8, 207.2)), ('A', '604', 'THR', 'check CA trace,carbonyls, peptide', 'turn\nTTT-S', (181.3, 170.3, 172.4)), ('A', '614', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\nETT--', (206.5, 173.5, 184.5)), ('A', '618', 'THR', 'check CA trace,carbonyls, peptide', 'bend\n-SS--', (205.9, 161.3, 188.2)), ('A', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (199.7, 174.0, 174.1)), ('A', '667', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nEEETT', (203.3, 175.1, 173.5)), ('A', '709', 'ASN', 'check CA trace,carbonyls, peptide', 'turn\n--TTE', (217.0, 175.7, 135.1)), ('A', '797', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\n--STT', (177.8, 197.5, 136.1)), ('A', '856', 'ASN', 'check CA trace,carbonyls, peptide', 'helix-3\n-GGGE', (178.6, 204.9, 190.3)), ('A', '1034', 'LEU', 'check CA trace,carbonyls, peptide', 'turn\nIITS-', (190.8, 204.7, 146.9)), ('A', '1040', 'VAL', 'check CA trace,carbonyls, peptide', 'turn\n--TTT', (202.1, 192.5, 147.5)), ('A', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'bend\nTTSSS', (195.4, 194.4, 150.5)), ('A', '1057', 'PRO', 'check CA trace,carbonyls, peptide', 'turn\nEETTE', (180.0, 198.6, 165.0)), ('A', '1092', 'GLU', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (207.1, 192.2, 127.5)), ('A', '1098', 'ASN', 'check CA trace,carbonyls, peptide', ' \nEE-SS', (205.5, 173.5, 124.3)), ('A', '1099', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\nE-SSS', (208.6, 172.1, 122.6)), ('A', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nTTS--', (198.3, 184.5, 131.8)), ('A', '34', 'ARG', 'check CA trace', 'turn\nTTTT-', (171.7, 168.0, 195.4)), ('A', '220', 'PHE', 'check CA trace', ' \n-S---', (168.7, 170.2, 191.2)), ('A', '293', 'LEU', 'check CA trace', 'bend\nTTS-H', (184.8, 168.8, 191.7)), ('A', '544', 'ASN', 'check CA trace', 'bend\nESSS-', (220.3, 178.8, 212.8)), ('A', '549', 'THR', 'check CA trace', 'strand\n-EEEE', (211.8, 175.7, 201.8)), ('A', '592', 'PHE', 'check CA trace', 'strand\n--EEE', (205.6, 174.5, 191.4)), ('A', '600', 'PRO', 'check CA trace', 'bend\nEES-T', (187.2, 171.3, 173.6)), ('B', '31', 'SER', 'check CA trace,carbonyls, peptide', ' \nEE-TT', (177.3, 243.9, 193.9)), ('B', '58', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n--TT-', (180.1, 238.6, 192.2)), ('B', '83', 'VAL', 'check CA trace,carbonyls, peptide', ' \n----B', (172.5, 246.7, 214.0)), ('B', '87', 'ASN', 'check CA trace,carbonyls, peptide', 'turn\nB-TT-', (177.0, 236.8, 209.3)), ('B', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\n-TT-E', (180.5, 235.4, 208.9)), ('B', '110', 'LEU', 'check CA trace,carbonyls, peptide', ' \nSS-ST', (177.1, 243.9, 220.5)), ('B', '372', 'ALA', 'check CA trace,carbonyls, peptide', ' \nTT--S', (180.1, 208.2, 232.7)), ('B', '487', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\n-SS-B', (204.8, 171.3, 237.2)), ('B', '518', 'LEU', 'check CA trace,carbonyls, peptide', ' \nE--SS', (174.4, 189.8, 209.6)), ('B', '600', 'PRO', 'check CA trace,carbonyls, peptide', 'bend\nEES-T', (181.2, 230.0, 170.5)), ('B', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nSEEET', (178.1, 217.6, 170.8)), ('B', '667', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nEEETT', (177.6, 214.0, 169.9)), ('B', '707', 'TYR', ' beta sheet', ' \n----T', (177.5, 207.5, 136.0)), ('B', '710', 'ASN', 'check CA trace,carbonyls, peptide', 'turn\n-TTEE', (179.4, 203.9, 127.7)), ('B', '797', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\n--STT', (215.4, 225.7, 137.7)), ('B', '857', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\n--SEE', (215.0, 218.3, 190.7)), ('B', '1036', 'GLN', 'check CA trace,carbonyls, peptide', ' \nTS---', (207.7, 209.2, 144.4)), ('B', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\nTTTSS', (201.9, 212.0, 150.4)), ('B', '1058', 'HIS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (210.7, 219.2, 167.5)), ('B', '1099', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\nE-SS-', (180.4, 211.9, 119.0)), ('B', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nTTS--', (194.9, 214.2, 130.3)), ('B', '34', 'ARG', 'check CA trace', ' \nTT--E', (183.0, 244.7, 193.3)), ('B', '220', 'PHE', 'check CA trace', ' \n-S--E', (186.5, 247.0, 189.1)), ('B', '293', 'LEU', 'check CA trace', 'bend\nTTS-H', (178.5, 233.1, 188.8)), ('B', '310', 'LYS', 'check CA trace', 'bend\n--SEE', (185.2, 228.0, 170.7)), ('B', '359', 'SER', 'check CA trace', ' \n---SE', (168.1, 191.1, 221.7)), ('B', '486', 'PHE', 'check CA trace', 'bend\n--SS-', (206.4, 169.3, 240.0)), ('B', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (170.5, 208.2, 199.1)), ('B', '1092', 'GLU', 'check CA trace', 'bend\nESSSE', (197.6, 202.9, 126.9)), ('C', '33', 'THR', 'check CA trace,carbonyls, peptide', 'bend\n--S--', (244.2, 198.9, 197.1)), ('C', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\n-TT-E', (234.6, 204.3, 214.3)), ('C', '108', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEES--', (236.5, 204.8, 226.2)), ('C', '123', 'ALA', 'check CA trace,carbonyls, peptide', 'turn\n--TTS', (252.9, 182.7, 223.8)), ('C', '132', 'GLU', ' beta sheet', ' \nEE---', (238.9, 197.7, 234.2)), ('C', '310', 'LYS', 'check CA trace,carbonyls, peptide', 'strand\n-EEEE', (233.2, 203.8, 174.9)), ('C', '543', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nEESSS', (212.7, 235.7, 206.7)), ('C', '545', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\nSSS--', (209.1, 232.7, 208.1)), ('C', '546', 'LEU', 'check CA trace,carbonyls, peptide', ' \nSS--E', (209.2, 231.6, 204.4)), ('C', '600', 'PRO', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (236.7, 205.8, 175.3)), ('C', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (227.4, 215.0, 174.3)), ('C', '667', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nEEETT', (224.8, 217.5, 173.4)), ('C', '709', 'ASN', 'check CA trace,carbonyls, peptide', 'turn\n--TTE', (220.4, 223.0, 133.3)), ('C', '797', 'PHE', 'check CA trace,carbonyls, peptide', ' \n---TT', (220.8, 178.8, 140.4)), ('C', '857', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\n-SSEE', (206.9, 183.0, 191.7)), ('C', '1036', 'GLN', 'check CA trace,carbonyls, peptide', ' \nTS---', (209.7, 193.8, 145.2)), ('C', '1040', 'VAL', 'check CA trace,carbonyls, peptide', 'turn\n--TTT', (212.3, 204.1, 148.0)), ('C', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\nTTTSS', (213.9, 197.5, 151.9)), ('C', '1057', 'PRO', 'check CA trace,carbonyls, peptide', 'turn\nEETTE', (216.4, 184.1, 168.5)), ('C', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nTTS--', (222.2, 202.3, 133.1)), ('C', '1111', 'GLU', ' beta sheet', ' \nS---B', (223.3, 201.7, 127.1)), ('C', '1116', 'THR', 'check CA trace,carbonyls, peptide', ' \n---SS', (215.3, 205.8, 115.9)), ('C', '1117', 'THR', 'check CA trace,carbonyls, peptide', 'bend\n--SSS', (211.6, 206.9, 115.4)), ('C', '1127', 'ASP', ' alpha helix', 'turn\n-TTSS', (209.6, 225.7, 119.1)), ('C', '34', 'ARG', 'check CA trace', ' \n-S--E', (244.2, 197.5, 200.6)), ('C', '140', 'PHE', 'check CA trace', 'beta bridge\n--B--', (256.5, 195.3, 227.1)), ('C', '161', 'SER', 'check CA trace', ' \nB----', (249.8, 194.8, 233.6)), ('C', '220', 'PHE', 'check CA trace', ' \n-S--E', (245.6, 193.2, 196.3)), ('C', '544', 'ASN', 'check CA trace', 'bend\nESSS-', (210.7, 235.5, 210.0)), ('C', '549', 'THR', 'check CA trace', 'strand\n-EEEE', (217.4, 227.5, 200.3)), ('C', '569', 'ILE', 'check CA trace', 'bend\nE-STT', (204.3, 229.8, 189.3)), ('C', '812', 'PRO', 'check CA trace', 'bend\nT-SSS', (223.1, 169.7, 163.1)), ('C', '970', 'PHE', 'check CA trace', 'turn\n--TTS', (209.7, 199.4, 202.2)), ('C', '1092', 'GLU', 'check CA trace', 'bend\nESSSE', (211.5, 205.7, 127.7)), ('L', '27C', 'VAL', 'check CA trace,carbonyls, peptide', ' ', ('', '', '')), ('L', '77', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\nESS--', (184.8, 226.5, 263.1)), ('L', '50', 'ASP', 'check CA trace', 'bend\nESSTT', (186.8, 207.8, 252.3)), ('H', '54', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\nETTS-', (177.6, 185.3, 250.8))]
data['smoc'] = [('A', 27, u'ALA', 0.847816901733487, (174.36, 151.29399999999998, 201.70999999999998)), ('A', 41, u'LYS', 0.8181129026950213, (169.65, 185.495, 201.35200000000003)), ('A', 46, u'SER', 0.8750167628437773, (169.651, 187.07299999999998, 186.61399999999998)), ('A', 52, u'GLN', 0.9321294202887599, (182.20999999999998, 179.841, 200.008)), ('A', 55, u'PHE', 0.8892481593009244, (178.431, 172.567, 201.55800000000002)), ('A', 62, u'VAL', 0.8856717696806493, (175.45000000000002, 159.931, 200.592)), ('A', 80, u'ASP', 0.8211130883037097, (167.77899999999997, 150.51399999999998, 214.56)), ('A', 90, u'VAL', 0.8512428901368858, (174.761, 167.477, 207.698)), ('A', 92, u'PHE', 0.8558710002008814, (169.565, 164.936, 205.535)), ('A', 105, u'ILE', 0.8476105170113271, (168.57299999999998, 164.994, 218.814)), ('A', 128, u'ILE', 0.882970160690163, (162.811, 172.5, 220.20299999999997)), ('A', 131, u'CYS', 0.8729516489389797, (168.859, 170.461, 228.51299999999998)), ('A', 135, u'PHE', 0.8113116821249724, (166.569, 159.292, 227.035)), ('A', 140, u'PHE', 0.8472141149211672, (160.034, 156.722, 219.342)), ('A', 141, u'LEU', 0.8158335238429225, (156.946, 158.90800000000002, 219.681)), ('A', 166, u'CYS', 0.8115708144951596, (167.758, 173.732, 230.71399999999997)), ('A', 173, u'GLN', 0.793803532392371, (154.933, 174.889, 212.646)), ('A', 187, u'LYS', 0.8090725658629654, (155.668, 160.82000000000002, 197.54299999999998)), ('A', 192, u'PHE', 0.8833643611271927, (167.126, 169.28, 205.20499999999998)), ('A', 207, u'HIS', 0.8853125745345377, (159.697, 169.71899999999997, 200.26399999999998)), ('A', 210, u'ILE', 0.8524645123762136, (159.93800000000002, 162.312, 194.477)), ('A', 215, u'ASP', 0.8242027362077605, (167.48700000000002, 156.52100000000002, 195.221)), ('A', 219, u'GLY', 0.8913633770415794, (168.15200000000002, 166.71599999999998, 189.74599999999998)), ('A', 224, u'GLU', 0.8959226130125935, (165.32000000000002, 177.436, 201.45800000000003)), ('A', 228, u'ASP', 0.9037448745719834, (168.39200000000002, 180.316, 212.817)), ('A', 231, u'ILE', 0.8901496026122518, (172.68, 176.936, 220.92800000000003)), ('A', 262, u'ALA', 0.7978747647146378, (159.845, 150.38500000000002, 207.40800000000002)), ('A', 291, u'CYS', 0.8855864106726014, (184.475, 174.453, 191.972)), ('A', 295, u'PRO', 0.9119492648362711, (189.24099999999999, 170.589, 186.29399999999998)), ('A', 301, u'CYS', 0.9248512807850812, (184.657, 178.909, 188.341)), ('A', 534, u'VAL', 0.8715684610278347, (217.02700000000002, 165.0, 205.38600000000002)), ('A', 538, u'CYS', 0.8761270703765427, (210.80200000000002, 168.767, 199.732)), ('A', 569, u'ILE', 0.9098716823710427, (223.19899999999998, 186.369, 191.21899999999997)), ('A', 580, u'GLN', 0.8765896383883096, (225.92600000000002, 170.315, 212.916)), ('A', 583, u'GLU', 0.9051640188905458, (228.72899999999998, 169.842, 205.02100000000002)), ('A', 590, u'CYS', 0.8963210841119514, (210.292, 172.77499999999998, 195.365)), ('A', 600, u'PRO', 0.9224038873908562, (187.18, 171.323, 173.6)), ('A', 603, u'ASN', 0.9163339632169336, (179.042, 172.218, 174.696)), ('A', 640, u'SER', 0.8040650435190911, (195.941, 157.369, 183.989)), ('A', 641, u'ASN', 0.8724783084676452, (196.89000000000001, 158.467, 180.49200000000002)), ('A', 649, u'CYS', 0.9095533394686146, (203.446, 167.36200000000002, 182.134)), ('A', 653, u'ALA', 0.9220040561110102, (195.311, 164.177, 176.49800000000002)), ('A', 654, u'GLU', 0.913845190761473, (196.061, 161.177, 174.30800000000002)), ('A', 662, u'CYS', 0.869461177611403, (196.972, 173.667, 165.7)), ('A', 669, u'GLY', 0.9189836314467864, (205.315, 172.996, 168.98600000000002)), ('A', 671, u'CYS', 0.8854650497330705, (198.936, 171.41299999999998, 170.017)), ('A', 675, u'GLN', 0.908658742105623, (188.738, 164.298, 167.236)), ('A', 676, u'THR', 0.8127967862796167, (186.765, 161.118, 166.694)), ('A', 690, u'GLN', 0.8628783657167364, (186.399, 160.414, 170.431)), ('A', 699, u'LEU', 0.9258685083384898, (203.38000000000002, 173.567, 159.845)), ('A', 707, u'TYR', 0.8892123953125372, (212.359, 173.93, 140.032)), ('A', 714, u'ILE', 0.888454846006502, (202.33700000000002, 179.98200000000003, 133.835)), ('A', 720, u'ILE', 0.8929195910159505, (189.206, 186.21699999999998, 141.39800000000002)), ('A', 727, u'LEU', 0.9105213137945852, (189.99, 195.959, 161.788)), ('A', 731, u'MET', 0.9220933835499714, (186.762, 201.925, 171.70499999999998)), ('A', 734, u'THR', 0.9371098185150321, (184.122, 205.369, 178.44)), ('A', 738, u'CYS', 0.9068810402204035, (186.795, 210.208, 189.512)), ('A', 745, u'ASP', 0.9258908217089528, (178.64299999999997, 211.67899999999997, 197.46)), ('A', 748, u'GLU', 0.9219001393198044, (183.96, 214.064, 204.037)), ('A', 749, u'CYS', 0.9106361747185263, (185.71299999999997, 211.759, 201.593)), ('A', 760, u'CYS', 0.9020837967896339, (191.314, 213.131, 189.784)), ('A', 775, u'ASP', 0.9095971481411427, (185.93800000000002, 210.429, 167.304)), ('A', 784, u'GLN', 0.9027583804043505, (188.24899999999997, 210.742, 153.61899999999997)), ('A', 794, u'ILE', 0.8872031211017442, (170.181, 202.343, 137.01899999999998)), ('A', 827, u'THR', 0.8735781237665802, (176.961, 191.345, 170.571)), ('A', 828, u'LEU', 0.8101342029509608, (177.516, 193.894, 173.32000000000002)), ('A', 854, u'LYS', 0.7898184990150281, (174.777, 205.261, 185.04399999999998)), ('A', 855, u'PHE', 0.8783854649671335, (176.39200000000002, 203.122, 187.707)), ('A', 883, u'THR', 0.904176445675391, (181.692, 204.86200000000002, 139.64)), ('A', 891, u'GLY', 0.9094815596728923, (190.23, 214.781, 143.268)), ('A', 895, u'GLN', 0.9163017377708166, (182.65800000000002, 208.68200000000002, 135.95800000000003)), ('A', 913, u'GLN', 0.899362788283795, (193.161, 194.376, 129.01)), ('A', 924, u'ALA', 0.9206523976238302, (181.424, 188.757, 136.824)), ('A', 941, u'THR', 0.8660466030544893, (179.74399999999997, 181.86700000000002, 162.004)), ('A', 942, u'ALA', 0.8562988617979236, (180.315, 185.29899999999998, 163.51899999999998)), ('A', 972, u'ALA', 0.9036796935534628, (189.184, 199.112, 206.033)), ('A', 976, u'VAL', 0.9023405523064583, (180.562, 200.60299999999998, 202.023)), ('A', 985, u'ASP', 0.9145111735270018, (183.762, 209.756, 214.237)), ('A', 990, u'GLU', 0.9094172006334856, (189.538, 209.687, 208.222)), ('A', 1004, u'LEU', 0.9249669679508794, (191.48700000000002, 203.51899999999998, 189.168)), ('A', 1008, u'VAL', 0.9343961599832145, (193.38200000000003, 204.399, 183.38400000000001)), ('A', 1011, u'GLN', 0.9315221451554001, (193.05, 202.07899999999998, 178.93800000000002)), ('A', 1019, u'ARG', 0.9176598094488486, (194.809, 204.111, 167.444)), ('A', 1048, u'HIS', 0.8842791243587323, (194.971, 193.493, 144.595)), ('A', 1049, u'LEU', 0.8614881362995722, (192.112, 194.554, 142.312)), ('A', 1055, u'SER', 0.8784253453910509, (180.967, 199.43, 158.407)), ('A', 1126, u'CYS', 0.8929275080225868, (223.92000000000002, 185.665, 120.472)), ('A', 1138, u'TYR', 0.9167797273582325, (209.07299999999998, 186.637, 112.20100000000001)), ('A', 1144, u'GLU', 0.8326321592538697, (205.70399999999998, 193.353, 101.63)), ('A', 1302, u'NAG', 0.8426032546339791, (202.75, 172.407, 138.009)), ('A', 1303, u'NAG', 0.8730656595868859, (171.222, 192.583, 138.74399999999997)), ('A', 1304, u'NAG', 0.8966385154057606, (220.287, 176.864, 130.70399999999998)), ('A', 1305, u'NAG', 0.8362408910519996, (201.11299999999997, 154.431, 166.43200000000002)), ('A', 1306, u'NAG', 0.8919865681016427, (212.04299999999998, 166.206, 182.289)), ('A', 1307, u'NAG', 0.8222000694817256, (181.59, 173.546, 168.57)), ('A', 1308, u'NAG', 0.8702308318512975, (181.254, 156.232, 194.969)), ('A', 1309, u'NAG', 0.8657632194107708, (162.57, 181.875, 185.32200000000003)), ('B', 28, u'TYR', 0.870967330829262, (169.01399999999998, 247.52200000000002, 197.18800000000002)), ('B', 42, u'VAL', 0.8283655210893227, (201.79399999999998, 236.972, 198.39700000000002)), ('B', 50, u'SER', 0.916154752395113, (192.82000000000002, 230.905, 191.654)), ('B', 55, u'PHE', 0.8825805835112133, (184.192, 236.546, 199.01899999999998)), ('B', 64, u'TRP', 0.8557650907618868, (171.123, 250.0, 200.985)), ('B', 80, u'ASP', 0.8252499629596178, (167.18800000000002, 255.232, 213.062)), ('B', 90, u'VAL', 0.8628226402504946, (180.983, 241.85600000000002, 205.895)), ('B', 101, u'ILE', 0.8850790048632828, (179.651, 257.84400000000005, 208.309)), ('B', 104, u'TRP', 0.8769842732124772, (181.781, 251.011, 213.42100000000002)), ('B', 105, u'ILE', 0.8782737280775471, (181.06, 248.79299999999998, 216.403)), ('B', 135, u'PHE', 0.8165155515468405, (177.636, 251.925, 223.70999999999998)), ('B', 157, u'PHE', 0.7436742786085299, (179.914, 263.615, 221.67899999999997)), ('B', 158, u'ARG', 0.7939705854624155, (180.88500000000002, 260.04, 222.52100000000002)), ('B', 187, u'LYS', 0.8420769311370346, (181.677, 262.35900000000004, 195.06)), ('B', 215, u'ASP', 0.8483435895386743, (174.30100000000002, 253.281, 193.35000000000002)), ('B', 219, u'GLY', 0.8853303106780492, (183.605, 248.963, 187.64)), ('B', 222, u'ALA', 0.8974787964113362, (190.495, 245.425, 194.68200000000002)), ('B', 231, u'ILE', 0.875720790396403, (190.32800000000003, 239.975, 218.755)), ('B', 235, u'ILE', 0.8358350141700976, (181.86100000000002, 238.516, 216.777)), ('B', 262, u'ALA', 0.79445632824056, (172.42800000000003, 263.29599999999994, 205.005)), ('B', 263, u'ALA', 0.8174217415269268, (174.33200000000002, 260.22799999999995, 203.80700000000002)), ('B', 287, u'ASP', 0.8946346649788023, (190.21899999999997, 241.36100000000002, 186.95700000000002)), ('B', 291, u'CYS', 0.871308720185589, (183.61499999999998, 230.36200000000002, 189.374)), ('B', 295, u'PRO', 0.9018918689886082, (178.265, 228.30200000000002, 183.42700000000002)), ('B', 311, u'GLY', 0.9233676093637097, (184.23999999999998, 224.44899999999998, 171.623)), ('B', 315, u'THR', 0.9233262202175166, (183.123, 221.756, 183.506)), ('B', 318, u'PHE', 0.9240255450721525, (175.727, 217.48100000000002, 188.285)), ('B', 336, u'CYS', 0.89907142541337, (166.761, 196.46200000000002, 226.531)), ('B', 340, u'GLU', 0.9052942545612322, (169.565, 194.71899999999997, 234.617)), ('B', 357, u'ARG', 0.8754214369108725, (172.026, 187.20299999999997, 224.178)), ('B', 379, u'CYS', 0.8883796838735668, (184.843, 201.127, 221.58700000000002)), ('B', 387, u'LEU', 0.9036678256063498, (176.411, 204.054, 218.36700000000002)), ('B', 391, u'CYS', 0.8691984353111898, (170.474, 198.781, 214.491)), ('B', 402, u'ILE', 0.9111889613226393, (189.534, 191.306, 236.647)), ('B', 405, u'ASP', 0.9002260443103763, (195.497, 196.642, 235.261)), ('B', 410, u'ILE', 0.8947004191142148, (190.629, 193.171, 227.319)), ('B', 413, u'GLY', 0.910474020095605, (194.996, 191.423, 219.82600000000002)), ('B', 414, u'GLN', 0.9149206485295174, (196.35800000000003, 191.762, 223.33700000000002)), ('B', 420, u'ASP', 0.8877004666556972, (195.668, 184.12800000000001, 226.655)), ('B', 449, u'TYR', 0.8879094455619733, (188.508, 184.42600000000002, 246.89700000000002)), ('B', 458, u'LYS', 0.8746663237486468, (198.094, 174.14499999999998, 227.33200000000002)), ('B', 462, u'LYS', 0.89709468806871, (190.08100000000002, 180.576, 220.812)), ('B', 471, u'GLU', 0.8608501336570601, (191.98800000000003, 169.377, 235.22)), ('B', 475, u'ALA', 0.8295620119095543, (203.783, 169.035, 233.936)), ('B', 486, u'PHE', 0.8185289640632369, (206.42700000000002, 169.342, 240.024)), ('B', 500, u'THR', 0.8725956598007429, (194.424, 197.41899999999998, 251.11899999999997)), ('B', 511, u'VAL', 0.8707802684108894, (181.14399999999998, 194.345, 230.71299999999997)), ('B', 517, u'LEU', 0.8519003701671376, (175.55200000000002, 192.907, 211.417)), ('B', 518, u'LEU', 0.8443896300486917, (174.39200000000002, 189.796, 209.58700000000002)), ('B', 519, u'HIS', 0.8007748639721567, (171.823, 189.347, 206.819)), ('B', 525, u'CYS', 0.8764237000143309, (168.118, 199.414, 217.48200000000003)), ('B', 528, u'LYS', 0.90961935768613, (165.423, 207.066, 216.784)), ('B', 532, u'ASN', 0.8626056803993583, (156.58, 207.995, 206.40800000000002)), ('B', 533, u'LEU', 0.8718329869134964, (158.24899999999997, 206.696, 203.23399999999998)), ('B', 538, u'CYS', 0.8888284985249076, (165.512, 211.71899999999997, 195.692)), ('B', 555, u'SER', 0.8939488057491581, (159.484, 196.784, 193.02700000000002)), ('B', 560, u'LEU', 0.9071166376333865, (161.54899999999998, 185.406, 199.42000000000002)), ('B', 562, u'PHE', 0.8830815019086383, (164.08, 185.737, 204.48100000000002)), ('B', 569, u'ILE', 0.8903144529604274, (175.411, 192.8, 189.88000000000002)), ('B', 580, u'GLN', 0.9086149116148524, (157.27299999999997, 198.289, 208.96200000000002)), ('B', 583, u'GLU', 0.9087261363679231, (157.237, 195.518, 201.319)), ('B', 598, u'ILE', 0.9163344819208707, (178.804, 224.712, 174.772)), ('B', 603, u'ASN', 0.9226399585692245, (186.23499999999999, 236.20899999999997, 171.52700000000002)), ('B', 607, u'GLN', 0.9250353228459008, (176.24499999999998, 233.569, 174.939)), ('B', 617, u'CYS', 0.8912580837475488, (165.015, 217.023, 180.54299999999998)), ('B', 641, u'ASN', 0.8697304277272747, (164.806, 227.164, 175.692)), ('B', 646, u'ARG', 0.9069871675180201, (170.48100000000002, 211.07, 172.526)), ('B', 662, u'CYS', 0.8818529063545957, (180.11499999999998, 220.412, 162.17899999999997)), ('B', 666, u'ILE', 0.9215373949376844, (178.092, 217.646, 170.77299999999997)), ('B', 671, u'CYS', 0.9028438543149956, (176.634, 219.65, 166.28)), ('B', 676, u'THR', 0.8359756382311941, (172.37, 234.941, 162.708)), ('B', 702, u'GLU', 0.9229560005923455, (175.37800000000001, 215.08200000000002, 148.121)), ('B', 714, u'ILE', 0.875269983110942, (188.594, 212.903, 131.39800000000002)), ('B', 720, u'ILE', 0.875906337791886, (199.349, 221.455, 140.53)), ('B', 738, u'CYS', 0.9082025341793375, (214.539, 211.41899999999998, 191.54899999999998)), ('B', 765, u'ARG', 0.9224286614658325, (216.73, 204.853, 183.6)), ('B', 775, u'ASP', 0.9045551227726105, (217.9, 211.923, 169.58200000000002)), ('B', 794, u'ILE', 0.8891899659125301, (222.35200000000003, 230.18, 139.93)), ('B', 806, u'LEU', 0.9040099827461662, (216.05800000000002, 227.083, 150.254)), ('B', 827, u'THR', 0.8775094498904645, (205.721, 229.667, 170.905)), ('B', 828, u'LEU', 0.8123628497464485, (206.501, 228.159, 174.297)), ('B', 855, u'PHE', 0.8746891530911536, (213.091, 224.506, 188.798)), ('B', 869, u'MET', 0.9147326560441231, (222.191, 221.60899999999998, 162.11899999999997)), ('B', 882, u'ILE', 0.9030772591474393, (216.271, 219.594, 143.47299999999998)), ('B', 901, u'GLN', 0.8585059860610946, (212.948, 215.547, 136.883)), ('B', 911, u'VAL', 0.9029767902312108, (201.162, 211.55, 132.164)), ('B', 913, u'GLN', 0.8935411667425249, (205.978, 213.98000000000002, 129.657)), ('B', 918, u'GLU', 0.8923456820400973, (204.44299999999998, 221.948, 126.41900000000001)), ('B', 938, u'LEU', 0.8967596067766467, (201.14499999999998, 229.559, 157.61299999999997)), ('B', 941, u'THR', 0.8601187283185916, (196.453, 230.39200000000002, 160.36200000000002)), ('B', 955, u'ASN', 0.9066814511832326, (204.757, 217.93200000000002, 177.985)), ('B', 965, u'GLN', 0.9266764712724207, (201.84, 217.82500000000002, 193.314)), ('B', 977, u'LEU', 0.9136528190856832, (209.107, 218.349, 204.691)), ('B', 995, u'ARG', 0.9224496524151504, (203.489, 208.93200000000002, 203.844)), ('B', 1017, u'GLU', 0.9327286605290986, (203.267, 207.608, 170.529)), ('B', 1019, u'ARG', 0.9213345206529802, (208.093, 207.38100000000003, 168.286)), ('B', 1027, u'THR', 0.9153182057414022, (208.74099999999999, 206.659, 156.11899999999997)), ('B', 1049, u'LEU', 0.8793707135069289, (204.97, 214.508, 142.38500000000002)), ('B', 1052, u'PHE', 0.8855568142263813, (210.038, 219.121, 150.189)), ('B', 1078, u'ALA', 0.8855308345671976, (183.95600000000002, 202.07, 123.929)), ('B', 1080, u'ALA', 0.9025194336001842, (187.346, 198.17499999999998, 122.17099999999999)), ('B', 1094, u'VAL', 0.8756825000431848, (191.192, 204.848, 126.44600000000001)), ('B', 1135, u'ASN', 0.8965803643342909, (185.73399999999998, 202.42800000000003, 113.13499999999999)), ('B', 1144, u'GLU', 0.799889523643856, (204.21899999999997, 203.578, 99.80499999999999)), ('B', 1301, u'NAG', 0.7958788967362992, (167.303, 240.756, 193.23999999999998)), ('B', 1302, u'NAG', 0.8495492174911731, (200.841, 247.135, 183.914)), ('B', 1303, u'NAG', 0.8627510384253225, (188.736, 234.864, 165.11299999999997)), ('B', 1304, u'NAG', 0.8581265773140618, (161.618, 225.494, 162.586)), ('B', 1305, u'NAG', 0.8387122578887802, (172.41299999999998, 204.11899999999997, 129.52)), ('B', 1307, u'NAG', 0.8504783122653219, (181.48700000000002, 217.696, 133.524)), ('B', 1308, u'NAG', 0.8400473041368648, (177.82200000000003, 198.05, 115.979)), ('B', 1310, u'NAG', 0.7736435336293528, (155.839, 202.05, 211.939)), ('B', 1311, u'NAG', 0.9017587317322753, (173.469, 200.692, 233.907)), ('C', 27, u'ALA', 0.8527195524347125, (255.05800000000002, 210.035, 208.653)), ('C', 46, u'SER', 0.8837471849171363, (231.758, 184.38600000000002, 189.448)), ('C', 50, u'SER', 0.9092680467260696, (228.142, 196.029, 195.6)), ('C', 67, u'ALA', 0.8310276591905171, (259.57599999999996, 200.16, 216.21499999999997)), ('C', 81, u'ASN', 0.856295614784414, (253.046, 203.26899999999998, 221.377)), ('C', 101, u'ILE', 0.8940410686169714, (253.605, 193.64299999999997, 217.79899999999998)), ('C', 104, u'TRP', 0.8773396458807845, (246.227, 195.923, 221.68800000000002)), ('C', 105, u'ILE', 0.8692141539471882, (244.11599999999999, 197.98000000000002, 224.08)), ('C', 128, u'ILE', 0.8836847981939954, (241.062, 188.516, 225.086)), ('C', 164, u'ASN', 0.8250446251263044, (241.722, 195.79299999999998, 237.261)), ('C', 166, u'CYS', 0.8312848405905371, (237.36700000000002, 191.73299999999998, 234.561)), ('C', 173, u'GLN', 0.8024571618500212, (244.88700000000003, 179.848, 219.242)), ('C', 174, u'PRO', 0.8318680999012519, (246.934, 182.889, 218.14)), ('C', 187, u'LYS', 0.8248965410089559, (259.79699999999997, 190.48600000000002, 206.284)), ('C', 215, u'ASP', 0.8250264565439294, (257.14200000000005, 199.903, 202.30800000000002)), ('C', 219, u'GLY', 0.8622514080644494, (248.98600000000002, 194.417, 195.157)), ('C', 231, u'ILE', 0.8826095467492353, (230.52100000000002, 193.74299999999997, 224.07399999999998)), ('C', 235, u'ILE', 0.8245395808073119, (235.137, 202.312, 222.459)), ('C', 291, u'CYS', 0.8772565202562507, (233.131, 203.653, 194.11399999999998)), ('C', 295, u'PRO', 0.9027585156946163, (234.63899999999998, 209.375, 188.554)), ('C', 305, u'SER', 0.9136786864197224, (231.232, 196.196, 185.77499999999998)), ('C', 533, u'LEU', 0.841656575513432, (222.11899999999997, 239.38600000000002, 205.493)), ('C', 534, u'VAL', 0.8318737002420572, (224.05, 237.59, 202.738)), ('C', 538, u'CYS', 0.8738568809276794, (223.88800000000003, 229.636, 198.141)), ('C', 544, u'ASN', 0.8986997949635771, (210.71699999999998, 235.525, 209.983)), ('C', 545, u'GLY', 0.9061083891896691, (209.063, 232.73399999999998, 208.054)), ('C', 548, u'GLY', 0.9046728924731611, (214.10399999999998, 228.154, 202.032)), ('C', 557, u'LYS', 0.8741229780215722, (211.065, 243.289, 190.504)), ('C', 569, u'ILE', 0.8905492991430649, (204.349, 229.798, 189.265)), ('C', 580, u'GLN', 0.8477396779021011, (213.83700000000002, 245.036, 208.405)), ('C', 587, u'ILE', 0.9053703161635147, (215.803, 233.789, 194.777)), ('C', 592, u'PHE', 0.9016882136739879, (222.23, 221.792, 190.73399999999998)), ('C', 598, u'ILE', 0.9110844966119791, (232.647, 210.417, 179.04899999999998)), ('C', 603, u'ASN', 0.8789247297812463, (239.534, 198.455, 177.07399999999998)), ('C', 617, u'CYS', 0.885471661743378, (232.347, 226.17499999999998, 185.242)), ('C', 641, u'ASN', 0.8797945358992845, (241.598, 221.798, 181.18800000000002)), ('C', 653, u'ALA', 0.8866195874229675, (238.499, 217.016, 177.542)), ('C', 662, u'CYS', 0.8689993781354747, (230.42200000000003, 211.82200000000003, 166.541)), ('C', 671, u'CYS', 0.895888640717884, (230.74399999999997, 215.35500000000002, 170.349)), ('C', 676, u'THR', 0.8264046397784167, (246.44899999999998, 210.754, 169.44)), ('C', 702, u'GLU', 0.9447904196101471, (229.899, 218.85800000000003, 151.83)), ('C', 705, u'VAL', 0.922260917907234, (226.85000000000002, 218.572, 143.18200000000002)), ('C', 707, u'TYR', 0.8741125404206477, (223.759, 221.029, 138.696)), ('C', 714, u'ILE', 0.849492028218071, (224.033, 208.512, 134.21499999999997)), ('C', 720, u'ILE', 0.8466377099385952, (224.64399999999998, 194.737, 143.88700000000003)), ('C', 738, u'CYS', 0.8843099320314802, (201.34, 186.57399999999998, 192.407)), ('C', 751, u'ASN', 0.9306870175469791, (194.708, 185.632, 204.231)), ('C', 759, u'PHE', 0.9001110527254524, (194.555, 192.5, 191.712)), ('C', 760, u'CYS', 0.9049972339996887, (196.12800000000001, 189.09, 191.201)), ('C', 765, u'ARG', 0.9161130560009592, (195.28, 188.504, 182.947)), ('C', 779, u'GLN', 0.9279261777688368, (202.666, 183.478, 163.46)), ('C', 784, u'GLN', 0.8889923423115557, (202.71299999999997, 183.94899999999998, 155.42800000000003)), ('C', 794, u'ILE', 0.8811138586198033, (220.281, 170.41299999999998, 142.455)), ('C', 797, u'PHE', 0.8931136379447812, (220.816, 178.781, 140.40800000000002)), ('C', 809, u'PRO', 0.8860363236142307, (221.955, 169.548, 154.687)), ('C', 814, u'LYS', 0.8451289930522242, (217.412, 172.80200000000002, 160.64499999999998)), ('C', 827, u'THR', 0.8621947090648663, (223.21499999999997, 184.966, 174.683)), ('C', 828, u'LEU', 0.7758880147360505, (221.73399999999998, 185.845, 178.063)), ('C', 854, u'LYS', 0.7875278698542442, (214.42700000000002, 178.28, 188.569)), ('C', 855, u'PHE', 0.8963984143349062, (213.032, 181.29399999999998, 190.44)), ('C', 869, u'MET', 0.9068309068819996, (210.069, 175.048, 163.242)), ('C', 876, u'ALA', 0.8990390660189496, (210.166, 177.441, 153.148)), ('C', 882, u'ILE', 0.910113559380034, (214.58100000000002, 181.107, 145.42100000000002)), ('C', 891, u'GLY', 0.8673492650030935, (199.071, 181.96800000000002, 144.907)), ('C', 895, u'GLN', 0.8931206739001543, (208.67, 177.63899999999998, 139.339)), ('C', 901, u'GLN', 0.8289772364894124, (213.35600000000002, 185.955, 138.17)), ('C', 904, u'TYR', 0.8340909005996248, (212.064, 190.474, 136.0)), ('C', 913, u'GLN', 0.8671126846360844, (216.494, 192.89100000000002, 131.394)), ('C', 935, u'GLN', 0.9130655942566328, (228.74899999999997, 186.555, 156.847)), ('C', 955, u'ASN', 0.9056209608868724, (213.728, 192.177, 179.695)), ('C', 965, u'GLN', 0.911103676437063, (212.73399999999998, 194.38400000000001, 194.945)), ('C', 969, u'ASN', 0.9133804961763854, (211.88800000000003, 196.529, 203.424)), ('C', 972, u'ALA', 0.9086831941941439, (208.82700000000003, 197.342, 207.16299999999998)), ('C', 977, u'LEU', 0.8920172904621609, (208.03, 187.697, 205.91899999999998)), ('C', 997, u'ILE', 0.902740940924313, (202.284, 193.61899999999997, 200.755)), ('C', 1008, u'VAL', 0.9116572575820704, (203.45000000000002, 194.646, 184.561)), ('C', 1014, u'ARG', 0.9135119187886201, (207.444, 197.101, 175.85500000000002)), ('C', 1017, u'GLU', 0.9178601367936612, (206.411, 198.54899999999998, 171.202)), ('C', 1019, u'ARG', 0.8904460963614498, (203.88500000000002, 194.61299999999997, 168.61299999999997)), ('C', 1049, u'LEU', 0.8540573971641244, (215.791, 193.51399999999998, 144.10999999999999)), ('C', 1050, u'MET', 0.842828147792212, (214.69899999999998, 190.895, 146.653)), ('C', 1052, u'PHE', 0.8711999060574023, (215.823, 186.86700000000002, 152.126)), ('C', 1053, u'PRO', 0.8598344680253722, (214.584, 186.258, 155.68200000000002)), ('C', 1055, u'SER', 0.870771247937765, (215.383, 183.537, 161.678)), ('C', 1073, u'LYS', 0.8781817117532623, (229.701, 209.76899999999998, 133.797)), ('C', 1080, u'ALA', 0.8837849572633165, (213.412, 216.798, 123.099)), ('C', 1081, u'ILE', 0.8928422653948169, (214.771, 216.576, 119.57)), ('C', 1105, u'THR', 0.8706612677720555, (219.625, 205.68, 127.12199999999999)), ('C', 1126, u'CYS', 0.8930783182918511, (209.06, 222.28, 117.426)), ('C', 1135, u'ASN', 0.9105499476788369, (219.38600000000002, 216.089, 115.611)), ('C', 1144, u'GLU', 0.7913698976888545, (212.311, 201.003, 101.349)), ('C', 1302, u'NAG', 0.8443897352862912, (239.436, 180.583, 190.39200000000002)), ('C', 1304, u'NAG', 0.8503818353589102, (230.48800000000003, 233.92200000000003, 185.737)), ('C', 1305, u'NAG', 0.8607590308859018, (244.268, 225.11299999999997, 167.89800000000002)), ('C', 1309, u'NAG', 0.8828880169588649, (218.85200000000003, 225.036, 118.15899999999999)), ('C', 1310, u'NAG', 0.8054849934478474, (248.835, 209.80200000000002, 200.282)), ('L', 2, u'SER', 0.8255780065169429, (197.14899999999997, 198.92200000000003, 266.96799999999996)), ('L', 8, u'PRO', 0.8485872137092632, (197.85800000000003, 211.67499999999998, 269.203)), ('L', 29, u'ALA', 0.8250972187727692, (197.142, 202.548, 249.409)), ('L', 58, u'VAL', 0.8314413075286288, (176.62800000000001, 214.993, 257.28599999999994)), ('L', 81, u'GLU', 0.8244894321653462, (180.134, 219.942, 270.952)), ('L', 84, u'ALA', 0.8404560808010398, (184.74699999999999, 213.815, 272.11)), ('L', 85, u'ASP', 0.8520298857988232, (186.975, 210.88500000000002, 271.277)), ('L', 96, u'THR', 0.8742170086645092, (190.039, 195.912, 260.161)), ('L', 106, u'VAL', 0.8354416419464781, (187.99800000000002, 222.536, 272.524)), ('H', 26, u'GLY', 0.8181687170499891, (165.916, 197.90800000000002, 257.558)), ('H', 33, u'GLY', 0.8768751538072042, (178.324, 193.78, 249.26899999999998)), ('H', 55, u'ASP', 0.8327030978061382, (178.075, 183.164, 253.978)), ('H', 62, u'SER', 0.8662736058958778, (194.727, 187.072, 267.21099999999996)), ('H', 71, u'LYS', 0.8562996671728915, (173.696, 184.161, 261.26)), ('H', 72, u'ASP', 0.8684943152437842, (170.108, 183.405, 260.33599999999996)), ('H', 73, u'THR', 0.8703648767726756, (168.88100000000003, 185.629, 257.517)), ('H', 101, u'ASP', 0.865394841133786, (178.389, 202.90800000000002, 258.658)), ('H', 112, u'SER', 0.802985124464392, (183.255, 187.369, 286.601)), ('H', 113, u'SER', 0.709639579418708, (181.166, 185.364, 289.082))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-23507/7lss/Model_validation_1/validation_cootdata/molprobity_probe7lss_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)
