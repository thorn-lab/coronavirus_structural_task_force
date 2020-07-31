
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
data['smoc'] = []
data['jpred'] = []
data['probe'] = [(' C1072  GLU  N  ', ' C1072  GLU  OE1', -0.855, (203.344, 236.993, 292.026)), (' A 804  GLN  OE1', ' A1310  NAG  O6 ', -0.846, (230.807, 256.543, 280.405)), (' G  29  PHE  O  ', ' G  72  ARG  NH2', -0.839, (205.528, 260.086, 203.559)), (' A 804  GLN  NE2', ' A 935  GLN  OE1', -0.822, (230.772, 253.828, 276.661)), (' A 385  THR  HG1', ' H 106  TYR  HH ', -0.799, (256.952, 214.04, 194.352)), (' C 811  LYS  NZ ', ' C 820  ASP  OD2', -0.783, (192.873, 206.49, 268.43)), (' D  29  PHE  O  ', ' D  72  ARG  NH2', -0.779, (203.457, 193.789, 199.306)), (' D  33  ASP  OD1', ' D  53  TYR  N  ', -0.777, (197.712, 197.484, 197.405)), (' B 328  ARG  NH2', ' B 580  GLN  OE1', -0.773, (186.13, 196.734, 220.588)), (' A 912  THR  OG1', ' A1106  GLN  OE1', -0.771, (231.87, 229.999, 299.507)), (' A 328  ARG  NH2', ' A 580  GLN  OE1', -0.76, (265.253, 205.414, 220.284)), (' B 386  LYS  NZ ', ' D 103  LEU  O  ', -0.76, (199.532, 206.915, 195.25)), (' C 804  GLN  NE2', ' C 935  GLN  OE1', -0.759, (192.565, 212.978, 275.975)), (' A 393  THR  OG1', ' A 516  GLU  O  ', -0.758, (247.164, 196.272, 199.4)), (' L  12  SER  OG ', ' L 106  GLU  OE2', -0.747, (234.363, 233.348, 167.925)), (' C 309  GLU  N  ', ' C 309  GLU  OE1', -0.743, (194.647, 231.605, 252.484)), (' A 385  THR  OG1', ' H 106  TYR  OH ', -0.742, (257.405, 213.302, 194.949)), (' C 557  LYS  NZ ', ' C 574  ASP  OD2', -0.74, (225.177, 259.574, 239.604)), (' H  29  PHE  O  ', ' H  72  ARG  NH2', -0.74, (260.113, 223.534, 200.827)), (' A 618  THR  OG1', ' A 619  GLU  OE1', -0.73, (262.479, 222.716, 239.352)), (' C 618  THR  OG1', ' C 619  GLU  OE1', -0.722, (204.949, 258.327, 240.521)), (' C 709  ASN  ND2', ' C1308  NAG  O7 ', -0.709, (220.15, 251.101, 297.883)), (' C 335  LEU HD11', ' C 364  ASP  HB2', -0.708, (224.419, 273.849, 207.848)), (' D   6  GLU  N  ', ' D   6  GLU  OE1', -0.699, (212.108, 188.889, 188.577)), (' F  12  SER  OG ', ' F 106  GLU  OE2', -0.695, (220.97, 211.958, 164.642)), (' B 393  THR  OG1', ' B 516  GLU  O  ', -0.694, (185.68, 217.882, 200.475)), (' I  12  SER  OG ', ' I 106  GLU  OE2', -0.691, (207.711, 237.339, 168.211)), (' B 802  PHE  HD2', ' B 805  ILE HD11', -0.689, (244.292, 208.285, 280.616)), (' G   6  GLU  N  ', ' G   6  GLU  OE1', -0.688, (195.903, 256.13, 193.315)), (' B 317  ASN  ND2', ' C 737  ASP  OD2', -0.684, (216.077, 202.526, 236.701)), (' A 498  GLN  N  ', ' A 501  ASN  OD1', -0.681, (274.999, 190.53, 171.916)), (' C 804  GLN  OE1', ' C1311  NAG  O6 ', -0.679, (190.887, 212.086, 279.109)), (' C 385  THR  HG1', ' G 106  TYR  HH ', -0.677, (215.742, 262.936, 197.143)), (' A 359  SER  OG ', ' A 394  ASN  OD1', -0.675, (251.969, 191.72, 200.972)), (' A 287  ASP  OD1', ' A 288  ALA  N  ', -0.662, (248.152, 254.659, 241.853)), (' A 869  MET  SD ', ' C 697  MET  HE3', -0.661, (208.843, 246.659, 263.934)), (' H 167  LEU HD21', ' H 190  VAL HG21', -0.66, (247.586, 257.232, 165.034)), (' A 281  GLU  N  ', ' A 281  GLU  OE1', -0.659, (237.369, 261.62, 245.817)), (' B 398  ASP  OD2', ' B 423  TYR  OH ', -0.658, (178.459, 213.897, 188.238)), (' B 498  GLN  N  ', ' B 501  ASN  OD1', -0.652, (165.626, 198.735, 172.803)), (' C 385  THR  OG1', ' G 106  TYR  OH ', -0.65, (215.921, 263.829, 197.432)), (' A1094  VAL HG11', ' B 904  TYR  OH ', -0.647, (239.546, 219.824, 297.063)), (' B 557  LYS  NZ ', ' B 574  ASP  OD2', -0.647, (191.501, 208.57, 237.695)), (' C 532  ASN  OD1', ' C 533  LEU  N  ', -0.646, (213.409, 269.308, 226.054)), (' A1074  ASN  OD1', ' A1312  NAG  N2 ', -0.645, (252.042, 227.015, 293.653)), (' B 359  SER  OG ', ' B 394  ASN  OD1', -0.643, (179.742, 215.906, 202.287)), (' L  36  TYR  HE1', ' L  46  LEU HD13', -0.642, (245.201, 223.259, 188.983)), (' A  33  THR  OG1', ' A 219  GLY  O  ', -0.637, (255.019, 259.568, 239.158)), (' F 166  GLU  N  ', ' F 166  GLU  OE1', -0.63, (221.507, 198.355, 166.655)), (' B1053  PRO  O  ', ' B1054  GLN  NE2', -0.627, (243.392, 211.188, 273.709)), (' I 166  GLU  N  ', ' I 166  GLU  OE1', -0.627, (196.686, 244.183, 171.511)), (' A 189  LEU  HB2', ' A 210  ILE HD13', -0.627, (258.888, 270.017, 233.532)), (' B 412  PRO  O  ', ' F  27  GLN  NE2', -0.625, (189.564, 213.69, 179.131)), (' C 619  GLU  N  ', ' C 619  GLU  OE1', -0.624, (204.036, 257.37, 240.225)), (' A 904  TYR  OH ', ' C1094  VAL HG11', -0.623, (216.911, 236.198, 296.737)), (' C 318  PHE  HE2', ' C 615  VAL HG11', -0.621, (206.018, 250.324, 241.485)), (' I   1  ASP  OD1', ' I   2  ILE  N  ', -0.618, (220.346, 262.146, 179.492)), (' A 619  GLU  N  ', ' A 619  GLU  OE1', -0.618, (261.881, 224.086, 238.899)), (' A 557  LYS  NZ ', ' A 574  ASP  OD2', -0.616, (252.693, 203.816, 237.652)), (' B 618  THR  OG1', ' B 619  GLU  OE1', -0.614, (203.022, 190.421, 238.835)), (' I 187  TYR  O  ', ' I 193  TYR  OH ', -0.612, (188.359, 257.495, 145.375)), (' B 357  ARG  NH1', ' B 359  SER  OG ', -0.611, (178.185, 216.393, 202.401)), (' D 167  LEU HD21', ' D 190  VAL HG21', -0.607, (235.737, 188.477, 161.07)), (' B 816  SER  OG ', ' B 819  GLU  OE1', -0.604, (247.563, 208.733, 271.821)), (' B 619  GLU  N  ', ' B 619  GLU  OE1', -0.603, (204.65, 190.453, 238.583)), (' A  81  ASN  O  ', ' A 239  GLN  NE2', -0.601, (264.785, 263.675, 212.564)), (' C1053  PRO  O  ', ' C1054  GLN  NE2', -0.596, (203.882, 211.28, 273.656)), (' F  88  CYS  O  ', ' F 100  GLY  N  ', -0.596, (205.043, 208.023, 176.936)), (' L 166  GLU  N  ', ' L 166  GLU  OE1', -0.596, (246.214, 240.719, 170.189)), (' C 331  ASN  OD1', ' C1304  NAG  N2 ', -0.59, (224.654, 274.824, 221.907)), (' H  89  GLU  N  ', ' H  89  GLU  OE1', -0.589, (265.804, 225.032, 172.22)), (' B 118  LEU HD11', ' B 120  VAL  CG2', -0.588, (247.705, 174.508, 207.981)), (' G  33  ASP  OD1', ' G  53  TYR  N  ', -0.587, (210.955, 262.779, 202.008)), (' B 697  MET  HE3', ' C 869  MET  SD ', -0.586, (210.803, 198.76, 262.934)), (' H   6  GLU  N  ', ' H   6  GLU  OE1', -0.585, (259.425, 234.666, 190.988)), (' A 802  PHE  HD2', ' A 805  ILE HD11', -0.581, (225.441, 247.273, 281.57)), (' H  87  ARG  N  ', ' H  90  ASP  OD2', -0.581, (269.208, 225.558, 176.398)), (' B 563  GLN  O  ', ' B 577  ARG  NH2', -0.58, (182.86, 210.49, 227.139)), (' L   3  GLN  N  ', ' L   3  GLN  OE1', -0.579, (249.568, 211.66, 174.111)), (' B 422  ASN  OD1', ' B 454  ARG  N  ', -0.576, (170.388, 215.631, 176.732)), (' C 591  SER  OG ', ' C 615  VAL HG12', -0.575, (208.455, 251.333, 241.696)), (' B1094  VAL HG11', ' C 904  TYR  OH ', -0.575, (213.98, 209.324, 296.754)), (' A 401  VAL HG21', ' A 451  TYR  CE1', -0.573, (267.285, 189.054, 181.932)), (' L  89  GLN  NE2', ' L  90  GLN  O  ', -0.571, (248.758, 216.354, 184.798)), (' G 105  VAL HG11', ' I  91  SER  O  ', -0.57, (220.929, 257.045, 190.938)), (' B 294  ASP  N  ', ' B 294  ASP  OD1', -0.567, (225.735, 185.26, 239.082)), (' B 287  ASP  OD1', ' B 288  ALA  N  ', -0.567, (237.857, 186.16, 239.353)), (' G 167  LEU HD21', ' G 190  VAL HG21', -0.567, (179.496, 238.346, 166.495)), (' A 128  ILE HD13', ' A 229  LEU HD11', -0.566, (245.556, 267.434, 215.171)), (' I  36  TYR  HE1', ' I  46  LEU HD13', -0.566, (213.072, 248.844, 190.08)), (' A  29  THR  OG1', ' A 215  ASP  OD2', -0.563, (265.791, 259.858, 234.179)), (' G 105  VAL HG12', ' G 106  TYR  H  ', -0.562, (218.682, 257.938, 192.568)), (' C 354  ASN  OD1', ' C 355  ARG  N  ', -0.561, (238.488, 277.516, 194.403)), (' L 187  TYR  O  ', ' L 193  TYR  OH ', -0.559, (258.908, 242.213, 142.523)), (' B 567  ARG  NH1', ' B 571  ASP  O  ', -0.558, (197.549, 214.261, 230.658)), (' B 350  VAL HG21', ' B 418  ILE HG23', -0.557, (174.332, 212.512, 178.988)), (' C 726  ILE HG12', ' C1061  VAL HG22', -0.557, (204.35, 218.61, 267.169)), (' A 401  VAL HG21', ' A 451  TYR  HE1', -0.556, (267.302, 188.267, 182.202)), (' H 124  THR HG22', ' H 155  PRO  HD3', -0.556, (269.946, 242.46, 173.323)), (' A 563  GLN  NE2', ' B  42  VAL  O  ', -0.555, (248.884, 195.077, 231.228)), (' C 310  LYS  NZ ', ' C 663  ASP  OD2', -0.555, (195.442, 239.146, 261.549)), (' C 498  GLN  N  ', ' C 501  ASN  OD1', -0.552, (228.393, 289.266, 176.139)), (' A 328  ARG  NH1', ' A 578  ASP  OD2', -0.552, (263.845, 204.856, 223.601)), (' A 118  LEU HD11', ' A 120  VAL  CG2', -0.552, (254.313, 271.022, 211.136)), (' D  83  MET  HB3', ' D  86  LEU HD21', -0.552, (199.384, 184.828, 180.136)), (' B 331  ASN  OD1', ' B1304  NAG  N2 ', -0.548, (179.345, 200.428, 218.867)), (' G  83  MET  HB3', ' G  86  LEU HD21', -0.547, (198.679, 269.539, 185.231)), (' B 310  LYS  NZ ', ' B 663  ASP  OD2', -0.545, (223.654, 190.64, 260.261)), (' C 122  ASN  O  ', ' C 124  THR  N  ', -0.544, (160.651, 220.225, 215.701)), (' I  88  CYS  O  ', ' I 100  GLY  N  ', -0.54, (215.212, 252.134, 180.357)), (' C  33  THR  OG1', ' C 219  GLY  O  ', -0.539, (177.068, 232.894, 238.011)), (' I 106  GLU  OE1', ' I 174  TYR  OH ', -0.538, (203.947, 238.95, 169.751)), (' B1304  NAG  O3 ', ' B1304  NAG  O7 ', -0.536, (176.875, 200.129, 220.673)), (' A 726  ILE HG12', ' A1061  VAL HG22', -0.536, (229.832, 241.446, 267.847)), (' A 224  GLU  N  ', ' A 224  GLU  OE1', -0.535, (244.902, 265.161, 231.277)), (' F  37  GLN  HB2', ' F  47  LEU HD11', -0.535, (215.645, 208.916, 181.754)), (' A 402  ILE HD11', ' A 510  VAL HG21', -0.533, (261.745, 196.025, 180.59)), (' D   2  VAL HG13', ' D  27  PHE  CD2', -0.531, (211.422, 195.858, 197.915)), (' A 890  ALA  O  ', ' C1045  LYS  NZ ', -0.529, (207.533, 232.433, 281.746)), (' D 124  THR HG22', ' D 155  PRO  HD3', -0.527, (212.543, 175.895, 170.918)), (' I  37  GLN  HB2', ' I  47  LEU HD11', -0.527, (210.152, 242.018, 185.268)), (' B 726  ILE HG12', ' B1061  VAL HG22', -0.525, (236.853, 207.779, 267.078)), (' H   2  VAL HG13', ' H  27  PHE  CD2', -0.525, (253.558, 229.738, 199.855)), (' I   3  GLN  N  ', ' I   3  GLN  OE1', -0.524, (220.761, 259.246, 176.551)), (' B 595  VAL HG22', ' B 612  TYR  CD2', -0.523, (214.099, 193.374, 240.674)), (' F 187  TYR  O  ', ' F 193  TYR  OH ', -0.523, (214.703, 186.451, 139.363)), (' C 969  ASN  OD1', ' C 975  SER  N  ', -0.523, (207.908, 220.111, 223.606)), (' B 122  ASN  O  ', ' B 124  THR  N  ', -0.522, (257.713, 171.673, 214.058)), (' A 201  PHE  HE2', ' A 203  ILE HD11', -0.52, (247.881, 264.099, 217.597)), (' H 105  VAL HG11', ' L  91  SER  O  ', -0.519, (249.753, 211.298, 188.804)), (' C 816  SER  N  ', ' C 819  GLU  OE1', -0.519, (199.115, 206.871, 270.933)), (' H 208  HIS  O  ', ' H 212  ASN  N  ', -0.518, (267.768, 250.349, 174.067)), (' B1312  NAG  O3 ', ' B1312  NAG  O7 ', -0.518, (214.661, 191.933, 291.054)), (' F  36  TYR  HE1', ' F  46  LEU HD13', -0.517, (209.035, 207.746, 186.933)), (' F   3  GLN  N  ', ' F   3  GLN  OE1', -0.516, (195.584, 209.385, 173.16)), (' B 811  LYS  NZ ', ' B 820  ASP  OD2', -0.515, (252.763, 203.682, 268.559)), (' A1072  GLU  HG2', ' B 894  LEU HD22', -0.514, (245.677, 228.733, 290.721)), (' A 570  ALA  HB1', ' B 963  VAL HG11', -0.514, (241.273, 210.296, 236.222)), (' F  33  LEU HD13', ' F  34  ASN  N  ', -0.514, (205.047, 212.343, 182.801)), (' H  83  MET  HB3', ' H  86  LEU HD21', -0.514, (269.221, 225.952, 182.079)), (' B 128  ILE HD13', ' B 229  LEU HD11', -0.512, (248.706, 183.718, 212.488)), (' B  91  TYR  OH ', ' B 191  GLU  OE2', -0.51, (240.496, 176.758, 228.816)), (' G 124  THR HG22', ' G 155  PRO  HD3', -0.508, (183.249, 264.153, 177.055)), (' A 591  SER  OG ', ' A 615  VAL HG12', -0.507, (255.119, 222.994, 240.573)), (' A 117  LEU HD11', ' A 128  ILE HG23', -0.504, (247.333, 266.723, 212.669)), (' A 697  MET  HE3', ' B 869  MET  SD ', -0.503, (251.372, 223.635, 263.904)), (' B 616  ASN  OD1', ' B 617  CYS  N  ', -0.502, (203.346, 190.066, 243.308)), (' C 600  PRO  HD3', ' C 692  ILE HD11', -0.502, (192.873, 242.339, 254.786)), (' L  33  LEU HD13', ' L  34  ASN  N  ', -0.501, (242.745, 218.116, 184.666)), (' L  36  TYR  CE1', ' L  46  LEU HD13', -0.499, (244.997, 223.789, 188.836)), (' B 201  PHE  HE2', ' B 203  ILE HD11', -0.498, (244.172, 183.013, 214.619)), (' B  40  ASP  N  ', ' B  40  ASP  OD1', -0.498, (243.301, 194.688, 227.539)), (' C 318  PHE  CE2', ' C 615  VAL HG11', -0.498, (206.091, 249.729, 241.201)), (' A 122  ASN  O  ', ' A 124  THR  N  ', -0.497, (251.516, 281.165, 218.245)), (' B  29  THR  OG1', ' B 215  ASP  OD2', -0.495, (233.191, 168.855, 231.1)), (' B 386  LYS  HZ3', ' D 101  GLY  HA2', -0.494, (200.731, 205.766, 196.72)), (' B 493  GLN  OE1', ' B 494  SER  N  ', -0.494, (164.476, 211.336, 172.217)), (' G   2  VAL HG13', ' G  27  PHE  CD2', -0.493, (202.766, 252.093, 202.071)), (' L 109  ARG  NH2', ' L 110  THR  O  ', -0.493, (231.325, 241.549, 164.385)), (' A 331  ASN  OD1', ' A1304  NAG  N2 ', -0.492, (266.084, 198.44, 218.142)), (' L  37  GLN  HB2', ' L  47  LEU HD11', -0.492, (239.943, 228.972, 184.81)), (' A 567  ARG  NH1', ' A 571  ASP  O  ', -0.492, (244.414, 205.803, 230.213)), (' F 109  ARG  NH2', ' F 110  THR  O  ', -0.492, (229.611, 210.52, 160.42)), (' B 462  LYS  N  ', ' B 465  GLU  OE1', -0.491, (177.922, 224.213, 181.98)), (' B 103  GLY  HA3', ' B 241  LEU HD12', -0.486, (245.717, 172.861, 211.238)), (' C 429  PHE  O  ', ' I  92  TYR  OH ', -0.484, (229.725, 260.074, 188.935)), (' G  89  GLU  N  ', ' G  89  GLU  OE1', -0.483, (200.808, 268.29, 176.012)), (' C 726  ILE  CG2', ' C 948  LEU HD13', -0.483, (205.903, 219.718, 264.057)), (' G 155  PRO  O  ', ' G 208  HIS  NE2', -0.482, (183.209, 259.224, 175.565)), (' A 110  LEU  N  ', ' A 110  LEU HD12', -0.48, (256.849, 259.169, 206.651)), (' C 442  ASP  OD1', ' C 451  TYR  OH ', -0.48, (232.573, 286.666, 186.847)), (' F   6  GLN  NE2', ' F  86  TYR  O  ', -0.479, (210.6, 209.691, 175.206)), (' B 110  LEU  N  ', ' B 110  LEU HD12', -0.479, (235.809, 178.125, 203.712)), (' H  47  TRP  HE1', ' H  50  VAL HG23', -0.479, (257.14, 218.581, 188.703)), (' B 532  ASN  OD1', ' B 533  LEU  N  ', -0.479, (189.557, 192.829, 223.596)), (' A 969  ASN  OD1', ' A 975  SER  N  ', -0.478, (227.377, 239.909, 224.342)), (' B 118  LEU HD12', ' B 119  ILE  N  ', -0.477, (245.909, 177.028, 208.976)), (' A 811  LYS  NZ ', ' A 820  ASP  OD2', -0.476, (225.254, 257.029, 270.611)), (' I  14  SER  N  ', ' I  17  ASP  OD2', -0.476, (210.505, 230.156, 174.504)), (' B 109  THR  OG1', ' B 114  THR HG22', -0.474, (235.265, 180.564, 200.394)), (' H 155  PRO  O  ', ' H 208  HIS  NE2', -0.47, (265.281, 244.917, 172.503)), (' C 462  LYS  N  ', ' C 465  GLU  OE1', -0.468, (244.505, 266.263, 183.124)), (' H  39  GLN  HB2', ' H  45  LEU HD23', -0.468, (253.72, 228.084, 180.625)), (' G  82  GLN  NE2', ' G  84  ASN  OD1', -0.465, (196.582, 273.941, 190.141)), (' C 356  LYS  NZ ', ' C 357  ARG  O  ', -0.464, (236.406, 275.147, 202.996)), (' D  89  GLU  N  ', ' D  89  GLU  OE1', -0.462, (198.938, 187.719, 170.968)), (' B 726  ILE HG22', ' B 948  LEU HD13', -0.46, (234.969, 209.553, 263.34)), (' G 208  HIS  O  ', ' G 212  ASN  N  ', -0.46, (177.216, 258.967, 177.561)), (' A 532  ASN  OD1', ' A 533  LEU  N  ', -0.458, (267.088, 210.23, 223.527)), (' A 565  PHE  O  ', ' B  43  PHE  N  ', -0.456, (249.639, 198.472, 230.892)), (' F  14  SER  N  ', ' F  17  ASP  OD2', -0.456, (225.51, 217.072, 171.486)), (' B 813  SER  O  ', ' B 815  ARG  N  ', -0.456, (253.335, 209.898, 269.04)), (' C 600  PRO  CD ', ' C 692  ILE HD11', -0.455, (192.315, 242.081, 254.541)), (' B 804  GLN  NE2', ' B 935  GLN  OE1', -0.455, (247.539, 200.122, 275.898)), (' B 454  ARG  HA ', ' B 492  LEU HD23', -0.454, (167.35, 217.801, 176.018)), (' C1304  NAG  H61', ' C1305  NAG  H82', -0.451, (219.439, 278.668, 224.307)), (' A1039  ARG  NH2', ' B1031  GLU  OE2', -0.451, (227.771, 223.746, 274.92)), (' A 493  GLN  OE1', ' A 494  SER  N  ', -0.451, (264.395, 183.148, 170.605)), (' C1106  GLN  NE2', ' C1111  GLU  OE1', -0.45, (209.333, 226.259, 301.122)), (' C1094  VAL HG13', ' C1107  ARG  HG2', -0.45, (216.626, 234.071, 297.598)), (' L  46  LEU HD12', ' L  47  LEU  N  ', -0.45, (242.665, 224.924, 189.16)), (' D  83  MET  CB ', ' D  86  LEU HD21', -0.45, (199.488, 184.261, 180.894)), (' A 736  VAL HG11', ' A1004  LEU HD21', -0.45, (218.275, 236.396, 239.27)), (' C 404  GLY  N  ', ' C 504  GLY  O  ', -0.449, (226.807, 279.02, 177.568)), (' C 423  TYR  CE2', ' C 425  LEU HD21', -0.448, (234.453, 268.666, 187.911)), (' B  91  TYR  CE2', ' B  93  ALA  HB2', -0.448, (239.127, 176.012, 226.079)), (' A 714  ILE HD12', ' A1096  VAL HG11', -0.447, (243.207, 224.827, 300.023)), (' A  84  LEU  N  ', ' A  84  LEU HD22', -0.445, (262.742, 259.031, 216.553)), (' A 802  PHE  CD2', ' A 805  ILE HD11', -0.445, (225.034, 246.938, 282.27)), (' A 895  GLN  N  ', ' A 895  GLN  OE1', -0.445, (210.772, 242.596, 291.461)), (' C 726  ILE HG22', ' C 948  LEU HD13', -0.444, (206.327, 219.636, 264.181)), (' A  81  ASN  N  ', ' A  81  ASN  OD1', -0.444, (267.055, 265.775, 215.234)), (' D 208  HIS  O  ', ' D 212  ASN  N  ', -0.443, (220.454, 173.808, 171.14)), (' C 386  LYS  NZ ', ' G 103  LEU  O  ', -0.443, (219.337, 255.509, 200.335)), (' B 105  ILE HD11', ' B 241  LEU HD21', -0.442, (242.255, 172.137, 207.592)), (' H   4  LEU HD23', ' H  24  ALA  HA ', -0.442, (257.5, 231.226, 197.785)), (' A 457  ARG  NH1', ' A 459  SER  OG ', -0.441, (245.824, 184.009, 175.371)), (' A 357  ARG  NH1', ' A 394  ASN  OD1', -0.441, (251.212, 190.746, 200.93)), (' A 318  PHE  HE2', ' A 615  VAL HG11', -0.441, (255.682, 225.448, 240.508)), (' A 895  GLN  NE2', ' C1074  ASN  OD1', -0.44, (207.923, 244.587, 294.677)), (' A 731  MET  N  ', ' A 774  GLN  OE1', -0.439, (220.234, 236.998, 257.1)), (' A 303  LEU HD11', ' A 313  TYR  CE2', -0.437, (244.897, 240.151, 250.424)), (' B 802  PHE  CD2', ' B 805  ILE HD11', -0.435, (244.555, 208.672, 281.295)), (' C 196  ASN  OD1', ' C 235  ILE HD12', -0.435, (182.603, 229.766, 212.924)), (' A 308  VAL HG11', ' A 599  THR HG21', -0.435, (249.319, 241.81, 250.838)), (' B 140  PHE  CD1', ' B 244  LEU HD12', -0.434, (243.799, 161.628, 208.433)), (' A 395  VAL HG22', ' A 515  PHE  CD1', -0.433, (254.087, 199.1, 197.193)), (' C 383  SER  O  ', ' C 387  LEU HD13', -0.432, (222.788, 263.267, 198.214)), (' F  46  LEU HD12', ' F  47  LEU  N  ', -0.432, (211.49, 208.425, 186.738)), (' C 393  THR  OG1', ' C 516  GLU  O  ', -0.432, (236.0, 261.649, 202.466)), (' I  29  ILE HG22', ' I  92  TYR  CB ', -0.432, (224.945, 256.632, 185.674)), (' C 312  ILE  O  ', ' C 312  ILE HG23', -0.431, (202.545, 237.953, 252.367)), (' B 909  ILE HG23', ' B1036  GLN  NE2', -0.429, (229.53, 214.126, 287.86)), (' B 403  ARG  NH1', ' B 405  ASP  OD2', -0.429, (175.579, 204.591, 170.55)), (' B  81  ASN  O  ', ' B 239  GLN  NE2', -0.429, (236.105, 169.222, 209.976)), (' D  91  THR HG23', ' D 118  THR  HA ', -0.427, (207.0, 185.225, 174.082)), (' A 428  ASP  N  ', ' A 428  ASP  OD1', -0.426, (243.377, 199.713, 185.659)), (' B 752  LEU HD12', ' B 993  ILE HG21', -0.426, (237.036, 226.12, 222.47)), (' G  12  VAL HG22', ' G  16  ARG  HB2', -0.426, (191.515, 272.535, 182.928)), (' C1028  LYS  O  ', ' C1032  CYS  CB ', -0.426, (214.882, 216.523, 275.94)), (' H  33  ASP  OD1', ' H  53  TYR  N  ', -0.425, (258.325, 217.275, 199.12)), (' A 423  TYR  CE2', ' A 425  LEU HD21', -0.425, (253.339, 194.703, 184.67)), (' A 106  PHE  O  ', ' A 116  SER  OG ', -0.425, (253.429, 261.83, 208.611)), (' F  36  TYR  CE1', ' F  46  LEU HD13', -0.425, (209.033, 207.185, 186.561)), (' C 616  ASN  OD1', ' C 617  CYS  N  ', -0.424, (204.509, 257.733, 245.264)), (' A1077  THR  OG1', ' A1078  ALA  N  ', -0.424, (244.019, 217.863, 300.861)), (' A 189  LEU  HB2', ' A 210  ILE HG21', -0.423, (257.8, 269.438, 234.829)), (' C 332  ILE HG21', ' C 335  LEU HD13', -0.422, (224.869, 274.335, 211.212)), (' A  43  PHE  N  ', ' C 565  PHE  O  ', -0.422, (232.25, 259.986, 233.716)), (' B 902  MET  HE1', ' B1049  LEU HD13', -0.421, (234.813, 209.075, 287.739)), (' A 430  THR  O  ', ' A 430  THR  OG1', -0.421, (249.087, 201.283, 192.457)), (' C 905  ARG  HD2', ' C1049  LEU  O  ', -0.421, (211.234, 216.812, 286.109)), (' C 502  GLY  O  ', ' C 506  GLN  N  ', -0.421, (224.664, 283.302, 176.276)), (' C 752  LEU HD12', ' C 993  ILE HG21', -0.42, (218.666, 211.305, 222.319)), (' B 738  CYS  SG ', ' B 739  THR  N  ', -0.42, (239.874, 227.738, 235.505)), (' C  84  LEU  N  ', ' C  84  LEU HD22', -0.419, (174.26, 241.15, 215.233)), (' L  14  SER  N  ', ' L  17  ASP  OD2', -0.419, (227.98, 234.319, 175.176)), (' L  14  SER  O  ', ' L  78  LEU HD23', -0.419, (229.287, 234.58, 177.554)), (' B 986  PRO  N  ', ' B 987  PRO  CD ', -0.419, (237.7, 226.216, 212.093)), (' A 986  PRO  N  ', ' A 987  PRO  CD ', -0.419, (214.226, 235.931, 212.382)), (' C 714  ILE HD12', ' C1096  VAL HG11', -0.418, (211.278, 237.389, 300.525)), (' C 395  VAL HG22', ' C 515  PHE  CD1', -0.418, (230.394, 266.338, 200.384)), (' C 168  PHE  CD2', ' C 169  GLU  N  ', -0.418, (176.587, 219.635, 206.942)), (' A 140  PHE  CD1', ' A 244  LEU HD12', -0.416, (266.454, 274.059, 211.723)), (' D 155  PRO  O  ', ' D 208  HIS  NE2', -0.416, (216.746, 178.83, 169.7)), (' I  36  TYR  CE1', ' I  46  LEU HD13', -0.414, (212.837, 248.724, 190.075)), (' H  60  TYR  CE1', ' H  70  ILE HG22', -0.414, (266.138, 218.263, 189.78)), (' C 715  PRO  HA ', ' C1071  GLN  O  ', -0.414, (204.814, 235.06, 294.256)), (' H  12  VAL HG22', ' H  16  ARG  HB2', -0.414, (274.642, 230.991, 178.83)), (' C 308  VAL HG11', ' C 599  THR HG21', -0.413, (194.702, 236.18, 250.36)), (' C 986  PRO  N  ', ' C 987  PRO  CD ', -0.413, (218.147, 210.877, 211.771)), (' A  48  LEU HD22', ' A 306  PHE  CE1', -0.413, (242.602, 252.236, 243.961)), (' A1142  GLN  N  ', ' A1143  PRO  HD2', -0.412, (231.634, 221.946, 322.489)), (' C 709  ASN  ND2', ' C1308  NAG  C7 ', -0.412, (220.373, 251.406, 299.138)), (' C 813  SER  O  ', ' C 815  ARG  N  ', -0.412, (197.827, 203.014, 269.05)), (' B 578  ASP  OD1', ' B 580  GLN  N  ', -0.412, (184.611, 200.777, 223.179)), (' A 201  PHE  CE2', ' A 203  ILE HD11', -0.411, (247.787, 263.588, 217.471)), (' A 122  ASN  N  ', ' A 122  ASN  OD1', -0.41, (252.223, 278.04, 215.643)), (' B1104  VAL  O  ', ' B1104  VAL HG13', -0.41, (219.95, 208.741, 305.701)), (' B 715  PRO  HA ', ' B1071  GLN  O  ', -0.409, (221.796, 199.247, 293.119)), (' C 110  LEU  N  ', ' C 110  LEU HD12', -0.409, (176.96, 236.387, 205.432)), (' C 599  THR  O  ', ' C 599  THR HG23', -0.409, (194.751, 237.767, 253.724)), (' L   1  ASP  OD1', ' L   2  ILE  N  ', -0.409, (252.166, 210.297, 177.587)), (' B  29  THR HG23', ' B  62  VAL  CG2', -0.409, (232.904, 171.976, 228.56)), (' B 741  TYR  CE1', ' B 966  LEU HD21', -0.409, (238.201, 217.525, 234.186)), (' C 358  ILE  HB ', ' C 395  VAL  HB ', -0.408, (233.202, 270.057, 202.334)), (' B 423  TYR  CE2', ' B 425  LEU HD21', -0.408, (180.313, 214.089, 185.589)), (' A 726  ILE HG22', ' A 948  LEU HD13', -0.408, (229.593, 239.326, 264.502)), (' C 886  TRP  HB2', ' C1034  LEU  O  ', -0.408, (216.94, 210.941, 283.42)), (' A 168  PHE  CD2', ' A 169  GLU  N  ', -0.408, (242.564, 268.489, 208.799)), (' G 105  VAL HG13', ' I  94  THR  OG1', -0.408, (220.782, 259.685, 192.422)), (' D  47  TRP  HE1', ' D  50  VAL HG23', -0.408, (198.825, 198.597, 187.435)), (' A  40  ASP  N  ', ' A  40  ASP  OD1', -0.407, (238.598, 256.342, 230.16)), (' B 128  ILE HG21', ' B 229  LEU HD13', -0.406, (248.053, 184.171, 210.832)), (' A 395  VAL HG22', ' A 515  PHE  HD1', -0.406, (254.029, 199.195, 197.43)), (' B 308  VAL HG11', ' B 599  THR HG21', -0.405, (226.527, 191.321, 249.529)), (' C 902  MET  HE1', ' C1049  LEU HD13', -0.404, (206.539, 219.157, 288.208)), (' F 106  GLU  OE1', ' F 174  TYR  OH ', -0.404, (222.171, 207.35, 165.601)), (' C 402  ILE HD11', ' C 510  VAL HG21', -0.404, (229.645, 275.294, 183.933)), (' C 368  LEU HD22', ' C 434  ILE  CD1', -0.404, (223.784, 273.477, 195.428)), (' A  29  THR HG23', ' A  62  VAL  CG2', -0.403, (263.089, 258.318, 231.152)), (' C1077  THR  OG1', ' C1078  ALA  N  ', -0.402, (217.275, 241.857, 301.843)), (' H  35  HIS  CD2', ' H  35  HIS  N  ', -0.401, (256.906, 221.748, 192.677)), (' A1028  LYS  O  ', ' A1032  CYS  CB ', -0.401, (222.943, 232.952, 276.26)), (' C 385  THR HG22', ' G  59  TYR  CE2', -0.4, (216.097, 267.208, 196.543)), (' I  46  LEU HD12', ' I  47  LEU  N  ', -0.4, (212.2, 246.27, 189.96))]
data['cbeta'] = []
data['rota'] = [('A', ' 331 ', 'ASN', 0.2539682676437606, (263.957, 200.81399999999996, 215.725)), ('A', ' 578 ', 'ASP', 0.2595148316724321, (260.389, 202.705, 225.718)), ('A', ' 760 ', 'CYS', 0.2577383395442585, (211.62500000000006, 231.12199999999996, 236.304)), ('A', ' 773 ', 'GLU', 0.0447910386263373, (213.4220000000001, 232.63699999999994, 257.164)), ('A', ' 948 ', 'LEU', 0.04535448373760502, (229.7330000000001, 240.364, 260.5880000000001)), ('B', '  66 ', 'HIS', 0.03507387581270258, (236.29400000000004, 163.31299999999993, 220.908)), ('B', '  84 ', 'LEU', 0.2516784072722438, (231.65500000000003, 174.86899999999994, 213.911)), ('B', ' 294 ', 'ASP', 0.1204827795529475, (223.86900000000006, 185.71299999999997, 239.80000000000004)), ('B', ' 331 ', 'ASN', 0.20749311907421025, (182.21600000000007, 200.57299999999995, 216.141)), ('B', ' 581 ', 'THR', 0.25178571283833273, (181.61700000000005, 199.87099999999995, 225.336)), ('B', ' 948 ', 'LEU', 0.0411214768479699, (235.68000000000006, 208.82099999999994, 259.859)), ('C', '  53 ', 'ASP', 0.22623819302799983, (191.07100000000003, 229.705, 227.133)), ('C', ' 205 ', 'SER', 0.04379214169129254, (174.776, 224.55199999999994, 225.385)), ('C', ' 207 ', 'HIS', 0.1664465746202396, (169.181, 224.54399999999995, 229.355)), ('C', ' 318 ', 'PHE', 0.014504900676156979, (205.16200000000015, 245.37399999999994, 237.903)), ('C', ' 331 ', 'ASN', 0.0024352966249260545, (223.581, 272.365, 218.845)), ('C', ' 387 ', 'LEU', 0.17809979064527023, (222.46, 264.322, 201.661)), ('C', ' 657 ', 'ASN', 0.19029950834593645, (197.607, 256.645, 264.605)), ('C', ' 760 ', 'CYS', 0.2844388263710635, (223.06000000000006, 209.50199999999995, 235.817)), ('C', ' 773 ', 'GLU', 0.02285701786279609, (220.12500000000003, 209.38799999999995, 256.60200000000003)), ('C', '1041 ', 'ASP', 0.14188131953249894, (213.98, 228.198, 277.356)), ('H', '  50 ', 'VAL', 0.17852524186117857, (260.126, 218.419, 191.06800000000004)), ('H', ' 105 ', 'VAL', 0.033939489401036346, (249.722, 212.463, 192.742)), ('H', ' 197 ', 'LEU', 0.19185513012377864, (246.62, 263.7809999999999, 156.485)), ('H', ' 217 ', 'LYS', 0.2000300782746585, (260.456, 258.62599999999986, 162.841)), ('D', '  50 ', 'VAL', 0.2469662155599314, (197.505, 195.85499999999996, 189.779)), ('D', ' 217 ', 'LYS', 0.16176066799607858, (230.30700000000002, 176.435, 159.136)), ('D', ' 224 ', 'CYS', 0.06932162647050091, (233.46100000000007, 181.65699999999995, 139.422)), ('G', ' 105 ', 'VAL', 0.17335128048394746, (219.972, 257.122, 194.919)), ('G', ' 197 ', 'LEU', 0.09708437703819296, (173.8690000000001, 235.82, 157.585)), ('G', ' 217 ', 'LYS', 0.15834101018153934, (172.68700000000007, 249.81799999999996, 165.459))]
data['omega'] = [('C', ' 123 ', 'ALA', None, (161.18700000000004, 222.59299999999993, 216.349)), ('D', ' 155 ', 'PRO', None, (213.569, 178.14599999999996, 169.901)), ('D', ' 157 ', 'PRO', None, (217.77100000000004, 182.17899999999997, 172.61500000000004)), ('F', '   8 ', 'PRO', None, (211.214, 214.895, 169.804)), ('F', ' 142 ', 'PRO', None, (223.40100000000007, 209.93999999999997, 159.37)), ('G', ' 155 ', 'PRO', None, (184.45500000000007, 262.06799999999987, 175.85100000000003)), ('G', ' 157 ', 'PRO', None, (185.672, 256.242, 178.271)), ('H', ' 155 ', 'PRO', None, (267.406, 242.45399999999995, 172.351)), ('H', ' 157 ', 'PRO', None, (261.967, 243.91899999999998, 175.468)), ('I', '   8 ', 'PRO', None, (216.60200000000006, 243.245, 172.84200000000004)), ('I', ' 142 ', 'PRO', None, (204.6500000000001, 236.44799999999995, 163.336)), ('L', '   8 ', 'PRO', None, (236.687, 223.03899999999993, 172.143)), ('L', ' 142 ', 'PRO', None, (234.85900000000007, 236.987, 163.037))]
data['rama'] = [('C', ' 123 ', 'ALA', 0.049782901789549874, (160.179, 222.08799999999994, 217.279))]
data['cablam'] = [('A', '33', 'THR', 'check CA trace,carbonyls, peptide', 'bend\n-SS--', (255.1, 257.0, 237.9)), ('A', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\n-SS-E', (251.6, 251.0, 219.9)), ('A', '108', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEESS-', (255.5, 255.8, 207.3)), ('A', '112', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n-SSSS', (255.2, 263.0, 200.4)), ('A', '215', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nSSS--', (265.4, 264.4, 234.6)), ('A', '231', 'ILE', ' beta sheet', ' \nEE---', (242.9, 261.0, 210.2)), ('A', '386', 'LYS', ' alpha helix', 'helix-3\nGGGGT', (255.2, 211.0, 198.7)), ('A', '430', 'THR', ' beta sheet', ' \nT--EE', (249.0, 202.2, 190.5)), ('A', '485', 'GLY', 'check CA trace,carbonyls, peptide', 'beta bridge\n--BTT', (256.8, 172.1, 160.7)), ('A', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTE', (254.6, 173.9, 158.2)), ('A', '519', 'HIS', 'check CA trace,carbonyls, peptide', 'bend\n--SS-', (240.3, 197.0, 202.8)), ('A', '617', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\n--TTT', (262.9, 225.0, 243.9)), ('A', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (251.8, 229.1, 255.4)), ('A', '667', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nEEETT', (250.9, 225.4, 256.0)), ('A', '797', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\n--STT', (223.0, 249.4, 291.1)), ('A', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'bend\nTTSSS', (229.4, 231.7, 277.6)), ('A', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (239.1, 209.4, 317.0)), ('A', '1098', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\nEESSS', (249.5, 226.3, 305.7)), ('A', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nTTS--', (238.4, 230.9, 296.7)), ('A', '1111', 'GLU', 'check CA trace,carbonyls, peptide', ' \nS----', (238.8, 231.3, 303.0)), ('A', '34', 'ARG', 'check CA trace', ' \nSS---', (254.5, 259.2, 234.8)), ('A', '293', 'LEU', 'check CA trace', 'bend\nTTSSH', (255.3, 245.4, 238.4)), ('A', '484', 'GLU', 'check CA trace', ' \nS--BT', (256.6, 171.4, 164.4)), ('A', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (253.1, 215.9, 228.4)), ('A', '856', 'ASN', 'check CA trace', 'bend\n--SSE', (218.3, 244.7, 236.9)), ('B', '33', 'THR', 'check CA trace,carbonyls, peptide', 'bend\n-SS--', (236.0, 179.6, 235.3)), ('B', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\n-SS-E', (232.0, 186.5, 217.7)), ('B', '112', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n-SSSS', (239.4, 177.9, 197.8)), ('B', '485', 'GLY', 'check CA trace,carbonyls, peptide', 'beta bridge\n--BTT', (158.5, 224.0, 163.3)), ('B', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTB', (161.0, 225.2, 160.7)), ('B', '519', 'HIS', 'check CA trace,carbonyls, peptide', 'bend\n--SS-', (190.3, 223.6, 203.8)), ('B', '617', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\n--TTT', (205.0, 188.6, 243.2)), ('B', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (214.7, 195.7, 254.7)), ('B', '667', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nEEETT', (211.8, 198.1, 255.3)), ('B', '709', 'ASN', 'check CA trace,carbonyls, peptide', 'turn\n--TTE', (203.5, 203.8, 295.4)), ('B', '797', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\n--STT', (247.5, 208.9, 290.1)), ('B', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\nBTTBS', (228.7, 212.8, 277.1)), ('B', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (205.6, 214.3, 317.4)), ('B', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nTTS--', (224.0, 204.8, 296.2)), ('B', '1111', 'GLU', ' beta sheet', ' \nS----', (224.4, 204.0, 302.3)), ('B', '34', 'ARG', 'check CA trace', ' \nSS--E', (238.1, 179.4, 232.1)), ('B', '215', 'ASP', 'check CA trace', 'bend\nSSS--', (237.0, 167.0, 231.7)), ('B', '293', 'LEU', 'check CA trace', 'bend\nTTSSH', (226.1, 185.2, 236.8)), ('B', '484', 'GLU', 'check CA trace', ' \nS--BT', (158.4, 224.6, 167.0)), ('B', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (201.5, 201.8, 228.2)), ('B', '856', 'ASN', 'check CA trace', 'bend\n--SSE', (244.3, 217.4, 235.9)), ('C', '33', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nE-S--', (179.3, 234.4, 236.7)), ('C', '41', 'LYS', 'check CA trace,carbonyls, peptide', 'bend\n-SSEE', (186.9, 216.4, 227.3)), ('C', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\n-SS-E', (186.6, 235.4, 218.9)), ('C', '112', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n-SSSS', (175.1, 233.8, 199.2)), ('C', '215', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nSSS--', (167.6, 240.0, 234.0)), ('C', '231', 'ILE', ' beta sheet', ' \nE----', (182.8, 223.3, 208.7)), ('C', '291', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\nEETTS', (192.7, 235.5, 237.4)), ('C', '389', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nGGS-E', (221.3, 262.9, 206.6)), ('C', '411', 'ALA', 'check CA trace,carbonyls, peptide', 'bend\nTSSTT', (229.5, 265.8, 183.8)), ('C', '485', 'GLY', 'check CA trace,carbonyls, peptide', 'beta bridge\n--BTT', (253.2, 283.5, 165.1)), ('C', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTE', (253.1, 280.8, 162.4)), ('C', '519', 'HIS', 'check CA trace,carbonyls, peptide', 'bend\n--SS-', (239.1, 254.6, 205.0)), ('C', '617', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\n--TTT', (202.5, 256.8, 245.1)), ('C', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (204.3, 244.3, 255.8)), ('C', '667', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nEEETT', (207.8, 245.5, 256.6)), ('C', '797', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\n--STT', (200.5, 207.8, 290.2)), ('C', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'bend\nTTSSS', (212.7, 222.8, 277.4)), ('C', '1058', 'HIS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (207.3, 212.6, 260.1)), ('C', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (226.3, 240.7, 318.1)), ('C', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nSSS--', (208.5, 230.2, 296.9)), ('C', '34', 'ARG', 'check CA trace', ' \n-S---', (177.9, 232.9, 233.5)), ('C', '293', 'LEU', 'check CA trace', 'bend\nTTSSH', (189.1, 240.3, 238.0)), ('C', '484', 'GLU', 'check CA trace', ' \nS--BT', (253.9, 283.4, 168.8)), ('C', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (215.6, 254.2, 230.0)), ('C', '856', 'ASN', 'check CA trace', 'bend\n--SSE', (208.0, 208.4, 235.8)), ('C', '1134', 'ASN', 'check CA trace', 'strand\n-EE--', (219.8, 244.8, 312.5)), ('D', '26', 'ALA', 'check CA trace,carbonyls, peptide', 'bend\nEESS-', (214.3, 194.5, 201.6)), ('F', '69', 'THR', 'check CA trace,carbonyls, peptide', 'strand\nEEEEE', (198.8, 218.8, 177.7)), ('F', '83', 'PHE', 'check CA trace,carbonyls, peptide', ' \nGG-SE', (222.3, 208.4, 175.7)), ('F', '50', 'ALA', 'check CA trace', 'turn\nEETTT', (204.5, 214.4, 188.8)), ('G', '26', 'ALA', 'check CA trace,carbonyls, peptide', 'bend\nEESS-', (199.9, 250.8, 206.0)), ('G', '113', 'GLN', 'check CA trace,carbonyls, peptide', ' \nB---E', (197.0, 252.1, 190.6)), ('H', '26', 'ALA', 'check CA trace,carbonyls, peptide', 'bend\nEESS-', (253.3, 232.7, 203.9)), ('H', '99', 'ASP', ' beta sheet', ' \nEE---', (252.2, 220.8, 195.3)), ('I', '69', 'THR', 'check CA trace,carbonyls, peptide', 'strand\n-EEEE', (227.3, 251.0, 180.2)), ('I', '83', 'PHE', 'check CA trace,carbonyls, peptide', ' \nGG-SE', (205.6, 237.5, 179.5)), ('I', '50', 'ALA', 'check CA trace', 'turn\nEETTT', (221.7, 248.2, 191.7)), ('L', '69', 'THR', 'check CA trace,carbonyls, peptide', 'strand\n-EEEE', (239.3, 209.5, 179.0)), ('L', '83', 'PHE', 'check CA trace,carbonyls, peptide', ' \nGG-SE', (237.3, 235.4, 179.0)), ('L', '50', 'ALA', 'check CA trace', 'turn\nESTTS', (241.0, 215.8, 190.3))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-11174/6zdh/Model_validation_8/validation_cootdata/molprobity_probe6zdh_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)
