
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
data['probe'] = [(' A 524  GLN  NE2', ' A 574  VAL HG11', -1.187, (162.47, 186.481, 174.212)), (' A 524  GLN HE21', ' A 574  VAL  CG1', -1.147, (162.188, 187.387, 174.587)), (' A 524  GLN HE21', ' A 574  VAL HG11', -0.956, (161.68, 187.223, 174.804)), (' A 524  GLN  HG2', ' A 574  VAL  CG2', -0.697, (163.555, 187.628, 175.294)), (' A 323  MET  HE2', ' A 376  MET  HE3', -0.691, (183.218, 196.016, 184.939)), (' A 524  GLN  NE2', ' A 574  VAL HG21', -0.676, (163.314, 186.747, 175.079)), (' A 435  GLU  OE2', ' A 541  LYS  NZ ', -0.651, (172.115, 203.699, 159.483)), (' A 524  GLN  HG2', ' A 574  VAL HG21', -0.634, (164.221, 187.19, 175.574)), (' A 524  GLN HE21', ' A 574  VAL  CB ', -0.577, (162.688, 187.3, 175.777)), (' A 192  ARG  NH2', ' A 197  GLU  O  ', -0.576, (170.466, 154.592, 176.173)), (' A 365  THR HG22', ' A 367  ASP  H  ', -0.569, (191.202, 195.885, 168.452)), (' A 288  LYS  NZ ', ' A 431  ASP  OD2', -0.567, (179.388, 206.584, 150.782)), (' A 394  ASN  HB2', ' A 562  LYS  HE3', -0.552, (174.488, 178.161, 187.484)), (' A  19  SER  OG ', ' A  23  GLU  OE1', -0.545, (164.431, 168.037, 212.487)), (' A 233  ILE HG12', ' A 581  VAL HG21', -0.534, (165.803, 181.271, 163.032)), (' E 353  TRP  O  ', ' E 466  ARG  NH1', -0.529, (183.507, 186.727, 227.456)), (' A 295  ASP  HA ', ' A 298  VAL HG12', -0.517, (196.492, 205.045, 166.21)), (' A 327  PHE  HZ ', ' A 358  ILE HD12', -0.515, (188.507, 193.751, 184.405)), (' A 284  PRO  HD3', ' A 440  LEU HD22', -0.513, (179.932, 191.982, 151.851)), (' A 524  GLN  HG2', ' A 574  VAL HG22', -0.512, (164.325, 188.532, 175.334)), (' A 524  GLN  CG ', ' A 574  VAL HG21', -0.51, (164.349, 186.889, 174.958)), (' E 474  GLN  HG3', ' E 474  GLN  O  ', -0.489, (170.954, 166.708, 218.515)), (' A 524  GLN  CD ', ' A 574  VAL HG21', -0.488, (163.919, 186.641, 174.947)), (' A 229  THR  O  ', ' A 233  ILE HG13', -0.476, (165.671, 179.31, 162.373)), (' A 482  ARG HH22', ' A 611  SER  HB3', -0.472, (179.884, 164.748, 145.215)), (' A 420  SER  OG ', ' A 902  NAG  O3 ', -0.468, (177.832, 210.991, 174.745)), (' A  22  GLU  HG3', ' A  88  ILE HG23', -0.467, (163.239, 169.536, 202.163)), (' A 145  GLU  OE1', ' A 149  ASN  ND2', -0.466, (196.05, 177.368, 164.721)), (' A 303  ASP  N  ', ' A 303  ASP  OD1', -0.464, (195.686, 204.529, 178.343)), (' A 327  PHE  CZ ', ' A 358  ILE HD12', -0.463, (188.253, 193.728, 185.149)), (' E 426  PRO  HD3', ' E 463  PRO  HB3', -0.462, (170.275, 192.172, 225.409)), (' A 284  PRO  HD2', ' A 437  ASN  OD1', -0.458, (180.63, 195.341, 151.78)), (' A 354  GLY  HA3', ' E 502  GLY  HA3', -0.445, (185.161, 190.626, 198.884)), (' A 335  ASP  HB2', ' A 361  CYS  HB3', -0.443, (200.564, 191.472, 177.862)), (' E 438  SER  O  ', ' E 438  SER  OG ', -0.44, (192.563, 194.194, 212.034)), (' A 217  TYR  OH ', ' A 225  ASP  OD2', -0.433, (162.803, 173.946, 173.784)), (' A 245  ARG  NH1', ' A 603  PHE  O  ', -0.433, (172.629, 179.488, 143.779)), (' A 152  MET  O  ', ' A 161  ARG  NH2', -0.432, (191.65, 179.177, 154.421)), (' A 145  GLU  HA ', ' A 146  PRO  HA ', -0.429, (198.574, 177.861, 164.01)), (' E 437  ASN  OD1', ' E 438  SER  N  ', -0.428, (190.008, 196.08, 209.075)), (' A 581  VAL  O  ', ' A 585  LEU  HG ', -0.427, (164.54, 185.39, 163.102)), (' A 416  LYS  HE3', ' A 543  ASP  HB3', -0.425, (173.252, 204.59, 170.711)), (' A 293  VAL  O  ', ' A 297  MET  HG2', -0.422, (191.881, 203.878, 168.463)), (' A 248  LEU HD21', ' A 278  LEU HD22', -0.421, (185.327, 182.925, 150.158)), (' A  23  GLU  H  ', ' A  23  GLU  HG3', -0.419, (163.111, 168.817, 208.745)), (' A 462  MET  HE3', ' A 468  ILE HD11', -0.416, (173.055, 160.414, 162.169)), (' A 198  ASP  N  ', ' A 198  ASP  OD1', -0.415, (170.58, 158.102, 176.36)), (' A 474  MET  HE1', ' A 500  PRO  CD ', -0.413, (183.667, 162.129, 161.197)), (' A 376  MET  O  ', ' A 380  GLN  HG2', -0.411, (180.551, 193.741, 184.487)), (' E 468  THR  O  ', ' E 468  THR HG22', -0.41, (183.532, 177.451, 225.939)), (' E 452  LEU HD23', ' E 494  SER  HB3', -0.409, (187.636, 178.844, 213.689)), (' A 474  MET  HE1', ' A 500  PRO  HD3', -0.408, (183.494, 161.841, 160.801)), (' A 132  VAL HG12', ' A 171  GLU  HG3', -0.408, (199.616, 165.368, 159.328)), (' A 215  TYR  CZ ', ' A 568  LEU HD13', -0.408, (157.672, 182.006, 185.507)), (' E 438  SER  HB2', ' E 509  ARG  HG3', -0.406, (190.188, 195.087, 213.764)), (' A 351  LEU  HB2', ' A 355  ASP  HB3', -0.405, (188.523, 186.051, 194.753)), (' A 524  GLN HE21', ' A 574  VAL  CG2', -0.404, (162.912, 187.173, 175.772)), (' A 371  THR  O  ', ' A 375  GLU  HG2', -0.403, (186.856, 191.1, 177.868)), (' A 535  HIS  CD2', ' A 542  CYS  HB3', -0.403, (168.336, 200.363, 168.454))]
data['smoc'] = [('A', 22, u'GLU', 0.6342982982606675, (164.042, 168.036, 205.60999999999999)), ('A', 25, u'ALA', 0.6931984436789185, (169.012, 168.324, 205.083)), ('A', 30, u'ASP', 0.6873215647063856, (174.531, 174.99200000000002, 205.85200000000003)), ('A', 35, u'GLU', 0.7183760167908037, (183.45600000000002, 174.48200000000003, 204.39200000000002)), ('A', 37, u'GLU', 0.7182466355554217, (183.671, 178.238, 200.30100000000002)), ('A', 44, u'SER', 0.715459407607357, (191.38100000000003, 179.033, 192.759)), ('A', 60, u'GLN', 0.6100287600696319, (202.823, 171.783, 192.38200000000003)), ('A', 82, u'MET', 0.6836782815457827, (171.531, 159.546, 202.42200000000003)), ('A', 92, u'THR', 0.6505768019996491, (165.553, 175.166, 196.85800000000003)), ('A', 94, u'LYS', 0.7066586604365046, (165.869, 170.061, 196.469)), ('A', 103, u'ASN', 0.6579879543689645, (177.212, 160.181, 190.946)), ('A', 111, u'ASP', 0.6271806320412732, (189.031, 149.178, 185.68)), ('A', 117, u'ASN', 0.6550487920833081, (190.586, 158.27299999999997, 181.752)), ('A', 119, u'ILE', 0.6793115542455045, (191.258, 156.959, 176.546)), ('A', 125, u'THR', 0.6832395123262612, (197.429, 164.459, 173.51)), ('A', 133, u'CYS', 0.6227418692672639, (204.918, 166.904, 156.61399999999998)), ('A', 141, u'CYS', 0.6353690306795259, (206.91, 169.948, 159.304)), ('A', 145, u'GLU', 0.6588274719286236, (198.92800000000003, 176.242, 165.267)), ('A', 149, u'ASN', 0.709790169148176, (196.045, 177.61299999999997, 160.25)), ('A', 155, u'SER', 0.7034136951725076, (196.364, 181.29, 151.146)), ('A', 160, u'GLU', 0.7021080560108433, (198.003, 174.191, 148.73299999999998)), ('A', 171, u'GLU', 0.679743091904985, (197.20299999999997, 162.248, 159.911)), ('A', 173, u'GLY', 0.696426442730077, (191.772, 161.70499999999998, 162.727)), ('A', 197, u'GLU', 0.6649388692312764, (168.92200000000003, 156.484, 178.26399999999998)), ('A', 200, u'GLY', 0.7183143880138129, (173.124, 162.63899999999998, 174.556)), ('A', 212, u'VAL', 0.6996716406547623, (157.053, 174.095, 188.732)), ('A', 231, u'GLU', 0.6795200434901328, (163.238, 175.90800000000002, 159.505)), ('A', 238, u'GLU', 0.7137453343586797, (170.107, 180.286, 151.30700000000002)), ('A', 251, u'ALA', 0.6878892188352022, (187.942, 184.045, 142.732)), ('A', 254, u'SER', 0.6869203278977322, (187.566, 176.687, 137.011)), ('A', 297, u'MET', 0.698253254005389, (193.248, 206.195, 170.127)), ('A', 325, u'GLN', 0.6722951899081523, (189.324, 198.135, 194.89700000000002)), ('A', 326, u'GLY', 0.703613267349721, (190.73299999999998, 194.624, 194.707)), ('A', 350, u'ASP', 0.6862268500775672, (185.54399999999998, 184.90200000000002, 190.54)), ('A', 361, u'CYS', 0.6449270412699311, (197.39100000000002, 191.48800000000003, 178.38700000000003)), ('A', 366, u'MET', 0.6521331922680862, (189.839, 198.45200000000003, 168.648)), ('A', 391, u'LEU', 0.7350400022019326, (175.61299999999997, 175.778, 194.701)), ('A', 411, u'SER', 0.6725545624747871, (175.975, 198.05, 172.05700000000002)), ('A', 420, u'SER', 0.7020007299346763, (179.925, 210.105, 171.99800000000002)), ('A', 427, u'ASP', 0.6689138902115349, (181.984, 215.288, 160.789)), ('A', 457, u'GLU', 0.7183509018282948, (175.237, 168.18800000000002, 167.508)), ('A', 462, u'MET', 0.7121482387529526, (172.123, 160.277, 166.64499999999998)), ('A', 467, u'GLU', 0.7027508859437772, (170.70999999999998, 155.312, 164.996)), ('A', 472, u'GLN', 0.6970153693484772, (178.048, 154.19899999999998, 158.377)), ('A', 483, u'GLU', 0.6756065114691718, (171.947, 168.784, 152.909)), ('A', 498, u'CYS', 0.68019393935624, (187.047, 160.27299999999997, 161.9)), ('A', 524, u'GLN', 0.6138292789497257, (166.083, 188.298, 172.324)), ('A', 530, u'CYS', 0.6451502052046014, (166.511, 198.417, 173.268)), ('A', 536, u'GLU', 0.7324231510515569, (163.28, 204.32000000000002, 167.053)), ('A', 542, u'CYS', 0.6561673121244731, (170.631, 200.727, 169.07399999999998)), ('A', 547, u'SER', 0.6931506221647522, (169.267, 204.009, 180.102)), ('A', 556, u'ASN', 0.7005602117434903, (166.181, 191.324, 187.798)), ('A', 557, u'MET', 0.6413772697284477, (167.49, 188.3, 185.879)), ('A', 564, u'GLU', 0.6996713309286694, (164.665, 179.672, 189.395)), ('A', 571, u'GLU', 0.6859348108141871, (160.418, 185.677, 180.92800000000003)), ('A', 582, u'ARG', 0.6768292256195917, (162.202, 186.541, 165.154)), ('A', 586, u'ASN', 0.6927942239532043, (164.844, 191.55, 162.656)), ('A', 589, u'GLU', 0.7163010053913923, (166.46200000000002, 192.706, 157.676)), ('A', 597, u'ASP', 0.6984378231893609, (167.771, 192.063, 145.121)), ('E', 341, u'VAL', 0.583657798913342, (189.547, 198.524, 225.93800000000002)), ('E', 345, u'THR', 0.6936193388889837, (196.80100000000002, 194.164, 221.05200000000002)), ('E', 346, u'ARG', 0.6739930595989733, (194.631, 191.01399999999998, 220.903)), ('E', 379, u'CYS', 0.6221577419225675, (174.589, 205.341, 219.63899999999998)), ('E', 396, u'TYR', 0.6059378490941134, (180.833, 197.791, 230.68)), ('E', 398, u'ASP', 0.6222022321322548, (182.455, 194.162, 225.461)), ('E', 406, u'GLU', 0.6601597926101849, (177.785, 190.98000000000002, 210.01)), ('E', 420, u'ASP', 0.6732153154694037, (171.105, 184.05100000000002, 217.641)), ('E', 424, u'LYS', 0.6673808377839819, (172.44, 189.007, 221.466)), ('E', 428, u'ASP', 0.6675511969879783, (165.412, 198.129, 224.817)), ('E', 432, u'CYS', 0.6317953872532034, (176.52800000000002, 202.54299999999998, 222.032)), ('E', 444, u'LYS', 0.711640989823627, (197.849, 186.999, 207.09)), ('E', 445, u'LYS', 0.7256235695231721, (198.93, 185.35600000000002, 203.85500000000002)), ('E', 465, u'GLU', 0.6179040891135801, (174.20899999999997, 185.64399999999998, 227.836)), ('E', 466, u'ARG', 0.685782351711323, (177.403, 183.777, 227.003)), ('E', 467, u'ASP', 0.6658772791350822, (178.046, 180.18200000000002, 225.91299999999998)), ('E', 470, u'MET', 0.6730605349192447, (182.16899999999998, 172.829, 223.147)), ('E', 481, u'ASN', 0.6485550141983087, (178.75, 159.377, 221.872)), ('E', 508, u'TYR', 0.6767683006444496, (186.252, 193.99800000000002, 211.99800000000002))]
data['rota'] = [('A', '  20 ', 'THR', 0.008087669993983582, (161.77400000000006, 165.412, 209.674)), ('A', '  21 ', 'ILE', 0.02153118454236032, (164.41700000000006, 164.506, 207.04700000000003))]
data['clusters'] = [('A', '284', 1, 'side-chain clash', (185.161, 190.626, 198.884)), ('A', '323', 1, 'side-chain clash', (183.218, 196.016, 184.939)), ('A', '327', 1, 'side-chain clash', (188.253, 193.728, 185.149)), ('A', '350', 1, 'smoc Outlier', (185.54399999999998, 184.90200000000002, 190.54)), ('A', '351', 1, 'side-chain clash', (188.523, 186.051, 194.753)), ('A', '353', 1, 'cablam Outlier', (184.8, 185.9, 199.2)), ('A', '355', 1, 'side-chain clash', (188.523, 186.051, 194.753)), ('A', '357', 1, 'Dihedral angle:CD:NE:CZ:NH1', (189.787, 189.783, 188.876)), ('A', '358', 1, 'side-chain clash', (188.253, 193.728, 185.149)), ('A', '376', 1, 'side-chain clash', (180.551, 193.741, 184.487)), ('A', '380', 1, 'side-chain clash', (180.551, 193.741, 184.487)), ('A', '437', 1, 'side-chain clash', (185.161, 190.626, 198.884)), ('A', '19', 2, 'side-chain clash', (164.431, 168.037, 212.487)), ('A', '20', 2, 'Rotamer', (161.77400000000006, 165.412, 209.674)), ('A', '21', 2, 'Rotamer', (164.41700000000006, 164.506, 207.04700000000003)), ('A', '22', 2, 'side-chain clash\nsmoc Outlier', (163.239, 169.536, 202.163)), ('A', '23', 2, 'side-chain clash', (163.111, 168.817, 208.745)), ('A', '25', 2, 'smoc Outlier', (169.012, 168.324, 205.083)), ('A', '88', 2, 'side-chain clash', (163.239, 169.536, 202.163)), ('A', '92', 2, 'smoc Outlier', (165.553, 175.166, 196.85800000000003)), ('A', '94', 2, 'smoc Outlier', (165.869, 170.061, 196.469)), ('A', '229', 3, 'side-chain clash', (165.671, 179.31, 162.373)), ('A', '231', 3, 'Dihedral angle:CB:CG:CD:OE1\nsmoc Outlier', (163.238, 175.90800000000002, 159.505)), ('A', '233', 3, 'side-chain clash', (165.671, 179.31, 162.373)), ('A', '581', 3, 'side-chain clash', (164.54, 185.39, 163.102)), ('A', '582', 3, 'smoc Outlier', (162.202, 186.541, 165.154)), ('A', '585', 3, 'side-chain clash', (164.54, 185.39, 163.102)), ('A', '586', 3, 'smoc Outlier', (164.844, 191.55, 162.656)), ('A', '589', 3, 'smoc Outlier', (166.46200000000002, 192.706, 157.676)), ('A', '293', 4, 'side-chain clash', (191.881, 203.878, 168.463)), ('A', '295', 4, 'side-chain clash', (196.492, 205.045, 166.21)), ('A', '297', 4, 'side-chain clash\nsmoc Outlier', (191.881, 203.878, 168.463)), ('A', '298', 4, 'side-chain clash', (196.492, 205.045, 166.21)), ('A', '365', 4, 'side-chain clash', (191.202, 195.885, 168.452)), ('A', '366', 4, 'smoc Outlier', (189.839, 198.45200000000003, 168.648)), ('A', '367', 4, 'side-chain clash', (191.202, 195.885, 168.452)), ('A', '169', 5, 'Dihedral angle:CD:NE:CZ:NH1', (192.33100000000002, 164.89100000000002, 157.95200000000003)), ('A', '173', 5, 'smoc Outlier', (191.772, 161.70499999999998, 162.727)), ('A', '177', 5, 'Dihedral angle:CD:NE:CZ:NH1', (188.92600000000002, 156.708, 165.127)), ('A', '474', 5, 'side-chain clash', (183.494, 161.841, 160.801)), ('A', '498', 5, 'smoc Outlier', (187.047, 160.27299999999997, 161.9)), ('A', '500', 5, 'side-chain clash', (183.494, 161.841, 160.801)), ('A', '416', 6, 'side-chain clash', (173.252, 204.59, 170.711)), ('A', '530', 6, 'smoc Outlier', (166.511, 198.417, 173.268)), ('A', '535', 6, 'side-chain clash', (168.336, 200.363, 168.454)), ('A', '536', 6, 'smoc Outlier', (163.28, 204.32000000000002, 167.053)), ('A', '542', 6, 'side-chain clash\nsmoc Outlier', (168.336, 200.363, 168.454)), ('A', '543', 6, 'side-chain clash', (173.252, 204.59, 170.711)), ('A', '215', 7, 'side-chain clash', (157.672, 182.006, 185.507)), ('A', '524', 7, 'side-chain clash\nsmoc Outlier', (162.912, 187.173, 175.772)), ('A', '568', 7, 'side-chain clash', (157.672, 182.006, 185.507)), ('A', '571', 7, 'smoc Outlier', (160.418, 185.677, 180.92800000000003)), ('A', '574', 7, 'side-chain clash', (162.912, 187.173, 175.772)), ('A', '110', 8, 'cablam Outlier', (187.6, 150.7, 188.9)), ('A', '111', 8, 'smoc Outlier', (189.031, 149.178, 185.68)), ('A', '115', 8, 'Dihedral angle:CD:NE:CZ:NH1', (190.23299999999998, 152.877, 181.05200000000002)), ('A', '117', 8, 'smoc Outlier', (190.586, 158.27299999999997, 181.752)), ('A', '119', 8, 'smoc Outlier', (191.258, 156.959, 176.546)), ('A', '132', 9, 'side-chain clash', (199.616, 165.368, 159.328)), ('A', '133', 9, 'smoc Outlier', (204.918, 166.904, 156.61399999999998)), ('A', '141', 9, 'smoc Outlier', (206.91, 169.948, 159.304)), ('A', '171', 9, 'side-chain clash\nsmoc Outlier', (199.616, 165.368, 159.328)), ('A', '192', 10, 'backbone clash\nDihedral angle:CD:NE:CZ:NH1', (172.778, 154.415, 181.372)), ('A', '197', 10, 'backbone clash\nsmoc Outlier', (170.466, 154.592, 176.173)), ('A', '198', 10, 'side-chain clash', (170.58, 158.102, 176.36)), ('A', '200', 10, 'smoc Outlier', (173.124, 162.63899999999998, 174.556)), ('A', '391', 11, 'smoc Outlier', (175.61299999999997, 175.778, 194.701)), ('A', '393', 11, 'cablam Outlier', (175.8, 180.6, 191.7)), ('A', '394', 11, 'side-chain clash', (174.488, 178.161, 187.484)), ('A', '562', 11, 'side-chain clash\ncablam Outlier', (174.488, 178.161, 187.484)), ('A', '217', 12, 'side-chain clash', (162.803, 173.946, 173.784)), ('A', '224', 12, 'Dihedral angle:CB:CG:CD:OE1', (161.92000000000002, 169.959, 168.819)), ('A', '225', 12, 'side-chain clash', (162.803, 173.946, 173.784)), ('A', '462', 13, 'side-chain clash\nsmoc Outlier', (173.055, 160.414, 162.169)), ('A', '467', 13, 'smoc Outlier', (170.70999999999998, 155.312, 164.996)), ('A', '468', 13, 'side-chain clash', (173.055, 160.414, 162.169)), ('A', '152', 14, 'side-chain clash', (191.65, 179.177, 154.421)), ('A', '155', 14, 'smoc Outlier', (196.364, 181.29, 151.146)), ('A', '161', 14, 'side-chain clash', (191.65, 179.177, 154.421)), ('A', '145', 15, 'side-chain clash\nsmoc Outlier', (198.574, 177.861, 164.01)), ('A', '146', 15, 'side-chain clash', (198.574, 177.861, 164.01)), ('A', '149', 15, 'side-chain clash\nsmoc Outlier', (196.05, 177.368, 164.721)), ('A', '288', 16, 'side-chain clash', (179.388, 206.584, 150.782)), ('A', '431', 16, 'side-chain clash', (179.388, 206.584, 150.782)), ('A', '435', 17, 'side-chain clash', (172.115, 203.699, 159.483)), ('A', '541', 17, 'side-chain clash', (172.115, 203.699, 159.483)), ('A', '420', 18, 'side-chain clash\nsmoc Outlier', (177.832, 210.991, 174.745)), ('A', '902', 18, 'side-chain clash', (177.832, 210.991, 174.745)), ('A', '371', 19, 'side-chain clash', (186.856, 191.1, 177.868)), ('A', '375', 19, 'side-chain clash', (186.856, 191.1, 177.868)), ('A', '248', 20, 'side-chain clash', (185.327, 182.925, 150.158)), ('A', '278', 20, 'side-chain clash', (185.327, 182.925, 150.158)), ('A', '335', 21, 'side-chain clash', (200.564, 191.472, 177.862)), ('A', '361', 21, 'side-chain clash\nsmoc Outlier', (200.564, 191.472, 177.862)), ('A', '301', 22, 'cablam Outlier', (197.8, 208.5, 174.0)), ('A', '303', 22, 'side-chain clash', (195.686, 204.529, 178.343)), ('A', '35', 23, 'smoc Outlier', (183.45600000000002, 174.48200000000003, 204.39200000000002)), ('A', '37', 23, 'smoc Outlier', (183.671, 178.238, 200.30100000000002)), ('A', '556', 24, 'smoc Outlier', (166.181, 191.324, 187.798)), ('A', '557', 24, 'smoc Outlier', (167.49, 188.3, 185.879)), ('A', '325', 25, 'smoc Outlier', (189.324, 198.135, 194.89700000000002)), ('A', '326', 25, 'smoc Outlier', (190.73299999999998, 194.624, 194.707)), ('A', '482', 26, 'side-chain clash', (179.884, 164.748, 145.215)), ('A', '611', 26, 'side-chain clash', (179.884, 164.748, 145.215)), ('E', '437', 1, 'backbone clash', (190.008, 196.08, 209.075)), ('E', '438', 1, 'side-chain clash\nbackbone clash', (190.188, 195.087, 213.764)), ('E', '442', 1, 'cablam Outlier', (194.0, 190.3, 212.0)), ('E', '508', 1, 'smoc Outlier', (186.252, 193.99800000000002, 211.99800000000002)), ('E', '509', 1, 'side-chain clash', (190.188, 195.087, 213.764)), ('E', '417', 2, 'cablam Outlier', (173.9, 183.6, 213.4)), ('E', '420', 2, 'smoc Outlier', (171.105, 184.05100000000002, 217.641)), ('E', '424', 2, 'smoc Outlier', (172.44, 189.007, 221.466)), ('E', '426', 2, 'side-chain clash', (170.275, 192.172, 225.409)), ('E', '463', 2, 'side-chain clash', (170.275, 192.172, 225.409)), ('E', '465', 3, 'smoc Outlier', (174.20899999999997, 185.64399999999998, 227.836)), ('E', '467', 3, 'smoc Outlier', (178.046, 180.18200000000002, 225.91299999999998)), ('E', '468', 3, 'side-chain clash', (183.532, 177.451, 225.939)), ('E', '470', 3, 'smoc Outlier', (182.16899999999998, 172.829, 223.147)), ('E', '474', 4, 'backbone clash', (170.954, 166.708, 218.515)), ('E', '477', 4, 'cablam Outlier', (167.2, 161.3, 216.6)), ('E', '452', 5, 'side-chain clash', (187.636, 178.844, 213.689)), ('E', '494', 5, 'side-chain clash', (187.636, 178.844, 213.689)), ('E', '396', 6, 'smoc Outlier', (180.833, 197.791, 230.68)), ('E', '398', 6, 'smoc Outlier', (182.455, 194.162, 225.461)), ('E', '345', 7, 'smoc Outlier', (196.80100000000002, 194.164, 221.05200000000002)), ('E', '346', 7, 'smoc Outlier', (194.631, 191.01399999999998, 220.903)), ('E', '353', 8, 'side-chain clash', (183.507, 186.727, 227.456)), ('E', '466', 8, 'side-chain clash\nsmoc Outlier', (183.507, 186.727, 227.456)), ('E', '444', 9, 'smoc Outlier', (197.849, 186.999, 207.09)), ('E', '445', 9, 'smoc Outlier', (198.93, 185.35600000000002, 203.85500000000002)), ('E', '379', 10, 'smoc Outlier', (174.589, 205.341, 219.63899999999998)), ('E', '432', 10, 'smoc Outlier', (176.52800000000002, 202.54299999999998, 222.032))]
data['omega'] = [('A', ' 146 ', 'PRO', None, (200.90400000000005, 177.57899999999998, 164.60000000000002))]
data['cablam'] = [('A', '103', 'ASN', 'check CA trace,carbonyls, peptide', ' \nS---G', (177.2, 160.2, 190.9)), ('A', '110', 'GLU', 'check CA trace,carbonyls, peptide', 'bend\nS-SHH', (187.6, 150.7, 188.9)), ('A', '301', 'ALA', 'check CA trace,carbonyls, peptide', 'turn\nTTT--', (197.8, 208.5, 174.0)), ('A', '353', 'LYS', 'check CA trace,carbonyls, peptide', 'bend\n-SSS-', (184.8, 185.9, 199.2)), ('A', '393', 'ARG', 'check CA trace,carbonyls, peptide', ' \nGG-S-', (175.8, 180.6, 191.7)), ('A', '495', 'GLU', 'check CA trace,carbonyls, peptide', 'turn\n--TT-', (185.3, 154.5, 156.9)), ('A', '562', 'LYS', 'check CA trace,carbonyls, peptide', 'turn\nTTTSS', (170.1, 179.5, 189.2)), ('E', '417', 'LYS', 'check CA trace,carbonyls, peptide', 'bend\n-SSII', (173.9, 183.6, 213.4)), ('E', '442', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nTTS--', (194.0, 190.3, 212.0)), ('E', '477', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\n-SSS-', (167.2, 161.3, 216.6)), ('E', '481', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\n--SSS', (178.8, 159.4, 221.9)), ('E', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTE', (176.4, 161.3, 210.7)), ('E', '484', 'LYS', 'check CA trace', ' \nSS-BT', (181.2, 163.6, 215.3))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-12187/7bh9/Model_validation_1/validation_cootdata/molprobity_probe7bh9_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)
