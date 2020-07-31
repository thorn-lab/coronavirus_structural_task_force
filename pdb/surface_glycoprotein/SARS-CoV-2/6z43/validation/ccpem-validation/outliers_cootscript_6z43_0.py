
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
data['smoc'] = []
data['jpred'] = []
data['rota'] = [('A', ' 332 ', 'ILE', 0.02217386553632367, (224.04099999999994, 182.153, 185.468)), ('A', ' 335 ', 'LEU', 0.017607304995893962, (219.90899999999996, 182.74, 179.009)), ('A', ' 389 ', 'ASP', 0.21819208204799007, (224.69699999999995, 196.239, 184.045)), ('A', ' 528 ', 'LYS', 0.0, (227.01799999999994, 190.207, 185.931)), ('A', ' 791 ', 'THR', 0.06136018894591334, (234.91399999999993, 241.853, 264.445)), ('A', ' 858 ', 'LEU', 0.23215617203083272, (227.24799999999993, 237.215, 222.57400000000004)), ('A', '1037 ', 'SER', 0.23549247926241437, (226.47999999999993, 219.191, 261.996)), ('B', ' 234 ', 'ASN', 0.06448605198012103, (198.84999999999997, 255.428, 191.157)), ('B', ' 333 ', 'THR', 0.2839252000924411, (242.03999999999994, 251.774, 183.824)), ('B', ' 335 ', 'LEU', 0.14390905777618843, (239.295, 247.078, 179.651)), ('B', ' 528 ', 'LYS', 5.366977624786665e-05, (232.35599999999994, 250.47, 189.892)), ('B', ' 591 ', 'SER', 0.10915490667839302, (228.77799999999993, 250.238, 218.804)), ('B', ' 607 ', 'GLN', 0.08484439873860727, (207.718, 256.7500000000001, 234.355)), ('B', ' 657 ', 'ASN', 0.09773790636248084, (224.40299999999993, 257.91, 247.452)), ('B', ' 760 ', 'CYS', 0.1608408067654656, (207.09899999999993, 211.045, 216.93899999999996)), ('C', ' 332 ', 'ILE', 0.26689938600193575, (176.061, 233.089, 191.505)), ('C', ' 738 ', 'CYS', 0.09045098441572218, (229.02499999999995, 210.316, 214.979)), ('C', ' 827 ', 'THR', 0.24137991815581125, (219.752, 191.649, 233.02899999999997)), ('C', ' 912 ', 'THR', 0.21086050690436578, (219.10599999999994, 202.912, 277.55))]
data['clusters'] = [('A', '220', 1, 'cablam CA Geom Outlier\nside-chain clash', (262.2, 227.1, 213.4)), ('A', '31', 1, 'backbone clash', (261.319, 216.711, 210.079)), ('A', '33', 1, 'cablam Outlier\nside-chain clash\nbackbone clash', (260.9, 221.6, 211.9)), ('A', '34', 1, 'cablam CA Geom Outlier', (261.6, 223.3, 208.6)), ('A', '59', 1, 'backbone clash', (261.319, 216.711, 210.079)), ('A', '403', 2, 'side-chain clash', (221.228, 197.969, 147.51)), ('A', '405', 2, 'side-chain clash', (221.228, 197.969, 147.51)), ('A', '501', 2, 'side-chain clash', (223.818, 192.869, 143.878)), ('A', '505', 2, 'side-chain clash', (223.818, 192.869, 143.878)), ('A', '122', 3, 'Dihedral angle:CA:C', (272.07599999999996, 237.208, 188.554)), ('A', '123', 3, 'Dihedral angle:N:CA', (273.621, 239.631, 191.015)), ('A', '759', 3, 'side-chain clash', (273.002, 238.808, 184.64)), ('A', '763', 3, 'side-chain clash', (273.002, 238.808, 184.64)), ('A', '332', 4, 'backbone clash\nside-chain clash\nRotamer', (224.04099999999994, 182.153, 185.468)), ('A', '389', 4, 'side-chain clash\nRotamer', (224.69699999999995, 196.239, 184.045)), ('A', '527', 4, 'cablam Outlier\nbackbone clash\nside-chain clash', (224.7, 188.1, 183.8)), ('A', '528', 4, 'cablam Outlier\nRotamer', (227.0, 190.2, 185.9)), ('A', '568', 5, 'backbone clash', (219.876, 191.832, 211.669)), ('A', '570', 5, 'cablam Outlier', (217.7, 196.7, 215.3)), ('A', '572', 5, 'backbone clash', (219.876, 191.832, 211.669)), ('A', '803', 5, 'side-chain clash', (212.886, 198.381, 212.453)), ('A', '598', 6, 'side-chain clash', (246.679, 204.282, 229.65)), ('A', '666', 6, 'cablam Outlier\nside-chain clash', (241.9, 203.6, 231.6)), ('A', '667', 6, 'cablam Outlier', (239.3, 201.1, 232.7)), ('A', '281', 7, 'side-chain clash', (252.34, 237.855, 219.692)), ('A', '283', 7, 'side-chain clash', (249.847, 237.057, 213.385)), ('A', '44', 7, 'side-chain clash', (249.847, 237.057, 213.385)), ('A', '112', 8, 'cablam CA Geom Outlier', (261.9, 221.7, 173.6)), ('A', '113', 8, 'cablam Outlier', (258.5, 220.5, 172.2)), ('A', '58', 8, 'side-chain clash', (258.452, 225.358, 172.906)), ('A', '791', 9, 'Rotamer', (234.91399999999993, 241.853, 264.445)), ('A', '792', 9, 'side-chain clash', (239.511, 243.217, 265.594)), ('A', '795', 9, 'side-chain clash', (239.511, 243.217, 265.594)), ('A', '1058', 10, 'cablam Outlier', (231.8, 231.7, 240.9)), ('A', '731', 10, 'side-chain clash', (226.31, 230.553, 236.983)), ('A', '774', 10, 'side-chain clash', (226.31, 230.553, 236.983)), ('A', '29', 11, 'backbone clash', (268.711, 216.174, 208.081)), ('A', '30', 11, 'backbone clash', (268.711, 216.174, 208.081)), ('A', '287', 12, 'backbone clash', (255.649, 225.328, 216.157)), ('A', '288', 12, 'backbone clash', (255.649, 225.328, 216.157)), ('A', '544', 13, 'cablam Outlier', (222.4, 189.7, 195.3)), ('A', '546', 13, 'side-chain clash', (224.473, 193.628, 199.912)), ('A', '811', 14, 'side-chain clash', (245.266, 239.583, 249.637)), ('A', '820', 14, 'side-chain clash', (245.266, 239.583, 249.637)), ('A', '804', 15, 'side-chain clash', (247.662, 233.763, 255.903)), ('A', '935', 15, 'side-chain clash', (247.662, 233.763, 255.903)), ('A', '350', 16, 'side-chain clash', (214.456, 197.217, 154.11)), ('A', '418', 16, 'side-chain clash', (214.456, 197.217, 154.11)), ('A', '326', 17, 'side-chain clash', (234.463, 189.626, 201.083)), ('A', '539', 17, 'side-chain clash', (234.463, 189.626, 201.083)), ('A', '703', 18, 'backbone clash', (225.138, 236.857, 191.319)), ('A', '704', 18, 'backbone clash', (225.138, 236.857, 191.319)), ('A', '986', 19, 'side-chain clash', (221.019, 242.56, 219.346)), ('A', '987', 19, 'side-chain clash', (221.019, 242.56, 219.346)), ('A', '108', 20, 'cablam Outlier', (258.0, 217.6, 182.2)), ('A', '110', 20, 'side-chain clash', (261.421, 219.052, 181.223)), ('A', '360', 21, 'side-chain clash', (211.521, 188.843, 180.779)), ('A', '523', 21, 'side-chain clash', (211.521, 188.843, 180.779)), ('A', '101', 22, 'side-chain clash', (273.672, 227.058, 191.493)), ('A', '242', 22, 'side-chain clash', (273.672, 227.058, 191.493)), ('A', '777', 23, 'side-chain clash', (223.994, 230.36, 246.415)), ('A', '781', 23, 'side-chain clash', (223.994, 230.36, 246.415)), ('A', '382', 24, 'side-chain clash', (221.952, 199.341, 175.738)), ('A', '387', 24, 'side-chain clash', (221.952, 199.341, 175.738)), ('A', '1109', 25, 'cablam Outlier', (239.0, 210.6, 274.7)), ('A', '430', 25, 'side-chain clash\nbackbone clash', (244.029, 208.262, 272.052)), ('A', '337', 26, 'side-chain clash', (215.536, 186.126, 173.83)), ('A', '358', 26, 'side-chain clash', (215.536, 186.126, 173.83)), ('A', '656', 27, 'side-chain clash', (253.725, 196.335, 239.313)), ('A', '658', 27, 'side-chain clash', (253.725, 196.335, 239.313)), ('A', '856', 28, 'cablam Outlier', (228.3, 238.2, 217.1)), ('A', '858', 28, 'Rotamer', (227.24799999999993, 237.215, 222.57400000000004)), ('A', '961', 29, 'side-chain clash', (233.671, 225.439, 218.114)), ('A', '964', 29, 'side-chain clash', (233.671, 225.439, 218.114)), ('B', '191', 1, 'side-chain clash', (190.067, 260.867, 215.926)), ('B', '193', 1, 'side-chain clash', (190.71, 255.858, 210.095)), ('B', '219', 1, 'backbone clash', (192.595, 258.134, 221.266)), ('B', '220', 1, 'cablam CA Geom Outlier\nside-chain clash', (190.3, 256.1, 221.4)), ('B', '223', 1, 'side-chain clash', (190.71, 255.858, 210.095)), ('B', '287', 1, 'backbone clash', (195.15, 250.663, 223.116)), ('B', '288', 1, 'backbone clash', (195.15, 250.663, 223.116)), ('B', '31', 1, 'backbone clash', (199.763, 260.628, 218.637)), ('B', '33', 1, 'side-chain clash\nbackbone clash', (196.414, 255.216, 220.805)), ('B', '34', 1, 'cablam CA Geom Outlier\nside-chain clash', (193.7, 258.0, 216.7)), ('B', '35', 1, 'cablam Outlier', (194.7, 256.2, 213.5)), ('B', '36', 1, 'side-chain clash', (193.901, 252.668, 218.562)), ('B', '58', 1, 'side-chain clash', (196.414, 255.216, 220.805)), ('B', '59', 1, 'backbone clash', (199.763, 260.628, 218.637)), ('B', '519', 2, 'side-chain clash', (241.32, 238.847, 202.605)), ('B', '520', 2, 'cablam CA Geom Outlier', (245.0, 237.2, 197.4)), ('B', '562', 2, 'side-chain clash', (250.301, 237.219, 201.539)), ('B', '564', 2, 'side-chain clash', (245.479, 244.247, 203.323)), ('B', '565', 2, 'side-chain clash\nbackbone clash', (242.345, 243.444, 205.244)), ('B', '575', 2, 'backbone clash', (242.277, 242.887, 206.405)), ('B', '576', 2, 'side-chain clash', (242.345, 243.444, 205.244)), ('B', '598', 3, 'side-chain clash', (214.168, 248.246, 237.37)), ('B', '611', 3, 'side-chain clash', (220.973, 247.779, 234.59)), ('B', '664', 3, 'side-chain clash', (214.168, 248.246, 237.37)), ('B', '666', 3, 'cablam Outlier\nside-chain clash', (220.5, 245.9, 237.4)), ('B', '667', 3, 'cablam Outlier', (224.0, 244.7, 238.1)), ('B', '130', 4, 'side-chain clash', (188.361, 253.494, 187.088)), ('B', '167', 4, 'side-chain clash', (188.361, 253.494, 187.088)), ('B', '231', 4, 'cablam Outlier\nside-chain clash\nbackbone clash', (191.7, 251.0, 190.8)), ('B', '232', 4, 'backbone clash', (193.751, 251.262, 191.367)), ('B', '234', 4, 'Rotamer', (198.84999999999997, 255.428, 191.157)), ('B', '240', 5, 'backbone clash\nside-chain clash', (209.238, 219.985, 267.62)), ('B', '241', 5, 'side-chain clash\nbackbone clash', (209.238, 219.985, 267.62)), ('B', '346', 5, 'backbone clash', (212.848, 220.619, 270.104)), ('B', '901', 5, 'side-chain clash', (207.824, 218.137, 271.536)), ('B', '905', 5, 'side-chain clash', (207.824, 218.137, 271.536)), ('B', '738', 6, 'backbone clash', (202.935, 212.548, 216.495)), ('B', '739', 6, 'backbone clash', (202.935, 212.548, 216.495)), ('B', '760', 6, 'Rotamer', (207.09899999999993, 211.045, 216.93899999999996)), ('B', '333', 7, 'Rotamer', (242.03999999999994, 251.774, 183.824)), ('B', '334', 7, 'cablam Outlier', (242.2, 249.0, 181.2)), ('B', '335', 7, 'Rotamer', (239.295, 247.078, 179.651)), ('B', '108', 8, 'cablam Outlier', (199.0, 262.7, 190.6)), ('B', '110', 8, 'side-chain clash', (196.128, 264.603, 190.081)), ('B', '111', 8, 'cablam Outlier', (193.6, 267.8, 186.1)), ('B', '1107', 9, 'Dihedral angle:CD:NE:CZ:NH1', (222.989, 228.30700000000002, 277.592)), ('B', '1109', 9, 'cablam Outlier', (217.5, 230.6, 278.8)), ('B', '796', 9, 'side-chain clash\nbackbone clash', (218.157, 232.982, 279.811)), ('B', '1045', 10, 'cablam Outlier', (215.3, 230.4, 260.9)), ('B', '578', 10, 'side-chain clash', (210.366, 230.594, 264.464)), ('B', '579', 10, 'side-chain clash', (210.366, 230.594, 264.464)), ('B', '1058', 11, 'cablam Outlier', (200.9, 221.7, 242.7)), ('B', '731', 11, 'side-chain clash', (204.646, 218.545, 238.019)), ('B', '774', 11, 'side-chain clash', (204.646, 218.545, 238.019)), ('B', '214', 12, 'cablam CA Geom Outlier', (188.8, 273.3, 219.2)), ('B', '215', 12, 'cablam CA Geom Outlier', (190.4, 270.2, 217.7)), ('B', '766', 13, 'side-chain clash', (208.196, 213.023, 230.261)), ('B', '770', 13, 'side-chain clash', (208.196, 213.023, 230.261)), ('B', '496', 14, 'side-chain clash', (224.69, 219.413, 160.506)), ('B', '501', 14, 'side-chain clash', (224.69, 219.413, 160.506)), ('B', '454', 15, 'side-chain clash', (237.389, 212.694, 170.135)), ('B', '492', 15, 'side-chain clash', (237.389, 212.694, 170.135)), ('B', '401', 16, 'side-chain clash', (231.296, 228.199, 168.432)), ('B', '509', 16, 'side-chain clash', (231.296, 228.199, 168.432)), ('B', '813', 17, 'backbone clash', (188.357, 220.536, 252.538)), ('B', '815', 17, 'backbone clash', (188.357, 220.536, 252.538)), ('B', '577', 18, 'side-chain clash', (213.343, 226.511, 284.866)), ('B', '584', 18, 'side-chain clash', (213.343, 226.511, 284.866)), ('B', '273', 19, 'side-chain clash', (204.598, 256.142, 213.04)), ('B', '57', 19, 'side-chain clash', (204.598, 256.142, 213.04)), ('B', '316', 20, 'backbone clash', (217.012, 246.834, 220.717)), ('B', '317', 20, 'cablam Outlier\nbackbone clash\nside-chain clash', (219.2, 246.0, 220.9)), ('B', '986', 21, 'side-chain clash', (201.817, 216.088, 193.851)), ('B', '987', 21, 'side-chain clash', (201.817, 216.088, 193.851)), ('B', '969', 22, 'backbone clash', (202.121, 229.015, 206.14)), ('B', '975', 22, 'backbone clash', (202.121, 229.015, 206.14)), ('B', '439', 23, 'side-chain clash', (224.599, 226.809, 159.613)), ('B', '443', 23, 'side-chain clash', (224.599, 226.809, 159.613)), ('B', '736', 24, 'side-chain clash', (200.409, 218.627, 223.283)), ('B', '858', 24, 'side-chain clash', (200.409, 218.627, 223.283)), ('B', '612', 25, 'side-chain clash', (219.847, 255.32, 227.116)), ('B', '651', 25, 'side-chain clash', (219.847, 255.32, 227.116)), ('C', '220', 1, 'cablam CA Geom Outlier\nside-chain clash', (198.4, 178.8, 213.6)), ('C', '287', 1, 'backbone clash', (200.992, 184.305, 216.905)), ('C', '288', 1, 'backbone clash', (200.992, 184.305, 216.905)), ('C', '31', 1, 'backbone clash', (189.716, 185.46, 211.669)), ('C', '33', 1, 'side-chain clash\nbackbone clash', (197.378, 182.178, 213.95)), ('C', '34', 1, 'cablam CA Geom Outlier', (195.1, 181.8, 209.4)), ('C', '59', 1, 'backbone clash', (189.716, 185.46, 211.669)), ('C', '328', 2, 'backbone clash', (174.721, 224.409, 201.362)), ('C', '531', 2, 'backbone clash', (174.721, 224.409, 201.362)), ('C', '532', 2, 'backbone clash', (172.466, 222.553, 203.908)), ('C', '533', 2, 'backbone clash', (172.466, 222.553, 203.908)), ('C', '393', 3, 'side-chain clash', (189.093, 241.816, 197.069)), ('C', '516', 3, 'side-chain clash', (193.598, 242.62, 192.716)), ('C', '518', 3, 'side-chain clash', (189.093, 241.816, 197.069)), ('C', '519', 3, 'cablam Outlier', (189.7, 242.9, 201.8)), ('C', '382', 4, 'side-chain clash', (194.503, 227.794, 191.336)), ('C', '383', 4, 'side-chain clash\nbackbone clash', (194.783, 221.427, 192.239)), ('C', '386', 4, 'side-chain clash\nBond angle:N:CA:CB', (191.71899999999997, 222.415, 192.538)), ('C', '387', 4, 'side-chain clash', (194.503, 227.794, 191.336)), ('C', '598', 5, 'side-chain clash', (191.252, 201.646, 234.541)), ('C', '666', 5, 'cablam Outlier\nside-chain clash', (193.5, 205.9, 236.3)), ('C', '667', 5, 'cablam Outlier', (193.1, 209.4, 237.6)), ('C', '310', 6, 'cablam CA Geom Outlier', (199.3, 194.5, 234.5)), ('C', '600', 6, 'cablam CA Geom Outlier\nside-chain clash', (195.1, 192.9, 234.7)), ('C', '692', 6, 'side-chain clash', (191.544, 193.488, 232.949)), ('C', '122', 7, 'backbone clash\nDihedral angle:CA:C', (197.738, 168.585, 185.833)), ('C', '123', 7, 'Dihedral angle:N:CA', (198.36700000000002, 165.23499999999999, 187.454)), ('C', '124', 7, 'backbone clash', (200.03, 166.009, 186.31)), ('C', '419', 8, 'side-chain clash', (210.79, 241.424, 184.567)), ('C', '424', 8, 'side-chain clash', (210.79, 241.424, 184.567)), ('C', '463', 8, 'side-chain clash', (206.771, 241.238, 187.37)), ('C', '195', 9, 'side-chain clash', (203.92, 189.902, 197.789)), ('C', '197', 9, 'side-chain clash', (203.237, 193.051, 196.463)), ('C', '202', 9, 'side-chain clash', (203.237, 193.051, 196.463)), ('C', '1058', 10, 'cablam Outlier', (225.2, 200.0, 238.3)), ('C', '731', 10, 'side-chain clash', (225.628, 205.804, 234.821)), ('C', '774', 10, 'side-chain clash', (225.628, 205.804, 234.821)), ('C', '484', 11, 'cablam Outlier', (217.6, 260.0, 168.6)), ('C', '599', 11, 'side-chain clash\nbackbone clash', (212.796, 256.569, 166.739)), ('C', '601', 11, 'side-chain clash\nbackbone clash', (212.796, 256.569, 166.739)), ('C', '216', 12, 'side-chain clash', (224.605, 195.562, 264.221)), ('C', '266', 12, 'side-chain clash', (224.605, 195.562, 264.221)), ('C', '496', 13, 'side-chain clash', (210.017, 236.0, 162.326)), ('C', '501', 13, 'side-chain clash', (210.017, 236.0, 162.326)), ('C', '405', 14, 'side-chain clash', (212.725, 230.38, 176.266)), ('C', '408', 14, 'side-chain clash', (212.725, 230.38, 176.266)), ('C', '973', 15, 'side-chain clash', (215.29, 210.37, 198.457)), ('C', '992', 15, 'side-chain clash', (215.29, 210.37, 198.457)), ('C', '273', 16, 'side-chain clash', (192.135, 192.978, 208.217)), ('C', '57', 16, 'side-chain clash', (192.135, 192.978, 208.217)), ('C', '326', 17, 'side-chain clash', (179.816, 220.114, 207.361)), ('C', '539', 17, 'side-chain clash', (179.816, 220.114, 207.361)), ('C', '986', 18, 'side-chain clash', (225.19, 213.825, 190.78)), ('C', '987', 18, 'side-chain clash', (225.19, 213.825, 190.78)), ('C', '895', 19, 'side-chain clash', (217.039, 198.849, 281.61)), ('C', '912', 19, 'Rotamer', (219.10599999999994, 202.912, 277.55)), ('C', '301', 20, 'side-chain clash', (205.0, 196.808, 219.16)), ('C', '304', 20, 'side-chain clash', (205.0, 196.808, 219.16)), ('C', '105', 21, 'side-chain clash', (191.932, 178.619, 184.935)), ('C', '241', 21, 'side-chain clash', (191.932, 178.619, 184.935)), ('C', '777', 22, 'side-chain clash', (228.82, 207.311, 243.734)), ('C', '781', 22, 'side-chain clash', (228.82, 207.311, 243.734)), ('C', '749', 23, 'side-chain clash', (227.236, 208.998, 202.638)), ('C', '977', 23, 'side-chain clash', (227.236, 208.998, 202.638)), ('C', '560', 24, 'side-chain clash', (185.033, 245.161, 210.855)), ('C', '562', 24, 'side-chain clash', (185.033, 245.161, 210.855)), ('C', '316', 25, 'backbone clash', (194.473, 205.774, 219.172)), ('C', '317', 25, 'backbone clash', (194.473, 205.774, 219.172)), ('C', '117', 26, 'side-chain clash', (200.507, 186.976, 186.828)), ('C', '231', 26, 'cablam Outlier\nside-chain clash', (204.1, 189.7, 185.0)), ('C', '1043', 27, 'cablam Outlier', (217.7, 205.5, 256.8)), ('C', '1045', 27, 'cablam Outlier', (211.2, 203.6, 258.4)), ('X', '30', 1, 'side-chain clash', (208.477, 178.854, 144.353)), ('X', '98', 1, 'side-chain clash', (208.477, 178.854, 144.353)), ('X', '126', 2, 'side-chain clash', (190.841, 172.586, 109.342)), ('X', '127', 2, 'side-chain clash', (190.841, 172.586, 109.342)), ('X', '6', 3, 'side-chain clash', (203.021, 169.986, 131.833)), ('X', '89', 3, 'side-chain clash', (195.949, 179.338, 112.795)), ('Y', '30', 1, 'side-chain clash', (240.949, 220.473, 154.428)), ('Y', '98', 1, 'side-chain clash', (240.949, 220.473, 154.428)), ('Y', '126', 2, 'side-chain clash', (249.264, 191.841, 128.382)), ('Y', '127', 2, 'side-chain clash', (249.264, 191.841, 128.382)), ('Y', '6', 3, 'side-chain clash', (245.328, 214.069, 140.112)), ('Y', '89', 3, 'side-chain clash', (242.88, 192.422, 134.993)), ('Z', '30', 1, 'side-chain clash', (200.507, 250.495, 159.042)), ('Z', '98', 1, 'side-chain clash', (200.507, 250.495, 159.042)), ('Z', '126', 2, 'side-chain clash', (219.576, 275.588, 134.902)), ('Z', '127', 2, 'side-chain clash', (219.576, 275.588, 134.902))]
data['probe'] = [(' B  33  THR HG22', ' B 220  PHE  HD1', -1.042, (194.051, 255.039, 220.07)), (' B  33  THR HG22', ' B 220  PHE  CD1', -0.833, (193.559, 254.612, 220.019)), (' A  33  THR  CG2', ' A 220  PHE  HD1', -0.83, (259.764, 224.863, 213.199)), (' C  33  THR  O  ', ' C  33  THR HG22', -0.829, (197.235, 182.427, 212.838)), (' A 501  ASN HD21', ' A 505  TYR  HB3', -0.758, (223.034, 192.244, 143.868)), (' A  33  THR  O  ', ' A  33  THR HG22', -0.757, (259.123, 223.406, 211.945)), (' A  33  THR HG22', ' A 220  PHE  HD1', -0.754, (259.385, 224.282, 212.605)), (' C1409  NAG  H3 ', ' C1409  NAG  H83', -0.748, (203.878, 182.546, 237.052)), (' B1307  NAG  H82', ' B1307  NAG  O3 ', -0.735, (227.711, 265.479, 247.579)), (' A  33  THR HG22', ' A 220  PHE  CD1', -0.733, (258.978, 224.95, 212.434)), (' C 195  LYS  HE3', ' C 202  LYS  CD ', -0.732, (203.42, 190.177, 197.296)), (' A1301  NAG  H82', ' A1301  NAG  O3 ', -0.732, (263.014, 206.261, 208.76)), (' A 619  GLU  N  ', ' A 619  GLU  OE1', -0.724, (243.605, 192.18, 215.195)), (' A  33  THR  CG2', ' A 220  PHE  CD1', -0.724, (258.681, 224.683, 212.939)), (' C 195  LYS  HE3', ' C 202  LYS  HD2', -0.724, (202.856, 190.643, 197.237)), (' C 383  SER  HB3', ' C 386  LYS  HG3', -0.712, (195.172, 221.284, 193.178)), (' A1306  NAG  O3 ', ' A1306  NAG  O7 ', -0.703, (258.979, 240.873, 219.963)), (' C 383  SER  O  ', ' C 386  LYS  HB2', -0.699, (193.641, 223.063, 191.923)), (' C  31  SER  O  ', ' C  59  PHE  N  ', -0.688, (189.716, 185.46, 211.669)), (' A 703  ASN  OD1', ' A 704  SER  N  ', -0.687, (244.073, 196.224, 259.102)), (' A 983  ARG  O  ', ' B 383  SER  N  ', -0.687, (225.138, 236.857, 191.319)), (' C 383  SER  HB3', ' C 386  LYS  CG ', -0.686, (194.89, 221.185, 192.484)), (' C 301  CYS  O  ', ' C 304  LYS  HD2', -0.685, (205.0, 196.808, 219.16)), (' B1315  NAG  O3 ', ' B1315  NAG  O7 ', -0.683, (221.036, 237.192, 299.788)), (' A1311  NAG  O3 ', ' A1311  NAG  O7 ', -0.682, (240.611, 186.492, 221.862)), (' A 731  MET  N  ', ' A 774  GLN  OE1', -0.679, (226.31, 230.553, 236.983)), (' Z 126  SER  O  ', ' Z 127  SER  OG ', -0.675, (219.576, 275.588, 134.902)), (' C  33  THR HG22', ' C 220  PHE  HD1', -0.672, (198.091, 182.407, 213.329)), (' B 983  ARG  O  ', ' C 383  SER  N  ', -0.672, (197.24, 223.557, 192.648)), (' X 126  SER  O  ', ' X 127  SER  OG ', -0.671, (190.841, 172.586, 109.342)), (' C1418  NAG  O6 ', ' C1419  NAG  H82', -0.667, (190.742, 204.163, 276.4)), (' C 908  GLY  O  ', ' C1038  LYS  NZ ', -0.662, (220.155, 209.363, 267.913)), (' A1028  LYS  NZ ', ' A1042  PHE  O  ', -0.66, (229.912, 218.463, 253.526)), (' C 599  THR HG22', ' C 601  GLY  H  ', -0.658, (196.64, 192.144, 232.054)), (' A 501  ASN  ND2', ' A 505  TYR  HB3', -0.658, (223.627, 192.383, 143.641)), (' B1311  NAG  O6 ', ' B1312  NAG  N2 ', -0.656, (188.392, 232.516, 265.083)), (' B 554  GLU  N  ', ' B 554  GLU  OE1', -0.643, (243.56, 254.717, 212.695)), (' B 578  ASP  OD2', ' B 581  THR  HB ', -0.631, (244.496, 253.178, 200.563)), (' A1074  ASN  OD1', ' C 895  GLN  NE2', -0.625, (243.213, 198.038, 270.21)), (' C1091  ARG  NH1', ' C1120  THR  O  ', -0.624, (216.462, 214.691, 289.336)), (' C 914  ASN  ND2', ' C1111  GLU  OE2', -0.62, (217.039, 198.849, 281.61)), (' C 197  ILE HD12', ' C 202  LYS  HZ2', -0.62, (203.113, 193.035, 196.971)), (' B1093  GLY  O  ', ' B1107  ARG  NH2', -0.617, (227.297, 225.198, 279.096)), (' Y 126  SER  O  ', ' Y 127  SER  OG ', -0.611, (249.264, 191.841, 128.382)), (' A 122  ASN HD22', ' A1302  NAG  H83', -0.61, (273.507, 238.672, 184.256)), (' B  33  THR  O  ', ' B  33  THR HG22', -0.605, (194.181, 255.649, 219.946)), (' C1031  GLU  OE1', ' C1039  ARG  NH1', -0.602, (221.581, 213.121, 255.227)), (' A  33  THR HG21', ' A 220  PHE  HD1', -0.601, (259.65, 224.212, 213.796)), (' B  33  THR  CG2', ' B 220  PHE  HD1', -0.597, (193.928, 254.997, 221.038)), (' A 961  THR  HA ', ' A 964  LYS  HE2', -0.592, (233.29, 225.771, 218.165)), (' B  31  SER  O  ', ' B  59  PHE  N  ', -0.59, (199.763, 260.628, 218.637)), (' C 731  MET  N  ', ' C 774  GLN  OE1', -0.588, (225.628, 205.804, 234.821)), (' A 803  SER  OG ', ' A 804  GLN  NE2', -0.587, (246.795, 236.364, 259.164)), (' B 731  MET  N  ', ' B 774  GLN  OE1', -0.583, (204.646, 218.545, 238.019)), (' A 571  ASP  OD2', ' C 964  LYS  NZ ', -0.581, (212.886, 198.381, 212.453)), (' C 382  VAL HG21', ' C 387  LEU HD21', -0.579, (194.503, 227.794, 191.336)), (' B 117  LEU HD21', ' B 231  ILE HD13', -0.576, (191.226, 254.808, 193.27)), (' A  33  THR HG21', ' A 220  PHE  CD1', -0.567, (258.872, 224.744, 213.758)), (' A  33  THR HG23', ' A  58  PHE  CZ ', -0.567, (257.923, 222.137, 212.334)), (' C 973  ILE  N  ', ' C 992  GLN  OE1', -0.563, (215.29, 210.37, 198.457)), (' C  33  THR  CG2', ' C  33  THR  O  ', -0.562, (196.164, 183.137, 213.025)), (' C 496  GLY  O  ', ' C 501  ASN  ND2', -0.562, (210.017, 236.0, 162.326)), (' C1420  NAG  O3 ', ' C1421  NAG  O5 ', -0.558, (200.463, 196.116, 292.811)), (' B 439  ASN  O  ', ' B 443  SER  OG ', -0.556, (225.349, 228.275, 159.382)), (' B  33  THR  HB ', ' B 219  GLY  O  ', -0.552, (192.595, 258.134, 221.266)), (' C 197  ILE  HB ', ' C 202  LYS  NZ ', -0.549, (203.65, 193.27, 195.728)), (' C 954  GLN  OE1', ' C1014  ARG  NE ', -0.547, (216.218, 207.173, 230.575)), (' B 496  GLY  O  ', ' B 501  ASN  ND2', -0.546, (224.69, 219.413, 160.506)), (' C 287  ASP  OD1', ' C 288  ALA  N  ', -0.546, (200.992, 184.305, 216.905)), (' A 132  GLU  CB ', ' A1323  NAG  H81', -0.545, (258.452, 225.358, 172.906)), (' B  33  THR  CG2', ' B 220  PHE  CD1', -0.545, (193.925, 254.908, 221.097)), (' C 195  LYS  HE3', ' C 202  LYS  HD3', -0.545, (203.92, 189.902, 197.789)), (' B 287  ASP  OD1', ' B 288  ALA  N  ', -0.544, (195.15, 250.663, 223.116)), (' A1094  VAL HG11', ' C 904  TYR  OH ', -0.543, (232.412, 202.033, 274.866)), (' C1409  NAG  C8 ', ' C1409  NAG  H3 ', -0.542, (203.702, 182.805, 236.984)), (' C 405  ASP  O  ', ' C 408  ARG  HG2', -0.541, (212.725, 230.38, 176.266)), (' A 326  ILE HD12', ' A 539  VAL HG21', -0.539, (234.463, 189.626, 201.083)), (' B 578  ASP  OD2', ' B 581  THR  CB ', -0.537, (244.737, 254.164, 200.342)), (' Z  89  GLU  N  ', ' Z  89  GLU  OE1', -0.536, (222.601, 268.878, 140.274)), (' B 200  TYR  OH ', ' C 516  GLU  OE1', -0.535, (193.598, 242.62, 192.716)), (' A  31  SER  O  ', ' A  59  PHE  N  ', -0.527, (261.319, 216.711, 210.079)), (' B 519  HIS  NE2', ' B 565  PHE  CE2', -0.524, (241.32, 238.847, 202.605)), (' A 501  ASN  ND2', ' A 505  TYR  CB ', -0.522, (223.818, 192.869, 143.878)), (' X  89  GLU  N  ', ' X  89  GLU  OE1', -0.521, (195.949, 179.338, 112.795)), (' A 568  ASP  N  ', ' A 572  THR  O  ', -0.521, (219.876, 191.832, 211.669)), (' C 749  CYS  HB2', ' C 977  LEU HD21', -0.521, (227.236, 208.998, 202.638)), (' C 326  ILE HD12', ' C 539  VAL HG21', -0.518, (179.816, 220.114, 207.361)), (' C 424  LYS  O  ', ' C 463  PRO  HA ', -0.518, (206.771, 241.238, 187.37)), (' B 565  PHE  HB2', ' B 576  VAL  HA ', -0.512, (242.502, 243.792, 205.598)), (' C 117  LEU HD21', ' C 231  ILE HD13', -0.511, (200.507, 186.976, 186.828)), (' B 787  GLN  OE1', ' C 703  ASN  ND2', -0.51, (196.191, 203.896, 263.204)), (' C 105  ILE HG13', ' C 241  LEU HD11', -0.508, (191.932, 178.619, 184.935)), (' A 914  ASN  N  ', ' A 914  ASN  OD1', -0.507, (236.034, 218.976, 279.807)), (' C 600  PRO  HD3', ' C 692  ILE HD11', -0.503, (191.544, 193.488, 232.949)), (' A 287  ASP  OD1', ' A 288  ALA  N  ', -0.498, (255.649, 225.328, 216.157)), (' A 804  GLN  OE1', ' A 935  GLN  NE2', -0.498, (247.662, 233.763, 255.903)), (' B 316  SER  OG ', ' B 317  ASN  N  ', -0.497, (217.012, 246.834, 220.717)), (' B  33  THR HG23', ' B  58  PHE  CE2', -0.497, (196.414, 255.216, 220.805)), (' B 564  GLN  O  ', ' B 577  ARG  HB2', -0.495, (245.479, 244.247, 203.323)), (' A  33  THR  CG2', ' A  33  THR  O  ', -0.495, (259.614, 222.959, 212.041)), (' A  41  LYS  HG2', ' B 562  PHE  HD2', -0.494, (250.301, 237.219, 201.539)), (' A1103  PHE  HZ ', ' A1319  NAG  HO6', -0.493, (244.075, 203.735, 287.134)), (' B 117  LEU  N  ', ' B 117  LEU HD12', -0.491, (191.205, 258.863, 190.996)), (' B 105  ILE HG13', ' B 241  LEU HD11', -0.491, (187.307, 266.481, 194.632)), (' A 770  ILE HD11', ' A1012  LEU HD23', -0.489, (218.87, 227.108, 230.634)), (' Y  30  SER  OG ', ' Y  98  ARG  NH2', -0.489, (240.949, 220.473, 154.428)), (' B  36  VAL HG21', ' B 220  PHE  HE1', -0.488, (193.901, 252.668, 218.562)), (' C 122  ASN  O  ', ' C 124  THR  N  ', -0.488, (200.03, 166.009, 186.31)), (' Y  89  GLU  N  ', ' Y  89  GLU  OE1', -0.488, (242.88, 192.422, 134.993)), (' B 110  LEU  N  ', ' B 110  LEU HD12', -0.487, (196.128, 264.603, 190.081)), (' C  33  THR  CG2', ' C 220  PHE  HD1', -0.486, (197.378, 182.178, 213.95)), (' A  44  ARG  O  ', ' A 283  GLY  HA2', -0.485, (249.847, 237.057, 213.385)), (' C1401  NAG  O3 ', ' C1401  NAG  O7 ', -0.485, (185.86, 227.532, 174.855)), (' B 130  VAL HG21', ' B 167  THR  OG1', -0.484, (188.361, 253.494, 187.088)), (' C 598  ILE  CD1', ' C 666  ILE HD11', -0.483, (190.821, 202.307, 234.452)), (' C 721  SER  OG ', ' C1066  THR  OG1', -0.482, (213.392, 199.32, 261.135)), (' B 577  ARG  NH1', ' B 584  ILE HD11', -0.481, (248.573, 246.023, 204.875)), (' B 200  TYR  CE2', ' C 518  LEU HD11', -0.481, (191.449, 243.818, 194.454)), (' B 969  ASN  OD1', ' B 975  SER  N  ', -0.479, (202.121, 229.015, 206.14)), (' B1032  CYS  SG ', ' B1048  HIS  CE1', -0.477, (210.603, 221.69, 260.779)), (' B 577  ARG  HG3', ' B 584  ILE  CD1', -0.476, (247.538, 246.951, 204.562)), (' B1011  GLN  OE1', ' B1014  ARG  NH1', -0.476, (208.086, 223.388, 230.356)), (' C1126  CYS  SG ', ' C1132  ILE HD13', -0.475, (203.588, 220.914, 291.205)), (' B 901  GLN  O  ', ' B 905  ARG  HG2', -0.474, (207.824, 218.137, 271.536)), (' B 738  CYS  SG ', ' B 739  THR  N  ', -0.473, (202.935, 212.548, 216.495)), (' C 393  THR HG21', ' C 518  LEU  HB2', -0.471, (189.093, 241.816, 197.069)), (' B 578  ASP  OD1', ' B 579  PRO  HD2', -0.47, (241.398, 251.242, 199.947)), (' B 721  SER  OG ', ' B1066  THR  OG1', -0.47, (210.366, 230.594, 264.464)), (' B 657  ASN  N  ', ' B 657  ASN  OD1', -0.469, (224.123, 259.759, 246.26)), (' A 350  VAL HG21', ' A 418  ILE HG23', -0.468, (214.456, 197.217, 154.11)), (' A  29  THR HG22', ' A  30  ASN  N  ', -0.46, (268.711, 216.174, 208.081)), (' C 777  ASN  O  ', ' C 781  VAL HG23', -0.459, (228.82, 207.311, 243.734)), (' B 468  ILE  C  ', ' B 468  ILE HD12', -0.459, (245.69, 215.701, 172.805)), (' A1028  LYS  O  ', ' A1032  CYS  CB ', -0.458, (227.978, 224.03, 256.641)), (' A 777  ASN  O  ', ' A 781  VAL HG23', -0.457, (223.994, 230.36, 246.415)), (' B 577  ARG  HG3', ' B 584  ILE HD13', -0.456, (247.122, 247.43, 204.055)), (' A 430  THR  O  ', ' A 430  THR HG22', -0.455, (219.347, 202.801, 173.444)), (' C  57  PRO  HG3', ' C 273  ARG  HE ', -0.454, (192.135, 192.978, 208.217)), (' A 716  THR  N  ', ' A1071  GLN  O  ', -0.451, (244.029, 208.262, 272.052)), (' B 762  GLN  OE1', ' C1006  THR HG21', -0.451, (214.566, 211.328, 220.524)), (' B1028  LYS  NZ ', ' B1042  PHE  O  ', -0.451, (214.011, 223.303, 255.054)), (' B 914  ASN  ND2', ' B1111  GLU  OE2', -0.449, (213.343, 226.511, 284.866)), (' A 792  PRO  O  ', ' A 795  LYS  NZ ', -0.448, (239.511, 243.217, 265.594)), (' B 565  PHE  HB2', ' B 575  ALA  O  ', -0.447, (242.277, 242.887, 206.405)), (' B1031  GLU  OE1', ' B1039  ARG  NH1', -0.447, (217.463, 216.67, 256.239)), (' C 986  PRO  N  ', ' C 987  PRO  CD ', -0.447, (225.19, 213.825, 190.78)), (' Z  30  SER  OG ', ' Z  98  ARG  NH2', -0.447, (200.507, 250.495, 159.042)), (' B 986  PRO  N  ', ' B 987  PRO  CD ', -0.446, (201.817, 216.088, 193.851)), (' A 360  ASN  N  ', ' A 523  THR  OG1', -0.445, (211.521, 188.843, 180.779)), (' B 454  ARG  HA ', ' B 492  LEU HD23', -0.444, (237.389, 212.694, 170.135)), (' X   6  GLU  N  ', ' X   6  GLU  OE1', -0.444, (203.021, 169.986, 131.833)), (' B 607  GLN  HB2', ' B 607  GLN HE21', -0.442, (207.145, 259.319, 235.113)), (' A1004  LEU  O  ', ' A1008  VAL HG23', -0.442, (220.919, 228.026, 222.429)), (' A 598  ILE HD13', ' A 666  ILE HD11', -0.442, (246.679, 204.282, 229.65)), (' Z   6  GLU  N  ', ' Z   6  GLU  OE1', -0.438, (202.793, 259.463, 145.83)), (' A 986  PRO  N  ', ' A 987  PRO  CD ', -0.438, (216.746, 236.789, 194.209)), (' C 598  ILE HD13', ' C 666  ILE HD11', -0.438, (191.252, 201.646, 234.541)), (' A 737  ASP  OD2', ' B 317  ASN  ND2', -0.436, (221.019, 242.56, 219.346)), (' Y   6  GLU  N  ', ' Y   6  GLU  OE1', -0.435, (245.328, 214.069, 140.112)), (' B 908  GLY  O  ', ' B1038  LYS  NZ ', -0.435, (217.457, 218.557, 269.504)), (' B 240  THR HG22', ' B 241  LEU  N  ', -0.433, (187.255, 268.47, 200.37)), (' C 560  LEU HD12', ' C 562  PHE  CZ ', -0.433, (185.033, 245.161, 210.855)), (' B 905  ARG  HD2', ' B1049  LEU  O  ', -0.432, (209.238, 219.985, 267.62)), (' B 439  ASN  OD1', ' B 443  SER  OG ', -0.432, (224.599, 226.809, 159.613)), (' B1053  PRO  O  ', ' B1054  GLN  NE2', -0.431, (198.446, 221.823, 256.665)), (' A 811  LYS  NZ ', ' A 820  ASP  OD2', -0.431, (245.266, 239.583, 249.637)), (' C 554  GLU  N  ', ' C 554  GLU  OE1', -0.431, (174.668, 226.518, 215.461)), (' B 796  ASP  N  ', ' B 796  ASP  OD1', -0.429, (191.314, 218.718, 273.713)), (' A 281  GLU  N  ', ' A 281  GLU  OE1', -0.429, (252.34, 237.855, 219.692)), (' X  30  SER  OG ', ' X  98  ARG  NH2', -0.427, (208.477, 178.854, 144.353)), (' C 216  LEU HD21', ' C 266  TYR  CD2', -0.426, (188.799, 176.376, 204.343)), (' B 715  PRO  O  ', ' B1110  TYR  N  ', -0.425, (218.157, 232.982, 279.811)), (' C 898  PHE  HZ ', ' C1050  MET  HE1', -0.425, (224.605, 195.562, 264.221)), (' B 766  ALA  O  ', ' B 770  ILE HG12', -0.424, (208.196, 213.023, 230.261)), (' C 383  SER  HB3', ' C 386  LYS  HG2', -0.424, (194.783, 221.427, 192.239)), (' B  57  PRO  HG3', ' B 273  ARG  HE ', -0.422, (204.598, 256.142, 213.04)), (' A 101  ILE  HA ', ' A 242  LEU  HA ', -0.422, (273.672, 227.058, 191.493)), (' C 468  ILE  C  ', ' C 468  ILE HD12', -0.421, (204.372, 253.622, 177.711)), (' C 316  SER  OG ', ' C 317  ASN  N  ', -0.42, (194.473, 205.774, 219.172)), (' B 231  ILE HG13', ' B 232  GLY  N  ', -0.419, (193.751, 251.262, 191.367)), (' A 382  VAL HG21', ' A 387  LEU HD21', -0.419, (221.952, 199.341, 175.738)), (' B1028  LYS  O  ', ' B1032  CYS  HB3', -0.418, (210.01, 218.796, 257.784)), (' B 346  ARG  HG3', ' B 346  ARG  O  ', -0.418, (239.121, 230.079, 165.908)), (' B 905  ARG  O  ', ' B1036  GLN  NE2', -0.418, (212.848, 220.619, 270.104)), (' B 565  PHE  CB ', ' B 576  VAL  HA ', -0.417, (242.345, 243.444, 205.244)), (' B1311  NAG  O6 ', ' B1312  NAG  C7 ', -0.415, (188.945, 231.811, 265.243)), (' B 307  THR  O  ', ' B 307  THR HG22', -0.415, (200.522, 244.465, 234.54)), (' C 599  THR HG22', ' C 601  GLY  N  ', -0.414, (196.758, 192.601, 232.373)), (' C1008  VAL  O  ', ' C1012  LEU HD13', -0.414, (223.228, 213.781, 226.264)), (' A 332  ILE HD11', ' A 527  PRO  CA ', -0.414, (224.725, 186.689, 184.785)), (' A1324  NAG  O3 ', ' A1324  NAG  O7 ', -0.414, (226.922, 182.362, 169.065)), (' C 484  GLU  OE2', ' Z  52  ARG  NE ', -0.413, (212.796, 256.569, 166.739)), (' A 904  TYR  CZ ', ' B1107  ARG  HD3', -0.412, (227.106, 226.845, 276.503)), (' A1011  GLN  OE1', ' A1014  ARG  NH1', -0.412, (227.376, 225.654, 229.198)), (' A 546  LEU  C  ', ' A 546  LEU HD12', -0.412, (224.473, 193.628, 199.912)), (' A 332  ILE HD11', ' A 527  PRO  HA ', -0.411, (224.35, 186.973, 184.619)), (' B 612  TYR  HE1', ' B 651  ILE HD12', -0.41, (219.847, 255.32, 227.116)), (' A 389  ASP  N  ', ' A 389  ASP  OD1', -0.41, (226.111, 195.753, 183.027)), (' C1032  CYS  SG ', ' C1048  HIS  CE1', -0.409, (221.086, 204.195, 258.303)), (' C 328  ARG  NH2', ' C 531  THR  O  ', -0.409, (174.721, 224.409, 201.362)), (' B1005  GLN  OE1', ' C1002  GLN  NE2', -0.408, (214.421, 217.786, 215.913)), (' A 656  VAL HG12', ' A 658  ASN  H  ', -0.408, (253.725, 196.335, 239.313)), (' B  34  ARG  HD3', ' B 191  GLU  OE2', -0.407, (190.067, 260.867, 215.926)), (' A 403  ARG  NE ', ' A 405  ASP  OD1', -0.407, (221.228, 197.969, 147.51)), (' B 611  LEU HD22', ' B 666  ILE HG23', -0.407, (220.973, 247.779, 234.59)), (' C 419  ALA  O  ', ' C 424  LYS  HB2', -0.406, (210.79, 241.424, 184.567)), (' C1060  VAL HG22', ' C1061  VAL  N  ', -0.406, (223.568, 199.717, 247.769)), (' A1126  CYS  SG ', ' A1132  ILE HD13', -0.406, (226.672, 191.516, 286.184)), (' B 598  ILE HG23', ' B 664  ILE HG21', -0.405, (214.168, 248.246, 237.37)), (' C 197  ILE  HB ', ' C 202  LYS  HZ2', -0.405, (203.237, 193.051, 196.463)), (' A 110  LEU  N  ', ' A 110  LEU HD12', -0.404, (261.421, 219.052, 181.223)), (' B 193  VAL HG23', ' B 223  LEU HD22', -0.404, (190.71, 255.858, 210.095)), (' A 759  PHE  O  ', ' A 763  LEU  HG ', -0.403, (214.878, 230.692, 220.664)), (' B 736  VAL HG22', ' B 858  LEU HD23', -0.403, (200.409, 218.627, 223.283)), (' B1309  NAG  H62', ' B1310  NAG  H82', -0.402, (205.19, 238.856, 273.726)), (' C 532  ASN  OD1', ' C 533  LEU  N  ', -0.401, (172.466, 222.553, 203.908)), (' B 401  VAL HG22', ' B 509  ARG  HG2', -0.401, (231.296, 228.199, 168.432)), (' A 122  ASN  ND2', ' A1302  NAG  H83', -0.401, (273.002, 238.808, 184.64)), (' A 337  PRO  HD2', ' A 358  ILE HD12', -0.401, (215.536, 186.126, 173.83)), (' A 961  THR  HA ', ' A 964  LYS  CE ', -0.401, (233.671, 225.439, 218.114)), (' B 813  SER  O  ', ' B 815  ARG  N  ', -0.4, (188.357, 220.536, 252.538))]
data['cablam'] = [('A', '33', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nESS--', (260.9, 221.6, 211.9)), ('A', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\n-SSEE', (253.3, 217.6, 194.7)), ('A', '108', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEESSS', (258.0, 217.6, 182.2)), ('A', '113', 'LYS', 'check CA trace,carbonyls, peptide', 'bend\nSSSS-', (258.5, 220.5, 172.2)), ('A', '484', 'GLU', 'check CA trace,carbonyls, peptide', ' \nT--BT', (197.2, 195.6, 137.5)), ('A', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTE', (198.7, 201.2, 133.5)), ('A', '519', 'HIS', 'check CA trace,carbonyls, peptide', 'bend\n--SS-', (205.4, 200.3, 184.0)), ('A', '527', 'PRO', ' beta sheet', ' \nE----', (224.7, 188.1, 183.8)), ('A', '528', 'LYS', ' beta sheet', ' \n-----', (227.0, 190.2, 185.9)), ('A', '544', 'ASN', 'check CA trace,carbonyls, peptide', 'turn\nEETTE', (222.4, 189.7, 195.3)), ('A', '570', 'ALA', 'check CA trace,carbonyls, peptide', 'turn\n-TTS-', (217.7, 196.7, 215.3)), ('A', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (241.9, 203.6, 231.6)), ('A', '667', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nEEETT', (239.3, 201.1, 232.7)), ('A', '797', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\n--STT', (240.2, 234.5, 270.7)), ('A', '856', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\n--SSE', (228.3, 238.2, 217.1)), ('A', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\nBTTBS', (231.3, 218.8, 256.8)), ('A', '1058', 'HIS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (231.8, 231.7, 240.9)), ('A', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (226.6, 193.3, 295.1)), ('A', '1092', 'GLU', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (228.1, 208.3, 279.7)), ('A', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nTTS--', (239.0, 210.6, 274.7)), ('A', '34', 'ARG', 'check CA trace', ' \nSS--E', (261.6, 223.3, 208.6)), ('A', '112', 'SER', 'check CA trace', 'bend\nSSSSS', (261.9, 221.7, 173.6)), ('A', '220', 'PHE', 'check CA trace', ' \n-S--E', (262.2, 227.1, 213.4)), ('A', '293', 'LEU', 'check CA trace', 'turn\nTTTSH', (253.9, 213.2, 213.2)), ('A', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (231.7, 196.1, 204.7)), ('A', '1134', 'ASN', 'check CA trace', 'strand\n-EE--', (233.6, 192.0, 288.7)), ('B', '35', 'GLY', 'check CA trace,carbonyls, peptide', ' \nS---B', (194.7, 256.2, 213.5)), ('B', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\n-SS-E', (202.5, 256.1, 201.8)), ('B', '108', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEESS-', (199.0, 262.7, 190.6)), ('B', '111', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nS-S--', (193.6, 267.8, 186.1)), ('B', '231', 'ILE', ' beta sheet', ' \nE----', (191.7, 251.0, 190.8)), ('B', '291', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\nEETTT', (205.5, 249.3, 219.7)), ('B', '317', 'ASN', 'check CA trace,carbonyls, peptide', 'strand\nEEEEE', (219.2, 246.0, 220.9)), ('B', '334', 'ASN', ' beta sheet', ' \n---B-', (242.2, 249.0, 181.2)), ('B', '484', 'GLU', 'check CA trace,carbonyls, peptide', ' \nT--BT', (242.6, 201.0, 163.7)), ('B', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTE', (237.9, 195.8, 164.9)), ('B', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (220.5, 245.9, 237.4)), ('B', '667', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nEEETT', (224.0, 244.7, 238.1)), ('B', '797', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\n--STT', (195.8, 220.7, 273.3)), ('B', '1045', 'LYS', 'check CA trace,carbonyls, peptide', 'bend\nSSSSE', (215.3, 230.4, 260.9)), ('B', '1058', 'HIS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (200.9, 221.7, 242.7)), ('B', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (239.5, 224.1, 297.0)), ('B', '1092', 'GLU', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (225.0, 221.0, 281.3)), ('B', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nTTS--', (217.5, 230.6, 278.8)), ('B', '34', 'ARG', 'check CA trace', ' \n-S---', (193.7, 258.0, 216.7)), ('B', '214', 'ARG', 'check CA trace', 'bend\n-SSS-', (188.8, 273.3, 219.2)), ('B', '215', 'ASP', 'check CA trace', 'bend\nSSS--', (190.4, 270.2, 217.7)), ('B', '220', 'PHE', 'check CA trace', ' \nSS---', (190.3, 256.1, 221.4)), ('B', '520', 'ALA', 'check CA trace', 'bend\n-SS--', (245.0, 237.2, 197.4)), ('B', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (229.7, 247.7, 208.3)), ('C', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\n-SS-E', (193.8, 193.9, 197.0)), ('C', '108', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEESS-', (190.3, 191.5, 184.3)), ('C', '111', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nS-SSS', (187.8, 186.5, 177.6)), ('C', '231', 'ILE', ' beta sheet', ' \nEE---', (204.1, 189.7, 185.0)), ('C', '484', 'GLU', 'check CA trace,carbonyls, peptide', ' \nT--BT', (217.6, 260.0, 168.6)), ('C', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTE', (224.5, 258.4, 169.0)), ('C', '519', 'HIS', 'check CA trace,carbonyls, peptide', 'bend\n--SS-', (189.7, 242.9, 201.8)), ('C', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (193.5, 205.9, 236.3)), ('C', '667', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nEEETT', (193.1, 209.4, 237.6)), ('C', '1036', 'GLN', 'check CA trace,carbonyls, peptide', ' \nSS---', (223.9, 206.9, 262.9)), ('C', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'bend\nTTSSS', (217.7, 205.5, 256.8)), ('C', '1045', 'LYS', 'check CA trace,carbonyls, peptide', 'bend\nSSSSE', (211.2, 203.6, 258.4)), ('C', '1058', 'HIS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (225.2, 200.0, 238.3)), ('C', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (206.7, 219.5, 299.6)), ('C', '1092', 'GLU', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (215.6, 212.2, 281.0)), ('C', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nTTS--', (210.7, 201.7, 276.5)), ('C', '34', 'ARG', 'check CA trace', ' \n-S--E', (195.1, 181.8, 209.4)), ('C', '215', 'ASP', 'check CA trace', 'bend\nSSS--', (185.4, 173.9, 208.3)), ('C', '220', 'PHE', 'check CA trace', ' \n-S--E', (198.4, 178.8, 213.6)), ('C', '310', 'LYS', 'check CA trace', 'bend\n--SEE', (199.3, 194.5, 234.5)), ('C', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (187.0, 219.3, 209.4)), ('C', '600', 'PRO', 'check CA trace', 'bend\nEES-T', (195.1, 192.9, 234.7)), ('C', '1134', 'ASN', 'check CA trace', 'strand\n-EE--', (200.8, 214.7, 294.1))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-11068/6z43/Model_validation_9/validation_cootdata/molprobity_probe6z43_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)
