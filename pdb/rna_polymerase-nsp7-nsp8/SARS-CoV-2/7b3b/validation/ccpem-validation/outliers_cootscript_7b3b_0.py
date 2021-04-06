
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
data['probe'] = [(' A 758  LEU HD23', ' A 759  SER  H  ', -0.757, (90.049, 96.947, 97.942)), (' A 740  ASP  OD2', ' A 741  PHE  N  ', -0.696, (91.484, 105.38, 69.477)), (' A 689  TYR  O  ', ' A 693  VAL HG23', -0.608, (91.141, 103.821, 93.93)), (' A 622  CYS  SG ', ' A 623  ASP  N  ', -0.592, (100.702, 99.851, 100.679)), (' A 503  GLY  O  ', ' A 507  ASN  N  ', -0.591, (91.23, 114.736, 119.105)), (' A 873  PRO  O  ', ' A 875  GLN  NE2', -0.571, (88.401, 64.619, 104.048)), (' A 472  VAL  O  ', ' A 476  VAL HG23', -0.567, (94.909, 104.434, 83.393)), (' A 837  ILE  O  ', ' A 884  TYR  OH ', -0.555, (88.683, 80.233, 115.565)), (' A 857  GLU  N  ', ' A 857  GLU  OE2', -0.547, (77.442, 86.207, 121.121)), (' B 159  VAL HG11', ' B 172  ILE HD11', -0.523, (122.678, 111.204, 129.687)), (' A 135  ASP  N  ', ' A 135  ASP  OD2', -0.517, (115.016, 91.69, 84.763)), (' A 623  ASP  N  ', ' A 623  ASP  OD1', -0.505, (101.908, 100.399, 102.279)), (' A 790  ASN  ND2', ' A 790  ASN  O  ', -0.504, (106.927, 101.266, 95.492)), (' B 101  ASP  N  ', ' B 101  ASP  OD1', -0.5, (110.861, 137.324, 121.907)), (' C  47  GLU  N  ', ' C  47  GLU  OE2', -0.499, (114.116, 74.856, 121.59)), (' A 153  ASP  OD1', ' A 154  ASP  N  ', -0.49, (133.257, 94.038, 91.977)), (' C   2  LYS  O  ', ' C   6  VAL HG23', -0.486, (104.318, 73.534, 125.672)), (' A 206  THR  OG1', ' A 209  ASN  ND2', -0.474, (118.409, 106.973, 67.604)), (' A 388  LEU HD22', ' A 672  SER  HB3', -0.472, (109.479, 115.311, 118.649)), (' B 132  ILE HD13', ' B 138  TYR  HD2', -0.469, (123.201, 111.152, 124.245)), (' A 564  SER  O  ', ' A 568  ASN  ND2', -0.465, (89.13, 115.493, 104.56)), (' A 470  LEU  O  ', ' A 473  VAL HG12', -0.464, (96.714, 109.724, 82.031)), (' A 200  GLY  O  ', ' A 225  THR  N  ', -0.458, (117.39, 121.756, 58.11)), (' A 487  CYS  SG ', ' A 642  HIS  CE1', -0.451, (82.285, 117.761, 94.786)), (' A 273  TYR  OH ', ' B 112  ASP  OD2', -0.451, (105.696, 134.839, 101.025)), (' B  77  GLU  N  ', ' B  77  GLU  OE2', -0.45, (74.195, 122.437, 121.439)), (' A 845  ASP  OD1', ' A 846  ASP  N  ', -0.45, (90.375, 92.333, 124.1)), (' A 758  LEU  O  ', ' A 759  SER  C  ', -0.448, (93.109, 96.796, 96.582)), (' A 278  GLU  N  ', ' A 278  GLU  OE1', -0.447, (114.836, 129.937, 91.794)), (' A  42  VAL HG12', ' A  43  ALA  N  ', -0.44, (107.739, 98.336, 65.918)), (' A 736  ASP  N  ', ' A 736  ASP  OD2', -0.44, (97.073, 114.91, 71.109)), (' A 291  ASP  N  ', ' A 291  ASP  OD1', -0.438, (108.239, 120.482, 74.434)), (' A 197  ARG  HG2', ' A 197  ARG HH11', -0.434, (118.096, 127.281, 67.128)), (' A 726  ARG  NH1', ' A 744  GLU  OE1', -0.433, (92.864, 100.887, 67.74)), (' A 531  THR HG21', ' A 567  THR HG21', -0.429, (87.39, 121.271, 104.956)), (' B 165  LYS  HA ', ' B 165  LYS  HE3', -0.423, (114.15, 108.81, 137.528)), (' A 499  ASP  OD2', ' A 513  ARG  NH2', -0.422, (78.562, 108.108, 119.442)), (' A 514  LEU HD13', ' B  79  LYS  HE2', -0.414, (79.88, 117.167, 123.308)), (' A 856  ILE  O  ', ' A 860  VAL HG23', -0.413, (77.392, 82.518, 118.806)), (' A 633  MET  HE1', ' A 697  CYS  HB2', -0.411, (96.901, 104.984, 88.621)), (' B 158  GLN  HA ', ' B 158  GLN  OE1', -0.409, (119.497, 116.682, 133.995)), (' C  14  LEU HD22', ' C  36  HIS  CG ', -0.408, (104.954, 87.783, 125.383)), (' B 132  ILE HD13', ' B 138  TYR  CD2', -0.408, (123.63, 111.13, 124.605)), (' A 246  THR HG21', ' A 462  THR  HA ', -0.407, (111.774, 108.618, 91.358)), (' A 844  VAL HG11', ' A 849  LYS  HB2', -0.4, (86.987, 89.226, 123.77)), (' B 164  SER  O  ', ' B 164  SER  OG ', -0.4, (111.35, 110.338, 134.91)), (' C  31  GLN  O  ', ' C  35  LEU HD23', -0.4, (112.943, 88.166, 126.398))]
data['smoc'] = [('A', 39, u'ASN', 0.7012833337366877, (108.303, 103.283, 61.752)), ('A', 143, u'LYS', 0.6470780217288866, (125.938, 94.238, 86.46300000000001)), ('A', 144, u'GLU', 0.6464883448272827, (128.38600000000002, 95.005, 83.657)), ('A', 145, u'ILE', 0.6210709652682755, (127.343, 98.667, 83.468)), ('A', 168, u'ASN', 0.5994718326449785, (119.57199999999999, 96.068, 101.06700000000001)), ('A', 171, u'ILE', 0.5667581195431101, (121.835, 99.71600000000001, 96.61)), ('A', 194, u'ASP', 0.7195993060002056, (121.303, 123.57, 70.357)), ('A', 200, u'GLY', 0.6138229689256738, (118.543, 123.759, 60.809999999999995)), ('A', 211, u'ASP', 0.5408581546295357, (126.56, 106.37499999999999, 74.601)), ('A', 222, u'PHE', 0.6467657481975747, (118.37799999999999, 114.424, 60.072)), ('A', 239, u'SER', 0.5071133057189561, (110.083, 110.48, 78.977)), ('A', 250, u'ALA', 0.5956012529583927, (121.257, 112.67599999999999, 89.099)), ('A', 254, u'GLU', 0.5829058007027865, (122.657, 120.927, 92.077)), ('A', 291, u'ASP', 0.6303204120880141, (108.046, 122.32, 74.323)), ('A', 308, u'LEU', 0.5662336696683201, (100.387, 115.93900000000001, 86.762)), ('A', 312, u'ASN', 0.5007384869175143, (106.226, 115.349, 87.886)), ('A', 317, u'PHE', 0.5779654875104314, (113.31700000000001, 119.785, 91.342)), ('A', 329, u'LEU', 0.5765215274346049, (103.84700000000001, 128.695, 105.723)), ('A', 330, u'VAL', 0.5917567314200198, (102.968, 130.74499999999998, 108.806)), ('A', 340, u'PHE', 0.6682175692346792, (98.49400000000001, 134.612, 116.89)), ('A', 372, u'LEU', 0.5687403739676542, (88.614, 124.577, 114.49400000000001)), ('A', 377, u'ASP', 0.5866932763110704, (96.66999999999999, 123.989, 112.235)), ('A', 385, u'GLY', 0.4138910076128617, (106.751, 123.29400000000001, 121.24100000000001)), ('A', 388, u'LEU', 0.5935550463761501, (113.458, 118.119, 119.10499999999999)), ('A', 416, u'ASN', 0.6343155360336683, (90.458, 81.754, 126.804)), ('A', 428, u'PHE', 0.6670529308151005, (92.498, 69.32499999999999, 118.41700000000002)), ('A', 435, u'VAL', 0.5980545246079805, (95.739, 72.56700000000001, 111.971)), ('A', 436, u'GLU', 0.6574657847435094, (97.95100000000001, 74.46400000000001, 114.422)), ('A', 445, u'ASP', 0.727776957047759, (108.11999999999999, 97.23, 123.518)), ('A', 453, u'TYR', 0.6320520343753466, (107.01100000000001, 105.284, 111.599)), ('A', 465, u'ASP', 0.568179146786221, (107.326, 108.59400000000001, 82.848)), ('A', 468, u'GLN', 0.46267241454876246, (103.104, 106.803, 80.197)), ('A', 472, u'VAL', 0.5797939142042827, (97.611, 105.262, 81.955)), ('A', 506, u'PHE', 0.5942661448248752, (90.48700000000001, 117.386, 119.15599999999999)), ('A', 507, u'ASN', 0.5739176379819138, (90.811, 114.074, 121.015)), ('A', 512, u'ALA', 0.5728927598738678, (83.768, 113.054, 116.745)), ('A', 513, u'ARG', 0.6202792956773758, (80.164, 113.17699999999999, 117.973)), ('A', 515, u'TYR', 0.5523665244366126, (82.21300000000001, 118.248, 116.94200000000001)), ('A', 534, u'ASN', 0.5186671041114068, (92.27, 127.82, 101.361)), ('A', 548, u'ILE', 0.7074229903336019, (95.63499999999999, 89.17899999999999, 115.827)), ('A', 576, u'LEU', 0.6071282889986663, (82.55499999999999, 106.394, 97.31700000000001)), ('A', 595, u'TYR', 0.6400626891539625, (74.754, 84.49400000000001, 99.568)), ('A', 657, u'ASN', 0.53800242621849, (94.104, 120.18799999999999, 101.113)), ('A', 658, u'GLU', 0.5033153925593938, (94.306, 116.44700000000002, 100.44600000000001)), ('A', 665, u'GLU', 0.568147348149482, (101.106, 115.94200000000001, 106.72)), ('A', 672, u'SER', 0.563958573041888, (106.506, 114.809, 119.167)), ('A', 673, u'LEU', 0.5837742354010921, (105.781, 116.21700000000001, 115.71000000000001)), ('A', 686, u'THR', 0.5788398373863907, (89.66, 107.54100000000001, 100.31700000000001)), ('A', 706, u'ALA', 0.5291649420141362, (104.574, 94.332, 78.119)), ('A', 729, u'GLU', 0.5786400664925223, (102.053, 106.853, 68.697)), ('A', 730, u'CYS', 0.5907844497827786, (99.583, 107.839, 71.429)), ('A', 765, u'CYS', 0.5939573822078713, (92.113, 86.26700000000001, 84.49100000000001)), ('A', 785, u'VAL', 0.557636158708897, (106.974, 98.10199999999999, 87.103)), ('A', 802, u'GLU', 0.6378369636990675, (96.74100000000001, 79.195, 88.729)), ('A', 804, u'ASP', 0.634050144114097, (93.24700000000001, 75.548, 86.226)), ('A', 815, u'GLN', 0.5731602995384674, (90.21000000000001, 83.529, 101.792)), ('A', 818, u'MET', 0.6015474616002229, (86.571, 75.687, 96.899)), ('A', 827, u'VAL', 0.6453518190944929, (79.56, 76.99300000000001, 93.381)), ('A', 831, u'TYR', 0.5847260169591706, (86.868, 79.02799999999999, 103.169)), ('A', 855, u'MET', 0.6752829136313361, (81.061, 85.049, 123.785)), ('A', 859, u'PHE', 0.6174371679545692, (81.539, 82.034, 118.345)), ('A', 860, u'VAL', 0.621932997741368, (78.421, 82.248, 116.161)), ('A', 865, u'ASP', 0.5638977325058399, (83.048, 82.20100000000001, 108.829)), ('A', 877, u'TYR', 0.6424678854457396, (89.333, 71.46400000000001, 108.536)), ('A', 878, u'ALA', 0.4369172265964575, (85.733, 70.23400000000001, 108.641)), ('A', 914, u'ARG', 0.6289505285848881, (69.556, 77.418, 115.284)), ('A', 924, u'MET', 0.6346995822622064, (74.33, 82.04400000000001, 104.65499999999999)), ('B', 77, u'GLU', 0.67158888652132, (74.96900000000001, 123.978, 122.361)), ('B', 80, u'ARG', 0.7007741835654009, (79.611, 123.549, 121.87199999999999)), ('B', 87, u'MET', 0.5994605482729535, (90.066, 125.739, 122.394)), ('B', 94, u'MET', 0.682984304201395, (100.187, 128.466, 123.968)), ('B', 114, u'CYS', 0.5873787155937839, (105.76400000000001, 134.48000000000002, 105.754)), ('B', 119, u'ILE', 0.6386873029440483, (112.309, 126.979, 111.10799999999999)), ('B', 125, u'ALA', 0.6448310609512947, (112.974, 127.301, 120.903)), ('B', 132, u'ILE', 0.6415247366873671, (119.501, 109.037, 121.94600000000001)), ('B', 155, u'GLU', 0.6396091899072196, (124.15799999999999, 123.374, 127.54700000000001)), ('B', 163, u'ASP', 0.7446944885329342, (112.002, 105.187, 132.996)), ('B', 175, u'ASP', 0.7672252676370934, (131.32600000000002, 100.57499999999999, 130.39200000000002)), ('B', 179, u'ASN', 0.7853902416271165, (123.119, 99.368, 132.798)), ('B', 180, u'LEU', 0.7116716585295968, (121.35799999999999, 102.46000000000001, 131.39600000000002)), ('B', 188, u'ALA', 0.5796459044542168, (119.40700000000001, 121.32, 127.233)), ('C', 10, u'SER', 0.6469264809386123, (103.909, 82.046, 127.76400000000001)), ('C', 31, u'GLN', 0.7040235301588458, (113.37799999999999, 91.17599999999999, 127.565)), ('C', 32, u'CYS', 0.7151582667565066, (110.019, 89.64, 128.484)), ('C', 40, u'LEU', 0.6951635058901711, (105.089, 82.224, 120.01100000000001)), ('C', 56, u'LEU', 0.6095635599203717, (109.12799999999999, 81.91100000000002, 134.67899999999997))]
data['rota'] = [('A', ' 235 ', 'ASP', 0.2958232965984312, (109.468, 113.35099999999997, 74.027)), ('A', ' 758 ', 'LEU', 0.12372917592768963, (89.97, 95.39199999999997, 96.352)), ('A', ' 790 ', 'ASN', 0.16118554044933223, (107.083, 101.782, 93.29499999999999)), ('A', ' 829 ', 'LEU', 0.24686483520038327, (82.81099999999998, 79.15299999999998, 98.21699999999998)), ('C', '  45 ', 'THR', 0.2489814349855088, (109.80000000000004, 72.74999999999999, 121.473))]
data['clusters'] = [('A', '811', 1, 'Dihedral angle:CB:CG:CD:OE1', (94.086, 83.579, 97.681)), ('A', '815', 1, 'smoc Outlier', (90.21000000000001, 83.529, 101.792)), ('A', '818', 1, 'smoc Outlier', (86.571, 75.687, 96.899)), ('A', '825', 1, 'Dihedral angle:CA:CB:CG:OD1', (74.898, 73.208, 90.988)), ('A', '827', 1, 'smoc Outlier', (79.56, 76.99300000000001, 93.381)), ('A', '829', 1, 'Rotamer', (82.81099999999998, 79.15299999999998, 98.21699999999998)), ('A', '831', 1, 'smoc Outlier', (86.868, 79.02799999999999, 103.169)), ('A', '833', 1, 'Dihedral angle:CA:CB:CG:OD1', (92.614, 79.43, 107.004)), ('A', '836', 1, 'Dihedral angle:CD:NE:CZ:NH1', (93.077, 82.17199999999998, 111.96000000000001)), ('A', '837', 1, 'side-chain clash', (88.683, 80.233, 115.565)), ('A', '884', 1, 'side-chain clash', (88.683, 80.233, 115.565)), ('A', '726', 2, 'side-chain clash', (92.864, 100.887, 67.74)), ('A', '729', 2, 'Dihedral angle:CB:CG:CD:OE1\nsmoc Outlier', (102.053, 106.853, 68.697)), ('A', '730', 2, 'smoc Outlier', (99.583, 107.839, 71.429)), ('A', '736', 2, 'side-chain clash\nDihedral angle:CA:CB:CG:OD1', (96.208, 115.32, 72.788)), ('A', '738', 2, 'Dihedral angle:CA:CB:CG:OD1', (92.959, 109.972, 71.526)), ('A', '740', 2, 'backbone clash\nDihedral angle:CA:CB:CG:OD1', (89.034, 106.07199999999999, 70.274)), ('A', '741', 2, 'backbone clash', (91.484, 105.38, 69.477)), ('A', '744', 2, 'side-chain clash', (92.864, 100.887, 67.74)), ('A', '470', 3, 'side-chain clash', (96.714, 109.724, 82.031)), ('A', '472', 3, 'side-chain clash\nsmoc Outlier', (94.909, 104.434, 83.393)), ('A', '473', 3, 'side-chain clash', (96.714, 109.724, 82.031)), ('A', '476', 3, 'side-chain clash', (94.909, 104.434, 83.393)), ('A', '477', 3, 'Dihedral angle:CA:CB:CG:OD1', (89.438, 106.723, 84.053)), ('A', '633', 3, 'side-chain clash', (96.901, 104.984, 88.621)), ('A', '697', 3, 'side-chain clash', (96.901, 104.984, 88.621)), ('A', '206', 4, 'side-chain clash', (118.409, 106.973, 67.604)), ('A', '209', 4, 'side-chain clash', (118.409, 106.973, 67.604)), ('A', '218', 4, 'Dihedral angle:CA:CB:CG:OD1', (123.397, 109.475, 65.366)), ('A', '220', 4, 'cablam Outlier', (120.4, 109.8, 60.5)), ('A', '221', 4, 'Dihedral angle:CA:CB:CG:OD1', (116.823, 110.93, 60.029)), ('A', '222', 4, 'smoc Outlier', (118.37799999999999, 114.424, 60.072)), ('A', '531', 5, 'side-chain clash', (87.39, 121.271, 104.956)), ('A', '564', 5, 'side-chain clash', (89.13, 115.493, 104.56)), ('A', '567', 5, 'side-chain clash', (87.39, 121.271, 104.956)), ('A', '568', 5, 'side-chain clash', (89.13, 115.493, 104.56)), ('A', '657', 5, 'smoc Outlier', (94.104, 120.18799999999999, 101.113)), ('A', '658', 5, 'Dihedral angle:CB:CG:CD:OE1\nsmoc Outlier', (94.306, 116.44700000000002, 100.44600000000001)), ('A', '851', 6, 'Dihedral angle:CA:CB:CG:OD1\ncablam CA Geom Outlier', (83.649, 84.415, 128.648)), ('A', '855', 6, 'smoc Outlier', (81.061, 85.049, 123.785)), ('A', '856', 6, 'side-chain clash', (77.392, 82.518, 118.806)), ('A', '857', 6, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1', (77.94200000000001, 86.008, 119.465)), ('A', '859', 6, 'smoc Outlier', (81.539, 82.034, 118.345)), ('A', '860', 6, 'side-chain clash\nsmoc Outlier', (77.392, 82.518, 118.806)), ('A', '689', 7, 'side-chain clash', (91.141, 103.821, 93.93)), ('A', '693', 7, 'side-chain clash', (91.141, 103.821, 93.93)), ('A', '757', 7, 'Dihedral angle:CA:C', (90.348, 94.76, 92.65599999999999)), ('A', '758', 7, 'Rotamer\nside-chain clash\nbackbone clash\nDihedral angle:CA:C\nDihedral angle:N:CA', (89.97, 95.392, 96.35199999999999)), ('A', '759', 7, 'side-chain clash\nbackbone clash\nDihedral angle:N:CA\ncablam Outlier', (92.24400000000001, 98.12299999999999, 97.74400000000001)), ('A', '499', 8, 'side-chain clash\nDihedral angle:CA:CB:CG:OD1', (82.046, 107.67899999999999, 118.93400000000001)), ('A', '512', 8, 'smoc Outlier', (83.768, 113.054, 116.745)), ('A', '513', 8, 'side-chain clash\nsmoc Outlier', (79.88, 117.167, 123.308)), ('A', '515', 8, 'smoc Outlier', (82.21300000000001, 118.248, 116.94200000000001)), ('A', '303', 9, 'Dihedral angle:CA:CB:CG:OD1', (93.93, 121.02799999999999, 83.70700000000001)), ('A', '304', 9, 'Dihedral angle:CA:CB:CG:OD1', (94.571, 117.929, 85.80199999999999)), ('A', '308', 9, 'smoc Outlier', (100.387, 115.93900000000001, 86.762)), ('A', '312', 9, 'smoc Outlier', (106.226, 115.349, 87.886)), ('A', '161', 10, 'Dihedral angle:CA:CB:CG:OD1', (118.96400000000001, 90.51, 97.918)), ('A', '164', 10, 'Dihedral angle:CA:CB:CG:OD1', (116.006, 94.695, 96.863)), ('A', '168', 10, 'smoc Outlier', (119.57199999999999, 96.068, 101.06700000000001)), ('A', '171', 10, 'smoc Outlier', (121.835, 99.71600000000001, 96.61)), ('A', '844', 11, 'side-chain clash', (86.987, 89.226, 123.77)), ('A', '845', 11, 'backbone clash', (90.375, 92.333, 124.1)), ('A', '846', 11, 'backbone clash', (90.375, 92.333, 124.1)), ('A', '849', 11, 'side-chain clash', (86.987, 89.226, 123.77)), ('A', '503', 12, 'backbone clash', (91.23, 114.736, 119.105)), ('A', '504', 12, 'cablam Outlier', (94.8, 115.8, 117.7)), ('A', '506', 12, 'smoc Outlier', (90.48700000000001, 117.386, 119.15599999999999)), ('A', '507', 12, 'backbone clash\nsmoc Outlier', (91.23, 114.736, 119.105)), ('A', '235', 13, 'Rotamer\nDihedral angle:CA:CB:CG:OD1', (109.468, 113.351, 74.027)), ('A', '239', 13, 'smoc Outlier', (110.083, 110.48, 78.977)), ('A', '465', 13, 'Dihedral angle:CA:CB:CG:OD1\nsmoc Outlier', (107.326, 108.59400000000001, 82.848)), ('A', '468', 13, 'smoc Outlier', (103.104, 106.803, 80.197)), ('A', '388', 14, 'side-chain clash\nsmoc Outlier', (109.479, 115.311, 118.649)), ('A', '672', 14, 'side-chain clash\nsmoc Outlier', (109.479, 115.311, 118.649)), ('A', '673', 14, 'smoc Outlier', (105.781, 116.21700000000001, 115.71000000000001)), ('A', '143', 15, 'smoc Outlier', (125.938, 94.238, 86.46300000000001)), ('A', '144', 15, 'Dihedral angle:CB:CG:CD:OE1\nsmoc Outlier', (128.38600000000002, 95.005, 83.657)), ('A', '145', 15, 'smoc Outlier', (127.343, 98.667, 83.468)), ('A', '39', 16, 'smoc Outlier', (108.303, 103.283, 61.752)), ('A', '42', 16, 'backbone clash', (107.739, 98.336, 65.918)), ('A', '43', 16, 'backbone clash', (107.739, 98.336, 65.918)), ('A', '876', 17, 'Dihedral angle:CB:CG:CD:OE1', (90.289, 68.303, 110.423)), ('A', '877', 17, 'smoc Outlier', (89.333, 71.46400000000001, 108.536)), ('A', '878', 17, 'smoc Outlier', (85.733, 70.23400000000001, 108.641)), ('A', '873', 18, 'side-chain clash', (88.401, 64.619, 104.048)), ('A', '875', 18, 'side-chain clash', (88.401, 64.619, 104.048)), ('A', '135', 19, 'side-chain clash\nDihedral angle:CA:CB:CG:OD1', (114.614, 90.657, 86.21100000000001)), ('A', '136', 19, 'Dihedral angle:CB:CG:CD:OE1', (116.80799999999999, 89.232, 88.96900000000001)), ('A', '246', 20, 'side-chain clash', (111.774, 108.618, 91.358)), ('A', '462', 20, 'side-chain clash', (111.774, 108.618, 91.358)), ('A', '677', 21, 'cablam Outlier', (108.0, 112.0, 103.7)), ('A', '678', 21, 'cablam CA Geom Outlier', (105.1, 110.8, 101.6)), ('A', '595', 22, 'smoc Outlier', (74.754, 84.49400000000001, 99.568)), ('A', '924', 22, 'smoc Outlier', (74.33, 82.04400000000001, 104.65499999999999)), ('A', '194', 23, 'smoc Outlier', (121.303, 123.57, 70.357)), ('A', '197', 23, 'side-chain clash', (118.096, 127.281, 67.128)), ('A', '277', 24, 'Dihedral angle:CB:CG:CD:OE1', (113.319, 131.106, 89.94600000000001)), ('A', '278', 24, 'side-chain clash', (114.836, 129.937, 91.794)), ('A', '487', 25, 'side-chain clash', (105.696, 134.839, 101.025)), ('A', '642', 25, 'side-chain clash', (105.696, 134.839, 101.025)), ('A', '435', 26, 'smoc Outlier', (95.739, 72.56700000000001, 111.971)), ('A', '436', 26, 'smoc Outlier', (97.95100000000001, 74.46400000000001, 114.422)), ('A', '622', 27, 'backbone clash', (100.702, 99.851, 100.679)), ('A', '623', 27, 'backbone clash\nside-chain clash', (101.908, 100.399, 102.279)), ('A', '329', 28, 'smoc Outlier', (103.84700000000001, 128.695, 105.723)), ('A', '330', 28, 'smoc Outlier', (102.968, 130.74499999999998, 108.806)), ('A', '200', 29, 'backbone clash\nsmoc Outlier', (117.39, 121.756, 58.11)), ('A', '225', 29, 'backbone clash', (117.39, 121.756, 58.11)), ('A', '153', 30, 'backbone clash', (133.257, 94.038, 91.977)), ('A', '154', 30, 'backbone clash\nDihedral angle:CA:CB:CG:OD1', (131.594, 92.356, 91.584)), ('A', '802', 31, 'smoc Outlier', (96.74100000000001, 79.195, 88.729)), ('A', '804', 31, 'Dihedral angle:CA:CB:CG:OD1\nsmoc Outlier', (93.24700000000001, 75.548, 86.226)), ('B', '132', 1, 'side-chain clash\nsmoc Outlier', (123.63, 111.13, 124.605)), ('B', '138', 1, 'side-chain clash', (123.63, 111.13, 124.605)), ('B', '159', 1, 'side-chain clash', (122.678, 111.204, 129.687)), ('B', '172', 1, 'side-chain clash', (122.678, 111.204, 129.687)), ('B', '134', 2, 'Dihedral angle:CA:CB:CG:OD1', (122.616, 104.167, 121.94000000000001)), ('B', '179', 2, 'smoc Outlier', (123.119, 99.368, 132.798)), ('B', '180', 2, 'smoc Outlier', (121.35799999999999, 102.46000000000001, 131.39600000000002)), ('B', '182', 2, 'cablam CA Geom Outlier', (118.2, 103.6, 126.6)), ('B', '163', 3, 'smoc Outlier', (112.002, 105.187, 132.996)), ('B', '164', 3, 'side-chain clash', (111.35, 110.338, 134.91)), ('B', '165', 3, 'side-chain clash', (114.15, 108.81, 137.528)), ('B', '77', 4, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1\nsmoc Outlier', (74.96900000000001, 123.978, 122.361)), ('B', '79', 4, 'side-chain clash', (79.88, 117.167, 123.308)), ('B', '80', 4, 'smoc Outlier', (79.611, 123.549, 121.87199999999999)), ('B', '155', 5, 'Dihedral angle:CB:CG:CD:OE1\nsmoc Outlier', (124.15799999999999, 123.374, 127.54700000000001)), ('B', '188', 5, 'smoc Outlier', (119.40700000000001, 121.32, 127.233)), ('B', '112', 6, 'side-chain clash', (105.696, 134.839, 101.025)), ('B', '114', 6, 'smoc Outlier', (105.76400000000001, 134.48000000000002, 105.754)), ('B', '101', 7, 'side-chain clash', (110.861, 137.324, 121.907)), ('B', '99', 7, 'Dihedral angle:CA:CB:CG:OD1', (107.74600000000001, 134.608, 123.027)), ('C', '10', 1, 'smoc Outlier', (103.909, 82.046, 127.76400000000001)), ('C', '14', 1, 'side-chain clash', (104.954, 87.783, 125.383)), ('C', '31', 1, 'side-chain clash\nsmoc Outlier', (112.943, 88.166, 126.398)), ('C', '32', 1, 'smoc Outlier', (110.019, 89.64, 128.484)), ('C', '35', 1, 'side-chain clash', (112.943, 88.166, 126.398)), ('C', '36', 1, 'side-chain clash', (104.954, 87.783, 125.383)), ('C', '2', 2, 'side-chain clash', (104.318, 73.534, 125.672)), ('C', '45', 2, 'Rotamer', (109.80000000000004, 72.74999999999999, 121.473)), ('C', '47', 2, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1', (113.99700000000001, 76.31, 122.692)), ('C', '6', 2, 'side-chain clash', (104.318, 73.534, 125.672)), ('C', '38', 3, 'Dihedral angle:CA:CB:CG:OD1', (110.146, 84.24100000000001, 120.194)), ('C', '40', 3, 'smoc Outlier', (105.089, 82.224, 120.01100000000001)), ('C', '56', 4, 'smoc Outlier', (109.12799999999999, 81.91100000000002, 134.67899999999997)), ('P', '15', 1, 'Backbone torsion suites: ', (91.905, 95.703, 103.08)), ('T', '18', 1, 'Backbone torsion suites: ', (62.037, 100.521, 119.151))]
data['omega'] = [('A', ' 505 ', 'PRO', None, (94.36500000000005, 118.22699999999999, 118.019)), ('B', ' 183 ', 'PRO', None, (116.24100000000004, 104.32899999999997, 125.35899999999998))]
data['cablam'] = [('A', '151', 'CYS', 'check CA trace,carbonyls, peptide', 'bend\nTTSS-', (129.4, 102.1, 91.1)), ('A', '220', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\n--SS-', (120.4, 109.8, 60.5)), ('A', '326', 'PHE', ' three-ten', 'bend\nSSSEE', (108.5, 122.7, 102.6)), ('A', '504', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n--TTG', (94.8, 115.8, 117.7)), ('A', '677', 'PRO', 'check CA trace,carbonyls, peptide', ' \nE--SS', (108.0, 112.0, 103.7)), ('A', '759', 'SER', 'check CA trace,carbonyls, peptide', 'bend\nE-SS-', (92.2, 98.1, 97.7)), ('A', '678', 'GLY', 'check CA trace', 'bend\n--SS-', (105.1, 110.8, 101.6)), ('A', '851', 'ASP', 'check CA trace', 'bend\nTSSSS', (83.6, 84.4, 128.6)), ('B', '182', 'TRP', 'check CA trace', 'bend\nS-SSE', (118.2, 103.6, 126.6))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-11993/7b3b/Model_validation_1/validation_cootdata/molprobity_probe7b3b_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)
