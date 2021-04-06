
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
data['probe'] = [(' A 338  VAL  CG1', ' B  95  LEU HD11', -1.08, (130.131, 170.253, 158.987)), (' A 497  ASN  H  ', ' A 497  ASN HD22', -0.873, (116.622, 138.641, 150.682)), (' A1003  H3U  N1 ', ' A1003  H3U  O25', -0.871, (117.813, 133.907, 143.809)), (' A 338  VAL HG12', ' B  95  LEU HD11', -0.861, (130.552, 170.223, 158.609)), (' A 553  ARG  NH1', ' A1004  H3U  O34', -0.85, (138.039, 128.4, 146.951)), (' A 338  VAL HG11', ' B  95  LEU HD11', -0.829, (129.951, 170.232, 159.725)), (' B  98  LEU  O  ', ' B  98  LEU HD12', -0.795, (139.185, 168.246, 160.158)), (' C  46  THR  O  ', ' C  50  GLU  HG3', -0.794, (151.746, 110.851, 164.6)), (' A 836  ARG  HG3', ' A1004  H3U  C14', -0.776, (128.981, 119.491, 150.895)), (' C  31  GLN  NE2', ' G 119  ILE HD12', -0.729, (152.372, 125.729, 169.869)), (' A  91  LYS  HB2', ' A  91  LYS  NZ ', -0.723, (165.313, 152.011, 100.264)), (' A 836  ARG  CG ', ' A1004  H3U  C27', -0.719, (128.213, 118.761, 151.418)), (' A1004  H3U  N1 ', ' A1004  H3U  S17', -0.707, (132.482, 123.523, 148.832)), (' A 497  ASN  N  ', ' A 497  ASN HD22', -0.683, (115.933, 138.053, 151.117)), (' A1003  H3U  N1 ', ' A1003  H3U  S17', -0.679, (117.317, 134.127, 144.662)), (' A 371  LEU HD12', ' B  91  LEU HD12', -0.673, (124.947, 162.76, 157.401)), (' A 836  ARG  HG2', ' A1004  H3U  C27', -0.672, (127.713, 118.05, 151.766)), (' A 371  LEU  CD1', ' B  91  LEU HD12', -0.67, (124.173, 162.527, 157.537)), (' B  95  LEU  C  ', ' B  95  LEU HD23', -0.652, (133.537, 167.909, 161.403)), (' A 836  ARG  HG3', ' A1004  H3U  C27', -0.648, (128.616, 118.486, 151.626)), (' A 338  VAL HG11', ' B  95  LEU  CD1', -0.635, (130.154, 169.53, 159.65)), (' C  23  GLU  HA ', ' C  29  TRP  HB2', -0.626, (143.488, 131.803, 169.977)), (' C  31  GLN  NE2', ' G 119  ILE  CD1', -0.622, (152.048, 125.276, 170.172)), (' A 371  LEU HD12', ' B  91  LEU  CD1', -0.607, (125.005, 162.263, 156.875)), (' G 168  GLN  HB2', ' G 171  GLU  HB2', -0.587, (172.977, 115.713, 191.48)), (' C  19  GLN  OE1', ' G  87  MET  HE2', -0.585, (132.552, 125.045, 175.364)), (' A  91  LYS  HB2', ' A  91  LYS  HZ2', -0.578, (165.826, 153.092, 100.411)), (' A 153  ASP  N  ', ' A 153  ASP  OD1', -0.573, (166.788, 132.206, 132.148)), (' A  77  PHE  CE1', ' A 103  LYS  NZ ', -0.57, (163.402, 140.669, 84.696)), (' A 836  ARG  HG3', ' A1004  H3U  C20', -0.559, (128.531, 119.243, 151.872)), (' A 388  LEU HD23', ' A 397  SER  HB2', -0.555, (145.34, 150.308, 153.967)), (' A  66  ILE HG23', ' A  68  SER  H  ', -0.543, (171.497, 136.588, 113.144)), (' A 503  GLY  O  ', ' A 507  ASN  ND2', -0.542, (127.918, 146.98, 156.812)), (' A 497  ASN  H  ', ' A 497  ASN  ND2', -0.539, (116.622, 138.124, 150.659)), (' A 614  LEU  HB2', ' A 802  GLU  HB3', -0.538, (129.755, 113.753, 129.093)), (' G 131  VAL HG12', ' G 185  ILE HG22', -0.534, (158.189, 122.538, 185.576)), (' B  98  LEU  C  ', ' B  98  LEU HD12', -0.531, (139.362, 168.017, 159.708)), (' A 340  PHE  CD1', ' B  95  LEU HD12', -0.528, (130.751, 168.259, 158.095)), (' G 100  ASN  HB3', ' G 103  LEU  HB2', -0.522, (145.919, 108.533, 172.831)), (' A 507  ASN  ND2', ' A 541  GLN  OE1', -0.519, (129.789, 145.719, 157.74)), (' A 476  VAL HG22', ' A 696  ILE HG22', -0.519, (127.77, 134.4, 124.931)), (' A 503  GLY  HA3', ' A 561  SER  HA ', -0.518, (126.797, 147.948, 152.561)), (' C   9  THR  OG1', ' G  94  MET  HE2', -0.513, (137.024, 112.192, 169.399)), (' B 112  ASP  N  ', ' B 112  ASP  OD1', -0.512, (140.266, 172.214, 140.043)), (' A 588  VAL HG23', ' A 758  LEU HD12', -0.508, (121.544, 125.802, 136.581)), (' A  91  LYS  CB ', ' A  91  LYS  NZ ', -0.507, (165.142, 152.156, 99.775)), (' A 388  LEU HD13', ' A 400  ALA  HB2', -0.499, (145.067, 151.592, 158.806)), (' A  99  HIS  NE2', ' A 217  TYR  O  ', -0.49, (159.903, 143.271, 101.789)), (' A 540  THR  OG1', ' A 665  GLU  OE1', -0.49, (131.512, 146.695, 147.662)), (' A 128  VAL HG22', ' A 244  ILE HG13', -0.489, (150.175, 139.499, 120.127)), (' B 181  ALA  HB1', ' C  26  SER  OG ', -0.488, (150.363, 137.181, 168.356)), (' A 333  ILE HD12', ' A 361  LEU  HA ', -0.488, (129.233, 171.793, 147.226)), (' A 606  TYR  HE1', ' A 614  LEU HD21', -0.487, (124.268, 115.751, 127.97)), (' A 273  TYR  OH ', ' B 112  ASP  OD2', -0.484, (138.51, 168.59, 138.324)), (' B 178  PRO  O  ', ' C  27  LYS  HE2', -0.482, (157.873, 133.535, 169.056)), (' C  12  VAL HG12', ' G  91  LEU  HB2', -0.481, (136.423, 117.543, 173.861)), (' G 161  ASP  HA ', ' G 184  LEU  HB2', -0.478, (163.5, 121.26, 189.896)), (' G 124  THR  HA ', ' G 190  ARG  HB3', -0.473, (163.31, 114.599, 168.635)), (' B 159  VAL HG22', ' B 186  VAL HG22', -0.473, (155.99, 149.991, 166.108)), (' C  31  GLN HE22', ' G 119  ILE HD12', -0.472, (152.633, 126.215, 170.75)), (' G 125  ALA  HA ', ' G 189  LEU  HB3', -0.47, (166.261, 117.276, 171.22)), (' A 499  ASP  OD1', ' A 513  ARG  NH2', -0.461, (114.478, 140.167, 158.817)), (' G 121  PRO  HD2', ' G 128  LEU HD12', -0.46, (158.259, 117.505, 173.504)), (' A 497  ASN  ND2', ' A 497  ASN  O  ', -0.459, (116.759, 139.364, 152.082)), (' A 603  LYS  HA ', ' A 603  LYS  HD2', -0.459, (117.699, 114.978, 127.898)), (' A 694  PHE  HZ ', ' A 790  ASN HD21', -0.459, (137.319, 134.178, 133.178)), (' C  31  GLN HE21', ' G 119  ILE  CD1', -0.456, (151.659, 125.418, 170.321)), (' A 123  THR  HA ', ' A 211  ASP  HA ', -0.456, (158.696, 138.946, 112.749)), (' A 545  LYS  HB3', ' A 555  ARG  HB2', -0.455, (133.305, 131.186, 154.462)), (' A  91  LYS  HB2', ' A  91  LYS  HZ3', -0.455, (165.682, 151.899, 99.919)), (' A 844  VAL HG13', ' A 848  VAL  HB ', -0.45, (123.193, 122.892, 163.495)), (' B  88  GLN  O  ', ' B  92  PHE  HD2', -0.447, (126.042, 164.264, 162.541)), (' A  18  ARG  NH2', ' A  60  ASP  O  ', -0.446, (181.978, 135.428, 112.922)), (' A1004  H3U  N1 ', ' A1004  H3U  O24', -0.445, (131.646, 122.992, 148.595)), (' A 606  TYR  CE1', ' A 614  LEU HD21', -0.445, (124.247, 115.64, 127.716)), (' B 162  ALA  HB2', ' B 183  PRO  HD2', -0.443, (149.36, 140.204, 165.074)), (' B 132  ILE HD13', ' B 138  TYR  HD1', -0.442, (158.161, 147.061, 161.922)), (' A 790  ASN  HB3', ' A 792  VAL HG22', -0.439, (142.086, 132.963, 133.504)), (' A 390  ASP  OD2', ' A 674  TYR  OH ', -0.438, (145.484, 145.709, 155.956)), (' A 259  THR HG21', ' A 285  ARG  NH2', -0.437, (157.354, 158.359, 125.069)), (' A 249  ARG  O  ', ' A 252  THR  OG1', -0.436, (155.529, 147.433, 130.686)), (' A 726  ARG  NH1', ' A 744  GLU  OE1', -0.436, (125.674, 133.547, 107.057)), (' A 333  ILE HG13', ' A 342  VAL  CG2', -0.434, (130.366, 167.878, 148.363)), (' B  94  MET  HB3', ' B  94  MET  HE2', -0.432, (134.109, 159.671, 160.655)), (' A 497  ASN  ND2', ' A1003  H3U  O35', -0.431, (117.68, 139.168, 149.861)), (' A 848  VAL HG11', ' A 858  ARG  HD2', -0.43, (121.568, 121.596, 161.329)), (' A 847  ILE  O  ', ' A 850  THR  OG1', -0.428, (120.155, 127.136, 167.682)), (' A 549  SER  HA ', ' A1004  H3U  O23', -0.428, (133.174, 122.854, 152.059)), (' A1004  H3U  N1 ', ' A1004  H3U  O23', -0.426, (131.877, 123.468, 150.182)), (' A 755  MET  HG2', ' A 764  VAL HG12', -0.422, (128.008, 124.456, 126.35)), (' C  53  VAL HG13', ' G 106  ILE HD11', -0.42, (151.395, 113.75, 173.719)), (' A 500  LYS  NZ ', ' A 683  GLY  O  ', -0.416, (123.734, 139.798, 148.176)), (' A 259  THR HG21', ' A 285  ARG HH22', -0.414, (157.168, 158.875, 125.013)), (' A 411  LYS  HB2', ' A 411  LYS  HE3', -0.414, (132.747, 128.774, 165.961)), (' A 366  LEU  HA ', ' A 366  LEU HD12', -0.414, (121.184, 167.541, 153.733)), (' A  79  ASN  N  ', ' A  79  ASN  OD1', -0.412, (155.668, 139.463, 90.066)), (' C  18  GLN  NE2', ' C  23  GLU  OE2', -0.412, (136.587, 131.653, 170.713)), (' C  36  HIS  HD2', ' C  37  ASN HD22', -0.411, (141.665, 122.985, 161.462)), (' A 260  ASP  HB3', ' A 263  LYS  CG ', -0.407, (165.344, 157.749, 130.693)), (' A  77  PHE  HE1', ' A 103  LYS  NZ ', -0.404, (163.28, 141.091, 85.576)), (' C   3  MET  HE3', ' C   7  LYS  HE3', -0.401, (141.83, 111.791, 159.569)), (' A 601  MET  O  ', ' A 605  VAL HG23', -0.401, (119.887, 120.34, 129.661))]
data['smoc'] = [('B', 87, u'MET', 0.6427293958365421, (123.74900000000001, 158.68200000000002, 160.86800000000002)), ('B', 94, u'MET', 0.66743118336029, (134.11899999999997, 162.292, 161.56)), ('B', 114, u'CYS', 0.6738701142863152, (138.681, 168.732, 143.267)), ('B', 131, u'VAL', 0.5989795277315576, (151.27299999999997, 146.698, 159.95000000000002)), ('B', 142, u'CYS', 0.6994030892400609, (160.436, 151.30800000000002, 160.094)), ('B', 162, u'ALA', 0.7111721088428232, (148.691, 141.23299999999998, 167.538)), ('C', 4, u'SER', 0.6901961156347498, (136.872, 109.585, 161.98200000000003)), ('C', 8, u'CYS', 0.6678624060825281, (135.997, 114.26100000000001, 165.695)), ('C', 33, u'VAL', 0.6854190598059037, (144.62, 126.033, 164.44299999999998)), ('C', 52, u'MET', 0.6650086118769278, (146.754, 114.959, 168.606)), ('C', 64, u'GLY', 0.7202943197982373, (142.034, 122.585, 183.035)), ('G', 103, u'LEU', 0.7912556382540249, (147.30700000000002, 109.989, 174.792)), ('G', 107, u'ILE', 0.8473406966673305, (146.45700000000002, 111.96900000000001, 180.535)), ('G', 115, u'VAL', 0.7863529674461918, (151.82700000000003, 118.277, 183.467)), ('G', 120, u'ILE', 0.7429994077571848, (154.98600000000002, 118.587, 173.206)), ('G', 124, u'THR', 0.8224472423737673, (163.474, 115.52, 166.788)), ('G', 143, u'ASP', 0.7768509868918698, (165.21299999999997, 106.06400000000001, 184.98000000000002)), ('G', 165, u'LYS', 0.7564785681998588, (169.762, 126.26700000000001, 189.672)), ('G', 174, u'MET', 0.7550191157664635, (165.14299999999997, 109.23, 198.05200000000002)), ('G', 177, u'SER', 0.7368259356174216, (163.74399999999997, 114.32799999999999, 198.157)), ('G', 186, u'VAL', 0.7741706816412797, (162.865, 118.989, 183.37800000000001)), ('A', 6, u'SER', 0.7483081371805697, (176.469, 128.248, 93.66)), ('A', 12, u'CYS', 0.7753091023740882, (176.187, 136.593, 100.203)), ('A', 14, u'VAL', 0.6749546326087933, (174.79, 140.383, 97.088)), ('A', 40, u'ASP', 0.7739907455303064, (138.796, 134.698, 98.394)), ('A', 54, u'CYS', 0.6603498875582026, (165.126, 129.89700000000002, 101.71100000000001)), ('A', 61, u'GLU', 0.7290776976621102, (182.79399999999998, 137.57299999999998, 115.098)), ('A', 65, u'LEU', 0.7497494732557037, (174.937, 131.787, 115.008)), ('A', 69, u'TYR', 0.7256675765346567, (168.221, 135.593, 108.85199999999999)), ('A', 83, u'GLU', 0.6812075637513093, (157.63899999999998, 144.668, 94.918)), ('A', 84, u'GLU', 0.7458092951047623, (160.654, 146.67499999999998, 93.582)), ('A', 90, u'LEU', 0.7063698851490835, (159.266, 153.056, 101.163)), ('A', 110, u'MET', 0.7734224336687511, (166.761, 133.431, 84.979)), ('A', 114, u'ILE', 0.7533470327469476, (163.725, 138.76399999999998, 96.473)), ('A', 116, u'ARG', 0.711796662988119, (165.016, 140.177, 102.72)), ('A', 125, u'ALA', 0.5407052289836151, (152.393, 136.654, 114.402)), ('A', 126, u'ASP', 0.6181716659971724, (154.363, 133.811, 115.979)), ('A', 171, u'ILE', 0.6028910787411937, (156.07399999999998, 134.45100000000002, 134.718)), ('A', 196, u'MET', 0.6878509319328998, (152.761, 154.509, 103.48400000000001)), ('A', 201, u'ILE', 0.744991829778073, (150.187, 153.319, 99.251)), ('A', 210, u'GLN', 0.6018521389508535, (156.67399999999998, 142.16899999999998, 110.753)), ('A', 211, u'ASP', 0.61027800544667, (159.502, 140.47, 112.583)), ('A', 239, u'SER', 0.5726424853968316, (143.153, 144.042, 117.423)), ('A', 240, u'LEU', 0.6046247159969207, (144.94299999999998, 140.686, 117.254)), ('A', 254, u'GLU', 0.671868480153245, (155.904, 155.585, 129.409)), ('A', 259, u'THR', 0.6601905274112746, (160.11399999999998, 157.127, 127.903)), ('A', 270, u'LEU', 0.6910910626970342, (149.494, 164.102, 143.601)), ('A', 279, u'ARG', 0.589797857592894, (145.662, 159.53, 127.21600000000001)), ('A', 298, u'CYS', 0.5852799040599641, (133.461, 157.345, 128.32200000000003)), ('A', 308, u'LEU', 0.5883892917665303, (133.435, 148.865, 125.274)), ('A', 309, u'HIS', 0.6203578624558775, (135.76299999999998, 150.09, 122.527)), ('A', 315, u'VAL', 0.5622572064727865, (142.661, 149.88200000000003, 130.64899999999997)), ('A', 326, u'PHE', 0.5799272223210807, (141.86200000000002, 156.767, 140.752)), ('A', 330, u'VAL', 0.6653924750238799, (136.363, 164.751, 146.561)), ('A', 350, u'GLU', 0.5630275690534879, (138.177, 152.009, 132.445)), ('A', 352, u'GLY', 0.6099113909205206, (137.901, 158.02100000000002, 132.608)), ('A', 373, u'VAL', 0.671223937538774, (124.436, 159.23999999999998, 150.416)), ('A', 376, u'ALA', 0.6298416985198824, (127.609, 155.77499999999998, 152.36800000000002)), ('A', 382, u'ALA', 0.670587790426102, (138.911, 158.168, 154.724)), ('A', 388, u'LEU', 0.6222132089422725, (147.74099999999999, 153.062, 156.62800000000001)), ('A', 390, u'ASP', 0.6380564458470591, (149.814, 147.471, 155.36700000000002)), ('A', 448, u'ALA', 0.6446427793893187, (142.98700000000002, 134.79399999999998, 157.554)), ('A', 452, u'ASP', 0.6557792399985501, (142.166, 135.933, 151.722)), ('A', 453, u'TYR', 0.6906088570433061, (142.04, 139.562, 150.601)), ('A', 465, u'ASP', 0.5524971424579017, (140.781, 141.76299999999998, 121.366)), ('A', 475, u'VAL', 0.5840878491085477, (126.386, 136.691, 119.918)), ('A', 502, u'ALA', 0.6245553478357071, (123.585, 146.40800000000002, 154.97)), ('A', 519, u'MET', 0.6728287990698018, (112.783, 155.016, 153.509)), ('A', 525, u'ASP', 0.6583212917976847, (112.536, 156.52, 143.88400000000001)), ('A', 575, u'LEU', 0.6538390585096374, (115.273, 140.935, 134.22299999999998)), ('A', 576, u'LEU', 0.5827886583051306, (116.61, 138.74399999999997, 137.029)), ('A', 595, u'TYR', 0.7132730037415139, (109.87299999999999, 117.468, 140.526)), ('A', 678, u'GLY', 0.6097124900250901, (138.19899999999998, 144.207, 140.489)), ('A', 692, u'SER', 0.5364008537538095, (126.518, 133.45700000000002, 133.55)), ('A', 727, u'LEU', 0.59698140294188, (133.305, 135.053, 110.68599999999999)), ('A', 761, u'ASP', 0.6175324352656596, (129.292, 126.187, 136.085)), ('A', 789, u'GLN', 0.5541176750699075, (141.911, 136.535, 128.40200000000002)), ('A', 811, u'GLU', 0.6504857145267502, (129.389, 117.039, 137.86100000000002)), ('A', 831, u'TYR', 0.6875306767778553, (122.703, 112.87799999999999, 143.854)), ('A', 837, u'ILE', 0.6535815940999694, (125.83, 114.519, 153.312)), ('A', 885, u'LEU', 0.5924461461029056, (115.392, 108.54100000000001, 157.806)), ('A', 894, u'GLU', 0.8130505666124301, (111.71700000000001, 112.285, 171.041)), ('A', 912, u'THR', 0.7216060147179474, (102.513, 111.827, 151.806)), ('A', 1002, u'ZN', 0.6882430496164941, (115.85799999999999, 151.731, 132.74699999999999))]
data['rota'] = [('G', '  91 ', 'LEU', 0.21831506540302986, (136.01499999999993, 115.47200000000002, 175.167)), ('G', ' 103 ', 'LEU', 0.11402937723319936, (147.30699999999993, 109.98900000000002, 174.79200000000006)), ('A', '  84 ', 'GLU', 0.21270844879196965, (160.654, 146.67500000000007, 93.582)), ('A', '  91 ', 'LYS', 0.0, (163.021, 152.38800000000006, 101.548)), ('A', ' 153 ', 'ASP', 0.01630073950713958, (167.33599999999998, 131.139, 130.873)), ('A', ' 340 ', 'PHE', 0.1474223391584506, (132.313, 168.93600000000004, 154.76)), ('A', ' 495 ', 'VAL', 0.03754029750588505, (112.74900000000004, 141.71500000000003, 148.784)), ('A', ' 497 ', 'ASN', 0.016757048173674856, (115.34600000000005, 138.13200000000006, 152.765))]
data['clusters'] = [('B', '132', 1, 'side-chain clash', (158.161, 147.061, 161.922)), ('B', '138', 1, 'side-chain clash', (158.161, 147.061, 161.922)), ('B', '142', 1, 'smoc Outlier', (160.436, 151.30800000000002, 160.094)), ('B', '159', 1, 'side-chain clash', (155.99, 149.991, 166.108)), ('B', '186', 1, 'side-chain clash', (155.99, 149.991, 166.108)), ('B', '87', 2, 'smoc Outlier', (123.74900000000001, 158.68200000000002, 160.86800000000002)), ('B', '88', 2, 'side-chain clash', (126.042, 164.264, 162.541)), ('B', '91', 2, 'side-chain clash', (125.005, 162.263, 156.875)), ('B', '92', 2, 'side-chain clash', (126.042, 164.264, 162.541)), ('B', '112', 3, 'side-chain clash\nbackbone clash', (157.873, 133.535, 169.056)), ('B', '177', 3, 'Bond angle:CA:C', (161.47299999999998, 137.997, 167.01899999999998)), ('B', '178', 3, 'Bond angle:N', (160.291, 134.363, 167.476)), ('B', '162', 4, 'side-chain clash\nsmoc Outlier', (149.36, 140.204, 165.074)), ('B', '182', 4, 'cablam CA Geom Outlier', (153.6, 139.1, 164.7)), ('B', '183', 4, 'side-chain clash', (149.36, 140.204, 165.074)), ('B', '96', 5, 'Dihedral angle:CD:NE:CZ:NH1', (135.01399999999998, 167.105, 163.985)), ('B', '98', 5, 'side-chain clash', (139.362, 168.017, 159.708)), ('C', '29', 1, 'side-chain clash', (137.024, 112.192, 169.399)), ('C', '3', 1, 'side-chain clash', (141.83, 111.791, 159.569)), ('C', '4', 1, 'smoc Outlier', (136.872, 109.585, 161.98200000000003)), ('C', '7', 1, 'side-chain clash', (141.83, 111.791, 159.569)), ('C', '8', 1, 'smoc Outlier', (135.997, 114.26100000000001, 165.695)), ('C', '33', 2, 'smoc Outlier', (144.62, 126.033, 164.44299999999998)), ('C', '36', 2, 'side-chain clash', (141.665, 122.985, 161.462)), ('C', '37', 2, 'side-chain clash', (141.665, 122.985, 161.462)), ('C', '18', 3, 'side-chain clash', (136.587, 131.653, 170.713)), ('C', '23', 3, 'side-chain clash', (136.587, 131.653, 170.713)), ('C', '50', 4, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1', (151.225, 112.65299999999999, 166.727)), ('C', '52', 4, 'smoc Outlier', (146.754, 114.959, 168.606)), ('G', '131', 1, 'side-chain clash', (158.189, 122.538, 185.576)), ('G', '161', 1, 'side-chain clash', (163.5, 121.26, 189.896)), ('G', '184', 1, 'side-chain clash', (163.5, 121.26, 189.896)), ('G', '185', 1, 'side-chain clash', (158.189, 122.538, 185.576)), ('G', '186', 1, 'smoc Outlier', (162.865, 118.989, 183.37800000000001)), ('G', '124', 2, 'side-chain clash\nsmoc Outlier', (163.31, 114.599, 168.635)), ('G', '125', 2, 'side-chain clash', (166.261, 117.276, 171.22)), ('G', '189', 2, 'side-chain clash', (166.261, 117.276, 171.22)), ('G', '190', 2, 'side-chain clash', (163.31, 114.599, 168.635)), ('G', '106', 3, 'side-chain clash', (151.395, 113.75, 173.719)), ('G', '120', 3, 'smoc Outlier', (154.98600000000002, 118.587, 173.206)), ('G', '121', 3, 'side-chain clash', (158.259, 117.505, 173.504)), ('G', '128', 3, 'side-chain clash', (158.259, 117.505, 173.504)), ('G', '91', 4, 'Rotamer\nside-chain clash', (136.423, 117.543, 173.861)), ('G', '94', 4, 'side-chain clash', (137.024, 112.192, 169.399)), ('G', '174', 5, 'smoc Outlier', (165.14299999999997, 109.23, 198.05200000000002)), ('G', '177', 5, 'smoc Outlier', (163.74399999999997, 114.32799999999999, 198.157)), ('G', '168', 6, 'side-chain clash', (172.977, 115.713, 191.48)), ('G', '171', 6, 'side-chain clash', (172.977, 115.713, 191.48)), ('G', '100', 7, 'side-chain clash', (145.919, 108.533, 172.831)), ('G', '103', 7, 'Rotamer\nside-chain clash\nsmoc Outlier', (145.919, 108.533, 172.831)), ('A', '123', 1, 'side-chain clash', (158.696, 138.946, 112.749)), ('A', '125', 1, 'smoc Outlier', (152.393, 136.654, 114.402)), ('A', '126', 1, 'smoc Outlier', (154.363, 133.811, 115.979)), ('A', '128', 1, 'side-chain clash', (150.175, 139.499, 120.127)), ('A', '210', 1, 'smoc Outlier', (156.67399999999998, 142.16899999999998, 110.753)), ('A', '211', 1, 'side-chain clash\nsmoc Outlier', (158.696, 138.946, 112.749)), ('A', '239', 1, 'smoc Outlier', (143.153, 144.042, 117.423)), ('A', '240', 1, 'smoc Outlier', (144.94299999999998, 140.686, 117.254)), ('A', '242', 1, 'Bond angle:CA:C', (145.959, 143.877, 121.861)), ('A', '243', 1, 'Bond angle:N', (146.064, 141.16899999999998, 124.63)), ('A', '244', 1, 'side-chain clash', (150.175, 139.499, 120.127)), ('A', '465', 1, 'smoc Outlier', (140.781, 141.76299999999998, 121.366)), ('A', '18', 2, 'backbone clash', (181.978, 135.428, 112.922)), ('A', '60', 2, 'backbone clash', (181.978, 135.428, 112.922)), ('A', '61', 2, 'Dihedral angle:CB:CG:CD:OE1\nsmoc Outlier', (182.79399999999998, 137.57299999999998, 115.098)), ('A', '63', 2, 'cablam Outlier', (181.5, 130.9, 114.3)), ('A', '65', 2, 'smoc Outlier', (174.937, 131.787, 115.008)), ('A', '66', 2, 'side-chain clash', (171.497, 136.588, 113.144)), ('A', '67', 2, 'cablam Outlier', (169.2, 135.9, 115.2)), ('A', '68', 2, 'side-chain clash', (171.497, 136.588, 113.144)), ('A', '69', 2, 'smoc Outlier', (168.221, 135.593, 108.85199999999999)), ('A', '692', 3, 'smoc Outlier', (126.518, 133.45700000000002, 133.55)), ('A', '755', 3, 'side-chain clash', (128.008, 124.456, 126.35)), ('A', '759', 3, 'Bond angle:C\ncablam Outlier', (126.837, 131.054, 137.172)), ('A', '760', 3, 'Bond angle:N:CA\nBond angle:CA:CB:CG\ncablam Outlier', (130.29299999999998, 129.875, 135.955)), ('A', '761', 3, 'smoc Outlier', (129.292, 126.187, 136.085)), ('A', '762', 3, 'Dihedral angle:CA:C', (128.594, 124.65899999999999, 132.69299999999998)), ('A', '763', 3, 'Dihedral angle:N:CA', (127.971, 121.465, 130.823)), ('A', '764', 3, 'side-chain clash', (128.008, 124.456, 126.35)), ('A', '502', 4, 'smoc Outlier', (123.585, 146.40800000000002, 154.97)), ('A', '503', 4, 'side-chain clash', (126.797, 147.948, 152.561)), ('A', '507', 4, 'side-chain clash', (129.789, 145.719, 157.74)), ('A', '540', 4, 'side-chain clash', (131.512, 146.695, 147.662)), ('A', '541', 4, 'side-chain clash', (129.789, 145.719, 157.74)), ('A', '561', 4, 'side-chain clash', (126.797, 147.948, 152.561)), ('A', '665', 4, 'side-chain clash', (131.512, 146.695, 147.662)), ('A', '333', 5, 'side-chain clash', (117.68, 139.168, 149.861)), ('A', '342', 5, 'side-chain clash', (117.68, 139.168, 149.861)), ('A', '495', 5, 'Rotamer', (112.74900000000004, 141.71500000000003, 148.784)), ('A', '497', 5, 'Rotamer\nside-chain clash\nbackbone clash', (116.759, 139.364, 152.082)), ('A', '500', 5, 'backbone clash', (123.734, 139.798, 148.176)), ('A', '683', 5, 'backbone clash', (123.734, 139.798, 148.176)), ('A', '607', 6, 'cablam Outlier', (118.6, 119.1, 122.2)), ('A', '608', 6, 'cablam Outlier', (119.4, 117.7, 118.8)), ('A', '609', 6, 'Dihedral angle:CA:C', (123.151, 117.421, 118.912)), ('A', '610', 6, 'Dihedral angle:N:CA', (124.096, 114.768, 116.41700000000002)), ('A', '611', 6, 'Dihedral angle:CA:C', (127.37799999999999, 113.127, 117.51)), ('A', '612', 6, 'Dihedral angle:N:CA', (127.109, 114.086, 121.139)), ('A', '335', 7, 'Bond angle:C', (126.42, 172.095, 154.737)), ('A', '336', 7, 'Bond angle:N:CA', (124.773, 174.698, 157.076)), ('A', '340', 7, 'Rotamer', (132.313, 168.93600000000004, 154.76)), ('A', '365', 7, 'Dihedral angle:CD:NE:CZ:NH1', (119.523, 171.286, 155.64299999999997)), ('A', '366', 7, 'side-chain clash', (121.184, 167.541, 153.733)), ('A', '802', 7, 'side-chain clash', (130.751, 168.259, 158.095)), ('A', '114', 8, 'smoc Outlier', (163.725, 138.76399999999998, 96.473)), ('A', '116', 8, 'smoc Outlier', (165.016, 140.177, 102.72)), ('A', '217', 8, 'backbone clash', (159.903, 143.271, 101.789)), ('A', '74', 8, 'Dihedral angle:CD:NE:CZ:NH1', (161.411, 133.411, 94.209)), ('A', '99', 8, 'backbone clash', (159.903, 143.271, 101.789)), ('A', '388', 9, 'side-chain clash\nsmoc Outlier', (145.067, 151.592, 158.806)), ('A', '390', 9, 'side-chain clash\nsmoc Outlier', (145.484, 145.709, 155.956)), ('A', '397', 9, 'side-chain clash', (145.34, 150.308, 153.967)), ('A', '400', 9, 'side-chain clash', (145.067, 151.592, 158.806)), ('A', '674', 9, 'side-chain clash', (145.484, 145.709, 155.956)), ('A', '843', 10, 'Dihedral angle:CA:C', (129.15200000000002, 118.846, 161.989)), ('A', '844', 10, 'side-chain clash\nDihedral angle:N:CA', (126.604, 121.5, 162.756)), ('A', '848', 10, 'side-chain clash', (121.568, 121.596, 161.329)), ('A', '857', 10, 'Dihedral angle:CB:CG:CD:OE1', (114.549, 120.793, 159.311)), ('A', '858', 10, 'side-chain clash\nDihedral angle:CD:NE:CZ:NH1', (118.281, 120.37899999999999, 158.655)), ('A', '601', 11, 'side-chain clash', (119.887, 120.34, 129.661)), ('A', '603', 11, 'side-chain clash', (117.699, 114.978, 127.898)), ('A', '605', 11, 'side-chain clash', (119.887, 120.34, 129.661)), ('A', '606', 11, 'side-chain clash', (124.247, 115.64, 127.716)), ('A', '614', 11, 'side-chain clash', (124.247, 115.64, 127.716)), ('A', '474', 12, 'Dihedral angle:CB:CG:CD:OE1', (126.409, 140.48800000000003, 119.893)), ('A', '475', 12, 'smoc Outlier', (126.386, 136.691, 119.918)), ('A', '476', 12, 'side-chain clash', (127.77, 134.4, 124.931)), ('A', '696', 12, 'side-chain clash', (127.77, 134.4, 124.931)), ('A', '694', 13, 'side-chain clash', (137.319, 134.178, 133.178)), ('A', '789', 13, 'smoc Outlier', (141.911, 136.535, 128.40200000000002)), ('A', '790', 13, 'side-chain clash', (142.086, 132.963, 133.504)), ('A', '792', 13, 'side-chain clash', (142.086, 132.963, 133.504)), ('A', '298', 14, 'smoc Outlier', (133.461, 157.345, 128.32200000000003)), ('A', '315', 14, 'smoc Outlier', (142.661, 149.88200000000003, 130.64899999999997)), ('A', '350', 14, 'Dihedral angle:CB:CG:CD:OE1\nsmoc Outlier', (138.177, 152.009, 132.445)), ('A', '352', 14, 'smoc Outlier', (137.901, 158.02100000000002, 132.608)), ('A', '448', 15, 'smoc Outlier', (142.98700000000002, 134.79399999999998, 157.554)), ('A', '452', 15, 'smoc Outlier', (142.166, 135.933, 151.722)), ('A', '453', 15, 'smoc Outlier', (142.04, 139.562, 150.601)), ('A', '274', 16, 'cablam Outlier', (142.5, 164.3, 134.7)), ('A', '275', 16, 'cablam Outlier', (145.1, 162.7, 132.4)), ('A', '279', 16, 'smoc Outlier', (145.662, 159.53, 127.21600000000001)), ('A', '499', 17, 'side-chain clash', (114.478, 140.167, 158.817)), ('A', '513', 17, 'side-chain clash', (114.478, 140.167, 158.817)), ('A', '545', 18, 'side-chain clash', (133.305, 131.186, 154.462)), ('A', '555', 18, 'side-chain clash\nDihedral angle:CD:NE:CZ:NH1', (135.429, 131.511, 153.126)), ('A', '677', 19, 'cablam Outlier', (141.3, 145.9, 141.8)), ('A', '678', 19, 'cablam CA Geom Outlier\nsmoc Outlier', (138.2, 144.2, 140.5)), ('A', '260', 20, 'side-chain clash', (165.344, 157.749, 130.693)), ('A', '263', 20, 'side-chain clash', (165.344, 157.749, 130.693)), ('A', '575', 21, 'smoc Outlier', (115.273, 140.935, 134.22299999999998)), ('A', '576', 21, 'smoc Outlier', (116.61, 138.74399999999997, 137.029)), ('A', '373', 22, 'smoc Outlier', (124.436, 159.23999999999998, 150.416)), ('A', '376', 22, 'smoc Outlier', (127.609, 155.77499999999998, 152.36800000000002)), ('A', '912', 23, 'smoc Outlier', (102.513, 111.827, 151.806)), ('A', '919', 23, 'Dihedral angle:CB:CG:CD:OE1', (106.93900000000001, 108.667, 150.342)), ('A', '196', 24, 'smoc Outlier', (152.761, 154.509, 103.48400000000001)), ('A', '201', 24, 'smoc Outlier', (150.187, 153.319, 99.251)), ('A', '249', 25, 'side-chain clash', (155.529, 147.433, 130.686)), ('A', '252', 25, 'side-chain clash', (155.529, 147.433, 130.686)), ('A', '83', 26, 'smoc Outlier', (157.63899999999998, 144.668, 94.918)), ('A', '84', 26, 'Rotamer\nDihedral angle:CB:CG:CD:OE1\nsmoc Outlier', (160.654, 146.67499999999998, 93.582)), ('A', '254', 27, 'smoc Outlier', (155.904, 155.585, 129.409)), ('A', '259', 27, 'side-chain clash\nsmoc Outlier', (157.168, 158.875, 125.013)), ('A', '308', 28, 'smoc Outlier', (133.435, 148.865, 125.274)), ('A', '309', 28, 'smoc Outlier', (135.76299999999998, 150.09, 122.527)), ('A', '588', 29, 'side-chain clash', (121.544, 125.802, 136.581)), ('A', '758', 29, 'side-chain clash', (121.544, 125.802, 136.581)), ('A', '103', 30, 'side-chain clash', (163.28, 141.091, 85.576)), ('A', '77', 30, 'side-chain clash', (163.28, 141.091, 85.576)), ('A', '105', 31, 'Dihedral angle:CD:NE:CZ:NH1', (170.078, 131.431, 86.48700000000001)), ('A', '110', 31, 'smoc Outlier', (166.761, 133.431, 84.979)), ('A', '847', 32, 'side-chain clash', (133.174, 122.854, 152.059)), ('A', '850', 32, 'side-chain clash', (133.174, 122.854, 152.059)), ('A', '90', 33, 'smoc Outlier', (159.266, 153.056, 101.163)), ('A', '91', 33, 'Rotamer\nside-chain clash', (165.682, 151.899, 99.919)), ('A', '12', 34, 'smoc Outlier', (176.187, 136.593, 100.203)), ('A', '14', 34, 'smoc Outlier', (174.79, 140.383, 97.088)), ('A', '726', 35, 'side-chain clash', (125.674, 133.547, 107.057)), ('A', '744', 35, 'side-chain clash', (125.674, 133.547, 107.057)), ('A', '806', 36, 'Dihedral angle:CA:C', (123.06700000000001, 107.553, 129.306)), ('A', '807', 36, 'Dihedral angle:N:CA', (125.45400000000001, 108.44500000000001, 132.068))]
data['omega'] = [('B', ' 183 ', 'PRO', None, (151.603, 139.972, 163.54600000000005))]
data['cablam'] = [('B', '182', 'TRP', 'check CA trace', 'bend\nS-S-E', (153.6, 139.1, 164.7)), ('A', '63', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nSSS-E', (181.5, 130.9, 114.3)), ('A', '67', 'ASP', 'check CA trace,carbonyls, peptide', 'strand\nEEEEE', (169.2, 135.9, 115.2)), ('A', '274', 'ASP', 'check CA trace,carbonyls, peptide', ' \n----H', (142.5, 164.3, 134.7)), ('A', '275', 'PHE', 'check CA trace,carbonyls, peptide', ' \n---HH', (145.1, 162.7, 132.4)), ('A', '607', 'SER', 'check CA trace,carbonyls, peptide', 'bend\nHSSS-', (118.6, 119.1, 122.2)), ('A', '608', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nSSS-S', (119.4, 117.7, 118.8)), ('A', '677', 'PRO', 'check CA trace,carbonyls, peptide', ' \nE--S-', (141.3, 145.9, 141.8)), ('A', '759', 'SER', 'check CA trace,carbonyls, peptide', 'turn\nEETTE', (126.8, 131.1, 137.2)), ('A', '760', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (130.3, 129.9, 136.0)), ('A', '326', 'PHE', 'check CA trace', ' \nGG-EE', (141.9, 156.8, 140.8)), ('A', '678', 'GLY', 'check CA trace', 'bend\n--S--', (138.2, 144.2, 140.5))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-30572/7d4f/Model_validation_1/validation_cootdata/molprobity_probe7d4f_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)
