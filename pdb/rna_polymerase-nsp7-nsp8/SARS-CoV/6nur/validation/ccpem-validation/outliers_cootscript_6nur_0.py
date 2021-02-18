
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
data['probe'] = [(' A 583  ARG  HG3', ' A 583  ARG HH11', -0.894, (124.906, 139.306, 145.095)), (' A 487  CYS  SG ', ' A 642  HIS  CE1', -0.863, (128.909, 161.139, 142.377)), (' A 412  PRO  HG3', ' C  14  LEU HD23', -0.801, (148.095, 138.694, 178.568)), (' A 631  ARG  HG3', ' A 663  LEU HD21', -0.732, (145.664, 154.338, 147.756)), (' A 306  CYS  HG ', ' A1001   ZN ZN  ', -0.719, (147.469, 164.842, 131.837)), (' A 619  TYR  HE1', ' A 786  LEU HD21', -0.718, (149.097, 140.25, 143.817)), (' A 583  ARG  HG3', ' A 583  ARG  NH1', -0.674, (124.577, 139.303, 146.168)), (' A 306  CYS  SG ', ' A1001   ZN ZN  ', -0.666, (147.459, 165.177, 131.349)), (' A 487  CYS  SG ', ' A 642  HIS  ND1', -0.664, (129.796, 161.36, 141.63)), (' A 372  LEU  HA ', ' B  87  MET  HE1', -0.652, (134.865, 171.205, 162.887)), (' A 631  ARG  HG3', ' A 663  LEU  CD2', -0.631, (146.271, 154.754, 148.143)), (' A 733  ARG  O  ', ' A 734  ASN  C  ', -0.62, (148.21, 151.919, 120.982)), (' A 718  LYS  HG2', ' A 721  ARG HH12', -0.602, (147.55, 130.954, 113.509)), (' C   5  ASP  OD2', ' D  97  LYS  NZ ', -0.569, (143.935, 119.625, 182.596)), (' A 712  GLY  O  ', ' A 721  ARG  HG3', -0.557, (151.975, 132.211, 117.531)), (' A 402  THR  O  ', ' B 129  MET  SD ', -0.53, (155.989, 166.461, 172.81)), (' A 412  PRO  HG3', ' C  14  LEU  CD2', -0.513, (148.919, 138.99, 179.225)), (' B 112  ASP  N  ', ' B 112  ASP  OD1', -0.501, (154.922, 182.798, 148.458)), (' A 571  PHE  CZ ', ' A 642  HIS  CD2', -0.497, (133.221, 160.44, 142.091)), (' A 306  CYS  O  ', ' A 310  CYS  SG ', -0.494, (148.844, 163.219, 132.902)), (' D 157  GLN  O  ', ' D 158  GLN  HG3', -0.492, (178.729, 134.853, 197.009)), (' A 456  TYR  CE1', ' A 624  ARG  HD3', -0.483, (151.082, 150.842, 156.514)), (' A 785  VAL HG13', ' A 789  GLN  HG3', -0.48, (151.808, 143.581, 138.95)), (' A 618  ASP  O  ', ' A 794  MET  SD ', -0.465, (150.701, 136.32, 146.315)), (' A 583  ARG  CG ', ' A 583  ARG  NH1', -0.457, (124.458, 138.548, 145.98)), (' C  14  LEU HD22', ' C  36  HIS  CG ', -0.457, (150.828, 137.021, 178.472)), (' A 619  TYR  CE1', ' A 786  LEU HD21', -0.447, (149.354, 140.744, 144.278)), (' B 177  SER  N  ', ' B 178  PRO  CD ', -0.446, (172.787, 149.479, 180.981)), (' A 647  ASN  O  ', ' A 651  ARG  HG3', -0.44, (134.412, 165.553, 137.151)), (' A 117  GLN  HG2', ' A 118  ARG  HG3', -0.436, (184.468, 146.45, 119.798)), (' C  14  LEU HD22', ' C  36  HIS  CD2', -0.435, (150.605, 137.59, 178.507)), (' A 164  ASP  OD1', ' A 165  PHE  N  ', -0.432, (161.524, 140.7, 149.877)), (' A 642  HIS  HB3', ' A 646  CYS  HB2', -0.422, (130.837, 162.872, 138.908)), (' A 456  TYR  CD1', ' A 624  ARG  HD3', -0.421, (151.604, 150.818, 156.513)), (' A 402  THR  OG1', ' A 403  ASN  N  ', -0.413, (152.969, 165.994, 175.548)), (' A 372  LEU  CA ', ' B  87  MET  HE1', -0.41, (134.961, 171.074, 162.459)), (' A 208  ASP  N  ', ' A 208  ASP  OD1', -0.406, (166.301, 145.305, 122.229)), (' A 712  GLY  O  ', ' A 721  ARG  CG ', -0.406, (151.924, 132.574, 117.67))]
data['smoc'] = [('A', 117, 'GLN', 0.37742502324079297, (181.39999389648438, 146.27200317382812, 118.78299713134766)), ('A', 131, 'LEU', 0.5651035704463465, (163.75399780273438, 142.031005859375, 137.10699462890625)), ('A', 135, 'ASP', 0.6637686523706707, (161.68699645996094, 133.57899475097656, 139.40499877929688)), ('A', 157, 'PHE', 0.5700859927497004, (173.43099975585938, 134.92599487304688, 146.86199951171875)), ('A', 160, 'LYS', 0.6301949834407796, (168.7830047607422, 132.8820037841797, 152.91200256347656)), ('A', 171, 'ILE', 0.46406716600154846, (168.47300720214844, 143.9199981689453, 148.3040008544922)), ('A', 178, 'LEU', 0.49121133755281443, (172.44700622558594, 149.66799926757812, 139.06399536132812)), ('A', 192, 'PHE', 0.5385259532214869, (170.85000610351562, 158.81500244140625, 120.29199981689453)), ('A', 193, 'CYS', 0.5757152099820967, (167.3780059814453, 160.14199829101562, 119.6500015258789)), ('A', 211, 'ASP', 0.5119437014862253, (173.6999969482422, 147.15899658203125, 125.87000274658203)), ('A', 241, 'LEU', 0.524625664385816, (162.17799377441406, 150.38999938964844, 131.54400634765625)), ('A', 242, 'MET', 0.5230445818805073, (159.80499267578125, 152.38499450683594, 133.76499938964844)), ('A', 247, 'LEU', 0.52951117537377, (163.5189971923828, 149.96299743652344, 141.70199584960938)), ('A', 273, 'TYR', 0.5563996039879606, (156.98800659179688, 173.56700134277344, 147.5989990234375)), ('A', 274, 'ASP', 0.5262539092683376, (156.2449951171875, 173.64700317382812, 143.88900756835938)), ('A', 279, 'ARG', 0.5701085424499036, (159.98399353027344, 168.1219940185547, 137.15699768066406)), ('A', 286, 'TYR', 0.5925401936116224, (165.5780029296875, 161.70799255371094, 130.4720001220703)), ('A', 291, 'ASP', 0.567307459245995, (155.7570037841797, 162.10800170898438, 122.76499938964844)), ('A', 298, 'CYS', 0.5252034000739334, (147.66299438476562, 166.67100524902344, 137.53399658203125)), ('A', 312, 'ASN', 0.5031394615425304, (153.5780029296875, 157.85400390625, 136.97799682617188)), ('A', 316, 'LEU', 0.5171278070690737, (159.90899658203125, 159.0030059814453, 139.7570037841797)), ('A', 350, 'GLU', 0.4178282634193834, (151.92599487304688, 161.73699951171875, 142.66900634765625)), ('A', 358, 'ASP', 0.615498915322726, (137.62100219726562, 178.7480010986328, 148.9530029296875)), ('A', 369, 'LYS', 0.46208564056383505, (131.60400390625, 173.66900634765625, 158.84500122070312)), ('A', 390, 'ASP', 0.5428299891782468, (161.63699340820312, 159.6020050048828, 166.9199981689453)), ('A', 398, 'VAL', 0.49682611978968555, (156.25399780273438, 166.05099487304688, 161.72999572753906)), ('A', 402, 'THR', 0.561856771803917, (152.38699340820312, 166.41700744628906, 173.70199584960938)), ('A', 408, 'GLN', 0.4669084362285927, (149.82699584960938, 151.5850067138672, 174.48899841308594)), ('A', 412, 'PRO', 0.5471651354533443, (145.3489990234375, 139.05499267578125, 177.58399963378906)), ('A', 419, 'PHE', 0.5197441183128122, (133.26699829101562, 126.74299621582031, 178.44700622558594)), ('A', 445, 'ASP', 0.5265286649035442, (154.22300720214844, 145.30499267578125, 174.9429931640625)), ('A', 452, 'ASP', 0.5414012877380464, (153.3300018310547, 148.44400024414062, 163.7030029296875)), ('A', 462, 'THR', 0.5545642421991744, (156.89599609375, 152.57000732421875, 142.4199981689453)), ('A', 474, 'GLU', 0.5329411721051369, (140.27200317382812, 149.2949981689453, 130.71600341796875)), ('A', 481, 'ASP', 0.6014154768672032, (130.61399841308594, 147.2169952392578, 134.02499389648438)), ('A', 516, 'TYR', 0.564242131184862, (125.73999786376953, 163.16200256347656, 162.1510009765625)), ('A', 519, 'MET', 0.5297335317322718, (124.93299865722656, 168.6959991455078, 161.0780029296875)), ('A', 525, 'ASP', 0.5319914304140719, (125.9739990234375, 168.49400329589844, 151.5290069580078)), ('A', 538, 'THR', 0.4784795356659475, (142.85299682617188, 165.16000366210938, 157.5240020751953)), ('A', 542, 'MET', 0.4945719965039513, (146.1020050048828, 154.41600036621094, 164.68899536132812)), ('A', 553, 'ARG', 0.5916935646886473, (152.13900756835938, 139.96800231933594, 166.13099670410156)), ('A', 560, 'VAL', 0.4332913340730392, (139.6929931640625, 157.4429931640625, 159.83799743652344)), ('A', 575, 'LEU', 0.6147458482401374, (128.47500610351562, 152.20799255371094, 143.96800231933594)), ('A', 577, 'LYS', 0.6749613876052895, (125.927001953125, 149.4499969482422, 147.77000427246094)), ('A', 582, 'THR', 0.6838677986530314, (124.97699737548828, 142.18800354003906, 143.0590057373047)), ('A', 610, 'GLU', 0.5692885967819357, (136.9929962158203, 123.81999969482422, 129.49899291992188)), ('A', 643, 'ASN', 0.6868689668995117, (129.8179931640625, 161.13400268554688, 134.58200073242188)), ('A', 655, 'LEU', 0.5077042864718952, (140.81900024414062, 162.36700439453125, 143.91900634765625)), ('A', 658, 'GLU', 0.4406262060114319, (140.9550018310547, 160.7969970703125, 148.77000427246094)), ('A', 663, 'LEU', 0.5003826819202705, (147.3470001220703, 157.65499877929688, 150.97799682617188)), ('A', 669, 'CYS', 0.40942308390871673, (150.3159942626953, 157.28199768066406, 166.9759979248047)), ('A', 676, 'LYS', 0.4687471142492634, (152.0469970703125, 157.8679962158203, 155.98599243164062)), ('A', 707, 'LEU', 0.47859104919437595, (150.52099609375, 135.79800415039062, 127.11799621582031)), ('A', 740, 'GLU', 0.6259412218177671, (136.61300659179688, 146.20399475097656, 120.7020034790039)), ('A', 756, 'MET', 0.4955708337462796, (135.94000244140625, 135.2729949951172, 142.20700073242188)), ('A', 785, 'VAL', 0.5302520208334696, (154.0290069580078, 140.6219940185547, 138.81199645996094)), ('A', 789, 'GLN', 0.48469971058846895, (154.3159942626953, 145.83099365234375, 141.11199951171875)), ('A', 790, 'ASN', 0.5069388896864596, (154.1840057373047, 145.81900024414062, 144.9149932861328)), ('A', 794, 'MET', 0.48398868526901306, (155.33700561523438, 135.95399475097656, 147.2480010986328)), ('A', 802, 'GLU', 0.6114728212798723, (143.57400512695312, 122.30999755859375, 143.57000732421875)), ('A', 817, 'THR', 0.5283021592361135, (135.16700744628906, 123.98200225830078, 151.0970001220703)), ('A', 824, 'ASP', 0.5811703826560708, (119.17500305175781, 114.00900268554688, 147.62399291992188)), ('A', 837, 'ILE', 0.4754832882110185, (135.91600036621094, 127.91400146484375, 166.77999877929688)), ('A', 859, 'PHE', 0.5124270447589797, (127.88500213623047, 130.98500061035156, 171.14100646972656)), ('A', 892, 'HIS', 0.4702729572131988, (119.38600158691406, 128.47000122070312, 177.43299865722656)), ('A', 915, 'ARG', 0.5309561650302027, (118.2300033569336, 125.68099975585938, 157.86900329589844)), ('B', 77, 'GLU', 0.49566253462553217, (120.72100067138672, 171.55499267578125, 169.52699279785156)), ('B', 83, 'VAL', 0.5188408554896089, (130.76400756835938, 170.45899963378906, 169.73300170898438)), ('B', 91, 'LEU', 0.5382941686547592, (141.43800354003906, 175.968994140625, 168.14199829101562)), ('B', 98, 'LEU', 0.3613730898170194, (151.093994140625, 179.0500030517578, 167.71400451660156)), ('B', 106, 'ILE', 0.5093162156997209, (158.697998046875, 181.6320037841797, 158.02099609375)), ('B', 111, 'ARG', 0.5198260962089555, (157.7209930419922, 183.76600646972656, 147.96299743652344)), ('B', 114, 'CYS', 0.4735862382757327, (152.78500366210938, 179.8470001220703, 151.4080047607422)), ('B', 117, 'LEU', 0.5737065530126649, (153.48300170898438, 172.4459991455078, 156.91600036621094)), ('B', 125, 'ALA', 0.5494507893497718, (159.01600646972656, 174.83200073242188, 167.83599853515625)), ('B', 150, 'ALA', 0.5793305602942518, (167.3939971923828, 170.3679962158203, 162.3300018310547)), ('B', 169, 'LEU', 0.4520655247305523, (172.1909942626953, 162.58799743652344, 182.36599731445312)), ('B', 172, 'ILE', 0.5905051196968173, (172.7209930419922, 157.30499267578125, 181.01400756835938)), ('B', 174, 'MET', 0.48053139316212473, (176.7220001220703, 151.9340057373047, 178.79299926757812)), ('B', 180, 'LEU', 0.682327276309291, (166.80299377441406, 152.03399658203125, 182.2779998779297)), ('C', 8, 'CYS', 0.42959925034634355, (144.79400634765625, 128.7429962158203, 179.6699981689453)), ('C', 11, 'VAL', 0.547161461223099, (146.1060028076172, 133.82200622558594, 180.19500732421875)), ('C', 22, 'VAL', 0.475651868539662, (152.54600524902344, 145.13499450683594, 186.31700134277344)), ('C', 23, 'GLU', 0.4486617419365401, (152.052001953125, 147.37100219726562, 183.2429962158203)), ('C', 33, 'VAL', 0.4782541501102034, (154.35800170898438, 139.5469970703125, 178.00399780273438)), ('C', 48, 'ALA', 0.21791717689511414, (155.66000366210938, 125.8949966430664, 178.52699279785156)), ('C', 51, 'LYS', 0.4104976488711174, (158.0489959716797, 129.79600524902344, 181.2220001220703)), ('C', 67, 'ASP', 0.114268845290516, (146.3209991455078, 135.5399932861328, 198.3459930419922)), ('D', 90, 'MET', 0.4443002734465865, (140.86000061035156, 130.5229949951172, 189.1649932861328)), ('D', 116, 'PRO', 0.4626131633339681, (161.9810028076172, 135.28399658203125, 194.8679962158203)), ('D', 123, 'THR', 0.5380590279425391, (169.53500366210938, 129.5449981689453, 181.66200256347656)), ('D', 159, 'VAL', 0.49203401178947803, (174.2519989013672, 135.3159942626953, 201.72799682617188)), ('D', 164, 'SER', 0.5087471380063764, (173.06100463867188, 144.28599548339844, 204.6909942626953)), ('D', 169, 'LEU', 0.0751957577407261, (177.22000122070312, 129.71299743652344, 205.32000732421875)), ('D', 172, 'ILE', 0.265451918535872, (173.58700561523438, 129.82000732421875, 209.43699645996094)), ('D', 180, 'LEU', 0.2641828586654796, (171.21200561523438, 136.73399353027344, 212.6840057373047)), ('D', 192, 'ASN', 0.461537718973424, (173.3699951171875, 123.71900177001953, 184.7740020751953))]
data['rota'] = [('A', ' 583 ', 'ARG', 0.028116265133834216, (125.30000000000004, 138.43, 142.7)), ('A', ' 631 ', 'ARG', 0.0, (145.66399999999993, 153.137, 144.937)), ('A', ' 651 ', 'ARG', 0.2810002969545315, (136.57199999999995, 164.612, 139.818)), ('A', ' 733 ', 'ARG', 0.0, (150.96399999999994, 151.433, 119.82299999999996)), ('A', ' 785 ', 'VAL', 0.25515418933865, (154.029, 140.622, 138.812))]
data['clusters'] = [('A', '571', 1, 'side-chain clash', (133.221, 160.44, 142.091)), ('A', '642', 1, 'side-chain clash', (130.837, 162.872, 138.908)), ('A', '643', 1, 'smoc Outlier', (129.8179931640625, 161.13400268554688, 134.58200073242188)), ('A', '646', 1, 'side-chain clash', (130.837, 162.872, 138.908)), ('A', '647', 1, 'side-chain clash', (134.412, 165.553, 137.151)), ('A', '651', 1, 'side-chain clash\nRotamer', (136.57199999999995, 164.612, 139.818)), ('A', '652', 1, 'Bond angle:CA:CB:CG', (140.164, 165.805, 140.287)), ('A', '655', 1, 'smoc Outlier', (140.81900024414062, 162.36700439453125, 143.91900634765625)), ('A', '658', 1, 'smoc Outlier', (140.9550018310547, 160.7969970703125, 148.77000427246094)), ('A', '456', 2, 'side-chain clash', (151.604, 150.818, 156.513)), ('A', '624', 2, 'side-chain clash', (151.604, 150.818, 156.513)), ('A', '631', 2, 'side-chain clash\nRotamer', (145.66399999999993, 153.137, 144.937)), ('A', '663', 2, 'side-chain clash\nsmoc Outlier', (146.271, 154.754, 148.143)), ('A', '676', 2, 'smoc Outlier', (152.0469970703125, 157.8679962158203, 155.98599243164062)), ('A', '677', 2, 'cablam Outlier', (154.1, 157.0, 152.8)), ('A', '678', 2, 'cablam CA Geom Outlier', (151.2, 154.9, 151.2)), ('A', '618', 3, 'side-chain clash', (150.701, 136.32, 146.315)), ('A', '619', 3, 'side-chain clash', (149.354, 140.744, 144.278)), ('A', '785', 3, 'side-chain clash\nRotamer\nsmoc Outlier', (154.029, 140.622, 138.812)), ('A', '786', 3, 'side-chain clash', (149.354, 140.744, 144.278)), ('A', '789', 3, 'side-chain clash\nsmoc Outlier', (151.808, 143.581, 138.95)), ('A', '790', 3, 'smoc Outlier', (154.1840057373047, 145.81900024414062, 144.9149932861328)), ('A', '794', 3, 'side-chain clash\nsmoc Outlier', (150.701, 136.32, 146.315)), ('A', '273', 4, 'smoc Outlier', (156.98800659179688, 173.56700134277344, 147.5989990234375)), ('A', '274', 4, 'cablam Outlier\nsmoc Outlier', (156.2, 173.6, 143.9)), ('A', '275', 4, 'cablam Outlier', (159.0, 172.0, 141.9)), ('A', '279', 4, 'smoc Outlier', (159.98399353027344, 168.1219940185547, 137.15699768066406)), ('A', '326', 4, 'cablam CA Geom Outlier', (155.5, 167.4, 150.4)), ('A', '241', 5, 'smoc Outlier', (162.17799377441406, 150.38999938964844, 131.54400634765625)), ('A', '242', 5, 'Bond angle:CA:C\nsmoc Outlier', (159.805, 152.38500000000002, 133.765)), ('A', '243', 5, 'Bond angle:N', (159.312, 149.786, 136.6)), ('A', '247', 5, 'smoc Outlier', (163.5189971923828, 149.96299743652344, 141.70199584960938)), ('A', '462', 5, 'smoc Outlier', (156.89599609375, 152.57000732421875, 142.4199981689453)), ('A', '369', 6, 'smoc Outlier', (131.60400390625, 173.66900634765625, 158.84500122070312)), ('A', '402', 6, 'backbone clash\nsmoc Outlier', (134.961, 171.074, 162.459)), ('A', '403', 6, 'backbone clash', (134.961, 171.074, 162.459)), ('A', '487', 6, 'side-chain clash', (134.865, 171.205, 162.887)), ('A', '712', 7, 'side-chain clash\nbackbone clash', (151.924, 132.574, 117.67)), ('A', '718', 7, 'side-chain clash', (147.55, 130.954, 113.509)), ('A', '721', 7, 'side-chain clash\nbackbone clash', (151.924, 132.574, 117.67)), ('A', '192', 8, 'smoc Outlier', (170.85000610351562, 158.81500244140625, 120.29199981689453)), ('A', '193', 8, 'smoc Outlier', (167.3780059814453, 160.14199829101562, 119.6500015258789)), ('A', '194', 8, 'Bond angle:CA:CB:CG', (168.724, 163.654, 118.962)), ('A', '298', 9, 'smoc Outlier', (147.66299438476562, 166.67100524902344, 137.53399658203125)), ('A', '306', 9, 'side-chain clash', (148.844, 163.219, 132.902)), ('A', '310', 9, 'side-chain clash', (148.844, 163.219, 132.902)), ('A', '516', 10, 'smoc Outlier', (125.73999786376953, 163.16200256347656, 162.1510009765625)), ('A', '517', 10, 'Bond angle:CA:CB:CG', (123.202, 164.336, 164.73)), ('A', '519', 10, 'smoc Outlier', (124.93299865722656, 168.6959991455078, 161.0780029296875)), ('A', '740', 11, 'smoc Outlier', (136.61300659179688, 146.20399475097656, 120.7020034790039)), ('A', '741', 11, 'Bond angle:CA:CB:CG', (139.991, 144.738, 121.59400000000001)), ('A', '743', 11, 'Bond angle:CA:CB:CG', (135.967, 143.571, 125.05)), ('A', '164', 12, 'backbone clash', (161.524, 140.7, 149.877)), ('A', '165', 12, 'backbone clash', (161.524, 140.7, 149.877)), ('A', '167', 12, 'cablam Outlier', (163.1, 140.1, 154.7)), ('A', '607', 13, 'cablam Outlier', (131.2, 128.6, 134.9)), ('A', '608', 13, 'cablam Outlier', (132.1, 126.8, 131.7)), ('A', '610', 13, 'smoc Outlier', (136.9929962158203, 123.81999969482422, 129.49899291992188)), ('A', '542', 14, 'smoc Outlier', (146.1020050048828, 154.41600036621094, 164.68899536132812)), ('A', '669', 14, 'smoc Outlier', (150.3159942626953, 157.28199768066406, 166.9759979248047)), ('A', '575', 15, 'smoc Outlier', (128.47500610351562, 152.20799255371094, 143.96800231933594)), ('A', '577', 15, 'smoc Outlier', (125.927001953125, 149.4499969482422, 147.77000427246094)), ('A', '412', 16, 'smoc Outlier', (145.3489990234375, 139.05499267578125, 177.58399963378906)), ('A', '441', 16, 'Bond angle:CA:CB:CG', (144.222, 137.0, 172.429)), ('A', '824', 17, 'cablam Outlier\nBond angle:C\nsmoc Outlier', (119.2, 114.0, 147.6)), ('A', '825', 17, 'Bond angle:N:CA', (121.482, 116.256, 145.642)), ('A', '377', 18, 'Bond angle:CA:CB:CG', (143.5, 170.22299999999998, 159.54299999999998)), ('A', '538', 18, 'smoc Outlier', (142.85299682617188, 165.16000366210938, 157.5240020751953)), ('A', '117', 19, 'side-chain clash\nsmoc Outlier', (184.468, 146.45, 119.798)), ('A', '118', 19, 'side-chain clash', (184.468, 146.45, 119.798)), ('A', '582', 20, 'smoc Outlier', (124.97699737548828, 142.18800354003906, 143.0590057373047)), ('A', '583', 20, 'side-chain clash\nRotamer', (125.30000000000004, 138.43, 142.7)), ('A', '845', 21, 'cablam Outlier', (136.7, 140.3, 174.7)), ('A', '846', 21, 'Bond angle:CA:CB:CG', (135.49200000000002, 140.98100000000002, 178.296)), ('A', '151', 22, 'cablam CA Geom Outlier', (176.3, 145.6, 142.8)), ('A', '178', 22, 'smoc Outlier', (172.44700622558594, 149.66799926757812, 139.06399536132812)), ('A', '733', 23, 'cablam CA Geom Outlier\nbackbone clash\nRotamer', (151.0, 151.4, 119.8)), ('A', '734', 23, 'backbone clash', (148.21, 151.919, 120.982)), ('B', '174', 1, 'smoc Outlier', (176.7220001220703, 151.9340057373047, 178.79299926757812)), ('B', '177', 1, 'side-chain clash', (172.787, 149.479, 180.981)), ('B', '178', 1, 'side-chain clash', (172.787, 149.479, 180.981)), ('B', '180', 1, 'smoc Outlier', (166.80299377441406, 152.03399658203125, 182.2779998779297)), ('B', '182', 1, 'cablam CA Geom Outlier', (164.1, 152.4, 177.3)), ('B', '111', 2, 'smoc Outlier', (157.7209930419922, 183.76600646972656, 147.96299743652344)), ('B', '112', 2, 'side-chain clash\nBond angle:CA:CB:CG', (153.935, 184.17899999999997, 148.117)), ('B', '114', 2, 'smoc Outlier', (152.78500366210938, 179.8470001220703, 151.4080047607422)), ('B', '98', 3, 'smoc Outlier', (151.093994140625, 179.0500030517578, 167.71400451660156)), ('B', '99', 3, 'cablam Outlier', (151.3, 182.8, 167.2)), ('B', '169', 4, 'smoc Outlier', (172.1909942626953, 162.58799743652344, 182.36599731445312)), ('B', '172', 4, 'smoc Outlier', (172.7209930419922, 157.30499267578125, 181.01400756835938)), ('C', '11', 1, 'smoc Outlier', (146.1060028076172, 133.82200622558594, 180.19500732421875)), ('C', '14', 1, 'side-chain clash', (150.605, 137.59, 178.507)), ('C', '33', 1, 'smoc Outlier', (154.35800170898438, 139.5469970703125, 178.00399780273438)), ('C', '36', 1, 'side-chain clash', (150.605, 137.59, 178.507)), ('C', '5', 1, 'Bond angle:CA:CB:CG', (145.74599999999998, 123.804, 180.61399999999998)), ('C', '8', 1, 'smoc Outlier', (144.79400634765625, 128.7429962158203, 179.6699981689453)), ('C', '22', 2, 'smoc Outlier', (152.54600524902344, 145.13499450683594, 186.31700134277344)), ('C', '23', 2, 'smoc Outlier', (152.052001953125, 147.37100219726562, 183.2429962158203)), ('C', '48', 3, 'smoc Outlier', (155.66000366210938, 125.8949966430664, 178.52699279785156)), ('C', '51', 3, 'smoc Outlier', (158.0489959716797, 129.79600524902344, 181.2220001220703)), ('C', '64', 4, 'cablam Outlier', (150.7, 143.1, 200.0)), ('C', '67', 4, 'smoc Outlier', (146.3209991455078, 135.5399932861328, 198.3459930419922)), ('D', '157', 1, 'side-chain clash', (178.729, 134.853, 197.009)), ('D', '158', 1, 'side-chain clash', (178.729, 134.853, 197.009)), ('D', '159', 1, 'smoc Outlier', (174.2519989013672, 135.3159942626953, 201.72799682617188)), ('D', '180', 2, 'smoc Outlier', (171.21200561523438, 136.73399353027344, 212.6840057373047)), ('D', '182', 2, 'cablam CA Geom Outlier', (166.6, 137.4, 209.4)), ('D', '169', 3, 'smoc Outlier', (177.22000122070312, 129.71299743652344, 205.32000732421875)), ('D', '172', 3, 'smoc Outlier', (173.58700561523438, 129.82000732421875, 209.43699645996094)), ('D', '90', 4, 'smoc Outlier', (140.86000061035156, 130.5229949951172, 189.1649932861328)), ('D', '92', 4, 'Bond angle:CA:CB:CG', (145.489, 128.999, 191.991))]
data['omega'] = [('A', ' 505 ', 'PRO', None, (140.83699999999988, 165.133, 165.982)), ('B', ' 183 ', 'PRO', None, (162.44799999999992, 153.121, 175.681)), ('D', ' 183 ', 'PRO', None, (165.02599999999995, 138.321, 207.82599999999994))]
data['cablam'] = [('A', '167', 'GLU', ' alpha helix', 'bend\nSSSST', (163.1, 140.1, 154.7)), ('A', '226', 'ALA', 'check CA trace,carbonyls, peptide', ' \nE--TT', (164.9, 163.6, 105.2)), ('A', '274', 'ASP', 'check CA trace,carbonyls, peptide', ' \n----H', (156.2, 173.6, 143.9)), ('A', '275', 'PHE', 'check CA trace,carbonyls, peptide', ' \n---HH', (159.0, 172.0, 141.9)), ('A', '481', 'ASP', ' alpha helix', 'turn\nTTTT-', (130.6, 147.2, 134.0)), ('A', '504', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n--TTG', (141.5, 162.7, 165.9)), ('A', '509', 'TRP', 'check CA trace,carbonyls, peptide', 'turn\nGGT-B', (134.3, 164.8, 172.0)), ('A', '607', 'SER', 'check CA trace,carbonyls, peptide', 'turn\nHHTT-', (131.2, 128.6, 134.9)), ('A', '608', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\nHTT-S', (132.1, 126.8, 131.7)), ('A', '677', 'PRO', 'check CA trace,carbonyls, peptide', ' \nE--S-', (154.1, 157.0, 152.8)), ('A', '824', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\n-SSSE', (119.2, 114.0, 147.6)), ('A', '845', 'ASP', 'check CA trace,carbonyls, peptide', ' \nEE-S-', (136.7, 140.3, 174.7)), ('A', '151', 'CYS', 'check CA trace', 'bend\nTTSS-', (176.3, 145.6, 142.8)), ('A', '326', 'PHE', 'check CA trace', 'bend\nGGSEE', (155.5, 167.4, 150.4)), ('A', '678', 'GLY', 'check CA trace', 'bend\n--S--', (151.2, 154.9, 151.2)), ('A', '733', 'ARG', 'check CA trace', 'bend\nTSS--', (151.0, 151.4, 119.8)), ('B', '99', 'ASP', 'check CA trace,carbonyls, peptide', ' \nHH-SH', (151.3, 182.8, 167.2)), ('B', '182', 'TRP', 'check CA trace', 'bend\nS-SSE', (164.1, 152.4, 177.3)), ('C', '64', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\nS-SS-', (150.7, 143.1, 200.0)), ('D', '182', 'TRP', 'check CA trace', 'bend\nS-SSE', (166.6, 137.4, 209.4))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-0520/6nur/Model_validation_1/validation_cootdata/molprobity_probe6nur_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)
