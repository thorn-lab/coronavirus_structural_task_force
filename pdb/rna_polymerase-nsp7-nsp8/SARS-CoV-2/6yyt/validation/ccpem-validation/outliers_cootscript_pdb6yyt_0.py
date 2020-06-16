
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
data['jpred'] = [('C', '2', 'K', '-', 'H', (105.2, 70.1, 122.7)), ('B', '135', 'Y', '-', 'H', (126.2, 106.1, 122.2)), ('B', '140', 'N', 'E', 'H', (128.6, 112.6, 117.2)), ('D', '112', 'D', '-', 'H', (113.5, 76.3, 148.0)), ('D', '135', 'Y', '-', 'H', (124.2, 75.3, 152.8)), ('D', '140', 'N', 'E', 'H', (122.7, 70.0, 146.5)), ('D', '141', 'T', 'E', 'H', (123.4, 72.3, 143.6))]
data['probe'] = [(' B  44  VAL HG22', " U  15    G  H4'", -0.692, (28.541, 99.956, 112.107)), (' C  58  VAL HG22', ' D 119  ILE HG12', -0.635, (115.541, 87.85, 131.658)), (' B  40  LYS  O  ', ' B  44  VAL HG23', -0.599, (26.898, 98.951, 115.012)), (" P   5    C  H2'", ' P   6    A  C8 ', -0.599, (57.198, 86.94, 107.279)), (' D 157  GLN  HG3', ' D 189  LEU HD23', -0.579, (132.308, 83.393, 134.786)), (' A 605  VAL HG21', ' A 756  MET  HE2', -0.575, (88.764, 86.786, 89.416)), (' D 131  VAL HG12', ' D 185  ILE HG13', -0.555, (122.325, 86.484, 145.418)), (' C  71  LEU HD21', ' D  88  GLN  HB3', -0.553, (100.023, 82.1, 139.43)), (' C   2  LYS  O  ', ' C   6  VAL HG23', -0.529, (105.952, 73.116, 124.037)), (' D 109  ASN  O  ', ' D 114  CYS  N  ', -0.516, (115.958, 79.034, 144.901)), (' A 606  TYR  HE1', ' A 614  LEU HD21', -0.514, (90.527, 82.14, 86.043)), (' A 491  ASN  N  ', ' A 491  ASN  OD1', -0.512, (72.249, 116.811, 104.104)), (' D 101  ASP  OD1', ' D 102  ALA  N  ', -0.51, (115.842, 70.475, 131.708)), (' A 335  VAL  O  ', ' A 338  VAL HG12', -0.501, (92.614, 138.083, 119.596)), (' D 117  LEU HD11', ' D 131  VAL HG13', -0.501, (120.621, 86.829, 143.735)), (' A 531  THR HG21', ' A 567  THR HG21', -0.501, (87.257, 120.013, 103.92)), (' A 330  VAL HG11', ' B 117  LEU HD13', -0.493, (102.948, 127.547, 110.563)), (' A 726  ARG  NH2', ' A 744  GLU  OE2', -0.488, (92.598, 100.016, 66.845)), (' A 900  LEU  O  ', ' A 900  LEU HD23', -0.487, (69.215, 76.264, 137.996)), (' A 303  ASP  N  ', ' A 303  ASP  OD1', -0.484, (93.719, 121.175, 81.751)), (' A 254  GLU  OE1', ' A 286  TYR  OH ', -0.484, (121.494, 120.999, 86.81)), (' C  13  LEU HD23', ' C  55  LEU  HB3', -0.482, (108.737, 82.699, 129.484)), (' A 242  MET  SD ', ' A 312  ASN  ND2', -0.482, (107.856, 113.389, 83.004)), (' A 628  ASN  HB3', ' A 663  LEU HD21', -0.479, (102.279, 113.195, 95.889)), (' A 503  GLY  O  ', ' A 507  ASN  N  ', -0.476, (90.984, 113.776, 118.373)), (' A 676  LYS  NZ ', ' A 681  SER  OG ', -0.474, (99.388, 109.311, 104.732)), (' A 647  SER  OG ', ' A 648  LEU  N  ', -0.472, (85.843, 125.087, 87.814)), (' A 859  PHE  HA ', ' A 862  LEU HD12', -0.462, (84.48, 81.369, 116.257)), (' C  71  LEU HD23', ' D  92  PHE  HE2', -0.459, (102.928, 81.194, 140.578)), (' A 340  PHE  CD2', ' A 380  MET  HE1', -0.458, (94.143, 131.041, 116.467)), (' B 132  ILE HG21', ' B 138  TYR  HB2', -0.456, (123.924, 109.762, 122.314)), (' B  58  LYS  HG2', ' B  62  MET  HE3', -0.455, (50.38, 110.483, 115.998)), (' D 127  LYS  HD2', ' D 189  LEU HD21', -0.454, (130.917, 85.674, 133.408)), (' A 689  TYR  O  ', ' A 693  VAL HG23', -0.442, (90.996, 103.21, 93.309)), (' A 340  PHE  HD2', ' A 380  MET  HE1', -0.442, (94.305, 130.697, 115.972)), (' A 852  GLY  O  ', ' A 853  THR  OG1', -0.441, (79.369, 85.106, 128.971)), (' B 141  THR  OG1', ' B 142  CYS  N  ', -0.437, (124.818, 114.67, 119.837)), (' A 633  MET  O  ', ' A 637  VAL HG23', -0.433, (93.446, 109.385, 88.202)), (' A 601  MET  O  ', ' A 605  VAL HG23', -0.432, (85.524, 86.607, 88.387)), (' A 631  ARG  HD3', ' A 680  THR HG22', -0.432, (98.187, 107.17, 97.871)), (" P   5    C  H2'", ' P   6    A  H8 ', -0.432, (57.569, 87.267, 107.757)), (' C  36  HIS  CE1', ' C  40  LEU HD11', -0.432, (103.749, 85.885, 121.196)), (' B  59  LEU  HA ', ' B  62  MET  HG2', -0.425, (51.184, 111.954, 118.471)), (' A 626  MET  HE3', ' A 680  THR HG21', -0.424, (98.935, 104.598, 97.223)), (' B  56  GLN  O  ', ' B  59  LEU  HG ', -0.423, (47.249, 110.164, 121.312)), (' A 711  ASP  OD1', ' A 713  ASN  ND2', -0.423, (111.288, 94.087, 64.513)), (' D 159  VAL HG22', ' D 186  VAL HG22', -0.421, (129.619, 81.793, 145.08)), (' A 374  TYR  HB3', ' A 380  MET  HE3', -0.42, (93.941, 128.254, 115.131)), (' A 278  GLU  N  ', ' A 278  GLU  OE1', -0.419, (113.898, 130.459, 91.405)), (' C  71  LEU HD23', ' D  92  PHE  CE2', -0.416, (102.774, 80.978, 140.568)), (' A 540  THR HG21', ' A 665  GLU  OE1', -0.413, (97.39, 112.398, 107.197)), (' A 155  ASP  N  ', ' A 155  ASP  OD1', -0.412, (133.421, 93.514, 93.407)), (' A 575  LEU HD22', ' A 641  LYS  HG3', -0.408, (83.884, 109.163, 90.7)), (" P   6    A  H2'", ' P   7    U  C6 ', -0.408, (60.323, 90.132, 105.139)), (' A 209  ASN  ND2', ' A 218  ASP  OD2', -0.408, (119.747, 108.174, 65.142)), (' C  54  SER  O  ', ' C  58  VAL HG23', -0.408, (114.095, 84.907, 131.383)), (' B 177  SER  N  ', ' B 178  PRO  CD ', -0.406, (127.06, 100.522, 128.625)), (' B  52  ASP  HA ', ' B  55  MET  HG3', -0.405, (41.401, 108.421, 117.826)), (' A 707  LEU  O  ', ' A 724  GLN  NE2', -0.405, (104.757, 95.628, 70.845)), (' A 715  ILE  O  ', ' A 721  ARG  NH2', -0.404, (103.21, 89.796, 62.038)), (' B 126  ALA  O  ', ' B 190  ARG  N  ', -0.404, (117.036, 126.754, 124.607)), (' A 623  ASP  N  ', ' A 623  ASP  OD1', -0.4, (101.833, 100.254, 102.085))]
data['cablam'] = [('A', '220', 'GLY', 'check CA trace,carbonyls, peptide', ' \n---S-', (119.7, 110.8, 59.5)), ('A', '259', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nTTS-S', (126.8, 123.8, 90.0)), ('A', '504', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n--TTG', (94.4, 115.0, 116.8)), ('A', '509', 'TRP', 'check CA trace,carbonyls, peptide', 'turn\nGGT-B', (87.4, 116.3, 123.7)), ('A', '608', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nTSS-S', (85.5, 84.5, 77.2)), ('A', '677', 'PRO', 'check CA trace,carbonyls, peptide', ' \nE--S-', (107.6, 112.3, 102.7)), ('A', '851', 'ASP', 'check CA trace,carbonyls, peptide', 'helix\nHHHSS', (85.2, 83.1, 128.9)), ('A', '151', 'CYS', 'check CA trace', 'bend\nTTSS-', (129.9, 103.3, 89.8)), ('A', '326', 'PHE', 'check CA trace', ' \nTT-EE', (107.9, 123.1, 102.0)), ('A', '607', 'SER', 'check CA trace', 'bend\nHTSS-', (84.5, 86.0, 80.5)), ('A', '678', 'GLY', 'check CA trace', 'bend\n--S--', (104.7, 110.6, 100.9)), ('A', '903', 'TYR', 'check CA trace', 'bend\nHHS--', (68.2, 81.1, 138.5)), ('B', '182', 'TRP', 'check CA trace', 'bend\nS-SSE', (118.3, 103.8, 125.6)), ('D', '83', 'VAL', ' alpha helix', 'bend\nHSSHH', (92.4, 87.7, 136.4)), ('D', '99', 'ASP', 'check CA trace,carbonyls, peptide', ' \nHH--H', (107.4, 68.5, 132.4)), ('D', '118', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\nBSS--', (119.0, 88.2, 136.0)), ('D', '182', 'TRP', 'check CA trace', 'bend\nS-SSE', (124.1, 83.9, 154.0))]
data['rota'] = [('A', ' 246 ', 'THR', 0.2556067653575468, (114.83, 110.63699999999997, 89.62599999999999)), ('A', ' 371 ', 'LEU', 0.028224641648028216, (87.456, 126.81699999999996, 115.475)), ('A', ' 440 ', 'PHE', 0.24708157751684684, (99.29900000000004, 84.587, 117.302)), ('A', ' 491 ', 'ASN', 0.0, (71.847, 115.325, 104.854))]
data['clusters'] = [('A', '503', 1, 'backbone clash\n', (90.984, 113.776, 118.373)), ('A', '504', 1, 'cablam Outlier\n', (94.4, 115.0, 116.8)), ('A', '507', 1, 'backbone clash\n', (90.984, 113.776, 118.373)), ('A', '509', 1, 'cablam Outlier\n', (87.4, 116.3, 123.7)), ('A', '537', 1, 'smoc Outlier\n', (96.59400177001953, 121.24099731445312, 106.71199798583984)), ('A', '538', 1, 'smoc Outlier\n', (95.65899658203125, 118.51100158691406, 109.1760025024414)), ('A', '539', 1, 'smoc Outlier\n', (97.33100128173828, 116.25299835205078, 111.73999786376953)), ('A', '540', 1, 'side-chain clash\n', (97.39, 112.398, 107.197)), ('A', '561', 1, 'smoc Outlier\n', (91.20500183105469, 114.2760009765625, 111.6240005493164)), ('A', '562', 1, 'smoc Outlier\n', (87.447998046875, 114.69100189208984, 111.31300354003906)), ('A', '628', 1, 'side-chain clash\n', (102.279, 113.195, 95.889)), ('A', '663', 1, 'side-chain clash\n', (102.279, 113.195, 95.889)), ('A', '665', 1, 'side-chain clash\n', (97.39, 112.398, 107.197)), ('A', '667', 1, 'smoc Outlier\n', (102.27799987792969, 112.93299865722656, 111.54299926757812)), ('A', '676', 1, 'side-chain clash\n', (99.388, 109.311, 104.732)), ('A', '677', 1, 'cablam Outlier\nsmoc Outlier', (107.6, 112.3, 102.7)), ('A', '678', 1, 'cablam CA Geom Outlier\n', (104.7, 110.6, 100.9)), ('A', '681', 1, 'side-chain clash\n', (99.388, 109.311, 104.732)), ('A', '601', 2, 'side-chain clash\n', (85.524, 86.607, 88.387)), ('A', '605', 2, 'side-chain clash\n', (85.524, 86.607, 88.387)), ('A', '606', 2, 'side-chain clash\n', (90.527, 82.14, 86.043)), ('A', '613', 2, 'smoc Outlier\n', (95.84100341796875, 81.22699737548828, 82.63600158691406)), ('A', '614', 2, 'side-chain clash\n', (90.527, 82.14, 86.043)), ('A', '751', 2, 'smoc Outlier\n', (89.35800170898438, 90.2699966430664, 75.98899841308594)), ('A', '754', 2, 'smoc Outlier\n', (90.43599700927734, 89.91400146484375, 82.52200317382812)), ('A', '755', 2, 'smoc Outlier\n', (91.00499725341797, 91.427001953125, 85.96099853515625)), ('A', '756', 2, 'side-chain clash\n', (88.764, 86.786, 89.416)), ('A', '801', 2, 'smoc Outlier\n', (100.5530014038086, 81.25399780273438, 88.40399932861328)), ('A', '802', 2, 'Dihedral angle:CB:CG:CD:OE1\n', (97.799, 78.71400000000001, 87.712)), ('A', '340', 3, 'side-chain clash\n', (94.305, 130.697, 115.972)), ('A', '370', 3, 'Dihedral angle:CB:CG:CD:OE1\n', (86.786, 128.399, 112.074)), ('A', '371', 3, 'Rotamer\n', (87.456, 126.81699999999996, 115.475)), ('A', '372', 3, 'smoc Outlier\n', (87.7249984741211, 123.39900207519531, 113.8239974975586)), ('A', '373', 3, 'smoc Outlier\n', (89.7979965209961, 124.81800079345703, 110.95999908447266)), ('A', '374', 3, 'side-chain clash\n', (93.941, 128.254, 115.131)), ('A', '375', 3, 'smoc Outlier\n', (92.35299682617188, 123.29100036621094, 115.72000122070312)), ('A', '380', 3, 'side-chain clash\n', (93.941, 128.254, 115.131)), ('A', '707', 4, 'side-chain clash\n', (104.757, 95.628, 70.845)), ('A', '711', 4, 'side-chain clash\nsmoc Outlier', (111.288, 94.087, 64.513)), ('A', '712', 4, 'smoc Outlier\n', (106.88800048828125, 93.6989974975586, 66.09300231933594)), ('A', '713', 4, 'side-chain clash\n', (111.288, 94.087, 64.513)), ('A', '715', 4, 'side-chain clash\n', (103.21, 89.796, 62.038)), ('A', '721', 4, 'side-chain clash\n', (103.21, 89.796, 62.038)), ('A', '724', 4, 'side-chain clash\n', (104.757, 95.628, 70.845)), ('A', '775', 4, 'smoc Outlier\n', (101.43099975585938, 90.4800033569336, 73.55999755859375)), ('A', '209', 5, 'side-chain clash\n', (119.747, 108.174, 65.142)), ('A', '218', 5, 'side-chain clash\nsmoc Outlier', (119.747, 108.174, 65.142)), ('A', '220', 5, 'cablam Outlier\n', (119.7, 110.8, 59.5)), ('A', '83', 5, 'Dihedral angle:CB:CG:CD:OE1\n', (124.657, 112.087, 56.598000000000006)), ('A', '84', 5, 'Dihedral angle:CB:CG:CD:OE1\n', (127.985, 113.73700000000001, 55.761)), ('A', '85', 5, 'smoc Outlier\n', (126.21800231933594, 116.95899963378906, 54.76100158691406)), ('A', '88', 5, 'smoc Outlier\n', (129.32000732421875, 119.22599792480469, 58.09400177001953)), ('A', '182', 6, 'smoc Outlier\n', (123.02400207519531, 111.59500122070312, 82.98899841308594)), ('A', '183', 6, 'smoc Outlier\n', (122.74400329589844, 115.2750015258789, 83.9209976196289)), ('A', '184', 6, 'smoc Outlier\n', (125.87699890136719, 116.21700286865234, 81.9800033569336)), ('A', '254', 6, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1\n', (121.91400000000002, 121.81700000000001, 91.23700000000001)), ('A', '259', 6, 'cablam Outlier\n', (126.8, 123.8, 90.0)), ('A', '260', 6, 'smoc Outlier\n', (129.8070068359375, 121.80400085449219, 91.12300109863281)), ('A', '286', 6, 'side-chain clash\n', (121.494, 120.999, 86.81)), ('A', '621', 7, 'smoc Outlier\n', (105.48899841308594, 98.125, 100.83399963378906)), ('A', '622', 7, 'smoc Outlier\n', (102.53399658203125, 99.41100311279297, 98.83799743652344)), ('A', '623', 7, 'side-chain clash\n', (101.833, 100.254, 102.085)), ('A', '626', 7, 'side-chain clash\n', (98.935, 104.598, 97.223)), ('A', '631', 7, 'side-chain clash\n', (98.187, 107.17, 97.871)), ('A', '680', 7, 'side-chain clash\nsmoc Outlier', (98.935, 104.598, 97.223)), ('A', '633', 8, 'side-chain clash\nsmoc Outlier', (93.446, 109.385, 88.202)), ('A', '634', 8, 'smoc Outlier\n', (94.12300109863281, 108.26399993896484, 91.4280014038086)), ('A', '637', 8, 'side-chain clash\n', (93.446, 109.385, 88.202)), ('A', '689', 8, 'side-chain clash\n', (90.996, 103.21, 93.309)), ('A', '693', 8, 'side-chain clash\n', (90.996, 103.21, 93.309)), ('A', '242', 9, 'side-chain clash\n', (107.856, 113.389, 83.004)), ('A', '246', 9, 'Rotamer\n', (114.83, 110.63699999999997, 89.62599999999999)), ('A', '312', 9, 'side-chain clash\n', (107.856, 113.389, 83.004)), ('A', '315', 9, 'smoc Outlier\n', (108.45999908447266, 116.36399841308594, 91.68800354003906)), ('A', '463', 9, 'smoc Outlier\n', (109.3759994506836, 110.8030014038086, 87.93499755859375)), ('A', '647', 10, 'backbone clash\n', (85.843, 125.087, 87.814)), ('A', '648', 10, 'backbone clash\n', (85.843, 125.087, 87.814)), ('A', '650', 10, 'smoc Outlier\n', (87.03399658203125, 123.9280014038086, 93.072998046875)), ('A', '335', 11, 'side-chain clash\n', (92.614, 138.083, 119.596)), ('A', '336', 11, 'smoc Outlier\n', (89.53700256347656, 140.5050048828125, 118.69599914550781)), ('A', '338', 11, 'side-chain clash\n', (92.614, 138.083, 119.596)), ('A', '379', 12, 'smoc Outlier\n', (100.51000213623047, 125.95099639892578, 112.8219985961914)), ('A', '531', 12, 'side-chain clash\n', (102.948, 127.547, 110.563)), ('A', '567', 12, 'side-chain clash\n', (102.948, 127.547, 110.563)), ('A', '275', 13, 'smoc Outlier\n', (111.03700256347656, 129.10800170898438, 94.052001953125)), ('A', '277', 13, 'Dihedral angle:CB:CG:CD:OE1\n', (111.903, 131.592, 89.16799999999999)), ('A', '278', 13, 'side-chain clash\n', (113.898, 130.459, 91.405)), ('A', '297', 14, 'smoc Outlier\n', (102.2300033569336, 126.58000183105469, 90.27400207519531)), ('A', '298', 14, 'smoc Outlier\n', (99.42900085449219, 124.11900329589844, 89.51300048828125)), ('A', '353', 14, 'smoc Outlier\n', (102.55599975585938, 127.46299743652344, 96.08899688720703)), ('A', '580', 15, 'smoc Outlier\n', (80.3030014038086, 99.2490005493164, 96.04100036621094)), ('A', '581', 15, 'smoc Outlier\n', (76.81900024414062, 98.62899780273438, 94.58399963378906)), ('A', '589', 15, 'smoc Outlier\n', (84.4020004272461, 96.14199829101562, 96.09600067138672)), ('A', '484', 16, 'smoc Outlier\n', (78.30400085449219, 107.67400360107422, 88.78099822998047)), ('A', '575', 16, 'side-chain clash\n', (83.884, 109.163, 90.7)), ('A', '641', 16, 'side-chain clash\n', (83.884, 109.163, 90.7)), ('A', '851', 17, 'cablam Outlier\n', (85.2, 83.1, 128.9)), ('A', '852', 17, 'side-chain clash\n', (79.369, 85.106, 128.971)), ('A', '853', 17, 'side-chain clash\n', (79.369, 85.106, 128.971)), ('A', '726', 18, 'side-chain clash\n', (92.598, 100.016, 66.845)), ('A', '740', 18, 'smoc Outlier\n', (88.72100067138672, 105.46499633789062, 69.43900299072266)), ('A', '744', 18, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1\n', (90.099, 99.549, 71.14)), ('A', '607', 19, 'cablam CA Geom Outlier\n', (84.5, 86.0, 80.5)), ('A', '608', 19, 'cablam Outlier\nsmoc Outlier', (85.5, 84.5, 77.2)), ('A', '610', 19, 'Dihedral angle:CB:CG:CD:OE1\n', (90.923, 81.667, 74.52799999999999)), ('A', '683', 20, 'smoc Outlier\n', (92.6240005493164, 106.25700378417969, 107.42500305175781)), ('A', '685', 20, 'smoc Outlier\n', (87.81500244140625, 107.8280029296875, 103.04000091552734)), ('A', '686', 20, 'smoc Outlier\n', (89.1780014038086, 106.81999969482422, 99.62000274658203)), ('A', '133', 21, 'smoc Outlier\n', (113.052001953125, 96.38899993896484, 81.86299896240234)), ('A', '134', 21, 'smoc Outlier\n', (115.03399658203125, 94.88999938964844, 84.74299621582031)), ('A', '137', 22, 'smoc Outlier\n', (118.27400207519531, 86.71700286865234, 85.40899658203125)), ('A', '138', 22, 'smoc Outlier\n', (119.78500366210938, 89.0199966430664, 82.7699966430664)), ('A', '488', 23, 'smoc Outlier\n', (76.21299743652344, 115.24700164794922, 98.03800201416016)), ('A', '570', 23, 'smoc Outlier\n', (81.01699829101562, 114.78299713134766, 101.06900024414062)), ('A', '283', 24, 'smoc Outlier\n', (113.06999969482422, 124.05599975585938, 82.99400329589844)), ('A', '287', 24, 'smoc Outlier\n', (113.83200073242188, 120.88500213623047, 79.18800354003906)), ('A', '303', 25, 'side-chain clash\n', (93.719, 121.175, 81.751)), ('A', '306', 25, 'smoc Outlier\n', (97.99700164794922, 119.70999908447266, 82.66300201416016)), ('A', '900', 26, 'side-chain clash\n', (69.215, 76.264, 137.996)), ('A', '903', 26, 'cablam CA Geom Outlier\n', (68.2, 81.1, 138.5)), ('A', '155', 27, 'side-chain clash\n', (133.421, 93.514, 93.407)), ('A', '158', 27, 'smoc Outlier\n', (128.3070068359375, 89.1050033569336, 94.90299987792969)), ('A', '856', 28, 'smoc Outlier\n', (79.09300231933594, 81.83899688720703, 121.00299835205078)), ('A', '888', 28, 'smoc Outlier\n', (79.68399810791016, 75.56999969482422, 120.37200164794922)), ('A', '859', 29, 'side-chain clash\n', (84.48, 81.369, 116.257)), ('A', '862', 29, 'side-chain clash\n', (84.48, 81.369, 116.257)), ('A', '729', 30, 'Dihedral angle:CB:CG:CD:OE1\n', (101.67099999999999, 106.988, 67.864)), ('A', '731', 30, 'smoc Outlier\n', (102.04199981689453, 107.80500030517578, 73.18099975585938)), ('A', '227', 31, 'smoc Outlier\n', (117.86399841308594, 128.01400756835938, 58.689998626708984)), ('A', '228', 31, 'smoc Outlier\n', (116.65499877929688, 129.36399841308594, 62.020999908447266)), ('A', '864', 32, 'smoc Outlier\n', (80.38700103759766, 80.21600341796875, 108.95899963378906)), ('A', '867', 32, 'smoc Outlier\n', (82.49700164794922, 75.6969985961914, 106.63400268554688)), ('A', '149', 33, 'smoc Outlier\n', (131.91000366210938, 104.0989990234375, 84.7959976196289)), ('A', '151', 33, 'cablam CA Geom Outlier\n', (129.9, 103.3, 89.8)), ('A', '323', 34, 'smoc Outlier\n', (112.81700134277344, 120.51200103759766, 102.63899993896484)), ('A', '326', 34, 'cablam CA Geom Outlier\n', (107.9, 123.1, 102.0)), ('A', '141', 35, 'smoc Outlier\n', (124.24299621582031, 95.14800262451172, 80.50700378417969)), ('A', '144', 35, 'Dihedral angle:CB:CG:CD:OE1\n', (128.82600000000002, 96.303, 82.67799999999998)), ('B', '132', 1, 'side-chain clash\n', (123.924, 109.762, 122.314)), ('B', '135', 1, 'jpred outlier', (126.2, 106.1, 122.2)), ('B', '138', 1, 'side-chain clash\n', (123.924, 109.762, 122.314)), ('B', '139', 1, 'smoc Outlier\n', (129.26100158691406, 111.37200164794922, 120.72899627685547)), ('B', '140', 1, 'jpred outlier', (128.6, 112.6, 117.2)), ('B', '141', 1, 'backbone clash\n', (124.818, 114.67, 119.837)), ('B', '142', 1, 'backbone clash\n', (124.818, 114.67, 119.837)), ('B', '143', 1, 'smoc Outlier\n', (129.093994140625, 115.93199920654297, 122.83000183105469)), ('B', '144', 1, 'smoc Outlier\n', (129.906005859375, 117.86199951171875, 125.99299621582031)), ('B', '19', 2, 'smoc Outlier\n', (26.552000045776367, 99.55899810791016, 126.39700317382812)), ('B', '38', 2, 'smoc Outlier\n', (21.3700008392334, 97.78600311279297, 119.64199829101562)), ('B', '40', 2, 'side-chain clash\n', (26.898, 98.951, 115.012)), ('B', '42', 2, 'smoc Outlier\n', (27.128000259399414, 99.1989974975586, 120.05799865722656)), ('B', '44', 2, 'side-chain clash\n', (26.898, 98.951, 115.012)), ('B', '56', 3, 'side-chain clash\n', (47.249, 110.164, 121.312)), ('B', '58', 3, 'side-chain clash\nsmoc Outlier', (50.38, 110.483, 115.998)), ('B', '59', 3, 'side-chain clash\n', (47.249, 110.164, 121.312)), ('B', '62', 3, 'side-chain clash\n', (51.184, 111.954, 118.471)), ('B', '177', 4, 'side-chain clash\n', (127.06, 100.522, 128.625)), ('B', '178', 4, 'side-chain clash\n', (127.06, 100.522, 128.625)), ('B', '180', 4, 'smoc Outlier\n', (121.66400146484375, 102.64199829101562, 130.39599609375)), ('B', '182', 4, 'cablam CA Geom Outlier\n', (118.3, 103.8, 125.6)), ('B', '149', 5, 'smoc Outlier\n', (122.427001953125, 122.7020034790039, 116.12899780273438)), ('B', '150', 5, 'smoc Outlier\n', (120.47000122070312, 124.8219985961914, 113.6449966430664)), ('B', '156', 6, 'smoc Outlier\n', (122.33399963378906, 120.58200073242188, 128.03500366210938)), ('B', '158', 6, 'smoc Outlier\n', (118.43399810791016, 117.63200378417969, 131.54400634765625)), ('B', '126', 7, 'backbone clash\n', (117.036, 126.754, 124.607)), ('B', '190', 7, 'backbone clash\n', (117.036, 126.754, 124.607)), ('B', '91', 8, 'smoc Outlier\n', (93.84600067138672, 127.75499725341797, 121.51599884033203)), ('B', '92', 8, 'smoc Outlier\n', (94.51100158691406, 130.63600158691406, 123.91200256347656)), ('B', '52', 9, 'side-chain clash\n', (41.401, 108.421, 117.826)), ('B', '55', 9, 'side-chain clash\n', (41.401, 108.421, 117.826)), ('C', '13', 1, 'side-chain clash\n', (102.928, 81.194, 140.578)), ('C', '36', 1, 'side-chain clash\n', (102.774, 80.978, 140.568)), ('C', '40', 1, 'side-chain clash\nsmoc Outlier', (102.774, 80.978, 140.568)), ('C', '55', 1, 'side-chain clash\n', (102.928, 81.194, 140.578)), ('C', '2', 2, 'side-chain clash\njpred outlier', (105.952, 73.116, 124.037)), ('C', '5', 2, 'smoc Outlier\n', (101.66899871826172, 74.12899780273438, 124.35199737548828)), ('C', '6', 2, 'side-chain clash\n', (105.952, 73.116, 124.037)), ('C', '23', 3, 'Dihedral angle:CB:CG:CD:OE1\n', (106.726, 96.992, 130.853)), ('C', '25', 3, 'smoc Outlier\n', (111.46199798583984, 98.83000183105469, 132.281005859375)), ('C', '30', 4, 'smoc Outlier\n', (112.06199645996094, 94.60900115966797, 125.00199890136719)), ('C', '31', 4, 'smoc Outlier\n', (114.08899688720703, 91.48799896240234, 125.79000091552734)), ('C', '54', 5, 'side-chain clash\n', (114.095, 84.907, 131.383)), ('C', '58', 5, 'side-chain clash\n', (114.095, 84.907, 131.383)), ('C', '49', 6, 'smoc Outlier\n', (112.45500183105469, 75.36299896240234, 125.41100311279297)), ('C', '50', 6, 'Dihedral angle:CB:CG:CD:OE1\n', (115.664, 77.307, 126.06400000000001)), ('C', '60', 7, 'smoc Outlier\n', (111.47899627685547, 84.23200225830078, 138.77000427246094)), ('C', '69', 7, 'smoc Outlier\n', (105.55599975585938, 78.4229965209961, 147.3939971923828)), ('D', '117', 1, 'side-chain clash\nsmoc Outlier', (120.621, 86.829, 143.735)), ('D', '131', 1, 'side-chain clash\n', (120.621, 86.829, 143.735)), ('D', '159', 1, 'side-chain clash\n', (129.619, 81.793, 145.08)), ('D', '161', 1, 'smoc Outlier\n', (128.23599243164062, 87.48300170898438, 150.7469940185547)), ('D', '182', 1, 'cablam CA Geom Outlier\n', (124.1, 83.9, 154.0)), ('D', '184', 1, 'smoc Outlier\n', (125.53399658203125, 84.06999969482422, 149.05599975585938)), ('D', '185', 1, 'side-chain clash\n', (122.325, 86.484, 145.418)), ('D', '186', 1, 'side-chain clash\n', (129.619, 81.793, 145.08)), ('D', '80', 2, 'Dihedral angle:CD:NE:CZ:NH1\n', (87.68599999999999, 91.35199999999999, 135.342)), ('D', '83', 2, 'cablam Outlier\n', (92.4, 87.7, 136.4)), ('D', '85', 2, 'smoc Outlier\n', (95.40699768066406, 84.6969985961914, 140.33099365234375)), ('D', '88', 2, 'side-chain clash\n', (100.023, 82.1, 139.43)), ('D', '89', 2, 'smoc Outlier\n', (97.48799896240234, 79.4010009765625, 138.32400512695312)), ('D', '92', 2, 'side-chain clash\n', (102.774, 80.978, 140.568)), ('D', '127', 3, 'side-chain clash\n', (130.917, 85.674, 133.408)), ('D', '155', 3, 'Dihedral angle:CB:CG:CD:OE1\n', (131.914, 76.979, 135.85500000000002)), ('D', '157', 3, 'side-chain clash\n', (132.308, 83.393, 134.786)), ('D', '189', 3, 'side-chain clash\n', (130.917, 85.674, 133.408)), ('D', '135', 4, 'jpred outlier', (124.2, 75.3, 152.8)), ('D', '138', 4, 'smoc Outlier\n', (124.37100219726562, 74.81600189208984, 148.11199951171875)), ('D', '140', 4, 'jpred outlier', (122.7, 70.0, 146.5)), ('D', '141', 4, 'jpred outlier', (123.4, 72.3, 143.6)), ('D', '109', 5, 'backbone clash\n', (115.958, 79.034, 144.901)), ('D', '112', 5, 'smoc Outlier\njpred outlier', (113.51599884033203, 76.26399993896484, 148.0279998779297)), ('D', '113', 5, 'smoc Outlier\n', (115.13099670410156, 79.70800018310547, 147.7429962158203)), ('D', '114', 5, 'backbone clash\n', (115.958, 79.034, 144.901)), ('D', '104', 6, 'smoc Outlier\n', (111.24700164794922, 71.66600036621094, 136.85400390625)), ('D', '95', 6, 'smoc Outlier\n', (104.3239974975586, 74.70800018310547, 133.30599975585938)), ('D', '96', 6, 'Dihedral angle:CD:NE:CZ:NH1\n', (103.94500000000001, 71.563, 135.412)), ('D', '99', 6, 'cablam Outlier\n', (107.4, 68.5, 132.4)), ('D', '118', 7, 'cablam Outlier\n', (119.0, 88.2, 136.0)), ('D', '119', 7, 'side-chain clash\n', (115.541, 87.85, 131.658)), ('D', '101', 8, 'backbone clash\n', (115.842, 70.475, 131.708)), ('D', '102', 8, 'backbone clash\n', (115.842, 70.475, 131.708)), ('D', '48', 9, 'Dihedral angle:CB:CG:CD:OE1\n', (41.577, 86.29, 122.783)), ('D', '52', 9, 'smoc Outlier\n', (46.970001220703125, 86.572998046875, 125.91200256347656)), ('D', '13', 10, 'smoc Outlier\n', (38.874000549316406, 76.94999694824219, 129.55099487304688)), ('D', '15', 10, 'smoc Outlier\n', (38.7130012512207, 78.09600067138672, 124.18000030517578))]
data['omega'] = [('A', ' 505 ', 'PRO', None, (93.77700000000006, 117.38099999999999, 117.106)), ('B', ' 183 ', 'PRO', None, (116.458, 104.639, 124.23999999999998)), ('D', ' 183 ', 'PRO', None, (122.311, 84.952, 152.684))]
data['smoc'] = [('A', 32, 'TYR', 0.24214537301514946, (120.96600341796875, 92.59100341796875, 71.125)), ('A', 38, 'TYR', 0.29689816166967825, (109.38200378417969, 104.09300231933594, 64.31999969482422)), ('A', 85, 'THR', 0.17181903248846936, (126.21800231933594, 116.95899963378906, 54.76100158691406)), ('A', 88, 'ASN', -0.06330186212764993, (129.32000732421875, 119.22599792480469, 58.09400177001953)), ('A', 92, 'ASP', -0.09748308859640856, (131.0659942626953, 123.36299896240234, 65.28500366210938)), ('A', 118, 'ARG', -0.37090493824579485, (134.697998046875, 108.43900299072266, 69.9260025024414)), ('A', 128, 'VAL', 0.24330926875360384, (117.09100341796875, 103.01300048828125, 79.92500305175781)), ('A', 133, 'HIS', 0.2123905336734089, (113.052001953125, 96.38899993896484, 81.86299896240234)), ('A', 134, 'PHE', 0.1906107391687069, (115.03399658203125, 94.88999938964844, 84.74299621582031)), ('A', 137, 'GLY', 0.18022847732232844, (118.27400207519531, 86.71700286865234, 85.40899658203125)), ('A', 138, 'ASN', 0.14016841993757145, (119.78500366210938, 89.0199966430664, 82.7699966430664)), ('A', 141, 'THR', 0.15028775564421676, (124.24299621582031, 95.14800262451172, 80.50700378417969)), ('A', 149, 'TYR', 0.2818066067230346, (131.91000366210938, 104.0989990234375, 84.7959976196289)), ('A', 158, 'ASN', 0.12995100362076467, (128.3070068359375, 89.1050033569336, 94.90299987792969)), ('A', 163, 'TYR', 0.23754852123311, (119.3270034790039, 94.84300231933594, 93.197998046875)), ('A', 168, 'ASN', 0.2072222669223725, (120.50199890136719, 96.80599975585938, 101.02100372314453)), ('A', 182, 'VAL', 0.27509821253862426, (123.02400207519531, 111.59500122070312, 82.98899841308594)), ('A', 183, 'ARG', 0.24781914109128428, (122.74400329589844, 115.2750015258789, 83.9209976196289)), ('A', 184, 'GLN', 0.23094626648561484, (125.87699890136719, 116.21700286865234, 81.9800033569336)), ('A', 213, 'ASN', 0.01956892930533644, (128.96499633789062, 110.22699737548828, 77.45600128173828)), ('A', 218, 'ASP', 0.41874122681681336, (122.94599914550781, 110.7229995727539, 64.5250015258789)), ('A', 224, 'GLN', -0.305461717457132, (116.55500030517578, 120.59100341796875, 55.5099983215332)), ('A', 227, 'PRO', -0.3731182800610204, (117.86399841308594, 128.01400756835938, 58.689998626708984)), ('A', 228, 'GLY', -0.32732201482157475, (116.65499877929688, 129.36399841308594, 62.020999908447266)), ('A', 260, 'ASP', 0.014701690785677108, (129.8070068359375, 121.80400085449219, 91.12300109863281)), ('A', 264, 'PRO', -0.10987885374670356, (129.63600158691406, 123.5250015258789, 99.0)), ('A', 275, 'PHE', 0.1590187093455003, (111.03700256347656, 129.10800170898438, 94.052001953125)), ('A', 283, 'PHE', 0.09629616219738875, (113.06999969482422, 124.05599975585938, 82.99400329589844)), ('A', 287, 'PHE', 0.1740775320220302, (113.83200073242188, 120.88500213623047, 79.18800354003906)), ('A', 291, 'ASP', 0.3123583218479208, (106.95999908447266, 122.6969985961914, 73.56400299072266)), ('A', 297, 'ASN', 0.09747752703846188, (102.2300033569336, 126.58000183105469, 90.27400207519531)), ('A', 298, 'CYS', 0.06601738600209041, (99.42900085449219, 124.11900329589844, 89.51300048828125)), ('A', 306, 'CYS', -0.01150975056140437, (97.99700164794922, 119.70999908447266, 82.66300201416016)), ('A', 315, 'VAL', 0.16170382176614076, (108.45999908447266, 116.36399841308594, 91.68800354003906)), ('A', 323, 'PRO', -0.02160103560509596, (112.81700134277344, 120.51200103759766, 102.63899993896484)), ('A', 336, 'ASP', -0.323215811274713, (89.53700256347656, 140.5050048828125, 118.69599914550781)), ('A', 353, 'VAL', 0.12874167259657568, (102.55599975585938, 127.46299743652344, 96.08899688720703)), ('A', 358, 'ASP', 0.10394383514877073, (89.3219985961914, 133.656005859375, 101.93399810791016)), ('A', 372, 'LEU', 0.08416203685608417, (87.7249984741211, 123.39900207519531, 113.8239974975586)), ('A', 373, 'VAL', 0.18895371393493296, (89.7979965209961, 124.81800079345703, 110.95999908447266)), ('A', 375, 'ALA', 0.13930200782465965, (92.35299682617188, 123.29100036621094, 115.72000122070312)), ('A', 379, 'ALA', 0.1489515785229114, (100.51000213623047, 125.95099639892578, 112.8219985961914)), ('A', 393, 'THR', 0.30328573412507603, (114.38600158691406, 108.072998046875, 112.0260009765625)), ('A', 400, 'ALA', -0.047128206699898666, (107.6520004272461, 118.0459976196289, 120.28199768066406)), ('A', 421, 'ASP', -0.35875829269337595, (91.95600128173828, 71.76499938964844, 125.83399963378906)), ('A', 445, 'ASP', 0.06057790865264841, (108.552001953125, 97.14900207519531, 122.58200073242188)), ('A', 460, 'LEU', 0.1415152844869838, (111.44000244140625, 108.18199920654297, 96.98500061035156)), ('A', 463, 'MET', 0.11773489085525715, (109.3759994506836, 110.8030014038086, 87.93499755859375)), ('A', 484, 'ASP', 0.163234084877716, (78.30400085449219, 107.67400360107422, 88.78099822998047)), ('A', 488, 'ILE', 0.24437424617599338, (76.21299743652344, 115.24700164794922, 98.03800201416016)), ('A', 523, 'ASP', 0.17343734333199437, (77.83599853515625, 124.17900085449219, 109.0979995727539)), ('A', 537, 'PRO', 0.02805366606485527, (96.59400177001953, 121.24099731445312, 106.71199798583984)), ('A', 538, 'THR', 0.1614526863150278, (95.65899658203125, 118.51100158691406, 109.1760025024414)), ('A', 539, 'ILE', 0.07409340131762936, (97.33100128173828, 116.25299835205078, 111.73999786376953)), ('A', 561, 'SER', 0.12123157004325359, (91.20500183105469, 114.2760009765625, 111.6240005493164)), ('A', 562, 'ILE', 0.08922853396185751, (87.447998046875, 114.69100189208984, 111.31300354003906)), ('A', 570, 'GLN', 0.03530257681623058, (81.01699829101562, 114.78299713134766, 101.06900024414062)), ('A', 580, 'ALA', 0.0959090036251045, (80.3030014038086, 99.2490005493164, 96.04100036621094)), ('A', 581, 'ALA', 0.002984292221389754, (76.81900024414062, 98.62899780273438, 94.58399963378906)), ('A', 589, 'ILE', 0.19152760325931673, (84.4020004272461, 96.14199829101562, 96.09600067138672)), ('A', 592, 'SER', 0.20953119646176852, (80.06999969482422, 89.34400177001953, 98.97200012207031)), ('A', 608, 'ASP', 0.14843257109285432, (85.48699951171875, 84.46600341796875, 77.15599822998047)), ('A', 613, 'HIS', 0.2354946339576774, (95.84100341796875, 81.22699737548828, 82.63600158691406)), ('A', 618, 'ASP', 0.19851879083391838, (101.5469970703125, 91.30599975585938, 95.71299743652344)), ('A', 621, 'LYS', 0.33206382291371583, (105.48899841308594, 98.125, 100.83399963378906)), ('A', 622, 'CYS', 0.34120851772785377, (102.53399658203125, 99.41100311279297, 98.83799743652344)), ('A', 633, 'MET', -0.10468614652551672, (96.51699829101562, 110.4520034790039, 89.43099975585938)), ('A', 634, 'ALA', 0.1776036711023036, (94.12300109863281, 108.26399993896484, 91.4280014038086)), ('A', 644, 'THR', -0.10651962277545134, (78.72200012207031, 119.54900360107422, 86.43499755859375)), ('A', 650, 'HIS', 0.15811492528446341, (87.03399658203125, 123.9280014038086, 93.072998046875)), ('A', 667, 'VAL', 0.15431828968275607, (102.27799987792969, 112.93299865722656, 111.54299926757812)), ('A', 677, 'PRO', 0.3266300604029316, (107.59100341796875, 112.2509994506836, 102.73899841308594)), ('A', 680, 'THR', 0.2912788084532168, (99.02400207519531, 106.59100341796875, 101.11199951171875)), ('A', 683, 'GLY', 0.12865357465510185, (92.6240005493164, 106.25700378417969, 107.42500305175781)), ('A', 685, 'ALA', 0.08362986181621641, (87.81500244140625, 107.8280029296875, 103.04000091552734)), ('A', 686, 'THR', 0.2306104308651287, (89.1780014038086, 106.81999969482422, 99.62000274658203)), ('A', 705, 'ASN', 0.22600776060282743, (105.30400085449219, 98.00399780273438, 78.5199966430664)), ('A', 711, 'ASP', 0.3075315466012295, (110.0510025024414, 93.31300354003906, 68.16999816894531)), ('A', 712, 'GLY', 0.252401233521418, (106.88800048828125, 93.6989974975586, 66.09300231933594)), ('A', 719, 'TYR', 0.15835801128684254, (95.7020034790039, 93.46600341796875, 64.1510009765625)), ('A', 731, 'LEU', 0.0634753337329583, (102.04199981689453, 107.80500030517578, 73.18099975585938)), ('A', 740, 'ASP', -0.047666677054096565, (88.72100067138672, 105.46499633789062, 69.43900299072266)), ('A', 751, 'LYS', 0.057803898320468665, (89.35800170898438, 90.2699966430664, 75.98899841308594)), ('A', 754, 'SER', 0.10607244687526951, (90.43599700927734, 89.91400146484375, 82.52200317382812)), ('A', 755, 'MET', 0.1803829100284177, (91.00499725341797, 91.427001953125, 85.96099853515625)), ('A', 759, 'SER', 0.22720871786313535, (92.3290023803711, 97.10099792480469, 96.77400207519531)), ('A', 775, 'LEU', 0.0960782489209208, (101.43099975585938, 90.4800033569336, 73.55999755859375)), ('A', 789, 'GLN', 0.24873990275378377, (107.80500030517578, 103.04100036621094, 89.06999969482422)), ('A', 801, 'THR', 0.2616381472387501, (100.5530014038086, 81.25399780273438, 88.40399932861328)), ('A', 812, 'PHE', 0.31321848863233154, (92.68399810791016, 85.73100280761719, 97.02300262451172)), ('A', 817, 'THR', 0.2447199467619669, (89.31600189208984, 78.2760009765625, 96.09600067138672)), ('A', 856, 'ILE', -0.2919952196349191, (79.09300231933594, 81.83899688720703, 121.00299835205078)), ('A', 864, 'ILE', -0.18297695073759057, (80.38700103759766, 80.21600341796875, 108.95899963378906)), ('A', 867, 'TYR', -0.20313631380090277, (82.49700164794922, 75.6969985961914, 106.63400268554688)), ('A', 882, 'HIS', -0.2366136771914322, (83.16799926757812, 69.55899810791016, 113.42500305175781)), ('A', 888, 'ILE', -0.3023601339013679, (79.68399810791016, 75.56999969482422, 120.37200164794922)), ('A', 898, 'HIS', -0.29809789610569104, (75.16500091552734, 78.21299743652344, 134.70599365234375)), ('A', 909, 'ASN', -0.26839090208741495, (66.49199676513672, 77.49500274658203, 124.3759994506836)), ('A', 929, 'THR', 0.3093505615838428, (69.625, 84.23300170898438, 98.7699966430664)), ('B', 7, 'SER', -0.35504129634185705, (36.44200134277344, 109.58499908447266, 129.1999969482422)), ('B', 19, 'GLN', -0.24596891113068614, (26.552000045776367, 99.55899810791016, 126.39700317382812)), ('B', 26, 'VAL', -0.11905082835925582, (19.222999572753906, 92.3010025024414, 127.95800018310547)), ('B', 38, 'LEU', -0.23028830107092466, (21.3700008392334, 97.78600311279297, 119.64199829101562)), ('B', 42, 'LEU', -0.27678175596090376, (27.128000259399414, 99.1989974975586, 120.05799865722656)), ('B', 58, 'LYS', 0.11380820581277527, (49.45800018310547, 107.9489974975586, 118.1969985961914)), ('B', 67, 'MET', 0.10628454518469982, (60.11800003051758, 115.29299926757812, 124.00800323486328)), ('B', 75, 'ARG', 0.2858151180100336, (72.1709976196289, 117.72200012207031, 125.0979995727539)), ('B', 91, 'LEU', 0.21715475758692968, (93.84600067138672, 127.75499725341797, 121.51599884033203)), ('B', 92, 'PHE', 0.20656984483345087, (94.51100158691406, 130.63600158691406, 123.91200256347656)), ('B', 103, 'LEU', 0.11784172868485777, (108.22899627685547, 135.28700256347656, 115.88999938964844)), ('B', 117, 'LEU', 0.33019761534489683, (105.87200164794922, 126.4020004272461, 109.27100372314453)), ('B', 121, 'PRO', 0.22481861202454512, (110.29299926757812, 125.88800048828125, 115.85299682617188)), ('B', 130, 'VAL', 0.24122191385273994, (117.0009994506836, 115.36799621582031, 121.177001953125)), ('B', 139, 'LYS', 0.2983567931289165, (129.26100158691406, 111.37200164794922, 120.72899627685547)), ('B', 143, 'ASP', 0.0971662409212347, (129.093994140625, 115.93199920654297, 122.83000183105469)), ('B', 144, 'GLY', 0.08102495466723614, (129.906005859375, 117.86199951171875, 125.99299621582031)), ('B', 149, 'TYR', 0.21550758260700964, (122.427001953125, 122.7020034790039, 116.12899780273438)), ('B', 150, 'ALA', 0.06976233707941698, (120.47000122070312, 124.8219985961914, 113.6449966430664)), ('B', 156, 'ILE', 0.38574087528310963, (122.33399963378906, 120.58200073242188, 128.03500366210938)), ('B', 158, 'GLN', 0.3516338933001641, (118.43399810791016, 117.63200378417969, 131.54400634765625)), ('B', 164, 'SER', 0.039483120652487096, (111.50700378417969, 108.50199890136719, 132.7790069580078)), ('B', 180, 'LEU', 0.3177752466556494, (121.66400146484375, 102.64199829101562, 130.39599609375)), ('C', 5, 'ASP', -0.319218916343661, (101.66899871826172, 74.12899780273438, 124.35199737548828)), ('C', 25, 'SER', -0.36158238680786076, (111.46199798583984, 98.83000183105469, 132.281005859375)), ('C', 30, 'ALA', -0.35596577138682434, (112.06199645996094, 94.60900115966797, 125.00199890136719)), ('C', 31, 'GLN', -0.31600686836357245, (114.08899688720703, 91.48799896240234, 125.79000091552734)), ('C', 40, 'LEU', -0.3133447430696575, (106.31900024414062, 82.00700378417969, 118.51699829101562)), ('C', 49, 'PHE', -0.291372226774613, (112.45500183105469, 75.36299896240234, 125.41100311279297)), ('C', 60, 'LEU', -0.5108468784317699, (111.47899627685547, 84.23200225830078, 138.77000427246094)), ('C', 69, 'ASN', -0.41439630254267545, (105.55599975585938, 78.4229965209961, 147.3939971923828)), ('D', 6, 'PHE', -0.36751406952442134, (48.80500030517578, 77.70099639892578, 128.8070068359375)), ('D', 13, 'ALA', -0.2702407094428338, (38.874000549316406, 76.94999694824219, 129.55099487304688)), ('D', 15, 'PHE', -0.30613665878107915, (38.7130012512207, 78.09600067138672, 124.18000030517578)), ('D', 22, 'TYR', -0.2796040164364973, (32.30699920654297, 72.81999969482422, 117.70999908447266)), ('D', 29, 'GLY', -0.33598369157096114, (25.635000228881836, 67.0530014038086, 111.75)), ('D', 37, 'LYS', -0.23554664402433037, (27.83300018310547, 80.50800323486328, 115.28700256347656)), ('D', 52, 'ASP', -0.16570876001915474, (46.970001220703125, 86.572998046875, 125.91200256347656)), ('D', 75, 'ARG', -0.16481342437546498, (80.44599914550781, 87.10199737548828, 134.13800048828125)), ('D', 85, 'SER', -0.3817633779792926, (95.40699768066406, 84.6969985961914, 140.33099365234375)), ('D', 89, 'THR', -0.27328198500477835, (97.48799896240234, 79.4010009765625, 138.32400512695312)), ('D', 95, 'LEU', -0.30000081622029007, (104.3239974975586, 74.70800018310547, 133.30599975585938)), ('D', 104, 'ASN', -0.2959961154383536, (111.24700164794922, 71.66600036621094, 136.85400390625)), ('D', 112, 'ASP', -0.45563142199376777, (113.51599884033203, 76.26399993896484, 148.0279998779297)), ('D', 113, 'GLY', -0.4882923996923603, (115.13099670410156, 79.70800018310547, 147.7429962158203)), ('D', 117, 'LEU', -0.3946381065851852, (119.26599884033203, 87.91100311279297, 139.76600646972656)), ('D', 124, 'THR', 0.4615612132151159, (128.2729949951172, 79.84400177001953, 125.42500305175781)), ('D', 138, 'TYR', -0.43603940295171517, (124.37100219726562, 74.81600189208984, 148.11199951171875)), ('D', 161, 'ASP', -0.5167292756305806, (128.23599243164062, 87.48300170898438, 150.7469940185547)), ('D', 184, 'LEU', -0.47700147987770214, (125.53399658203125, 84.06999969482422, 149.05599975585938))]
handle_read_draw_probe_dots_unformatted("/Users/agnel/projects_ccpem/validation/Model_validation_600/validation_cootdata/molprobity_probepdb6yyt_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)
