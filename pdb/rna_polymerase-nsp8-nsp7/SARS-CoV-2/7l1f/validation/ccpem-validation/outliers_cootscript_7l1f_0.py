
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
data['rota'] = []
data['jpred'] = []
data['probe'] = [(' A 389  LEU  HB3', ' C 130  VAL HG22', -0.583, (191.515, 149.133, 179.235)), (' A 292  GLN  HB3', ' A 309  HIS  HE1', -0.569, (160.036, 171.968, 197.128)), (' D   4  SER  HA ', ' D   7  LYS  HD2', -0.559, (204.833, 185.161, 154.786)), (' A 569  ARG  O  ', ' A 573  GLN  HB2', -0.537, (158.5, 171.82, 163.211)), (' A 202  VAL HG22', ' A 231  VAL  H  ', -0.533, (157.441, 177.872, 214.371)), (' A 536  ILE  O  ', ' A 661  GLN  NE2', -0.527, (166.502, 159.024, 172.546)), (' A 181  ARG  NH2', ' A 213  ASN  OD1', -0.522, (187.298, 174.883, 212.188)), (' A 591  THR HG23', ' A 601  MET  HE1', -0.519, (168.832, 192.345, 161.245)), (' A 197  ARG  NH2', ' A 198  ASN  OD1', -0.507, (161.125, 167.454, 217.698)), (' A 715  ILE  O  ', ' A 721  ARG  NH2', -0.498, (168.736, 205.394, 197.639)), (' P  12    U  O4 ', ' T   6    A  N6 ', -0.497, (172.961, 181.351, 148.742)), (' A 778  SER  OG ', ' A 779  ILE  N  ', -0.497, (180.968, 196.337, 183.626)), (' A 755  MET  HG2', ' A 764  VAL HG12', -0.488, (171.983, 194.266, 175.864)), (' A 311  ALA  HB1', ' A 350  GLU  HB3', -0.487, (167.375, 167.251, 186.554)), (' A 825  ASP  N  ', ' A 825  ASP  OD1', -0.482, (171.038, 211.459, 153.166)), (' A 377  ASP  HA ', ' A 537  PRO  HG2', -0.479, (168.668, 153.134, 171.001)), (' A 857  GLU  HA ', ' A 860  VAL HG22', -0.474, (180.494, 186.595, 141.547)), (' C 112  ASP  N  ', ' C 112  ASP  OD1', -0.473, (163.964, 142.978, 188.05)), (' A 516  TYR  OH ', ' A 569  ARG  NH1', -0.472, (162.435, 166.405, 158.785)), (' A 806  THR  OG1', ' A 807  LYS  N  ', -0.47, (180.841, 208.56, 166.071)), (' A 846  ASP  HB3', ' A 849  LYS  HG3', -0.465, (187.863, 173.919, 145.586)), (' A 140  ASP  N  ', ' A 140  ASP  OD2', -0.465, (191.881, 190.565, 198.935)), (' A 459  ASN  ND2', ' A 678  GLY  O  ', -0.461, (178.862, 168.99, 179.803)), (' C  87  MET  HB3', ' C  87  MET  HE2', -0.453, (165.082, 147.132, 158.228)), (' A 452  ASP  OD2', ' A 624  ARG  NH2', -0.451, (185.693, 169.746, 169.53)), (' C 134  ASP  N  ', ' C 134  ASP  OD1', -0.45, (202.164, 157.286, 178.272)), (' A 144  GLU  HA ', ' A 147  VAL HG22', -0.447, (196.169, 183.662, 203.754)), (' A 527  LEU HD23', ' A 566  MET  HE1', -0.445, (158.788, 159.019, 163.166)), (' A 497  ASN  HB2', ' A 500  LYS  HE2', -0.445, (169.668, 170.621, 153.677)), (' A 194  ASP  O  ', ' A 198  ASN  ND2', -0.445, (164.373, 168.561, 217.838)), (' D  61  SER  OG ', ' D  62  MET  SD ', -0.445, (213.132, 163.511, 153.651)), (' A 589  ILE HG21', ' A 689  TYR  HE2', -0.442, (166.766, 182.818, 165.645)), (' A  88  ASN  O  ', ' A  91  LYS  NZ ', -0.442, (168.624, 175.981, 230.398)), (' A 371  LEU HD13', ' C  87  MET  HE1', -0.441, (162.058, 146.529, 159.817)), (' A 505  PRO  HD3', ' A 539  ILE HD13', -0.438, (172.421, 154.091, 165.938)), (' A 206  THR  OG1', ' A 209  ASN  OD1', -0.434, (171.832, 184.967, 211.788)), (' A 428  PHE  HE2', ' A 883  LEU  HB2', -0.432, (195.93, 196.679, 144.306)), (' A 537  PRO  HA ', ' A 661  GLN HE22', -0.432, (167.904, 157.98, 172.706)), (' A 612  PRO  HG2', ' A 805  LEU HD13', -0.43, (174.639, 207.249, 172.021)), (' A 708  LEU  HA ', ' A 724  GLN HE22', -0.43, (170.231, 194.249, 195.489)), (' A 260  ASP  HB3', ' A 263  LYS  HD2', -0.427, (185.813, 155.311, 209.025)), (' C 104  ASN  HA ', ' C 107  ILE HG22', -0.426, (169.803, 135.502, 181.611)), (' A  40  ASP  N  ', ' A  40  ASP  OD1', -0.424, (162.875, 197.643, 207.289)), (' A 606  TYR  HE1', ' A 614  LEU HD21', -0.423, (174.997, 202.549, 171.077)), (' A 705  ASN  ND2', ' A 788  TYR  OH ', -0.42, (174.747, 185.871, 190.355)), (' A 189  THR HG22', ' A 216  TRP  HE1', -0.42, (174.221, 175.563, 211.544)), (' A 221  ASP  N  ', ' A 221  ASP  OD1', -0.42, (166.573, 186.855, 216.467)), (' A 628  ASN  HB3', ' A 663  LEU HD21', -0.412, (171.642, 168.527, 182.339)), (' C 159  VAL HG13', ' C 186  VAL HG12', -0.405, (200.197, 146.966, 174.175)), (' A 303  ASP  N  ', ' A 303  ASP  OD1', -0.403, (153.746, 170.422, 188.96)), (' A 330  VAL HG22', ' C 115  VAL  H  ', -0.4, (168.458, 144.925, 183.069)), (' A 701  THR  HA ', ' A 704  VAL HG12', -0.4, (169.382, 187.94, 187.119)), (' A 540  THR  OG1', ' A 665  GLU  OE2', -0.4, (173.737, 162.374, 169.807))]
data['cbeta'] = [('A', ' 144 ', 'GLU', ' ', 0.2695146145193747, (194.33999999999997, 185.66799999999998, 205.03399999999993)), ('A', ' 304 ', 'ASP', ' ', 0.2500212513698436, (155.5279999999999, 173.08900000000003, 184.033)), ('A', ' 698 ', 'GLN', ' ', 0.25687760894183087, (174.61999999999995, 185.03500000000003, 181.444))]
data['smoc'] = [('A', 34, u'ALA', 0.6281966041922965, (179.23499999999999, 190.287, 203.966)), ('A', 35, u'PHE', 0.6783142290378418, (175.71899999999997, 190.17899999999997, 205.412)), ('A', 40, u'ASP', 0.7011293939816543, (162.01399999999998, 197.181, 205.606)), ('A', 44, u'GLY', 0.7154520784581151, (169.99200000000002, 192.405, 199.606)), ('A', 91, u'LYS', 0.711740508117633, (172.333, 175.102, 226.804)), ('A', 119, u'LEU', 0.648777037464391, (185.261, 181.512, 217.51899999999998)), ('A', 128, u'VAL', 0.7807289709818998, (179.972, 182.394, 200.196)), ('A', 132, u'ARG', 0.7685128742869035, (180.45200000000003, 184.94299999999998, 194.121)), ('A', 139, u'CYS', 0.8044325812368636, (191.112, 189.282, 196.208)), ('A', 144, u'GLU', 0.7932494868601486, (194.29299999999998, 184.687, 203.835)), ('A', 153, u'ASP', 0.6630462563957865, (201.541, 177.823, 201.36700000000002)), ('A', 161, u'ASP', 0.694054099536233, (198.51, 182.91299999999998, 186.155)), ('A', 173, u'ARG', 0.7604654338463057, (192.73999999999998, 170.4, 194.126)), ('A', 176, u'ALA', 0.819612755867944, (188.782, 170.55100000000002, 197.226)), ('A', 180, u'GLU', 0.767795495051248, (184.813, 168.39700000000002, 205.197)), ('A', 183, u'ARG', 0.7103362116532251, (179.845, 168.804, 205.954)), ('A', 191, u'GLN', 0.7478778149196739, (171.474, 169.151, 214.978)), ('A', 197, u'ARG', 0.7136419938594949, (161.67499999999998, 171.916, 216.687)), ('A', 206, u'THR', 0.6999637357891727, (170.55700000000002, 183.748, 208.61399999999998)), ('A', 218, u'ASP', 0.6370171921167241, (173.98800000000003, 185.231, 216.905)), ('A', 225, u'THR', 0.6663353342893549, (155.38100000000003, 178.77399999999997, 221.02800000000002)), ('A', 226, u'THR', 0.698913758299389, (153.92600000000002, 175.373, 221.99800000000002)), ('A', 235, u'ASP', 0.7181942784543569, (164.833, 178.923, 202.553)), ('A', 239, u'SER', 0.7071879983016977, (169.10399999999998, 178.627, 198.65)), ('A', 242, u'MET', 0.6190570069982589, (173.784, 175.92800000000003, 196.647)), ('A', 254, u'GLU', 0.7623202474658793, (179.606, 159.76899999999998, 201.816)), ('A', 259, u'THR', 0.7562678434651426, (181.781, 158.478, 207.303)), ('A', 277, u'GLU', 0.7311649261089062, (164.914, 154.441, 199.84)), ('A', 278, u'GLU', 0.7749684325171377, (168.467, 155.379, 200.829)), ('A', 284, u'ASP', 0.5931488038707466, (165.812, 163.348, 205.37800000000001)), ('A', 285, u'ARG', 0.6789218101574682, (169.3, 163.265, 206.912)), ('A', 299, u'VAL', 0.7295502310033919, (156.65, 161.334, 186.611)), ('A', 307, u'ILE', 0.670565992625424, (160.48600000000002, 169.424, 187.791)), ('A', 308, u'LEU', 0.6710319378984066, (163.21699999999998, 172.072, 188.17899999999997)), ('A', 310, u'CYS', 0.6555255110234008, (163.54299999999998, 167.82800000000003, 191.85500000000002)), ('A', 328, u'PRO', 0.662802157827386, (169.38400000000001, 152.871, 180.32600000000002)), ('A', 377, u'ASP', 0.655699364200226, (168.83100000000002, 151.655, 170.071)), ('A', 385, u'GLY', 0.7431661524393135, (181.537, 144.996, 171.79299999999998)), ('A', 390, u'ASP', 0.6652709616955871, (190.98100000000002, 154.469, 178.137)), ('A', 413, u'GLY', 0.664899451372272, (195.097, 174.13899999999998, 152.011)), ('A', 416, u'ASN', 0.6870221621794265, (196.508, 180.843, 144.453)), ('A', 446, u'GLY', 0.5889664730478144, (195.959, 162.154, 163.74299999999997)), ('A', 483, u'TYR', 0.7274264783765667, (154.548, 184.976, 169.07399999999998)), ('A', 484, u'ASP', 0.7350019406039706, (152.194, 182.132, 168.178)), ('A', 488, u'ILE', 0.7195140195445475, (151.42000000000002, 170.49800000000002, 163.87)), ('A', 496, u'ASN', 0.7347523758899122, (164.664, 173.04299999999998, 154.064)), ('A', 515, u'TYR', 0.631665522344301, (163.813, 158.313, 155.684)), ('A', 522, u'GLU', 0.6297894861953077, (149.39000000000001, 158.36700000000002, 159.577)), ('A', 532, u'LYS', 0.7142139794339368, (154.46200000000002, 160.641, 174.10399999999998)), ('A', 558, u'ALA', 0.6074000356511705, (178.474, 167.278, 166.22899999999998)), ('A', 559, u'GLY', 0.6090753278033216, (175.92100000000002, 165.181, 164.34)), ('A', 567, u'THR', 0.7323301534668961, (159.93800000000002, 164.365, 166.345)), ('A', 589, u'ILE', 0.7382093949324869, (168.07399999999998, 186.567, 164.11299999999997)), ('A', 601, u'MET', 0.7666095117377058, (169.642, 197.93200000000002, 163.508)), ('A', 609, u'VAL', 0.7361989872088781, (168.512, 206.035, 176.131)), ('A', 618, u'ASP', 0.643652757292978, (182.311, 186.55100000000002, 173.51399999999998)), ('A', 635, u'SER', 0.767278351770464, (164.26, 173.812, 176.989)), ('A', 641, u'LYS', 0.7385784421243308, (152.71599999999998, 177.39000000000001, 174.157)), ('A', 651, u'ARG', 0.6912642060330575, (155.26299999999998, 167.289, 177.561)), ('A', 658, u'GLU', 0.6739467379901202, (165.034, 166.11899999999997, 174.849)), ('A', 665, u'GLU', 0.7149347262657098, (173.80200000000002, 160.906, 175.30100000000002)), ('A', 668, u'MET', 0.7272452297182107, (180.80800000000002, 158.353, 169.789)), ('A', 694, u'PHE', 0.7445758127812455, (170.974, 181.19899999999998, 177.258)), ('A', 703, u'ASN', 0.7963776091634696, (171.343, 192.607, 186.105)), ('A', 714, u'LYS', 0.7103339845213221, (173.17899999999997, 205.686, 198.418)), ('A', 726, u'ARG', 0.6489013001847053, (159.798, 193.995, 196.181)), ('A', 730, u'CYS', 0.683650708956804, (159.471, 188.21699999999998, 195.395)), ('A', 731, u'LEU', 0.7013026769109212, (162.44899999999998, 185.875, 195.441)), ('A', 749, u'LEU', 0.7508760949836552, (165.067, 196.135, 181.44899999999998)), ('A', 750, u'ARG', 0.6956922194129957, (163.51299999999998, 197.141, 178.129)), ('A', 756, u'MET', 0.7627787691091703, (170.58700000000002, 192.96200000000002, 170.531)), ('A', 759, u'SER', 0.7596003459603801, (173.265, 183.531, 169.706)), ('A', 760, u'ASP', 0.7078241149484631, (176.629, 184.445, 171.248)), ('A', 775, u'LEU', 0.7187369056897015, (172.089, 200.258, 189.184)), ('A', 782, u'PHE', 0.7088118113774047, (179.648, 189.569, 184.083)), ('A', 794, u'MET', 0.6885563979906137, (186.75, 185.607, 180.766)), ('A', 825, u'ASP', 0.7072243291588075, (171.791, 212.01, 154.757)), ('A', 826, u'TYR', 0.7601555450648168, (174.26, 209.702, 156.52100000000002)), ('A', 831, u'TYR', 0.7181168688607753, (183.135, 197.277, 156.668)), ('A', 842, u'CYS', 0.7097871098145936, (194.71499999999997, 183.6, 147.722)), ('A', 845, u'ASP', 0.719995063336722, (190.66899999999998, 174.911, 149.85000000000002)), ('A', 851, u'ASP', 0.5807438607830596, (188.472, 177.095, 137.67)), ('A', 871, u'LYS', 0.7137546969557761, (185.146, 206.037, 151.82600000000002)), ('A', 911, u'ASN', 0.15543244389354827, (176.667, 201.39600000000002, 134.523)), ('A', 912, u'THR', 0.1264979824660677, (173.66299999999998, 200.635, 136.755)), ('A', 924, u'MET', 0.7834732790929054, (173.089, 197.43800000000002, 146.7)), ('A', 929, u'THR', 0.7129205266314338, (164.36100000000002, 198.18800000000002, 147.39800000000002)), ('C', 78, u'ASP', 0.3987602572297166, (160.997, 148.924, 146.636)), ('C', 99, u'ASP', 0.47864841597078434, (172.42100000000002, 134.38200000000003, 171.996)), ('C', 111, u'ARG', 0.5336814220202586, (164.606, 141.011, 190.76)), ('C', 117, u'LEU', 0.7254496229936855, (173.155, 148.611, 180.74899999999997)), ('C', 124, u'THR', 0.7896485071895019, (180.55100000000002, 139.329, 180.255)), ('C', 127, u'LYS', 0.7156205939458185, (188.186, 140.848, 175.553)), ('C', 134, u'ASP', 0.6968448871463806, (203.732, 156.792, 177.072)), ('C', 139, u'LYS', 0.7234118100299765, (204.88700000000003, 151.507, 184.42000000000002)), ('C', 141, u'THR', 0.7069628473198256, (199.313, 150.221, 184.61499999999998)), ('C', 149, u'TYR', 0.7861425654381291, (191.164, 145.064, 186.19)), ('C', 155, u'GLU', 0.6182240989768172, (196.64399999999998, 137.60899999999998, 179.80200000000002)), ('C', 158, u'GLN', 0.7103720272323159, (199.18, 141.45100000000002, 171.171)), ('C', 165, u'LYS', 0.6129917424239247, (202.829, 146.086, 163.727)), ('C', 175, u'ASP', 0.6891431248807587, (216.54399999999998, 152.86, 176.627)), ('D', 8, u'CYS', 0.6876862390774792, (203.782, 180.994, 150.583)), ('D', 21, u'ARG', 0.6689575751963295, (202.36200000000002, 160.248, 150.485)), ('D', 31, u'GLN', 0.6481229786870505, (207.539, 167.259, 163.80800000000002)), ('D', 32, u'CYS', 0.6441100834648065, (207.077, 168.68, 160.27899999999997)), ('D', 38, u'ASP', 0.6945264725428509, (206.29399999999998, 177.435, 164.108)), ('D', 60, u'LEU', 0.534753181547188, (215.07899999999998, 167.319, 149.30200000000002)), ('P', 10, u'U', 0.6761815921000675, (171.033, 173.72899999999998, 141.262)), ('T', 12, u'U', 0.6679994158855119, (156.072, 178.037, 135.809)), ('T', 15, u'U', 0.6117967725950364, (149.685, 191.553, 135.025))]
data['clusters'] = [('A', '377', 1, 'side-chain clash\nsmoc Outlier', (168.668, 153.134, 171.001)), ('A', '452', 1, 'side-chain clash', (185.693, 169.746, 169.53)), ('A', '502', 1, 'cablam Outlier', (171.6, 160.6, 158.5)), ('A', '504', 1, 'cablam CA Geom Outlier', (174.5, 156.3, 163.3)), ('A', '505', 1, 'side-chain clash', (172.421, 154.091, 165.938)), ('A', '507', 1, 'cablam Outlier', (173.8, 156.4, 157.8)), ('A', '527', 1, 'side-chain clash', (158.788, 159.019, 163.166)), ('A', '536', 1, 'side-chain clash', (166.502, 159.024, 172.546)), ('A', '537', 1, 'side-chain clash', (167.904, 157.98, 172.706)), ('A', '539', 1, 'side-chain clash', (172.421, 154.091, 165.938)), ('A', '540', 1, 'side-chain clash', (173.737, 162.374, 169.807)), ('A', '555', 1, 'Dihedral angle:CA:C', (186.712, 172.38600000000002, 166.009)), ('A', '556', 1, 'Bond angle:C\nDihedral angle:CA:C\nDihedral angle:N:CA\ncablam Outlier', (185.125, 169.283, 164.684)), ('A', '557', 1, 'Bond angle:N:CA\nBond angle:N:CA:CB\nBond angle:CA:CB:CG1\nDihedral angle:N:CA\nDihedral angle:CA:C\ncablam Outlier', (181.22899999999998, 168.93200000000002, 164.24599999999998)), ('A', '558', 1, 'Dihedral angle:N:CA\nsmoc Outlier', (178.474, 167.278, 166.22899999999998)), ('A', '559', 1, 'smoc Outlier', (175.92100000000002, 165.181, 164.34)), ('A', '562', 1, 'Dihedral angle:CA:C', (167.135, 161.26299999999998, 162.39700000000002)), ('A', '563', 1, 'Dihedral angle:N:CA', (164.411, 160.206, 164.829)), ('A', '566', 1, 'side-chain clash', (158.788, 159.019, 163.166)), ('A', '567', 1, 'smoc Outlier', (159.93800000000002, 164.365, 166.345)), ('A', '623', 1, 'Dihedral angle:CA:CB:CG:OD1', (180.068, 174.82500000000002, 173.39000000000001)), ('A', '624', 1, 'side-chain clash', (185.693, 169.746, 169.53)), ('A', '658', 1, 'smoc Outlier', (165.034, 166.11899999999997, 174.849)), ('A', '661', 1, 'side-chain clash\nBond angle:CB:CG:CD', (169.20299999999997, 163.453, 173.372)), ('A', '665', 1, 'side-chain clash\nsmoc Outlier', (173.737, 162.374, 169.807)), ('A', '680', 1, 'Dihedral angle:CA:C', (174.972, 171.564, 174.124)), ('A', '681', 1, 'Dihedral angle:N:CA', (175.627, 169.42000000000002, 171.12800000000001)), ('A', '682', 1, 'cablam Outlier', (176.5, 171.5, 168.1)), ('A', '235', 2, 'smoc Outlier', (164.833, 178.923, 202.553)), ('A', '239', 2, 'smoc Outlier', (169.10399999999998, 178.627, 198.65)), ('A', '242', 2, 'Bond angle:CB:CG:SD\nBond angle:CA:C\nsmoc Outlier', (173.784, 175.92800000000003, 196.647)), ('A', '243', 2, 'Bond angle:N\ncablam Outlier', (176.411, 176.997, 194.006)), ('A', '304', 2, 'C-beta\nBond angle:CA:CB:CG\nBond angle:C:CA:CB\nBond angle:CB:CG:OD1', (156.10299999999998, 172.45600000000002, 185.32800000000003)), ('A', '307', 2, 'smoc Outlier', (160.48600000000002, 169.424, 187.791)), ('A', '308', 2, 'smoc Outlier', (163.21699999999998, 172.072, 188.17899999999997)), ('A', '310', 2, 'smoc Outlier', (163.54299999999998, 167.82800000000003, 191.85500000000002)), ('A', '311', 2, 'side-chain clash', (167.375, 167.251, 186.554)), ('A', '350', 2, 'side-chain clash', (167.375, 167.251, 186.554)), ('A', '351', 2, 'cablam Outlier', (164.9, 163.8, 186.1)), ('A', '463', 2, 'Dihedral angle:CA:C', (173.819, 173.32500000000002, 190.535)), ('A', '464', 2, 'Dihedral angle:N:CA', (172.191, 176.70499999999998, 190.945)), ('A', '628', 2, 'side-chain clash', (171.642, 168.527, 182.339)), ('A', '629', 2, 'Bond angle:CB:CG:SD', (170.092, 173.224, 184.778)), ('A', '663', 2, 'side-chain clash', (171.642, 168.527, 182.339)), ('A', '618', 3, 'smoc Outlier', (182.311, 186.55100000000002, 173.51399999999998)), ('A', '620', 3, 'cablam Outlier', (185.1, 181.5, 176.3)), ('A', '755', 3, 'side-chain clash', (171.983, 194.266, 175.864)), ('A', '756', 3, 'smoc Outlier', (170.58700000000002, 192.96200000000002, 170.531)), ('A', '758', 3, 'Bond angle:C', (172.369, 186.771, 167.894)), ('A', '759', 3, 'Bond angle:N:CA\nsmoc Outlier', (173.265, 183.531, 169.706)), ('A', '760', 3, 'Dihedral angle:CA:C\nsmoc Outlier', (176.629, 184.445, 171.248)), ('A', '761', 3, 'Dihedral angle:N:CA', (177.34, 188.054, 170.502)), ('A', '762', 3, 'Dihedral angle:CA:C', (175.665, 191.089, 171.961)), ('A', '763', 3, 'Dihedral angle:N:CA', (175.777, 194.805, 171.976)), ('A', '764', 3, 'side-chain clash', (171.983, 194.266, 175.864)), ('A', '778', 3, 'backbone clash', (180.968, 196.337, 183.626)), ('A', '779', 3, 'backbone clash\ncablam Outlier', (180.968, 196.337, 183.626)), ('A', '782', 3, 'smoc Outlier', (179.648, 189.569, 184.083)), ('A', '783', 3, 'Bond angle:CA:CB:CG', (183.14399999999998, 188.502, 185.228)), ('A', '794', 3, 'smoc Outlier', (186.75, 185.607, 180.766)), ('A', '128', 4, 'smoc Outlier', (179.972, 182.394, 200.196)), ('A', '132', 4, 'smoc Outlier', (180.45200000000003, 184.94299999999998, 194.121)), ('A', '694', 4, 'smoc Outlier', (170.974, 181.19899999999998, 177.258)), ('A', '698', 4, 'C-beta\nside-chain clash\nBond angle:CB:CG:CD', (173.185, 185.409, 181.845)), ('A', '701', 4, 'side-chain clash', (169.382, 187.94, 187.119)), ('A', '703', 4, 'smoc Outlier', (171.343, 192.607, 186.105)), ('A', '704', 4, 'side-chain clash', (169.382, 187.94, 187.119)), ('A', '705', 4, 'side-chain clash', (174.747, 185.871, 190.355)), ('A', '788', 4, 'side-chain clash', (174.747, 185.871, 190.355)), ('A', '411', 5, 'Bond angle:CB:CG:CD', (194.312, 168.42000000000002, 155.35000000000002)), ('A', '413', 5, 'smoc Outlier', (195.097, 174.13899999999998, 152.011)), ('A', '845', 5, 'smoc Outlier', (190.66899999999998, 174.911, 149.85000000000002)), ('A', '846', 5, 'side-chain clash', (187.863, 173.919, 145.586)), ('A', '849', 5, 'side-chain clash', (187.863, 173.919, 145.586)), ('A', '850', 5, 'Dihedral angle:CA:C', (190.786, 177.14399999999998, 140.676)), ('A', '851', 5, 'Dihedral angle:N:CA\nsmoc Outlier', (188.472, 177.095, 137.67)), ('A', '206', 6, 'side-chain clash\nsmoc Outlier', (171.832, 184.967, 211.788)), ('A', '209', 6, 'side-chain clash', (171.832, 184.967, 211.788)), ('A', '218', 6, 'smoc Outlier', (173.98800000000003, 185.231, 216.905)), ('A', '219', 6, 'cablam CA Geom Outlier', (170.5, 185.0, 218.4)), ('A', '220', 6, 'cablam Outlier', (168.1, 187.7, 219.4)), ('A', '221', 6, 'side-chain clash', (166.573, 186.855, 216.467)), ('A', '254', 7, 'smoc Outlier', (179.606, 159.76899999999998, 201.816)), ('A', '257', 7, 'cablam Outlier', (182.3, 153.0, 204.9)), ('A', '258', 7, 'Dihedral angle:CA:C\ncablam CA Geom Outlier', (180.751, 154.82800000000003, 207.87)), ('A', '259', 7, 'Dihedral angle:N:CA\nsmoc Outlier', (181.781, 158.478, 207.303)), ('A', '260', 7, 'side-chain clash', (185.813, 155.311, 209.025)), ('A', '263', 7, 'side-chain clash', (185.813, 155.311, 209.025)), ('A', '173', 8, 'smoc Outlier', (192.73999999999998, 170.4, 194.126)), ('A', '176', 8, 'smoc Outlier', (188.782, 170.55100000000002, 197.226)), ('A', '178', 8, 'Dihedral angle:CA:C', (187.58700000000002, 172.671, 202.189)), ('A', '179', 8, 'Dihedral angle:N:CA', (184.562, 170.38100000000003, 201.965)), ('A', '180', 8, 'smoc Outlier', (184.813, 168.39700000000002, 205.197)), ('A', '183', 8, 'smoc Outlier', (179.845, 168.804, 205.954)), ('A', '34', 9, 'smoc Outlier', (179.23499999999999, 190.287, 203.966)), ('A', '35', 9, 'smoc Outlier', (175.71899999999997, 190.17899999999997, 205.412)), ('A', '44', 9, 'smoc Outlier', (169.99200000000002, 192.405, 199.606)), ('A', '45', 9, 'cablam Outlier', (173.4, 190.7, 199.9)), ('A', '708', 9, 'side-chain clash', (170.231, 194.249, 195.489)), ('A', '724', 9, 'side-chain clash', (170.231, 194.249, 195.489)), ('A', '139', 10, 'cablam Outlier\nsmoc Outlier', (191.1, 189.3, 196.2)), ('A', '140', 10, 'side-chain clash\nDihedral angle:CA:CB:CG:OD1', (193.14899999999997, 189.465, 199.41299999999998)), ('A', '143', 10, 'Bond angle:C', (194.09, 184.69, 200.026)), ('A', '144', 10, 'C-beta\nside-chain clash\nBond angle:N:CA:CB\nBond angle:N:CA\nBond angle:CA:CB:CG\nsmoc Outlier', (194.29299999999998, 184.687, 203.835)), ('A', '147', 10, 'side-chain clash', (196.169, 183.662, 203.754)), ('A', '583', 11, 'Dihedral angle:CD:NE:CZ:NH1', (161.14399999999998, 192.38500000000002, 161.939)), ('A', '591', 11, 'side-chain clash\nDihedral angle:CA:C', (166.863, 190.01, 159.667)), ('A', '592', 11, 'Dihedral angle:N:CA', (169.483, 191.195, 157.25)), ('A', '594', 11, 'cablam Outlier', (171.7, 194.7, 153.5)), ('A', '601', 11, 'side-chain clash\nsmoc Outlier', (168.832, 192.345, 161.245)), ('A', '429', 12, 'cablam Outlier', (203.2, 193.7, 149.1)), ('A', '430', 12, 'Dihedral angle:CA:C', (206.101, 195.68, 150.434)), ('A', '431', 12, 'Dihedral angle:N:CA', (207.736, 195.751, 153.819)), ('A', '434', 12, 'cablam Outlier', (201.2, 196.9, 157.1)), ('A', '435', 12, 'Bond angle:CG1:CB:CG2', (200.994, 195.632, 153.455)), ('A', '496', 13, 'smoc Outlier', (164.664, 173.04299999999998, 154.064)), ('A', '497', 13, 'side-chain clash', (169.668, 170.621, 153.677)), ('A', '499', 13, 'cablam Outlier', (171.0, 166.6, 150.9)), ('A', '500', 13, 'side-chain clash', (169.668, 170.621, 153.677)), ('A', '274', 14, 'cablam Outlier', (166.4, 151.8, 191.9)), ('A', '275', 14, 'cablam Outlier', (168.2, 154.0, 194.5)), ('A', '277', 14, 'smoc Outlier', (164.914, 154.441, 199.84)), ('A', '278', 14, 'smoc Outlier', (168.467, 155.379, 200.829)), ('A', '606', 15, 'side-chain clash', (174.997, 202.549, 171.077)), ('A', '612', 15, 'side-chain clash', (174.639, 207.249, 172.021)), ('A', '614', 15, 'side-chain clash', (174.997, 202.549, 171.077)), ('A', '805', 15, 'side-chain clash', (174.639, 207.249, 172.021)), ('A', '726', 16, 'smoc Outlier', (159.798, 193.995, 196.181)), ('A', '730', 16, 'smoc Outlier', (159.471, 188.21699999999998, 195.395)), ('A', '731', 16, 'smoc Outlier', (162.44899999999998, 185.875, 195.441)), ('A', '732', 16, 'cablam Outlier', (162.8, 184.7, 199.0)), ('A', '831', 17, 'smoc Outlier', (183.135, 197.277, 156.668)), ('A', '867', 17, 'Bond angle:CA:C', (182.64899999999997, 198.046, 149.184)), ('A', '868', 17, 'Bond angle:N\ncablam Outlier', (182.742, 200.336, 152.33100000000002)), ('A', '871', 17, 'smoc Outlier', (185.146, 206.037, 151.82600000000002)), ('A', '459', 18, 'backbone clash', (178.862, 168.99, 179.803)), ('A', '677', 18, 'cablam Outlier', (179.1, 164.7, 180.7)), ('A', '678', 18, 'backbone clash\ncablam CA Geom Outlier', (178.862, 168.99, 179.803)), ('A', '714', 19, 'smoc Outlier', (173.17899999999997, 205.686, 198.418)), ('A', '715', 19, 'side-chain clash', (168.736, 205.394, 197.639)), ('A', '721', 19, 'side-chain clash', (168.736, 205.394, 197.639)), ('A', '531', 20, 'Dihedral angle:CA:C', (156.90200000000002, 159.105, 171.69299999999998)), ('A', '532', 20, 'Dihedral angle:N:CA\nsmoc Outlier', (154.46200000000002, 160.641, 174.10399999999998)), ('A', '533', 20, 'Dihedral angle:CD:NE:CZ:NH1', (154.461, 157.10899999999998, 175.626)), ('A', '291', 21, 'Dihedral angle:CA:CB:CG:OD1', (159.476, 173.001, 202.946)), ('A', '292', 21, 'side-chain clash', (160.036, 171.968, 197.128)), ('A', '309', 21, 'side-chain clash', (160.036, 171.968, 197.128)), ('A', '194', 22, 'side-chain clash', (164.373, 168.561, 217.838)), ('A', '197', 22, 'side-chain clash\nsmoc Outlier', (161.125, 167.454, 217.698)), ('A', '198', 22, 'side-chain clash', (164.373, 168.561, 217.838)), ('A', '580', 23, 'cablam Outlier', (162.4, 184.3, 162.5)), ('A', '589', 23, 'side-chain clash\nsmoc Outlier', (166.766, 182.818, 165.645)), ('A', '689', 23, 'side-chain clash', (166.766, 182.818, 165.645)), ('A', '857', 24, 'side-chain clash', (180.494, 186.595, 141.547)), ('A', '858', 24, 'Dihedral angle:CD:NE:CZ:NH1', (182.82100000000003, 184.393, 144.67299999999997)), ('A', '860', 24, 'side-chain clash', (180.494, 186.595, 141.547)), ('A', '189', 25, 'side-chain clash', (174.221, 175.563, 211.544)), ('A', '216', 25, 'side-chain clash', (174.221, 175.563, 211.544)), ('A', '181', 26, 'side-chain clash', (187.298, 174.883, 212.188)), ('A', '213', 26, 'side-chain clash', (187.298, 174.883, 212.188)), ('A', '119', 27, 'smoc Outlier', (185.261, 181.512, 217.51899999999998)), ('A', '211', 27, 'Dihedral angle:CA:CB:CG:OD1', (181.349, 179.983, 212.406)), ('A', '668', 28, 'smoc Outlier', (180.80800000000002, 158.353, 169.789)), ('A', '670', 28, 'cablam Outlier', (186.0, 157.6, 166.4)), ('A', '284', 29, 'smoc Outlier', (165.812, 163.348, 205.37800000000001)), ('A', '285', 29, 'Dihedral angle:CD:NE:CZ:NH1\nsmoc Outlier', (169.3, 163.265, 206.912)), ('A', '268', 30, 'Dihedral angle:CA:C', (177.58200000000002, 147.89700000000002, 196.18200000000002)), ('A', '269', 30, 'Dihedral angle:N:CA', (176.24899999999997, 144.971, 194.281)), ('A', '416', 31, 'smoc Outlier', (196.508, 180.843, 144.453)), ('A', '842', 31, 'smoc Outlier', (194.71499999999997, 183.6, 147.722)), ('A', '825', 32, 'side-chain clash\nsmoc Outlier', (171.038, 211.459, 153.166)), ('A', '826', 32, 'smoc Outlier', (174.26, 209.702, 156.52100000000002)), ('A', '922', 33, 'Dihedral angle:CB:CG:CD:OE1', (176.23299999999998, 201.507, 145.29)), ('A', '924', 33, 'smoc Outlier', (173.089, 197.43800000000002, 146.7)), ('A', '88', 34, 'side-chain clash', (162.058, 146.529, 159.817)), ('A', '91', 34, 'side-chain clash\nsmoc Outlier', (162.058, 146.529, 159.817)), ('A', '390', 35, 'smoc Outlier', (190.98100000000002, 154.469, 178.137)), ('A', '391', 35, 'Bond angle:CB:CG:CD', (193.696, 156.465, 179.894)), ('A', '428', 36, 'side-chain clash\ncablam CA Geom Outlier', (195.93, 196.679, 144.306)), ('A', '883', 36, 'side-chain clash', (195.93, 196.679, 144.306)), ('A', '911', 37, 'smoc Outlier', (176.667, 201.39600000000002, 134.523)), ('A', '912', 37, 'smoc Outlier', (173.66299999999998, 200.635, 136.755)), ('A', '303', 38, 'side-chain clash', (168.458, 144.925, 183.069)), ('A', '331', 38, 'Bond angle:CA:CB:CG', (164.559, 143.52700000000002, 179.732)), ('A', '516', 39, 'side-chain clash', (162.435, 166.405, 158.785)), ('A', '569', 39, 'side-chain clash', (162.435, 166.405, 158.785)), ('A', '749', 40, 'smoc Outlier', (165.067, 196.135, 181.44899999999998)), ('A', '750', 40, 'smoc Outlier', (163.51299999999998, 197.141, 178.129)), ('A', '225', 41, 'smoc Outlier', (155.38100000000003, 178.77399999999997, 221.02800000000002)), ('A', '226', 41, 'smoc Outlier', (153.92600000000002, 175.373, 221.99800000000002)), ('A', '153', 42, 'smoc Outlier', (201.541, 177.823, 201.36700000000002)), ('A', '155', 42, 'Dihedral angle:CA:CB:CG:OD1', (204.955, 180.45700000000002, 197.502)), ('A', '202', 43, 'side-chain clash', (157.441, 177.872, 214.371)), ('A', '231', 43, 'side-chain clash', (157.441, 177.872, 214.371)), ('A', '483', 44, 'smoc Outlier', (154.548, 184.976, 169.07399999999998)), ('A', '484', 44, 'smoc Outlier', (152.194, 182.132, 168.178)), ('A', '806', 45, 'backbone clash', (180.841, 208.56, 166.071)), ('A', '807', 45, 'backbone clash', (180.841, 208.56, 166.071)), ('C', '155', 1, 'smoc Outlier', (196.64399999999998, 137.60899999999998, 179.80200000000002)), ('C', '157', 1, 'Bond angle:CA:CB:CG', (198.648, 138.538, 173.626)), ('C', '158', 1, 'smoc Outlier', (199.18, 141.45100000000002, 171.171)), ('C', '159', 1, 'side-chain clash', (200.197, 146.966, 174.175)), ('C', '186', 1, 'side-chain clash', (200.197, 146.966, 174.175)), ('C', '111', 2, 'Dihedral angle:CD:NE:CZ:NH1\nsmoc Outlier', (164.606, 141.011, 190.76)), ('C', '112', 2, 'side-chain clash', (163.964, 142.978, 188.05)), ('C', '115', 2, 'side-chain clash', (168.458, 144.925, 183.069)), ('C', '117', 2, 'smoc Outlier', (173.155, 148.611, 180.74899999999997)), ('C', '139', 3, 'smoc Outlier', (204.88700000000003, 151.507, 184.42000000000002)), ('C', '140', 3, 'Dihedral angle:CA:C', (201.842, 152.318, 186.547)), ('C', '141', 3, 'Dihedral angle:N:CA\nsmoc Outlier', (199.313, 150.221, 184.61499999999998)), ('C', '96', 4, 'Dihedral angle:CD:NE:CZ:NH1\ncablam Outlier', (176.946, 135.96200000000002, 167.871)), ('C', '98', 4, 'Dihedral angle:CA:C\ncablam Outlier', (174.45000000000002, 137.60999999999999, 172.031)), ('C', '99', 4, 'Dihedral angle:N:CA\ncablam Outlier\nsmoc Outlier', (172.42100000000002, 134.38200000000003, 171.996)), ('C', '178', 5, 'Dihedral angle:CA:C\ncablam Outlier', (213.148, 158.29299999999998, 172.354)), ('C', '179', 5, 'Dihedral angle:N:CA', (213.076, 156.19299999999998, 169.227)), ('C', '182', 6, 'Bond angle:C\ncablam CA Geom Outlier', (203.6, 156.3, 170.395)), ('C', '183', 6, 'Bond angle:N:CD', (200.57899999999998, 155.893, 171.523)), ('C', '104', 7, 'side-chain clash', (169.803, 135.502, 181.611)), ('C', '107', 7, 'side-chain clash', (169.803, 135.502, 181.611)), ('D', '60', 1, 'smoc Outlier', (215.07899999999998, 167.319, 149.30200000000002)), ('D', '61', 1, 'side-chain clash', (213.132, 163.511, 153.651)), ('D', '62', 1, 'side-chain clash', (213.132, 163.511, 153.651)), ('D', '4', 2, 'side-chain clash', (204.833, 185.161, 154.786)), ('D', '7', 2, 'side-chain clash', (204.833, 185.161, 154.786)), ('D', '8', 2, 'smoc Outlier', (203.782, 180.994, 150.583)), ('D', '31', 3, 'smoc Outlier', (207.539, 167.259, 163.80800000000002)), ('D', '32', 3, 'smoc Outlier', (207.077, 168.68, 160.27899999999997)), ('D', '21', 4, 'smoc Outlier', (202.36200000000002, 160.248, 150.485)), ('D', '38', 4, 'smoc Outlier', (206.29399999999998, 177.435, 164.108)), ('P', '10', 1, 'smoc Outlier', (171.033, 173.72899999999998, 141.262)), ('T', '5', 1, 'Backbone torsion suites: ', (170.19, 186.278, 154.68)), ('T', '6', 1, 'side-chain clash', (172.961, 181.351, 148.742)), ('T', '12', 1, 'smoc Outlier', (156.072, 178.037, 135.809)), ('T', '15', 1, 'smoc Outlier', (149.685, 191.553, 135.025))]
data['omega'] = [('A', ' 505 ', 'PRO', None, (172.887, 154.468, 163.60999999999996)), ('A', ' 557 ', 'VAL', None, (182.684, 168.708, 164.402)), ('C', '  99 ', 'ASP', None, (172.80499999999998, 135.809, 171.966)), ('C', ' 183 ', 'PRO', None, (201.202, 156.856, 170.608))]
data['cablam'] = [('A', '45', 'PHE', 'check CA trace,carbonyls, peptide', 'strand\nEEEEE', (173.4, 190.7, 199.9)), ('A', '139', 'CYS', 'check CA trace,carbonyls, peptide', ' \nTS-HH', (191.1, 189.3, 196.2)), ('A', '149', 'TYR', 'check CA trace,carbonyls, peptide', 'turn\nHHTTS', (193.7, 176.6, 207.2)), ('A', '220', 'GLY', 'check CA trace,carbonyls, peptide', ' \n---S-', (168.1, 187.7, 219.4)), ('A', '243', 'PRO', ' alpha helix', 'helix\nHHHHH', (176.4, 177.0, 194.0)), ('A', '257', 'VAL', 'check CA trace,carbonyls, peptide', 'bend\nSBSSS', (182.3, 153.0, 204.9)), ('A', '274', 'ASP', 'check CA trace,carbonyls, peptide', ' \n-----', (166.4, 151.8, 191.9)), ('A', '275', 'PHE', 'check CA trace,carbonyls, peptide', ' \n----H', (168.2, 154.0, 194.5)), ('A', '351', 'LEU', 'check CA trace,carbonyls, peptide', 'bend\nSSS-E', (164.9, 163.8, 186.1)), ('A', '429', 'PHE', 'check CA trace,carbonyls, peptide', ' \nT---S', (203.2, 193.7, 149.1)), ('A', '434', 'SER', 'check CA trace,carbonyls, peptide', 'bend\nSSS-S', (201.2, 196.9, 157.1)), ('A', '438', 'LYS', 'check CA trace,carbonyls, peptide', ' \nS---B', (197.9, 187.7, 159.0)), ('A', '499', 'ASP', 'check CA trace,carbonyls, peptide', ' \n-S-S-', (171.0, 166.6, 150.9)), ('A', '502', 'ALA', 'check CA trace,carbonyls, peptide', ' \nS---B', (171.6, 160.6, 158.5)), ('A', '507', 'ASN', ' three-ten', 'helix-3\nTGGGT', (173.8, 156.4, 157.8)), ('A', '519', 'MET', 'check CA trace,carbonyls, peptide', 'bend\nHSS-H', (156.5, 156.2, 156.2)), ('A', '556', 'THR', 'check CA trace,carbonyls, peptide', ' \n-----', (185.1, 169.3, 164.7)), ('A', '557', 'VAL', 'check CA trace,carbonyls, peptide', ' \n----B', (181.2, 168.9, 164.2)), ('A', '580', 'ALA', ' alpha helix', 'turn\nHHTT-', (162.4, 184.3, 162.5)), ('A', '594', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-STTT', (171.7, 194.7, 153.5)), ('A', '620', 'PRO', 'check CA trace,carbonyls, peptide', 'turn\n--TTS', (185.1, 181.5, 176.3)), ('A', '670', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\nBSSSS', (186.0, 157.6, 166.4)), ('A', '677', 'PRO', 'check CA trace,carbonyls, peptide', ' \n---SS', (179.1, 164.7, 180.7)), ('A', '682', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n--SS-', (176.5, 171.5, 168.1)), ('A', '732', 'TYR', ' alpha helix', 'helix\nHHHT-', (162.8, 184.7, 199.0)), ('A', '779', 'ILE', 'check CA trace,carbonyls, peptide', 'helix\n--HHH', (182.1, 194.3, 182.9)), ('A', '868', 'PRO', ' three-ten', 'turn\nT-TTT', (182.7, 200.3, 152.3)), ('A', '219', 'PHE', 'check CA trace', ' \n----S', (170.5, 185.0, 218.4)), ('A', '258', 'ASP', 'check CA trace', 'bend\nBSSS-', (180.8, 154.8, 207.9)), ('A', '428', 'PHE', 'check CA trace', ' \nTT---', (201.9, 196.0, 146.3)), ('A', '504', 'PHE', 'check CA trace', 'beta bridge\n--BTG', (174.5, 156.3, 163.3)), ('A', '678', 'GLY', 'check CA trace', 'bend\n--SS-', (176.7, 167.5, 179.7)), ('C', '96', 'ARG', 'check CA trace,carbonyls, peptide', 'turn\nTTTTS', (176.9, 136.0, 167.9)), ('C', '98', 'LEU', 'check CA trace,carbonyls, peptide', 'bend\nTTSSS', (174.5, 137.6, 172.0)), ('C', '99', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nTSSSH', (172.4, 134.4, 172.0)), ('C', '172', 'ILE', 'check CA trace,carbonyls, peptide', ' \nTT-SG', (209.9, 148.2, 176.2)), ('C', '178', 'PRO', ' alpha helix', 'turn\nGTTTS', (213.1, 158.3, 172.4)), ('C', '182', 'TRP', 'check CA trace', ' \nS---E', (203.6, 156.3, 170.4))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-23109/7l1f/Model_validation_1/validation_cootdata/molprobity_probe7l1f_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)
