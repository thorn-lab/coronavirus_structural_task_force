
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
data['rama'] = []
data['cbeta'] = []
data['jpred'] = []
data['probe'] = [(' B 379  CYS  HA ', ' B 432  CYS  HB3', -0.761, (119.614, 83.94, 56.475)), (' A 177  ARG  NH2', ' A 495  GLU  O  ', -0.742, (68.63, 79.877, 110.265)), (' A  95  ARG  NH2', ' A 209  GLU  OE1', -0.699, (103.277, 80.057, 96.701)), (' A 245  ARG  NH2', ' A 260  GLY  O  ', -0.698, (78.202, 105.17, 116.466)), (' B 386  LYS  H  ', ' B 386  LYS  HD2', -0.69, (123.514, 93.249, 48.882)), (' A 245  ARG  NH1', ' A 603  PHE  O  ', -0.688, (81.289, 108.029, 116.851)), (' A 457  GLU  HG2', ' A 513  ILE  HB ', -0.68, (88.31, 85.95, 102.76)), (' A 344  CYS  HA ', ' A 359  LYS  HE3', -0.671, (78.856, 92.789, 77.981)), (' A 460  ARG  NH2', ' A 510  TYR  O  ', -0.651, (82.325, 83.664, 99.607)), (' A 133  CYS  HB3', ' A 141  CYS  HA ', -0.639, (56.669, 92.609, 95.676)), (' A  88  ILE HD13', ' A  97  LEU HD13', -0.635, (104.72, 66.124, 90.25)), (' A 201  ASP  OD1', ' A 219  ARG  NE ', -0.617, (93.986, 73.742, 104.718)), (' A  41  TYR  OH ', ' B 500  THR  OG1', -0.61, (91.261, 83.152, 68.417)), (' B 454  ARG  NH2', ' B 467  ASP  O  ', -0.61, (107.606, 62.006, 63.129)), (' A  30  GLU  OE1', ' B 417  LYS  NZ ', -0.61, (108.531, 68.835, 76.291)), (' B 349  SER  HB3', ' B 452  LEU  H  ', -0.603, (101.707, 69.189, 60.828)), (' A 294  THR HG23', ' A 365  THR  HA ', -0.6, (81.479, 111.588, 80.295)), (' B 501  ASN  O  ', ' B 506  GLN  NE2', -0.599, (97.041, 86.074, 65.72)), (' A 152  MET  O  ', ' A 161  ARG  NH2', -0.599, (70.732, 102.349, 99.373)), (' A 131  LYS  HG2', ' A 143  LEU  HG ', -0.596, (62.126, 89.161, 90.701)), (' B 364  ASP  N  ', ' B 364  ASP  OD1', -0.593, (117.064, 84.993, 41.367)), (' A 252  TYR  HB3', ' A 255  ARG  HB2', -0.592, (67.31, 108.449, 110.225)), (' A 574  VAL HG23', ' A 576  GLU  H  ', -0.586, (107.859, 94.939, 100.281)), (' A  42  GLN  OE1', ' B 498  GLN  NE2', -0.584, (89.219, 76.86, 68.114)), (' A 177  ARG  NH1', ' A 470  LYS  O  ', -0.578, (71.635, 77.248, 111.818)), (' A 595  LEU  O  ', ' A 599  ASN  ND2', -0.569, (86.893, 112.851, 112.679)), (' B 462  LYS  HB2', ' B 465  GLU  HB2', -0.563, (119.3, 63.674, 61.695)), (' A 353  LYS  HB3', ' B 505  TYR  CG ', -0.561, (98.005, 81.228, 71.162)), (' A 402  GLU  HB3', ' A 518  ARG  HG3', -0.547, (92.28, 93.127, 93.523)), (' A 490  PRO  HA ', ' A 612  PRO  HG2', -0.545, (67.819, 98.528, 112.912)), (' B 391  CYS  HB3', ' B 522  ALA  HB1', -0.537, (129.126, 77.702, 42.253)), (' B 367  VAL  O  ', ' B 371  SER  OG ', -0.534, (110.184, 90.973, 46.581)), (' A 108  LEU HD11', ' A 190  MET  HB2', -0.534, (82.84, 67.09, 98.055)), (' A 208  GLU  HB2', ' A 219  ARG  HG2', -0.534, (97.389, 76.965, 102.511)), (' B 392  PHE  N  ', ' B 524  VAL  O  ', -0.528, (125.964, 78.862, 43.883)), (' A 356  PHE  HB3', ' A 379  ILE HD12', -0.525, (93.565, 91.416, 76.744)), (' B 408  ARG  NH2', ' B 414  GLN  OE1', -0.524, (114.932, 80.154, 71.007)), (' A 414  THR HG22', ' A 416  ASN  H  ', -0.524, (96.814, 114.881, 88.707)), (' A 351  LEU  HB2', ' A 355  ASP  HB3', -0.524, (91.181, 85.811, 72.709)), (' B 379  CYS  CA ', ' B 432  CYS  HB3', -0.524, (119.385, 84.842, 57.136)), (' B 385  THR  OG1', ' B 386  LYS  N  ', -0.516, (124.189, 91.963, 49.804)), (' B 439  ASN  ND2', ' B 499  PRO  O  ', -0.513, (93.668, 85.801, 62.656)), (' B 443  SER  HB3', ' B 507  PRO  HG3', -0.513, (96.237, 80.427, 61.162)), (' A 450  LEU HD21', ' A 519  THR  HB ', -0.507, (91.126, 96.15, 101.274)), (' B 418  ILE  HA ', ' B 422  ASN  HB2', -0.502, (110.042, 71.591, 66.267)), (' A 357  ARG HH12', ' B 500  THR HG21', -0.502, (88.034, 85.851, 68.48)), (' A 184  VAL HG22', ' A 464  PHE  HE1', -0.501, (79.246, 76.15, 104.29)), (' A 417  HIS  HB2', ' A 543  ASP  OD2', -0.501, (98.205, 111.254, 86.347)), (' A 133  CYS  HB3', ' A 141  CYS  CA ', -0.499, (56.098, 93.172, 95.552)), (' A 368  ASP  HA ', ' A 371  THR HG22', -0.499, (84.337, 103.258, 82.122)), (' A  48  TRP  CZ3', ' A 359  LYS  HB2', -0.498, (83.684, 91.213, 75.346)), (' A 303  ASP  N  ', ' A 303  ASP  OD1', -0.497, (85.976, 109.792, 70.637)), (' B 411  ALA  HB3', ' B 414  GLN  HG3', -0.496, (117.189, 79.692, 67.704)), (' B 493  GLN  NE2', ' B 494  SER  O  ', -0.496, (97.615, 69.971, 68.739)), (' A 404  VAL  O  ', ' A 408  MET  HG2', -0.493, (96.175, 98.79, 87.169)), (' A 355  ASP  OD2', ' B 500  THR  OG1', -0.492, (91.784, 84.509, 68.596)), (' A 529  LEU HD11', ' A 554  LEU HD13', -0.492, (103.134, 98.343, 90.263)), (' A  48  TRP  HZ3', ' A 359  LYS  HB2', -0.49, (83.961, 91.103, 75.661)), (' A 381  TYR  HD1', ' A 401  HIS  HA ', -0.482, (96.154, 91.25, 88.355)), (' A 524  GLN  HB3', ' A 574  VAL HG11', -0.481, (103.0, 96.585, 98.723)), (' A 400  PHE  O  ', ' A 404  VAL HG23', -0.481, (97.15, 92.769, 90.36)), (' A 153  GLU  OE1', ' A 154  ASN  ND2', -0.478, (72.162, 105.583, 92.69)), (' B 405  ASP  N  ', ' B 405  ASP  OD1', -0.477, (105.047, 81.325, 69.231)), (' A 132  ALA  HB3', ' A 148  LEU HD11', -0.474, (63.006, 92.81, 96.979)), (' B 350  VAL HG22', ' B 422  ASN  HB3', -0.468, (108.95, 70.367, 63.737)), (' A 458  LYS  HD3', ' A 480  MET  HE3', -0.465, (84.437, 87.466, 112.489)), (' A 385  TYR  OH ', ' A 401  HIS  NE2', -0.464, (95.326, 87.421, 85.137)), (' B 398  ASP  HB2', ' B 512  VAL HG13', -0.461, (113.933, 74.825, 56.006)), (' A 292  ASP  OD1', ' A 294  THR  OG1', -0.461, (81.686, 113.175, 83.787)), (' A 493  HIS  ND1', ' A 499  ASP  OD2', -0.46, (68.695, 89.382, 108.836)), (' A 248  LEU HD11', ' A 278  LEU HD21', -0.459, (75.565, 106.525, 105.533)), (' A 332  MET  HE1', ' A 344  CYS  HB3', -0.456, (78.463, 94.58, 75.893)), (' B 475  ALA  HB3', ' B 487  ASN  HB3', -0.455, (105.231, 57.278, 80.647)), (' B 376  THR  HB ', ' B 435  ALA  HB3', -0.454, (109.939, 84.71, 60.319)), (' A 293  VAL HG22', ' A 366  MET  HG3', -0.454, (86.644, 112.249, 83.956)), (' A 562  LYS  HB2', ' A 562  LYS  HE2', -0.454, (98.738, 81.148, 89.24)), (' A  37  GLU  OE1', ' A 393  ARG  NH1', -0.453, (98.352, 78.378, 77.1)), (' A 315  PHE  HD2', ' A 320  LEU HD12', -0.452, (100.233, 99.21, 82.201)), (' B 385  THR  OG1', ' B 386  LYS  HD2', -0.449, (124.769, 92.84, 49.731)), (' B 350  VAL  O  ', ' B 353  TRP  HD1', -0.449, (109.029, 68.988, 60.599)), (' B 334  ASN  HB2', ' B 362  VAL HG12', -0.448, (119.917, 81.443, 35.664)), (' B 358  ILE  HB ', ' B 395  VAL HG13', -0.446, (117.668, 75.63, 45.198)), (' A 526  GLN  O  ', ' A 530  CYS  N  ', -0.444, (104.226, 104.371, 93.91)), (' A 459  TRP  N  ', ' A 480  MET  HE1', -0.439, (83.213, 85.977, 110.791)), (' B 454  ARG  NH1', ' B 491  PRO  HB2', -0.439, (106.149, 61.446, 67.098)), (' B 503  VAL  HA ', ' B 506  GLN  HB2', -0.437, (99.496, 86.148, 66.012)), (' A  29  LEU HD11', ' A  97  LEU  HG ', -0.437, (103.04, 68.48, 87.282)), (' A 144  LEU  O  ', ' A 149  ASP  N  ', -0.436, (67.89, 96.176, 93.433)), (' A 381  TYR  CD1', ' A 401  HIS  HA ', -0.435, (96.576, 90.971, 88.157)), (' B 394  ASN  HB2', ' B 516  GLU  OE1', -0.435, (122.003, 70.988, 47.31)), (' A 423  LEU  HA ', ' A 423  LEU HD12', -0.431, (90.382, 116.93, 77.863)), (' B 517  LEU  HA ', ' B 517  LEU HD23', -0.431, (128.208, 74.55, 47.124)), (' B 401  VAL HG22', ' B 509  ARG  HG2', -0.429, (102.777, 78.189, 56.613)), (' A 237  TYR  OH ', ' A 485  VAL  O  ', -0.429, (81.595, 99.419, 109.89)), (' A 532  ILE  O  ', ' A 534  LYS  NZ ', -0.426, (111.766, 107.366, 90.153)), (' B 351  TYR  HB3', ' B 453  TYR  HA ', -0.426, (105.186, 67.86, 63.855)), (' A 160  GLU  HA ', ' A 163  TRP  CD1', -0.425, (60.307, 100.944, 101.478)), (' A 577  LYS  HB2', ' A 577  LYS  HE3', -0.424, (108.307, 87.693, 104.628)), (' A 482  ARG  HD3', ' A 488  VAL HG23', -0.419, (73.241, 95.272, 116.44)), (' A  25  ALA  HB1', ' A  97  LEU HD11', -0.418, (105.15, 66.127, 87.701)), (' A 477  TRP  CZ3', ' A 500  PRO  HB3', -0.416, (77.326, 86.51, 106.501)), (' A 147  GLY  O  ', ' A 151  ILE HG12', -0.414, (64.397, 99.267, 94.171)), (' A 365  THR  OG1', ' A 366  MET  N  ', -0.413, (82.112, 109.831, 82.549)), (' A 318  VAL  O  ', ' A 551  GLY  HA3', -0.411, (106.387, 101.618, 83.521)), (' A 441  LYS  O  ', ' A 445  THR HG22', -0.41, (85.515, 106.27, 97.973)), (' A 435  GLU  HB3', ' A 540  HIS  NE2', -0.406, (94.5, 116.18, 98.579)), (' A 534  LYS  HB2', ' A 534  LYS  HE2', -0.404, (111.333, 110.394, 90.71)), (' A 232  GLN  HB2', ' A 581  VAL HG11', -0.402, (96.925, 98.1, 109.453))]
data['smoc'] = [('A', 69, u'TRP', 0.7572492290244566, (86.68199999999999, 71.365, 78.59700000000001)), ('A', 100, u'LEU', 0.5631594040006128, (96.268, 69.998, 88.506)), ('A', 105, u'SER', 0.7185941770807349, (84.195, 67.684, 94.18599999999999)), ('A', 125, u'THR', 0.7801037177918684, (69.077, 80.307, 90.40100000000001)), ('A', 133, u'CYS', 0.610817792850921, (57.136, 92.923, 97.955)), ('A', 141, u'CYS', 0.64917949360045, (56.836, 93.239, 94.02199999999999)), ('A', 160, u'GLU', 0.6255926849834645, (61.529, 102.606, 101.861)), ('A', 169, u'ARG', 0.6319833009222388, (66.428, 88.983, 103.368)), ('A', 183, u'TYR', 0.6902494646098741, (75.766, 72.839, 101.167)), ('A', 186, u'LEU', 0.6817553783462373, (78.581, 68.569, 101.7)), ('A', 199, u'TYR', 0.6446479394268625, (85.893, 74.12899999999999, 103.485)), ('A', 203, u'TRP', 0.6452111283624237, (89.46300000000001, 78.29700000000001, 100.589)), ('A', 222, u'LEU', 0.6382735068484697, (96.588, 84.009, 106.77499999999999)), ('A', 226, u'VAL', 0.5421125487623923, (94.277, 89.337, 108.26400000000001)), ('A', 241, u'HIS', 0.5992068619424936, (82.553, 105.589, 110.68599999999999)), ('A', 264, u'ALA', 0.5671041531984888, (72.539, 98.12299999999999, 107.806)), ('A', 282, u'THR', 0.6611356399243415, (78.529, 113.345, 103.96600000000001)), ('A', 286, u'GLY', 0.5823293928918203, (79.166, 120.657, 99.189)), ('A', 308, u'PHE', 0.6633760006911946, (90.90700000000001, 103.51, 75.023)), ('A', 312, u'GLU', 0.5710713211283394, (96.902, 102.90700000000001, 76.07199999999999)), ('A', 329, u'GLU', 0.6959520634025168, (89.465, 94.73400000000001, 66.05199999999999)), ('A', 336, u'PRO', 0.7184050724830119, (76.222, 97.17899999999999, 68.91900000000001)), ('A', 351, u'LEU', 0.5290847246617251, (90.79100000000001, 84.117, 75.35)), ('A', 359, u'LYS', 0.5564682612096989, (83.542, 93.64999999999999, 76.181)), ('A', 360, u'MET', 0.5561514912152247, (82.66999999999999, 96.94100000000002, 77.883)), ('A', 368, u'ASP', 0.614636017594446, (83.952, 104.85199999999999, 81.755)), ('A', 371, u'THR', 0.6514425061315352, (87.02, 101.96400000000001, 84.44600000000001)), ('A', 375, u'GLU', 0.5684407556325136, (90.17799999999998, 96.699, 82.456)), ('A', 382, u'ASP', 0.48771327871661707, (97.10199999999999, 88.91100000000002, 81.63199999999999)), ('A', 390, u'PHE', 0.6705826789887721, (99.403, 77.05799999999999, 81.111)), ('A', 398, u'GLU', 0.6627274525188027, (93.37499999999999, 85.91700000000002, 94.53)), ('A', 412, u'ALA', 0.5627267693125053, (94.788, 107.94500000000001, 86.018)), ('A', 423, u'LEU', 0.6711310400391055, (91.459, 116.98400000000001, 79.23400000000001)), ('A', 474, u'MET', 0.6312924055490632, (72.456, 84.32, 112.766)), ('A', 481, u'LYS', 0.5750944119437201, (78.65299999999999, 92.782, 112.648)), ('A', 493, u'HIS', 0.7244026282548933, (66.41700000000002, 87.97, 112.692)), ('A', 503, u'LEU', 0.6142225841522722, (75.093, 88.402, 99.112)), ('A', 507, u'ALA', 0.6186414730133627, (74.871, 82.248, 97.65899999999999)), ('A', 511, u'SER', 0.6245823790741976, (85.51700000000001, 83.254, 98.40100000000001)), ('A', 521, u'TYR', 0.613364426635651, (98.21400000000001, 95.12799999999999, 98.134)), ('A', 522, u'GLN', 0.6177596712725384, (97.357, 98.051, 95.849)), ('A', 526, u'GLN', 0.5877814261213392, (101.3, 102.415, 94.563)), ('A', 529, u'LEU', 0.6058777101081289, (105.568, 102.63499999999999, 92.68499999999999)), ('A', 547, u'SER', 0.668822052123086, (107.938, 106.936, 84.848)), ('A', 558, u'LEU', 0.5552494777831987, (103.61999999999999, 90.779, 86.681)), ('A', 562, u'LYS', 0.5647602170271008, (101.848, 81.79100000000001, 90.024)), ('A', 566, u'TRP', 0.6163937780970777, (103.104, 85.32499999999999, 96.35799999999999)), ('A', 569, u'ALA', 0.5960258638648168, (106.41400000000002, 88.17699999999999, 94.353)), ('A', 570, u'LEU', 0.5633266252091069, (105.12499999999999, 90.84700000000001, 96.745)), ('A', 576, u'GLU', 0.5149949018081389, (108.30499999999999, 93.44200000000001, 102.345)), ('A', 584, u'LEU', 0.5781210401290827, (97.104, 102.274, 103.073)), ('A', 595, u'LEU', 0.6478833798171787, (88.596, 113.49400000000001, 110.568)), ('A', 601, u'ASN', 0.680868036955248, (82.819, 117.01700000000001, 120.004)), ('A', 603, u'PHE', 0.5998018188490399, (81.84, 109.93100000000001, 120.007)), ('A', 613, u'TYR', 0.7163287625180323, (64.11999999999999, 98.429, 116.978)), ('B', 527, u'PRO', 0.18013878576522935, (124.23100000000001, 87.27199999999999, 38.6)), ('B', 333, u'THR', -0.03788410574111205, (118.034, 82.319, 31.267999999999997)), ('B', 341, u'VAL', 0.6174827215347111, (107.97, 77.157, 47.373)), ('B', 357, u'ARG', 0.6179605134648778, (115.977, 70.87499999999999, 46.586)), ('B', 373, u'SER', 0.6314162577758734, (106.167, 90.835, 52.73800000000001)), ('B', 382, u'VAL', 0.6537400196248541, (126.224, 84.518, 55.18)), ('B', 423, u'TYR', 0.6123443785270196, (113.44600000000001, 70.67099999999999, 63.190000000000005)), ('B', 435, u'ALA', 0.5195526188470322, (108.786, 83.7, 58.275000000000006)), ('B', 456, u'PHE', 0.5353522120807516, (107.66999999999999, 63.846999999999994, 72.62599999999999)), ('B', 480, u'CYS', 0.6700824600093191, (101.62299999999999, 50.483, 75.585)), ('B', 497, u'PHE', 0.5759903138463787, (95.17599999999999, 77.71900000000001, 64.508))]
data['rota'] = [('A', ' 133 ', 'CYS', 0.06839917194370489, (57.13599999999998, 92.92299999999999, 97.955)), ('A', ' 142 ', 'LEU', 0.0007511453352496635, (60.226, 93.665, 92.367)), ('A', ' 153 ', 'GLU', 0.27512236662223866, (71.34799999999994, 102.72199999999998, 96.025)), ('A', ' 166 ', 'GLU', 0.2173094879385073, (63.93899999999998, 93.00599999999997, 105.12)), ('A', ' 208 ', 'GLU', 0.25746239734955073, (99.14699999999999, 78.29899999999999, 101.312)), ('A', ' 251 ', 'THR', 0.24508600126653654, (69.48599999999996, 112.95099999999998, 106.63199999999999)), ('A', ' 261 ', 'CYS', 0.2998488106561528, (76.41999999999996, 101.94499999999998, 115.262)), ('A', ' 283 ', 'VAL', 0.26807572627403076, (80.62899999999996, 115.28699999999999, 101.418)), ('A', ' 287 ', 'GLN', 0.2851537545857306, (79.83499999999998, 123.848, 97.221)), ('A', ' 334 ', 'THR', 0.20195187022757247, (81.20799999999997, 100.04399999999997, 71.69)), ('A', ' 343 ', 'VAL', 0.21376809814521633, (75.05599999999997, 91.56099999999998, 78.346)), ('A', ' 360 ', 'MET', 0.26676675015953266, (82.66999999999997, 96.94099999999999, 77.883)), ('A', ' 365 ', 'THR', 0.21129634257550625, (81.80099999999997, 109.93899999999996, 80.531)), ('A', ' 371 ', 'THR', 0.20653090062327206, (87.01999999999995, 101.964, 84.446)), ('A', ' 401 ', 'HIS', 0.13755099274192778, (94.83199999999998, 91.00499999999998, 89.4)), ('A', ' 410 ', 'LEU', 0.2114314277727312, (94.294, 105.51, 90.922)), ('A', ' 439 ', 'LEU', 0.19196390497031615, (89.92399999999996, 111.437, 99.667)), ('A', ' 440 ', 'LEU', 0.2922831587497319, (86.59699999999997, 111.208, 101.509)), ('A', ' 463 ', 'VAL', 0.20362416604474531, (80.97799999999997, 78.419, 110.30599999999998)), ('A', ' 512 ', 'PHE', 0.29225637901470025, (85.43799999999995, 86.79499999999999, 99.775)), ('A', ' 555 ', 'LEU', 0.29134445780168666, (106.326, 94.344, 85.124)), ('A', ' 571 ', 'GLU', 0.2522962705945602, (108.60499999999999, 91.36899999999999, 98.207)), ('A', ' 572 ', 'HIS', 0.22515490331482896, (109.85199999999999, 92.03, 94.665)), ('A', ' 593 ', 'THR', 0.27269600889458356, (93.933, 114.345, 110.32999999999998)), ('B', ' 338 ', 'PHE', 0.16965585843556535, (110.716, 80.16399999999997, 43.569)), ('B', ' 340 ', 'GLU', 0.27848127160612307, (106.356, 76.68099999999997, 43.928)), ('B', ' 350 ', 'VAL', 0.29078588006022377, (106.525, 71.075, 61.014)), ('B', ' 358 ', 'ILE', 0.14591093305814135, (116.733, 73.40899999999998, 43.846)), ('B', ' 364 ', 'ASP', 0.1401912962240615, (117.932, 86.46499999999997, 43.013)), ('B', ' 373 ', 'SER', 0.27877480573490515, (106.167, 90.83500000000004, 52.73800000000001)), ('B', ' 385 ', 'THR', 0.26840485229759276, (123.15399999999998, 91.33100000000003, 51.776)), ('B', ' 387 ', 'LEU', 0.12929426241734934, (123.848, 88.01500000000001, 47.932)), ('B', ' 395 ', 'VAL', 0.13132645210153066, (119.728, 75.038, 47.832)), ('B', ' 432 ', 'CYS', 0.012105804489692673, (118.54599999999999, 81.951, 56.532000000000004)), ('B', ' 481 ', 'ASN', 0.18076149515888149, (100.677, 47.351, 73.583)), ('B', ' 503 ', 'VAL', 0.16466563302123888, (100.269, 87.107, 67.206)), ('B', ' 506 ', 'GLN', 0.23999221017262073, (99.093, 83.011, 65.277)), ('B', ' 512 ', 'VAL', 0.15491450238990714, (114.29699999999998, 78.09, 55.841))]
data['clusters'] = [('A', '209', 1, 'side-chain clash', (103.277, 80.057, 96.701)), ('A', '332', 1, 'side-chain clash', (78.463, 94.58, 75.893)), ('A', '343', 1, 'Rotamer', (75.05599999999997, 91.56099999999998, 78.346)), ('A', '344', 1, 'side-chain clash', (78.463, 94.58, 75.893)), ('A', '351', 1, 'side-chain clash\nsmoc Outlier', (91.181, 85.811, 72.709)), ('A', '354', 1, 'cablam Outlier', (96.8, 85.5, 73.2)), ('A', '355', 1, 'side-chain clash\ncablam Outlier', (91.181, 85.811, 72.709)), ('A', '356', 1, 'side-chain clash', (93.565, 91.416, 76.744)), ('A', '357', 1, 'Dihedral angle:CD:NE:CZ:NH1', (89.73, 91.581, 74.6)), ('A', '359', 1, 'side-chain clash\nsmoc Outlier', (83.961, 91.103, 75.661)), ('A', '360', 1, 'Rotamer\nsmoc Outlier', (82.66999999999997, 96.94099999999999, 77.883)), ('A', '37', 1, 'side-chain clash', (98.352, 78.378, 77.1)), ('A', '379', 1, 'side-chain clash', (93.565, 91.416, 76.744)), ('A', '381', 1, 'side-chain clash', (96.576, 90.971, 88.157)), ('A', '382', 1, 'smoc Outlier', (97.10199999999999, 88.91100000000002, 81.63199999999999)), ('A', '385', 1, 'side-chain clash', (95.326, 87.421, 85.137)), ('A', '390', 1, 'smoc Outlier', (99.403, 77.05799999999999, 81.111)), ('A', '393', 1, 'side-chain clash', (98.352, 78.378, 77.1)), ('A', '400', 1, 'side-chain clash', (97.15, 92.769, 90.36)), ('A', '401', 1, 'Rotamer\nside-chain clash', (96.576, 90.971, 88.157)), ('A', '402', 1, 'side-chain clash', (92.28, 93.127, 93.523)), ('A', '404', 1, 'side-chain clash', (97.15, 92.769, 90.36)), ('A', '408', 1, 'side-chain clash', (91.784, 84.509, 68.596)), ('A', '450', 1, 'side-chain clash', (88.034, 85.851, 68.48)), ('A', '48', 1, 'side-chain clash', (83.961, 91.103, 75.661)), ('A', '518', 1, 'side-chain clash\nDihedral angle:CD:NE:CZ:NH1', (93.642, 93.13, 97.26700000000001)), ('A', '519', 1, 'side-chain clash', (88.034, 85.851, 68.48)), ('A', '521', 1, 'smoc Outlier', (98.21400000000001, 95.12799999999999, 98.134)), ('A', '522', 1, 'smoc Outlier', (97.357, 98.051, 95.849)), ('A', '524', 1, 'side-chain clash', (103.0, 96.585, 98.723)), ('A', '566', 1, 'smoc Outlier', (103.104, 85.32499999999999, 96.35799999999999)), ('A', '569', 1, 'smoc Outlier', (106.41400000000002, 88.17699999999999, 94.353)), ('A', '570', 1, 'smoc Outlier', (105.12499999999999, 90.84700000000001, 96.745)), ('A', '571', 1, 'Rotamer', (108.60499999999999, 91.36899999999999, 98.207)), ('A', '572', 1, 'Rotamer', (109.85199999999999, 92.03, 94.665)), ('A', '574', 1, 'side-chain clash', (103.0, 96.585, 98.723)), ('A', '576', 1, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1\nsmoc Outlier', (108.30499999999999, 93.44200000000001, 102.345)), ('A', '577', 1, 'side-chain clash', (108.307, 87.693, 104.628)), ('A', '595', 1, 'side-chain clash\nsmoc Outlier', (98.005, 81.228, 71.162)), ('A', '599', 1, 'side-chain clash', (98.005, 81.228, 71.162)), ('A', '95', 1, 'side-chain clash', (103.277, 80.057, 96.701)), ('A', '105', 2, 'smoc Outlier', (84.195, 67.684, 94.18599999999999)), ('A', '108', 2, 'side-chain clash', (82.84, 67.09, 98.055)), ('A', '183', 2, 'smoc Outlier', (75.766, 72.839, 101.167)), ('A', '184', 2, 'side-chain clash', (79.246, 76.15, 104.29)), ('A', '186', 2, 'smoc Outlier', (78.581, 68.569, 101.7)), ('A', '190', 2, 'side-chain clash', (82.84, 67.09, 98.055)), ('A', '199', 2, 'smoc Outlier', (85.893, 74.12899999999999, 103.485)), ('A', '203', 2, 'smoc Outlier', (89.46300000000001, 78.29700000000001, 100.589)), ('A', '457', 2, 'side-chain clash', (88.31, 85.95, 102.76)), ('A', '460', 2, 'backbone clash', (82.325, 83.664, 99.607)), ('A', '463', 2, 'Rotamer', (80.97799999999997, 78.419, 110.30599999999998)), ('A', '464', 2, 'side-chain clash', (79.246, 76.15, 104.29)), ('A', '467', 2, 'Dihedral angle:CB:CG:CD:OE1', (82.99400000000001, 77.195, 116.26)), ('A', '510', 2, 'backbone clash', (82.325, 83.664, 99.607)), ('A', '511', 2, 'smoc Outlier', (85.51700000000001, 83.254, 98.40100000000001)), ('A', '512', 2, 'Rotamer', (85.43799999999995, 86.79499999999999, 99.775)), ('A', '513', 2, 'side-chain clash', (88.31, 85.95, 102.76)), ('A', '131', 3, 'side-chain clash', (62.126, 89.161, 90.701)), ('A', '132', 3, 'side-chain clash', (63.006, 92.81, 96.979)), ('A', '133', 3, 'Rotamer\nside-chain clash\nbackbone clash\nsmoc Outlier', (56.098, 93.172, 95.552)), ('A', '141', 3, 'side-chain clash\nbackbone clash\nsmoc Outlier', (56.098, 93.172, 95.552)), ('A', '142', 3, 'Rotamer', (60.226, 93.665, 92.367)), ('A', '143', 3, 'side-chain clash', (62.126, 89.161, 90.701)), ('A', '144', 3, 'backbone clash', (67.89, 96.176, 93.433)), ('A', '147', 3, 'side-chain clash', (64.397, 99.267, 94.171)), ('A', '148', 3, 'side-chain clash', (63.006, 92.81, 96.979)), ('A', '149', 3, 'backbone clash', (67.89, 96.176, 93.433)), ('A', '151', 3, 'side-chain clash', (64.397, 99.267, 94.171)), ('A', '237', 4, 'backbone clash', (81.595, 99.419, 109.89)), ('A', '241', 4, 'smoc Outlier', (82.553, 105.589, 110.68599999999999)), ('A', '245', 4, 'backbone clash\nDihedral angle:CD:NE:CZ:NH1', (77.38799999999999, 108.642, 111.524)), ('A', '248', 4, 'side-chain clash', (75.565, 106.525, 105.533)), ('A', '260', 4, 'backbone clash', (78.202, 105.17, 116.466)), ('A', '261', 4, 'Rotamer', (76.41999999999996, 101.94499999999998, 115.262)), ('A', '278', 4, 'side-chain clash', (75.565, 106.525, 105.533)), ('A', '485', 4, 'backbone clash', (81.595, 99.419, 109.89)), ('A', '603', 4, 'backbone clash\nsmoc Outlier', (81.289, 108.029, 116.851)), ('A', '431', 5, 'Dihedral angle:CA:CB:CG:OD1', (92.295, 123.57, 96.095)), ('A', '435', 5, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1', (91.91000000000001, 117.026, 98.086)), ('A', '439', 5, 'Rotamer', (89.92399999999996, 111.437, 99.667)), ('A', '440', 5, 'Rotamer', (86.59699999999997, 111.208, 101.509)), ('A', '441', 5, 'side-chain clash', (85.515, 106.27, 97.973)), ('A', '445', 5, 'side-chain clash', (85.515, 106.27, 97.973)), ('A', '540', 5, 'side-chain clash', (94.5, 116.18, 98.579)), ('A', '315', 6, 'side-chain clash', (100.233, 99.21, 82.201)), ('A', '318', 6, 'side-chain clash', (106.387, 101.618, 83.521)), ('A', '320', 6, 'side-chain clash', (100.233, 99.21, 82.201)), ('A', '532', 6, 'side-chain clash', (111.766, 107.366, 90.153)), ('A', '534', 6, 'side-chain clash', (111.333, 110.394, 90.71)), ('A', '547', 6, 'smoc Outlier', (107.938, 106.936, 84.848)), ('A', '551', 6, 'side-chain clash', (106.387, 101.618, 83.521)), ('A', '292', 7, 'side-chain clash', (81.686, 113.175, 83.787)), ('A', '293', 7, 'side-chain clash', (86.644, 112.249, 83.956)), ('A', '294', 7, 'side-chain clash', (81.686, 113.175, 83.787)), ('A', '365', 7, 'Rotamer\nside-chain clash\nbackbone clash', (82.112, 109.831, 82.549)), ('A', '366', 7, 'side-chain clash\nbackbone clash', (82.112, 109.831, 82.549)), ('A', '368', 7, 'side-chain clash\nsmoc Outlier', (84.337, 103.258, 82.122)), ('A', '371', 7, 'Rotamer\nside-chain clash\nsmoc Outlier', (84.337, 103.258, 82.122)), ('A', '410', 8, 'Rotamer', (94.294, 105.51, 90.922)), ('A', '412', 8, 'smoc Outlier', (94.788, 107.94500000000001, 86.018)), ('A', '414', 8, 'side-chain clash', (96.814, 114.881, 88.707)), ('A', '416', 8, 'side-chain clash', (96.814, 114.881, 88.707)), ('A', '417', 8, 'side-chain clash', (98.205, 111.254, 86.347)), ('A', '543', 8, 'side-chain clash', (98.205, 111.254, 86.347)), ('A', '280', 9, 'cablam Outlier', (76.2, 113.0, 98.5)), ('A', '282', 9, 'smoc Outlier', (78.529, 113.345, 103.96600000000001)), ('A', '283', 9, 'Rotamer', (80.62899999999996, 115.28699999999999, 101.418)), ('A', '286', 9, 'smoc Outlier', (79.166, 120.657, 99.189)), ('A', '287', 9, 'Rotamer', (79.83499999999998, 123.848, 97.221)), ('A', '303', 10, 'side-chain clash', (85.976, 109.792, 70.637)), ('A', '305', 10, 'Dihedral angle:CD:NE:CZ:NH1', (88.142, 104.562, 70.798)), ('A', '308', 10, 'smoc Outlier', (90.90700000000001, 103.51, 75.023)), ('A', '310', 10, 'Dihedral angle:CB:CG:CD:OE1', (94.23400000000001, 107.561, 75.935)), ('A', '312', 10, 'smoc Outlier', (96.902, 102.90700000000001, 76.07199999999999)), ('A', '208', 11, 'Rotamer\nside-chain clash', (97.389, 76.965, 102.511)), ('A', '219', 11, 'side-chain clash\nDihedral angle:CD:NE:CZ:NH1', (96.849, 78.473, 105.826)), ('A', '222', 11, 'smoc Outlier', (96.588, 84.009, 106.77499999999999)), ('A', '226', 11, 'smoc Outlier', (94.277, 89.337, 108.26400000000001)), ('A', '166', 12, 'Rotamer\nDihedral angle:CB:CG:CD:OE1', (63.939, 93.006, 105.11999999999999)), ('A', '169', 12, 'Dihedral angle:CD:NE:CZ:NH1\nsmoc Outlier', (66.428, 88.983, 103.368)), ('A', '493', 12, 'side-chain clash\nsmoc Outlier', (68.695, 89.382, 108.836)), ('A', '499', 12, 'side-chain clash', (68.695, 89.382, 108.836)), ('A', '177', 13, 'backbone clash\nDihedral angle:CD:NE:CZ:NH1', (69.013, 78.67499999999998, 104.851)), ('A', '470', 13, 'backbone clash', (71.635, 77.248, 111.818)), ('A', '474', 13, 'smoc Outlier', (72.456, 84.32, 112.766)), ('A', '495', 13, 'backbone clash', (68.63, 79.877, 110.265)), ('A', '264', 14, 'smoc Outlier', (72.539, 98.12299999999999, 107.806)), ('A', '490', 14, 'side-chain clash', (67.819, 98.528, 112.912)), ('A', '612', 14, 'side-chain clash', (67.819, 98.528, 112.912)), ('A', '613', 14, 'smoc Outlier', (64.11999999999999, 98.429, 116.978)), ('A', '25', 15, 'side-chain clash', (105.15, 66.127, 87.701)), ('A', '29', 15, 'side-chain clash', (103.04, 68.48, 87.282)), ('A', '88', 15, 'side-chain clash', (104.72, 66.124, 90.25)), ('A', '97', 15, 'side-chain clash', (105.15, 66.127, 87.701)), ('A', '334', 16, 'Rotamer', (81.20799999999997, 100.04399999999997, 71.69)), ('A', '336', 16, 'cablam Outlier\nsmoc Outlier', (76.2, 97.2, 68.9)), ('A', '338', 16, 'cablam CA Geom Outlier', (71.4, 96.8, 66.3)), ('A', '339', 16, 'cablam Outlier', (69.8, 93.4, 67.1)), ('A', '251', 17, 'Rotamer', (69.48599999999996, 112.95099999999998, 106.63199999999999)), ('A', '252', 17, 'side-chain clash', (67.31, 108.449, 110.225)), ('A', '254', 17, 'cablam Outlier', (65.6, 110.5, 114.6)), ('A', '255', 17, 'side-chain clash', (67.31, 108.449, 110.225)), ('A', '152', 18, 'side-chain clash', (70.732, 102.349, 99.373)), ('A', '153', 18, 'Rotamer\nside-chain clash\nDihedral angle:CB:CG:CD:OE1', (71.348, 102.722, 96.02499999999999)), ('A', '154', 18, 'side-chain clash', (72.162, 105.583, 92.69)), ('A', '161', 18, 'side-chain clash', (70.732, 102.349, 99.373)), ('A', '192', 19, 'Dihedral angle:CD:NE:CZ:NH1', (87.79400000000001, 66.502, 104.52499999999999)), ('A', '195', 19, 'cablam Outlier', (92.8, 66.2, 103.0)), ('A', '197', 19, 'cablam Outlier', (90.2, 70.5, 107.9)), ('A', '555', 20, 'Rotamer', (106.326, 94.344, 85.124)), ('A', '558', 20, 'smoc Outlier', (103.61999999999999, 90.779, 86.681)), ('A', '560', 20, 'cablam Outlier', (105.9, 85.9, 87.3)), ('A', '458', 21, 'side-chain clash', (84.437, 87.466, 112.489)), ('A', '459', 21, 'side-chain clash', (83.213, 85.977, 110.791)), ('A', '480', 21, 'side-chain clash', (83.213, 85.977, 110.791)), ('A', '160', 22, 'side-chain clash\nsmoc Outlier', (60.307, 100.944, 101.478)), ('A', '163', 22, 'side-chain clash', (60.307, 100.944, 101.478)), ('A', '526', 23, 'backbone clash\nsmoc Outlier', (104.226, 104.371, 93.91)), ('A', '530', 23, 'backbone clash', (104.226, 104.371, 93.91)), ('A', '529', 24, 'side-chain clash\nsmoc Outlier', (103.134, 98.343, 90.263)), ('A', '554', 24, 'side-chain clash', (103.134, 98.343, 90.263)), ('A', '232', 25, 'side-chain clash', (96.925, 98.1, 109.453)), ('A', '581', 25, 'side-chain clash', (96.925, 98.1, 109.453)), ('A', '201', 26, 'side-chain clash', (108.531, 68.835, 76.291)), ('A', '30', 26, 'Dihedral angle:CB:CG:CD:OE1', (103.771, 68.644, 78.424)), ('A', '503', 27, 'smoc Outlier', (75.093, 88.402, 99.112)), ('A', '507', 27, 'smoc Outlier', (74.871, 82.248, 97.65899999999999)), ('A', '477', 28, 'side-chain clash', (77.326, 86.51, 106.501)), ('A', '500', 28, 'side-chain clash', (77.326, 86.51, 106.501)), ('A', '74', 29, 'Dihedral angle:CB:CG:CD:OE1', (88.55799999999999, 66.354, 85.31700000000001)), ('A', '75', 29, 'Dihedral angle:CB:CG:CD:OE1', (90.054, 63.368, 83.495)), ('A', '482', 30, 'side-chain clash', (73.241, 95.272, 116.44)), ('A', '488', 30, 'side-chain clash', (73.241, 95.272, 116.44)), ('B', '349', 1, 'side-chain clash', (101.707, 69.189, 60.828)), ('B', '350', 1, 'Rotamer\nside-chain clash', (109.029, 68.988, 60.599)), ('B', '351', 1, 'side-chain clash', (105.186, 67.86, 63.855)), ('B', '353', 1, 'side-chain clash', (109.029, 68.988, 60.599)), ('B', '417', 1, 'side-chain clash', (108.531, 68.835, 76.291)), ('B', '418', 1, 'side-chain clash', (110.042, 71.591, 66.267)), ('B', '420', 1, 'Dihedral angle:CA:CB:CG:OD1', (114.709, 69.44000000000001, 69.70700000000001)), ('B', '422', 1, 'side-chain clash', (108.95, 70.367, 63.737)), ('B', '423', 1, 'smoc Outlier', (113.44600000000001, 70.67099999999999, 63.190000000000005)), ('B', '452', 1, 'side-chain clash', (101.707, 69.189, 60.828)), ('B', '453', 1, 'side-chain clash', (105.186, 67.86, 63.855)), ('B', '454', 1, 'backbone clash\nside-chain clash', (106.149, 61.446, 67.098)), ('B', '456', 1, 'smoc Outlier', (107.66999999999999, 63.846999999999994, 72.62599999999999)), ('B', '467', 1, 'backbone clash', (107.606, 62.006, 63.129)), ('B', '491', 1, 'side-chain clash', (106.149, 61.446, 67.098)), ('B', '439', 2, 'backbone clash', (93.668, 85.801, 62.656)), ('B', '443', 2, 'side-chain clash', (96.237, 80.427, 61.162)), ('B', '497', 2, 'smoc Outlier', (95.17599999999999, 77.71900000000001, 64.508)), ('B', '499', 2, 'backbone clash', (93.668, 85.801, 62.656)), ('B', '500', 2, 'side-chain clash\nDihedral angle:CA:C\ncablam Outlier', (91.66999999999999, 85.62899999999999, 66.096)), ('B', '501', 2, 'side-chain clash\nDihedral angle:N:CA\ncablam Outlier', (94.756, 83.95, 67.569)), ('B', '502', 2, 'Dihedral angle:CA:C', (96.96000000000001, 86.721, 69.015)), ('B', '503', 2, 'Rotamer\nside-chain clash\nDihedral angle:N:CA', (100.269, 87.107, 67.206)), ('B', '505', 2, 'side-chain clash', (98.005, 81.228, 71.162)), ('B', '506', 2, 'Rotamer\nside-chain clash', (99.496, 86.148, 66.012)), ('B', '507', 2, 'side-chain clash', (96.237, 80.427, 61.162)), ('B', '357', 3, 'smoc Outlier', (115.977, 70.87499999999999, 46.586)), ('B', '358', 3, 'Rotamer\nside-chain clash', (117.668, 75.63, 45.198)), ('B', '391', 3, 'side-chain clash', (129.126, 77.702, 42.253)), ('B', '392', 3, 'backbone clash', (125.964, 78.862, 43.883)), ('B', '394', 3, 'side-chain clash', (122.003, 70.988, 47.31)), ('B', '395', 3, 'Rotamer\nside-chain clash', (117.668, 75.63, 45.198)), ('B', '516', 3, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1', (125.144, 73.826, 50.508)), ('B', '517', 3, 'side-chain clash', (128.208, 74.55, 47.124)), ('B', '521', 3, 'cablam Outlier', (131.1, 72.7, 39.9)), ('B', '522', 3, 'side-chain clash', (129.126, 77.702, 42.253)), ('B', '524', 3, 'backbone clash', (125.964, 78.862, 43.883)), ('B', '405', 4, 'side-chain clash', (105.047, 81.325, 69.231)), ('B', '406', 4, 'Dihedral angle:CB:CG:CD:OE1', (108.253, 79.29700000000001, 67.952)), ('B', '408', 4, 'side-chain clash\nDihedral angle:CD:NE:CZ:NH1', (112.598, 82.23700000000001, 67.488)), ('B', '411', 4, 'side-chain clash', (117.189, 79.692, 67.704)), ('B', '414', 4, 'side-chain clash', (117.189, 79.692, 67.704)), ('B', '385', 5, 'Rotamer\nbackbone clash\nside-chain clash\ncablam Outlier', (124.769, 92.84, 49.731)), ('B', '386', 5, 'side-chain clash\nbackbone clash\ncablam CA Geom Outlier', (124.769, 92.84, 49.731)), ('B', '387', 5, 'Rotamer', (123.848, 88.01500000000001, 47.932)), ('B', '388', 5, 'cablam Outlier', (124.5, 88.4, 44.2)), ('B', '527', 5, 'smoc Outlier', (124.23100000000001, 87.27199999999999, 38.6)), ('B', '338', 6, 'Rotamer', (110.716, 80.16399999999997, 43.569)), ('B', '340', 6, 'Rotamer', (106.356, 76.68099999999997, 43.928)), ('B', '341', 6, 'smoc Outlier', (107.97, 77.157, 47.373)), ('B', '333', 7, 'smoc Outlier', (118.034, 82.319, 31.267999999999997)), ('B', '334', 7, 'side-chain clash', (119.917, 81.443, 35.664)), ('B', '362', 7, 'side-chain clash', (119.917, 81.443, 35.664)), ('B', '475', 8, 'side-chain clash', (105.231, 57.278, 80.647)), ('B', '486', 8, 'cablam Outlier', (99.3, 54.8, 81.4)), ('B', '487', 8, 'side-chain clash', (105.231, 57.278, 80.647)), ('B', '480', 9, 'smoc Outlier', (101.62299999999999, 50.483, 75.585)), ('B', '481', 9, 'Rotamer', (100.677, 47.351, 73.583)), ('B', '484', 9, 'cablam CA Geom Outlier', (97.5, 54.8, 74.5)), ('B', '493', 10, 'backbone clash', (97.615, 69.971, 68.739)), ('B', '494', 10, 'backbone clash', (97.615, 69.971, 68.739)), ('B', '398', 11, 'side-chain clash', (113.933, 74.825, 56.006)), ('B', '512', 11, 'Rotamer\nside-chain clash', (113.933, 74.825, 56.006)), ('B', '376', 12, 'side-chain clash', (109.939, 84.71, 60.319)), ('B', '435', 12, 'side-chain clash\nsmoc Outlier', (109.939, 84.71, 60.319)), ('B', '367', 13, 'side-chain clash', (110.184, 90.973, 46.581)), ('B', '371', 13, 'side-chain clash', (110.184, 90.973, 46.581)), ('B', '401', 14, 'side-chain clash', (102.777, 78.189, 56.613)), ('B', '509', 14, 'side-chain clash', (102.777, 78.189, 56.613)), ('B', '462', 15, 'side-chain clash', (119.3, 63.674, 61.695)), ('B', '465', 15, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1', (116.67499999999998, 64.849, 60.234)), ('B', '379', 16, 'side-chain clash', (119.385, 84.842, 57.136)), ('B', '432', 16, 'Rotamer\nside-chain clash', (119.385, 84.842, 57.136))]
data['omega'] = [('A', ' 146 ', 'PRO', None, (66.40599999999995, 95.49, 88.83))]
data['cablam'] = [('A', '136', 'ASN', ' alpha helix', 'turn\n-TT-T', (50.4, 98.6, 101.2)), ('A', '195', 'ASN', 'check CA trace,carbonyls, peptide', 'turn\nHTT-S', (92.8, 66.2, 103.0)), ('A', '197', 'GLU', 'check CA trace,carbonyls, peptide', 'bend\nT-SSH', (90.2, 70.5, 107.9)), ('A', '211', 'TRP', 'check CA trace,carbonyls, peptide', 'bend\nB-SSS', (108.3, 74.1, 98.6)), ('A', '254', 'SER', 'check CA trace,carbonyls, peptide', 'turn\n-TTSS', (65.6, 110.5, 114.6)), ('A', '280', 'PRO', ' alpha helix', 'helix\nGHHHH', (76.2, 113.0, 98.5)), ('A', '336', 'PRO', ' beta sheet', ' \nS---S', (76.2, 97.2, 68.9)), ('A', '339', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n-SS--', (69.8, 93.4, 67.1)), ('A', '354', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\nSSS-E', (96.8, 85.5, 73.2)), ('A', '355', 'ASP', 'check CA trace,carbonyls, peptide', ' \nSS-EE', (93.5, 87.1, 72.3)), ('A', '427', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\n-SS--', (94.7, 127.2, 84.2)), ('A', '539', 'LEU', 'check CA trace,carbonyls, peptide', 'turn\nS-TTS', (100.1, 110.0, 98.7)), ('A', '560', 'LEU', 'check CA trace,carbonyls, peptide', 'turn\nHTTGG', (105.9, 85.9, 87.3)), ('A', '338', 'ASP', 'check CA trace', 'bend\n--SS-', (71.4, 96.8, 66.3)), ('B', '385', 'THR', 'check CA trace,carbonyls, peptide', 'bend\n-SS--', (123.2, 91.3, 51.8)), ('B', '388', 'ASN', 'check CA trace,carbonyls, peptide', 'turn\n--TT-', (124.5, 88.4, 44.2)), ('B', '477', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n-SSS-', (108.6, 50.9, 81.6)), ('B', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTE', (99.3, 54.8, 81.4)), ('B', '500', 'THR', 'check CA trace,carbonyls, peptide', 'bend\n-SS--', (91.7, 85.6, 66.1)), ('B', '501', 'ASN', 'check CA trace,carbonyls, peptide', ' \nSS--T', (94.8, 84.0, 67.6)), ('B', '519', 'HIS', 'check CA trace,carbonyls, peptide', 'bend\n--SS-', (133.0, 69.4, 45.9)), ('B', '521', 'PRO', ' beta sheet', ' \nSS---', (131.1, 72.7, 39.9)), ('B', '386', 'LYS', 'check CA trace', ' \nSS--T', (122.1, 91.4, 48.1)), ('B', '484', 'GLU', 'check CA trace', ' \nTS-BT', (97.5, 54.8, 74.5))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-30305/7c8d/Model_validation_1/validation_cootdata/molprobity_probe7c8d_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)
