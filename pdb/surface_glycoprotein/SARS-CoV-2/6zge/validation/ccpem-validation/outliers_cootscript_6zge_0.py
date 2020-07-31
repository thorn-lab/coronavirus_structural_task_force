
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
data['cbeta'] = []
data['smoc'] = []
data['jpred'] = []
data['rota'] = [('A', ' 312 ', 'ILE', 0.024658307039693874, (232.65700000000007, 240.145, 227.46999999999994)), ('A', ' 331 ', 'ASN', 0.0, (255.968, 220.30199999999994, 182.41099999999997)), ('A', ' 525 ', 'CYS', 0.06658192723989487, (246.448, 218.95499999999996, 182.17699999999994)), ('A', ' 563 ', 'GLN', 0.28486177013918096, (250.33500000000004, 208.576, 195.08499999999998)), ('A', ' 878 ', 'LEU', 0.05798985264728657, (200.50700000000015, 233.10999999999996, 257.465)), ('A', ' 916 ', 'LEU', 0.1937144265816937, (213.11500000000007, 235.94500000000005, 275.487)), ('A', '1039 ', 'ARG', 0.20642985381994094, (219.82700000000006, 221.97999999999996, 259.185)), ('B', ' 312 ', 'ILE', 0.024610800002673586, (229.46800000000005, 192.81299999999996, 227.46999999999994)), ('B', ' 331 ', 'ASN', 0.0, (200.626, 182.53899999999996, 182.414)), ('B', ' 525 ', 'CYS', 0.06658192723989487, (204.218, 191.457, 182.179)), ('B', ' 563 ', 'GLN', 0.28339598327079046, (193.287, 193.27999999999994, 195.088)), ('B', ' 878 ', 'LEU', 0.05827639972252902, (239.44800000000006, 224.178, 257.462)), ('B', ' 916 ', 'LEU', 0.19359691601857426, (235.603, 211.842, 275.485)), ('B', '1039 ', 'ARG', 0.20391003941131375, (220.15100000000007, 213.00799999999998, 259.184)), ('C', ' 312 ', 'ILE', 0.024671717607668283, (190.077, 219.239, 227.46899999999997)), ('C', ' 331 ', 'ASN', 0.0, (195.60300000000007, 249.35099999999994, 182.41099999999997)), ('C', ' 525 ', 'CYS', 0.06658192723989487, (201.53000000000006, 241.78, 182.17599999999996)), ('C', ' 563 ', 'GLN', 0.28563192947981253, (208.57500000000005, 250.33499999999998, 195.084)), ('C', ' 878 ', 'LEU', 0.05803773803548787, (212.2460000000001, 194.913, 257.462)), ('C', ' 916 ', 'LEU', 0.19284406923704409, (203.487, 204.41400000000004, 275.484)), ('C', '1039 ', 'ARG', 0.20331592727515962, (212.22500000000005, 217.21, 259.183))]
data['clusters'] = [('A', '185', 1, 'cablam CA Geom Outlier\nbackbone clash', (230.6, 279.0, 200.2)), ('A', '212', 1, 'backbone clash', (231.049, 276.579, 201.904)), ('A', '214', 1, 'cablam CA Geom Outlier', (236.0, 272.5, 202.8)), ('A', '215', 1, 'Ramachandran', (236.18500000000003, 268.889, 203.883)), ('A', '216', 1, 'side-chain clash', (230.764, 265.847, 202.064)), ('A', '217', 1, 'side-chain clash', (230.764, 265.847, 202.064)), ('A', '218', 1, 'cablam CA Geom Outlier', (229.5, 264.3, 208.5)), ('A', '29', 1, 'backbone clash\nside-chain clash', (238.14, 262.432, 201.219)), ('A', '30', 1, 'backbone clash', (238.702, 262.731, 204.538)), ('A', '62', 1, 'side-chain clash', (238.14, 262.432, 201.219)), ('A', '391', 2, 'side-chain clash', (245.048, 218.79, 183.124)), ('A', '524', 2, 'cablam Outlier', (247.0, 215.6, 180.4)), ('A', '525', 2, 'cablam Outlier\nside-chain clash\nRotamer', (246.4, 219.0, 182.2)), ('A', '527', 2, 'cablam Outlier', (246.0, 225.1, 179.2)), ('A', '638', 3, 'cablam Outlier', (248.8, 246.7, 218.9)), ('A', '640', 3, 'cablam CA Geom Outlier', (249.5, 250.2, 223.9)), ('A', '642', 3, 'side-chain clash', (248.364, 244.464, 222.848)), ('A', '651', 3, 'side-chain clash', (248.364, 244.464, 222.848)), ('A', '14', 4, 'side-chain clash', (238.606, 271.649, 171.396)), ('A', '158', 4, 'side-chain clash', (238.606, 271.649, 171.396)), ('A', '159', 4, 'cablam Outlier', (235.4, 266.3, 174.5)), ('A', '101', 5, 'backbone clash\nside-chain clash', (234.236, 268.774, 187.927)), ('A', '242', 5, 'side-chain clash', (234.236, 268.774, 187.927)), ('A', '96', 5, 'backbone clash', (230.46, 270.964, 188.434)), ('A', '310', 6, 'cablam CA Geom Outlier', (228.5, 245.7, 229.6)), ('A', '600', 6, 'cablam CA Geom Outlier', (231.6, 248.8, 229.6)), ('A', '570', 7, 'Bond angle:C', (238.627, 214.69899999999998, 208.353)), ('A', '571', 7, 'Bond angle:N:CA', (239.40200000000002, 213.64499999999998, 204.724)), ('A', '331', 8, 'side-chain clash\nRotamer', (255.968, 220.30199999999994, 182.41099999999997)), ('A', '580', 8, 'side-chain clash', (259.02, 222.002, 187.933)), ('A', '105', 9, 'side-chain clash', (238.18, 261.242, 179.719)), ('A', '239', 9, 'side-chain clash', (238.18, 261.242, 179.719)), ('A', '641', 10, 'backbone clash', (228.224, 238.434, 273.597)), ('A', '653', 10, 'backbone clash', (228.224, 238.434, 273.597)), ('A', '833', 11, 'side-chain clash', (199.433, 233.12, 228.384)), ('A', '860', 11, 'side-chain clash', (199.433, 233.12, 228.384)), ('A', '354', 12, 'side-chain clash', (206.028, 220.064, 239.709)), ('A', '398', 12, 'side-chain clash', (206.028, 220.064, 239.709)), ('A', '21', 13, 'backbone clash\nside-chain clash', (189.553, 224.415, 258.477)), ('A', '79', 13, 'backbone clash\nside-chain clash', (189.553, 224.415, 258.477)), ('A', '206', 14, 'side-chain clash', (222.389, 260.588, 197.969)), ('A', '223', 14, 'side-chain clash', (222.389, 260.588, 197.969)), ('A', '108', 15, 'cablam Outlier\nside-chain clash', (239.0, 250.9, 179.0)), ('A', '109', 15, 'side-chain clash', (241.225, 249.53, 177.089)), ('A', '981', 16, 'side-chain clash', (203.784, 227.254, 194.015)), ('A', '983', 16, 'cablam Outlier', (205.9, 231.2, 188.7)), ('A', '481', 17, 'cablam Outlier', (225.2, 173.5, 163.9)), ('A', '483', 17, 'cablam Outlier', (224.4, 176.5, 159.3)), ('A', '262', 18, 'side-chain clash', (238.584, 229.531, 163.039)), ('A', '67', 18, 'side-chain clash', (238.584, 229.531, 163.039)), ('A', '477', 19, 'cablam CA Geom Outlier\nside-chain clash', (215.1, 175.3, 169.7)), ('A', '478', 19, 'cablam Outlier\nside-chain clash', (216.5, 172.9, 167.2)), ('A', '376', 20, 'side-chain clash', (226.835, 213.951, 169.028)), ('A', '435', 20, 'side-chain clash', (226.835, 213.951, 169.028)), ('A', '805', 21, 'Bond length:C', (202.70299999999997, 241.026, 255.33200000000002)), ('A', '806', 21, 'Bond length:N', (199.077, 240.577, 256.15400000000005)), ('B', '185', 1, 'cablam CA Geom Outlier\nbackbone clash', (264.2, 175.1, 200.2)), ('B', '212', 1, 'backbone clash', (261.762, 175.822, 201.972)), ('B', '214', 1, 'cablam CA Geom Outlier', (255.8, 173.7, 202.8)), ('B', '215', 1, 'Ramachandran', (252.598, 175.387, 203.883)), ('B', '29', 1, 'backbone clash\nside-chain clash', (245.678, 177.066, 201.015)), ('B', '30', 1, 'backbone clash', (246.115, 176.498, 204.622)), ('B', '62', 1, 'side-chain clash', (245.678, 177.066, 201.015)), ('B', '638', 2, 'cablam Outlier', (227.1, 175.5, 218.9)), ('B', '640', 2, 'cablam CA Geom Outlier', (229.8, 173.2, 223.9)), ('B', '641', 2, 'backbone clash', (229.802, 176.91, 228.797)), ('B', '642', 2, 'side-chain clash', (225.509, 177.229, 223.412)), ('B', '651', 2, 'side-chain clash', (225.509, 177.229, 223.412)), ('B', '653', 2, 'backbone clash', (229.802, 176.91, 228.797)), ('B', '312', 3, 'side-chain clash\nRotamer', (229.46800000000005, 192.81299999999996, 227.46999999999994)), ('B', '598', 3, 'side-chain clash', (228.429, 189.485, 227.377)), ('B', '666', 3, 'cablam Outlier', (224.7, 189.2, 232.1)), ('B', '100', 4, 'side-chain clash', (262.169, 173.926, 187.429)), ('B', '245', 4, 'side-chain clash', (262.169, 173.926, 187.429)), ('B', '260', 4, 'cablam Outlier', (259.2, 168.6, 186.9)), ('B', '524', 5, 'cablam Outlier', (201.0, 192.6, 180.4)), ('B', '525', 5, 'cablam Outlier\nside-chain clash\nRotamer', (204.2, 191.5, 182.2)), ('B', '527', 5, 'cablam Outlier', (209.7, 188.8, 179.2)), ('B', '101', 6, 'backbone clash\nside-chain clash', (253.516, 177.147, 187.892)), ('B', '242', 6, 'side-chain clash', (253.516, 177.147, 187.892)), ('B', '96', 6, 'backbone clash', (257.392, 179.208, 188.425)), ('B', '14', 7, 'side-chain clash', (253.452, 171.834, 171.057)), ('B', '158', 7, 'side-chain clash', (253.452, 171.834, 171.057)), ('B', '159', 7, 'cablam Outlier', (250.8, 177.3, 174.5)), ('B', '216', 8, 'side-chain clash', (255.948, 201.527, 210.929)), ('B', '217', 8, 'side-chain clash', (255.948, 201.527, 210.929)), ('B', '262', 9, 'side-chain clash', (208.204, 184.527, 209.861)), ('B', '67', 9, 'side-chain clash', (208.204, 184.527, 209.861)), ('B', '21', 10, 'backbone clash\nside-chain clash', (225.188, 189.649, 258.467)), ('B', '79', 10, 'backbone clash\nside-chain clash', (225.188, 189.649, 258.467)), ('B', '518', 11, 'side-chain clash', (205.782, 195.045, 192.542)), ('B', '546', 11, 'side-chain clash', (205.782, 195.045, 192.542)), ('B', '376', 12, 'side-chain clash', (209.651, 210.913, 169.064)), ('B', '435', 12, 'side-chain clash', (209.651, 210.913, 169.064)), ('B', '310', 13, 'cablam CA Geom Outlier', (236.4, 193.7, 229.6)), ('B', '600', 13, 'cablam CA Geom Outlier', (237.5, 189.4, 229.6)), ('B', '354', 14, 'side-chain clash', (225.252, 225.845, 239.556)), ('B', '398', 14, 'side-chain clash', (225.252, 225.845, 239.556)), ('B', '833', 15, 'side-chain clash', (239.996, 225.147, 228.357)), ('B', '860', 15, 'side-chain clash', (239.996, 225.147, 228.357)), ('B', '108', 16, 'cablam Outlier\nside-chain clash', (235.7, 181.9, 179.0)), ('B', '109', 16, 'side-chain clash', (233.41, 180.894, 177.011)), ('B', '105', 17, 'side-chain clash', (245.176, 177.089, 179.927)), ('B', '239', 17, 'side-chain clash', (245.176, 177.089, 179.927)), ('B', '570', 18, 'Bond angle:C', (204.444, 200.36100000000002, 208.354)), ('B', '571', 18, 'Bond angle:N:CA', (203.14299999999997, 200.21599999999998, 204.726)), ('B', '206', 19, 'side-chain clash', (251.892, 191.505, 197.915)), ('B', '223', 19, 'side-chain clash', (251.892, 191.505, 197.915)), ('B', '481', 20, 'cablam Outlier', (175.4, 232.6, 163.9)), ('B', '483', 20, 'cablam Outlier', (178.5, 231.7, 159.3)), ('B', '477', 21, 'cablam CA Geom Outlier\nside-chain clash', (182.1, 240.4, 169.7)), ('B', '478', 21, 'cablam Outlier\nside-chain clash', (179.2, 240.4, 167.2)), ('B', '805', 22, 'Bond length:C', (245.207, 218.319, 255.329)), ('B', '806', 22, 'Bond length:N', (246.63, 221.683, 256.15000000000003)), ('C', '185', 1, 'cablam CA Geom Outlier\nbackbone clash', (157.4, 198.0, 200.2)), ('C', '212', 1, 'backbone clash', (159.273, 199.693, 201.987)), ('C', '214', 1, 'cablam CA Geom Outlier', (160.3, 206.0, 202.8)), ('C', '215', 1, 'Ramachandran', (163.419, 207.92299999999994, 203.88199999999998)), ('C', '29', 1, 'side-chain clash\nbackbone clash', (167.48, 213.157, 204.634)), ('C', '30', 1, 'backbone clash', (167.48, 213.157, 204.634)), ('C', '62', 1, 'side-chain clash', (168.088, 213.003, 201.366)), ('C', '638', 2, 'cablam Outlier', (176.3, 229.9, 218.9)), ('C', '640', 2, 'cablam CA Geom Outlier', (173.0, 228.8, 223.9)), ('C', '641', 2, 'backbone clash', (176.107, 227.057, 228.837)), ('C', '642', 2, 'side-chain clash', (178.212, 230.659, 223.461)), ('C', '651', 2, 'side-chain clash', (178.212, 230.659, 223.461)), ('C', '653', 2, 'backbone clash', (176.107, 227.057, 228.837)), ('C', '100', 3, 'side-chain clash', (157.388, 200.311, 187.437)), ('C', '245', 3, 'side-chain clash', (157.388, 200.311, 187.437)), ('C', '260', 3, 'cablam Outlier', (154.3, 205.6, 186.9)), ('C', '262', 3, 'side-chain clash', (156.892, 204.962, 191.92)), ('C', '67', 3, 'side-chain clash', (156.892, 204.962, 191.92)), ('C', '312', 4, 'side-chain clash\nRotamer', (190.077, 219.239, 227.46899999999997)), ('C', '596', 4, 'side-chain clash', (189.726, 223.32, 225.951)), ('C', '598', 4, 'side-chain clash', (188.036, 221.889, 227.132)), ('C', '666', 4, 'cablam Outlier', (189.4, 225.2, 232.1)), ('C', '391', 5, 'side-chain clash', (202.42, 240.89, 183.099)), ('C', '524', 5, 'cablam Outlier', (204.1, 244.0, 180.4)), ('C', '525', 5, 'cablam Outlier\nside-chain clash\nRotamer', (201.5, 241.8, 182.2)), ('C', '527', 5, 'cablam Outlier', (196.4, 238.4, 179.2)), ('C', '805', 6, 'Bond length:C', (204.29299999999998, 192.85700000000003, 255.329)), ('C', '806', 6, 'Bond length:N', (206.495, 189.941, 256.151)), ('C', '808', 6, 'side-chain clash', (204.596, 184.021, 254.664)), ('C', '809', 6, 'side-chain clash', (204.596, 184.021, 254.664)), ('C', '21', 7, 'backbone clash', (158.489, 213.213, 184.845)), ('C', '78', 7, 'side-chain clash', (155.474, 214.739, 189.665)), ('C', '79', 7, 'backbone clash', (158.489, 213.213, 184.845)), ('C', '101', 8, 'side-chain clash\nbackbone clash', (164.786, 201.946, 188.463)), ('C', '242', 8, 'side-chain clash', (164.678, 206.069, 188.244)), ('C', '96', 8, 'backbone clash', (164.786, 201.946, 188.463)), ('C', '216', 9, 'side-chain clash\nbackbone clash', (184.588, 192.239, 210.671)), ('C', '217', 9, 'side-chain clash\nbackbone clash', (184.588, 192.239, 210.671)), ('C', '376', 10, 'side-chain clash', (215.552, 227.437, 169.098)), ('C', '435', 10, 'side-chain clash', (215.552, 227.437, 169.098)), ('C', '310', 11, 'cablam CA Geom Outlier', (187.3, 212.8, 229.6)), ('C', '600', 11, 'cablam CA Geom Outlier', (183.1, 214.0, 229.6)), ('C', '354', 12, 'side-chain clash', (218.86, 241.044, 171.28)), ('C', '398', 12, 'side-chain clash', (218.86, 241.044, 171.28)), ('C', '833', 13, 'side-chain clash', (213.014, 194.252, 228.104)), ('C', '860', 13, 'side-chain clash', (213.014, 194.252, 228.104)), ('C', '108', 14, 'cablam Outlier\nside-chain clash', (177.6, 219.3, 179.0)), ('C', '109', 14, 'side-chain clash', (177.623, 221.707, 176.592)), ('C', '105', 15, 'side-chain clash', (169.058, 213.501, 179.719)), ('C', '239', 15, 'side-chain clash', (169.058, 213.501, 179.719)), ('C', '570', 16, 'Bond angle:C', (209.127, 237.134, 208.35200000000003)), ('C', '571', 16, 'Bond angle:N:CA', (209.653, 238.33200000000002, 204.72299999999998)), ('C', '206', 17, 'side-chain clash', (177.581, 200.083, 197.874)), ('C', '223', 17, 'side-chain clash', (177.581, 200.083, 197.874)), ('C', '14', 18, 'side-chain clash', (159.822, 209.071, 171.074)), ('C', '158', 18, 'side-chain clash', (159.822, 209.071, 171.074)), ('C', '481', 19, 'cablam Outlier', (251.5, 246.2, 163.9)), ('C', '483', 19, 'cablam Outlier', (249.3, 243.9, 159.3)), ('C', '477', 20, 'cablam CA Geom Outlier\nside-chain clash', (255.0, 236.4, 169.7)), ('C', '478', 20, 'cablam Outlier\nside-chain clash', (256.4, 238.9, 167.2))]
data['probe'] = [(' C  67  ALA  O  ', ' C 262  ALA  HA ', -0.746, (156.892, 204.962, 191.92)), (' A  67  ALA  O  ', ' A 262  ALA  HA ', -0.736, (237.517, 275.935, 191.727)), (' B  67  ALA  O  ', ' B 262  ALA  HA ', -0.729, (258.045, 170.69, 191.727)), (' B 588  THR HG21', ' C 841  LEU HD12', -0.601, (208.204, 184.527, 209.861)), (' A 588  THR HG21', ' B 841  LEU HD12', -0.596, (250.424, 225.942, 209.934)), (' C 391  CYS  HA ', ' C 525  CYS  HA ', -0.587, (202.42, 240.89, 183.099)), (' B 391  CYS  HA ', ' B 525  CYS  HA ', -0.582, (204.19, 192.965, 183.483)), (' A 841  LEU HD12', ' C 588  THR HG21', -0.577, (194.137, 241.765, 209.716)), (' A 370  ASN  HB3', ' C 455  LEU HD21', -0.571, (238.584, 229.531, 163.039)), (' A 391  CYS  HA ', ' A 525  CYS  HA ', -0.568, (245.048, 218.79, 183.124)), (' B 922  LEU HD11', ' T   1  NAG  H5 ', -0.563, (241.581, 201.542, 271.569)), (' C 331  ASN  N  ', ' C 331  ASN  OD1', -0.557, (195.938, 249.858, 184.159)), (' C 777  ASN  OD1', ' C1019 BARG  NH1', -0.556, (220.805, 206.346, 239.541)), (' A 331  ASN  N  ', ' A 331  ASN  OD1', -0.553, (256.421, 219.723, 183.944)), (' B 153  MET  HE1', ' B1307  NAG  H4 ', -0.552, (273.463, 176.782, 174.152)), (' A 153  MET  HE1', ' A1307  NAG  H4 ', -0.552, (224.653, 286.324, 174.212)), (' A 922  LEU HD11', ' J   1  NAG  H5 ', -0.551, (218.644, 245.873, 271.419)), (' C 153  MET  HE1', ' C1307  NAG  H4 ', -0.549, (154.351, 189.753, 174.296)), (' A  21  ARG  NH1', ' A  79  PHE  O  ', -0.548, (243.181, 270.599, 184.845)), (' A 455  LEU HD21', ' B 370  ASN  HB3', -0.546, (216.794, 192.872, 163.048)), (' C 922  LEU HD11', ' D   1  NAG  H5 ', -0.546, (192.075, 204.207, 271.389)), (' A 787  GLN  OE1', ' C 703  ASN  ND2', -0.54, (189.553, 224.415, 258.477)), (' C 354  ASN  O  ', ' C 398  ASP  HA ', -0.538, (218.86, 241.044, 171.28)), (' B 455  LEU HD21', ' C 370  ASN  HB3', -0.538, (196.325, 230.29, 163.327)), (' A 354  ASN  O  ', ' A 398  ASP  HA ', -0.537, (237.534, 204.003, 171.022)), (' B 354  ASN  O  ', ' B 398  ASP  HA ', -0.537, (196.152, 206.709, 171.317)), (' B 777  ASN  OD1', ' B1019 BARG  NH1', -0.536, (225.252, 225.845, 239.556)), (' B 331  ASN  N  ', ' B 331  ASN  OD1', -0.536, (199.866, 182.491, 184.024)), (' B1048  HIS  HA ', ' B1066  THR HG22', -0.535, (229.432, 211.195, 260.991)), (' G   2  NAG  H3 ', ' G   2  NAG  H83', -0.534, (201.919, 245.574, 297.244)), (' A1048  HIS  HA ', ' A1066  THR HG22', -0.533, (216.877, 231.256, 260.71)), (' M   2  NAG  H3 ', ' M   2  NAG  H83', -0.532, (249.312, 216.321, 297.486)), (' C1048  HIS  HA ', ' C1066  THR HG22', -0.531, (205.549, 209.871, 260.839)), (' C  21  ARG  NH1', ' C  79  PHE  O  ', -0.531, (158.489, 213.213, 184.845)), (' B  21  ARG  NH1', ' B  79  PHE  O  ', -0.531, (250.531, 168.558, 184.813)), (' W   2  NAG  H3 ', ' W   2  NAG  H83', -0.527, (200.702, 190.292, 297.571)), (' B 703  ASN  ND2', ' C 787  GLN  OE1', -0.519, (225.188, 189.649, 258.467)), (' A 703  ASN  ND2', ' B 787  GLN  OE1', -0.518, (237.456, 238.039, 258.983)), (' A 777  ASN  OD1', ' A1019 BARG  NH1', -0.498, (206.028, 220.064, 239.709)), (' A 376  THR  HB ', ' A 435  ALA  HB3', -0.496, (226.835, 213.951, 169.028)), (' B 716  THR  N  ', ' B1071  GLN  O  ', -0.491, (230.389, 197.525, 273.693)), (' C 376  THR  HB ', ' C 435  ALA  HB3', -0.49, (215.552, 227.437, 169.098)), (' B 376  THR  HB ', ' B 435  ALA  HB3', -0.487, (209.651, 210.913, 169.064)), (' A  96  GLU  OE2', ' A 101  ILE  N  ', -0.487, (230.46, 270.964, 188.434)), (' C 216  LEU HD12', ' C 217  PRO  HD2', -0.479, (168.647, 204.704, 202.002)), (' A 108  THR HG22', ' A 109  THR HG23', -0.475, (241.225, 249.53, 177.089)), (' A 216  LEU HD12', ' A 217  PRO  HD2', -0.471, (230.764, 265.847, 202.064)), (' C 716  THR  N  ', ' C1071  GLN  O  ', -0.471, (193.74, 216.131, 273.628)), (' B  96  GLU  OE2', ' B 101  ILE  N  ', -0.47, (257.392, 179.208, 188.425)), (' B 108  THR HG22', ' B 109  THR HG23', -0.469, (233.41, 180.894, 177.011)), (' C 280  ASN HD22', ' C1312  NAG  H83', -0.469, (184.588, 192.239, 210.671)), (' A1130  ILE HD11', ' B 921  LYS  NZ ', -0.467, (246.744, 213.229, 278.733)), (' B 216  LEU HD12', ' B 217  PRO  HD2', -0.466, (252.661, 181.623, 202.064)), (' B1130  ILE HD11', ' C 921  LYS  NZ ', -0.465, (199.538, 194.093, 278.775)), (' A 312  ILE HD11', ' A 596  SER  HB3', -0.464, (236.408, 238.462, 225.495)), (' A 280  ASN HD22', ' A1312  NAG  H83', -0.462, (212.027, 258.299, 210.806)), (' C 108  THR HG22', ' C 109  THR HG23', -0.461, (177.623, 221.707, 176.592)), (' B 280  ASN HD22', ' B1312  NAG  H83', -0.46, (255.948, 201.527, 210.929)), (' C 312  ILE HD11', ' C 596  SER  HB3', -0.457, (189.726, 223.32, 225.951)), (' A 921  LYS  NZ ', ' C1130  ILE HD11', -0.457, (206.453, 244.814, 278.569)), (' B 641  ASN  HB3', ' B 653  ALA  O  ', -0.455, (229.802, 176.91, 228.797)), (' A 641  ASN  HB3', ' A 653  ALA  O  ', -0.453, (246.355, 248.143, 228.697)), (' C 641  ASN  HB3', ' C 653  ALA  O  ', -0.453, (176.107, 227.057, 228.837)), (' A 716  THR  N  ', ' A1071  GLN  O  ', -0.452, (228.224, 238.434, 273.597)), (' C  78  ARG  HA ', ' C  78  ARG  HD2', -0.45, (155.474, 214.739, 189.665)), (' B 312  ILE HD11', ' B 596  SER  HB3', -0.45, (226.09, 190.485, 225.496)), (' A 370  ASN  N  ', ' A 370  ASN  OD1', -0.448, (238.966, 226.053, 164.59)), (' A 763  LEU HD22', ' A1008  VAL HG21', -0.446, (207.903, 220.29, 219.39)), (' B 763  LEU HD22', ' B1008  VAL HG21', -0.44, (224.471, 224.263, 218.964)), (' A 185  ASN  HB2', ' A 212  LEU  O  ', -0.44, (231.049, 276.579, 201.904)), (' C 477  SER  O  ', ' C 478  THR  OG1', -0.44, (255.137, 237.077, 166.266)), (' A 477  SER  O  ', ' A 478  THR  OG1', -0.437, (215.57, 174.707, 166.386)), (' A 580  GLN  HB3', ' A 580  GLN HE21', -0.436, (259.02, 222.002, 187.933)), (' C 580  GLN  HB3', ' C 580  GLN HE21', -0.434, (192.5, 251.135, 187.988)), (' B  14  GLN  O  ', ' B 158  ARG  HD3', -0.433, (253.452, 171.834, 171.057)), (' C 763  LEU HD22', ' C1008  VAL HG21', -0.433, (219.549, 207.729, 219.321)), (' A 105  ILE HD11', ' A 239  GLN HE21', -0.432, (238.18, 261.242, 179.719)), (' B 185  ASN  HB2', ' B 212  LEU  O  ', -0.431, (261.762, 175.822, 201.972)), (' C  14  GLN  O  ', ' C 158  ARG  HD3', -0.431, (159.822, 209.071, 171.074)), (' C 185  ASN  HB2', ' C 212  LEU  O  ', -0.43, (159.273, 199.693, 201.987)), (' B 101  ILE HG13', ' B 242  LEU  CD2', -0.43, (253.516, 177.147, 187.892)), (' A 101  ILE HG13', ' A 242  LEU  CD2', -0.429, (234.236, 268.774, 187.927)), (' B 833  PHE  HE2', ' B 860  VAL HG12', -0.427, (239.996, 225.147, 228.357)), (' C 105  ILE HD11', ' C 239  GLN HE21', -0.427, (169.058, 213.501, 179.719)), (' A  14  GLN  O  ', ' A 158  ARG  HD3', -0.425, (238.606, 271.649, 171.396)), (' C 101  ILE HG13', ' C 242  LEU  CD2', -0.424, (164.678, 206.069, 188.244)), (' B 477  SER  O  ', ' B 478  THR  OG1', -0.423, (181.525, 240.308, 166.296)), (' A1116  THR  HB ', ' A1140  PRO  HD3', -0.422, (224.479, 223.374, 294.796)), (' B 105  ILE HD11', ' B 239  GLN HE21', -0.42, (245.176, 177.089, 179.927)), (' A 833  PHE  HE2', ' A 860  VAL HG12', -0.419, (199.433, 233.12, 228.384)), (' B  29  THR  OG1', ' B  30  ASN  N  ', -0.419, (246.115, 176.498, 204.622)), (' C1116  THR  HB ', ' C1140  PRO  HD3', -0.418, (208.65, 220.467, 294.814)), (' A  29  THR  OG1', ' A  30  ASN  N  ', -0.418, (238.702, 262.731, 204.538)), (' C 833  PHE  HE2', ' C 860  VAL HG12', -0.418, (213.014, 194.252, 228.104)), (' B  29  THR HG23', ' B  62  VAL HG23', -0.418, (245.678, 177.066, 201.015)), (' C 808  ASP  HA ', ' C 809  PRO  HD3', -0.415, (204.596, 184.021, 254.664)), (' C  29  THR HG23', ' C  62  VAL HG23', -0.414, (168.088, 213.003, 201.366)), (' B1130  ILE HD11', ' C 921  LYS  HZ2', -0.413, (199.153, 194.686, 278.792)), (' B1116  THR  HB ', ' B1140  PRO  HD3', -0.413, (219.125, 208.232, 294.374)), (' A1130  ILE HD11', ' B 921  LYS  HZ1', -0.412, (246.923, 213.421, 278.742)), (' B  78  ARG  HA ', ' B  78  ARG  HD2', -0.411, (250.666, 164.991, 189.68)), (' B 206  LYS  HB3', ' B 223  LEU HD22', -0.411, (251.892, 191.505, 197.915)), (' B 100  ILE HD11', ' B 245  HIS  HE1', -0.41, (262.169, 173.926, 187.429)), (' C 100  ILE HD11', ' C 245  HIS  HE1', -0.409, (157.388, 200.311, 187.437)), (' B 312  ILE HD12', ' B 598  ILE HG13', -0.409, (228.429, 189.485, 227.377)), (' B 518  LEU HD22', ' B 546  LEU  HB2', -0.408, (205.782, 195.045, 192.542)), (' A 206  LYS  HB3', ' A 223  LEU HD22', -0.408, (222.389, 260.588, 197.969)), (' A 981  LEU  HA ', ' A 981  LEU HD23', -0.407, (203.784, 227.254, 194.015)), (' C 206  LYS  HB3', ' C 223  LEU HD22', -0.406, (177.581, 200.083, 197.874)), (' A  29  THR HG23', ' A  62  VAL HG23', -0.406, (238.14, 262.432, 201.219)), (' C 312  ILE HD12', ' C 598  ILE HG13', -0.406, (188.036, 221.889, 227.132)), (' B 642  VAL HG22', ' B 651  ILE HG12', -0.405, (225.509, 177.229, 223.412)), (' C  96  GLU  OE2', ' C 101  ILE  N  ', -0.404, (164.786, 201.946, 188.463)), (' C 642  VAL HG22', ' C 651  ILE HG12', -0.404, (178.212, 230.659, 223.461)), (' C  29  THR  OG1', ' C  30  ASN  N  ', -0.401, (167.48, 213.157, 204.634)), (' B1073  LYS  HE2', ' B1075  PHE  CZ ', -0.401, (227.476, 194.199, 279.329)), (' A 642  VAL HG22', ' A 651  ILE HG12', -0.4, (248.364, 244.464, 222.848)), (' C 981  LEU  HA ', ' C 981  LEU HD23', -0.4, (216.179, 200.376, 193.838))]
data['rama'] = [('A', ' 215 ', 'ASP', 0.03331934927572898, (236.18500000000003, 268.889, 203.883)), ('B', ' 215 ', 'ASP', 0.03333389912294256, (252.598, 175.387, 203.883)), ('C', ' 215 ', 'ASP', 0.03328847312425611, (163.419, 207.92299999999994, 203.88199999999998))]
data['cablam'] = [('A', '20', 'THR', 'check CA trace,carbonyls, peptide', ' \n-----', (249.5, 277.2, 183.1)), ('A', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\n-SS-E', (234.4, 247.5, 191.5)), ('A', '108', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEESS-', (239.0, 250.9, 179.0)), ('A', '112', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n-BSSS', (238.2, 254.6, 169.4)), ('A', '159', 'VAL', 'check CA trace,carbonyls, peptide', 'strand\nEEEEE', (235.4, 266.3, 174.5)), ('A', '178', 'ASP', ' beta sheet', ' \n-----', (221.9, 278.9, 185.6)), ('A', '231', 'ILE', ' beta sheet', ' \nEE---', (225.3, 249.2, 177.8)), ('A', '251', 'PRO', 'check CA trace,carbonyls, peptide', ' \nTS-S-', (243.8, 287.3, 178.6)), ('A', '260', 'ALA', 'check CA trace,carbonyls, peptide', ' \n-B---', (238.7, 278.0, 186.9)), ('A', '316', 'SER', 'check CA trace,carbonyls, peptide', ' \nE----', (235.2, 235.2, 215.8)), ('A', '446', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\n-SS-B', (225.6, 203.0, 145.6)), ('A', '478', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nSSS--', (216.5, 172.9, 167.2)), ('A', '481', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\n--SS-', (225.2, 173.5, 163.9)), ('A', '483', 'VAL', 'check CA trace,carbonyls, peptide', ' \nSS---', (224.4, 176.5, 159.3)), ('A', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n--TTE', (215.3, 178.8, 159.7)), ('A', '519', 'HIS', 'check CA trace,carbonyls, peptide', 'bend\n-SSS-', (242.8, 211.5, 193.0)), ('A', '524', 'VAL', 'check CA trace,carbonyls, peptide', ' \n-S---', (247.0, 215.6, 180.4)), ('A', '525', 'CYS', 'check CA trace,carbonyls, peptide', ' \nS---S', (246.4, 219.0, 182.2)), ('A', '527', 'PRO', 'check CA trace,carbonyls, peptide', 'bend\n--S--', (246.0, 225.1, 179.2)), ('A', '638', 'THR', 'check CA trace,carbonyls, peptide', ' \nS---S', (248.8, 246.7, 218.9)), ('A', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (238.2, 237.8, 232.1)), ('A', '699', 'LEU', 'check CA trace,carbonyls, peptide', ' \n----B', (238.7, 236.6, 247.6)), ('A', '797', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\n--STT', (200.9, 239.4, 269.3)), ('A', '846', 'ALA', 'check CA trace,carbonyls, peptide', 'turn\nSBTTB', (203.6, 242.7, 212.4)), ('A', '891', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\nGTSS-', (197.0, 218.1, 262.3)), ('A', '983', 'ARG', 'check CA trace,carbonyls, peptide', 'bend\nHSSS-', (205.9, 231.2, 188.7)), ('A', '1034', 'LEU', 'check CA trace,carbonyls, peptide', 'bend\nIISS-', (205.5, 224.7, 258.9)), ('A', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\nTTTSS', (216.3, 228.6, 256.1)), ('A', '1058', 'HIS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (205.8, 232.9, 238.7)), ('A', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSS-', (237.3, 216.5, 296.7)), ('A', '1139', 'ASP', 'check CA trace,carbonyls, peptide', ' \n---TT', (226.1, 221.8, 297.3)), ('A', '185', 'ASN', 'check CA trace', 'bend\n-SSEE', (230.6, 279.0, 200.2)), ('A', '214', 'ARG', 'check CA trace', 'bend\nESSS-', (236.0, 272.5, 202.8)), ('A', '218', 'GLN', 'check CA trace', ' \n-----', (229.5, 264.3, 208.5)), ('A', '310', 'LYS', 'check CA trace', 'bend\n--SEE', (228.5, 245.7, 229.6)), ('A', '477', 'SER', 'check CA trace', 'bend\n-SSS-', (215.1, 175.3, 169.7)), ('A', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (244.0, 228.3, 200.4)), ('A', '600', 'PRO', 'check CA trace', 'bend\nEES-T', (231.6, 248.8, 229.6)), ('A', '640', 'SER', 'check CA trace', 'bend\n--S-E', (249.5, 250.2, 223.9)), ('B', '20', 'THR', 'check CA trace,carbonyls, peptide', ' \n-----', (253.2, 159.7, 183.1)), ('B', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\n-SS-E', (235.0, 187.6, 191.5)), ('B', '108', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEESS-', (235.7, 181.9, 179.0)), ('B', '112', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n-BSSS', (239.2, 180.8, 169.4)), ('B', '159', 'VAL', 'check CA trace,carbonyls, peptide', 'strand\nEEEEE', (250.8, 177.3, 174.5)), ('B', '178', 'ASP', ' beta sheet', ' \n-----', (268.4, 182.7, 185.6)), ('B', '231', 'ILE', ' beta sheet', ' \nEE---', (241.0, 194.7, 177.8)), ('B', '251', 'PRO', 'check CA trace,carbonyls, peptide', ' \nTS-S-', (264.7, 159.6, 178.6)), ('B', '260', 'ALA', 'check CA trace,carbonyls, peptide', ' \n-B---', (259.2, 168.6, 186.9)), ('B', '316', 'SER', 'check CA trace,carbonyls, peptide', ' \nE----', (223.9, 193.1, 215.8)), ('B', '446', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\n-SS-B', (200.8, 217.5, 145.6)), ('B', '478', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nSSS--', (179.2, 240.4, 167.2)), ('B', '481', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\n--SS-', (175.4, 232.6, 163.9)), ('B', '483', 'VAL', 'check CA trace,carbonyls, peptide', ' \nSS---', (178.5, 231.7, 159.3)), ('B', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n--TTE', (185.1, 238.5, 159.7)), ('B', '519', 'HIS', 'check CA trace,carbonyls, peptide', 'bend\n-SSS-', (199.6, 198.3, 193.0)), ('B', '524', 'VAL', 'check CA trace,carbonyls, peptide', ' \n-S---', (201.0, 192.6, 180.4)), ('B', '525', 'CYS', 'check CA trace,carbonyls, peptide', ' \nS---S', (204.2, 191.5, 182.2)), ('B', '527', 'PRO', 'check CA trace,carbonyls, peptide', 'bend\n--S--', (209.7, 188.8, 179.2)), ('B', '638', 'THR', 'check CA trace,carbonyls, peptide', ' \nS---S', (227.1, 175.5, 218.9)), ('B', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (224.7, 189.2, 232.1)), ('B', '699', 'LEU', 'check CA trace,carbonyls, peptide', ' \n----B', (223.4, 189.4, 247.6)), ('B', '797', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\n--STT', (244.7, 220.7, 269.3)), ('B', '846', 'ALA', 'check CA trace,carbonyls, peptide', 'turn\nSBTTB', (246.2, 216.8, 212.4)), ('B', '891', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\nGTSS-', (228.2, 234.8, 262.3)), ('B', '983', 'ARG', 'check CA trace,carbonyls, peptide', 'bend\nHSSS-', (235.1, 220.5, 188.7)), ('B', '1034', 'LEU', 'check CA trace,carbonyls, peptide', 'bend\nIISS-', (229.7, 224.1, 258.9)), ('B', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\nTTTSS', (227.7, 212.7, 256.1)), ('B', '1058', 'HIS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (236.6, 219.7, 238.7)), ('B', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSS-', (206.6, 200.6, 296.7)), ('B', '1139', 'ASP', 'check CA trace,carbonyls, peptide', ' \n---TT', (216.8, 207.6, 297.3)), ('B', '185', 'ASN', 'check CA trace', 'bend\n-SSEE', (264.2, 175.1, 200.2)), ('B', '214', 'ARG', 'check CA trace', 'bend\nESSS-', (255.8, 173.7, 202.8)), ('B', '218', 'GLN', 'check CA trace', ' \n-----', (252.0, 183.4, 208.5)), ('B', '310', 'LYS', 'check CA trace', 'bend\n--SEE', (236.4, 193.7, 229.6)), ('B', '477', 'SER', 'check CA trace', 'bend\n-SSS-', (182.1, 240.4, 169.7)), ('B', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (213.6, 188.9, 200.4)), ('B', '600', 'PRO', 'check CA trace', 'bend\nEES-T', (237.5, 189.4, 229.6)), ('B', '640', 'SER', 'check CA trace', 'bend\n--S-E', (229.8, 173.2, 223.9)), ('C', '20', 'THR', 'check CA trace,carbonyls, peptide', ' \n-----', (149.5, 215.3, 183.1)), ('C', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\n-SS-E', (182.8, 217.1, 191.5)), ('C', '108', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEESS-', (177.6, 219.3, 179.0)), ('C', '112', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n-BSSS', (174.8, 216.8, 169.4)), ('C', '159', 'VAL', 'check CA trace,carbonyls, peptide', 'strand\nEEEEE', (166.0, 208.6, 174.5)), ('C', '178', 'ASP', ' beta sheet', ' \n-----', (161.9, 190.6, 185.6)), ('C', '231', 'ILE', ' beta sheet', ' \nEE---', (185.9, 208.4, 177.8)), ('C', '251', 'PRO', 'check CA trace,carbonyls, peptide', ' \nTS-S-', (143.7, 205.3, 178.6)), ('C', '260', 'ALA', 'check CA trace,carbonyls, peptide', ' \n-B---', (154.3, 205.6, 186.9)), ('C', '316', 'SER', 'check CA trace,carbonyls, peptide', ' \nE----', (193.1, 223.9, 215.8)), ('C', '446', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\n-SS-B', (225.8, 231.7, 145.6)), ('C', '478', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nSSS--', (256.4, 238.9, 167.2)), ('C', '481', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\n--SS-', (251.5, 246.2, 163.9)), ('C', '483', 'VAL', 'check CA trace,carbonyls, peptide', ' \nSS---', (249.3, 243.9, 159.3)), ('C', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n--TTE', (251.9, 234.8, 159.7)), ('C', '519', 'HIS', 'check CA trace,carbonyls, peptide', 'bend\n-SSS-', (209.8, 242.4, 193.0)), ('C', '524', 'VAL', 'check CA trace,carbonyls, peptide', ' \n-S---', (204.1, 244.0, 180.4)), ('C', '525', 'CYS', 'check CA trace,carbonyls, peptide', ' \nS---S', (201.5, 241.8, 182.2)), ('C', '527', 'PRO', 'check CA trace,carbonyls, peptide', 'bend\n--S--', (196.4, 238.4, 179.2)), ('C', '638', 'THR', 'check CA trace,carbonyls, peptide', ' \nS---S', (176.3, 229.9, 218.9)), ('C', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (189.4, 225.2, 232.1)), ('C', '699', 'LEU', 'check CA trace,carbonyls, peptide', ' \n----B', (190.1, 226.2, 247.6)), ('C', '797', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\n--STT', (206.6, 192.1, 269.3)), ('C', '846', 'ALA', 'check CA trace,carbonyls, peptide', 'turn\nSBTTB', (202.5, 192.8, 212.4)), ('C', '891', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\nGTSS-', (227.0, 199.3, 262.3)), ('C', '983', 'ARG', 'check CA trace,carbonyls, peptide', 'bend\nHSSS-', (211.2, 200.5, 188.7)), ('C', '1034', 'LEU', 'check CA trace,carbonyls, peptide', 'bend\nIISS-', (217.1, 203.4, 258.9)), ('C', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\nTTTSS', (208.2, 210.9, 256.1)), ('C', '1058', 'HIS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (209.8, 199.6, 238.7)), ('C', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSS-', (208.3, 235.1, 296.7)), ('C', '1139', 'ASP', 'check CA trace,carbonyls, peptide', ' \n---TT', (209.2, 222.8, 297.3)), ('C', '185', 'ASN', 'check CA trace', 'bend\n-SSEE', (157.4, 198.0, 200.2)), ('C', '214', 'ARG', 'check CA trace', 'bend\nESSS-', (160.3, 206.0, 202.8)), ('C', '218', 'GLN', 'check CA trace', ' \n-----', (170.7, 204.4, 208.5)), ('C', '310', 'LYS', 'check CA trace', 'bend\n--SEE', (187.3, 212.8, 229.6)), ('C', '477', 'SER', 'check CA trace', 'bend\n-SSS-', (255.0, 236.4, 169.7)), ('C', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (194.6, 234.9, 200.4)), ('C', '600', 'PRO', 'check CA trace', 'bend\nEES-T', (183.1, 214.0, 229.6)), ('C', '640', 'SER', 'check CA trace', 'bend\n--S-E', (173.0, 228.8, 223.9))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-11203/6zge/Model_validation_2/validation_cootdata/molprobity_probe6zge_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)
