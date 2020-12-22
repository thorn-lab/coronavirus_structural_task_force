
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
data['cbeta'] = []
data['jpred'] = []
data['clusters'] = [('A', '848', 1, 'side-chain clash', (79.204, 85.654, 124.497)), ('A', '854', 1, 'side-chain clash', (79.204, 85.654, 124.497)), ('A', '856', 1, 'side-chain clash', (75.014, 78.685, 119.661)), ('A', '857', 1, 'smoc Outlier', (75.24700000000001, 82.048, 120.103)), ('A', '858', 1, 'side-chain clash\nDihedral angle:CD:NE:CZ:NH1', (78.96300000000001, 81.765, 119.315)), ('A', '859', 1, 'side-chain clash', (81.309, 78.061, 123.491)), ('A', '860', 1, 'side-chain clash\nsmoc Outlier', (75.014, 78.685, 119.661)), ('A', '862', 1, 'side-chain clash', (80.784, 79.711, 117.246)), ('A', '887', 1, 'side-chain clash', (79.236, 74.553, 126.699)), ('A', '891', 1, 'side-chain clash', (79.236, 74.553, 126.699)), ('A', '366', 2, 'smoc Outlier', (81.76100000000001, 129.089, 112.612)), ('A', '367', 2, 'backbone clash', (77.988, 124.99, 111.526)), ('A', '368', 2, 'backbone clash', (77.988, 124.99, 111.526)), ('A', '369', 2, 'smoc Outlier', (80.395, 122.17199999999998, 109.084)), ('A', '372', 2, 'side-chain clash', (83.771, 116.298, 109.906)), ('A', '376', 2, 'smoc Outlier', (89.68599999999999, 117.18799999999999, 111.327)), ('A', '538', 2, 'smoc Outlier', (91.93, 113.79700000000001, 107.566)), ('A', '563', 2, 'side-chain clash', (83.771, 116.298, 109.906)), ('A', '660', 2, 'side-chain clash', (94.928, 110.858, 103.703)), ('A', '665', 2, 'side-chain clash\nsmoc Outlier', (94.928, 110.858, 103.703)), ('A', '193', 3, 'smoc Outlier', (115.362, 112.16799999999999, 67.617)), ('A', '196', 3, 'side-chain clash', (112.563, 110.239, 65.475)), ('A', '203', 3, 'side-chain clash', (112.253, 105.587, 60.725)), ('A', '204', 3, 'side-chain clash', (107.374, 105.215, 65.482)), ('A', '221', 3, 'smoc Outlier', (112.709, 101.056, 58.507)), ('A', '222', 3, 'side-chain clash', (112.253, 105.587, 60.725)), ('A', '223', 3, 'side-chain clash', (110.853, 108.516, 55.29)), ('A', '232', 3, 'side-chain clash', (112.563, 110.239, 65.475)), ('A', '233', 3, 'side-chain clash', (107.374, 105.215, 65.482)), ('A', '330', 4, 'backbone clash', (96.673, 125.728, 105.379)), ('A', '342', 4, 'backbone clash', (96.673, 125.728, 105.379)), ('A', '380', 4, 'side-chain clash', (95.577, 124.177, 114.732)), ('A', '382', 4, 'smoc Outlier', (100.88499999999999, 119.627, 113.554)), ('A', '401', 4, 'side-chain clash', (101.333, 115.168, 117.924)), ('A', '419', 4, 'side-chain clash', (98.071, 121.767, 109.303)), ('A', '672', 4, 'smoc Outlier', (102.069, 111.13499999999999, 117.27799999999999)), ('A', '673', 4, 'smoc Outlier', (101.52, 111.65199999999999, 113.576)), ('A', '855', 4, 'side-chain clash', (99.884, 128.609, 112.112)), ('A', '117', 5, 'side-chain clash\nsmoc Outlier', (130.694, 100.982, 64.005)), ('A', '192', 5, 'side-chain clash', (118.834, 106.382, 63.97)), ('A', '217', 5, 'cablam CA Geom Outlier', (121.8, 101.7, 65.2)), ('A', '218', 5, 'cablam Outlier', (119.9, 99.5, 62.7)), ('A', '219', 5, 'side-chain clash', (118.834, 106.382, 63.97)), ('A', '90', 5, 'smoc Outlier', (122.786, 111.18499999999999, 61.146)), ('A', '97', 5, 'smoc Outlier', (126.909, 104.48400000000001, 66.908)), ('A', '98', 5, 'side-chain clash', (130.694, 100.982, 64.005)), ('A', '452', 6, 'smoc Outlier', (104.01400000000001, 96.785, 112.336)), ('A', '453', 6, 'smoc Outlier', (103.621, 100.37899999999999, 111.015)), ('A', '544', 6, 'side-chain clash', (98.443, 97.035, 115.144)), ('A', '545', 6, 'side-chain clash', (92.614, 95.208, 114.183)), ('A', '553', 6, 'cablam Outlier\nsmoc Outlier', (101.9, 89.0, 113.7)), ('A', '555', 6, 'smoc Outlier', (97.063, 92.586, 112.955)), ('A', '556', 6, 'side-chain clash', (98.443, 97.035, 115.144)), ('A', '557', 6, 'side-chain clash', (92.614, 95.208, 114.183)), ('A', '42', 7, 'side-chain clash', (104.024, 86.534, 65.548)), ('A', '44', 7, 'smoc Outlier', (104.624, 91.374, 69.922)), ('A', '703', 7, 'smoc Outlier', (96.824, 87.599, 80.119)), ('A', '706', 7, 'smoc Outlier', (101.16, 86.23, 78.17499999999998)), ('A', '707', 7, 'side-chain clash', (101.191, 86.734, 72.204)), ('A', '710', 7, 'side-chain clash', (101.607, 84.075, 70.127)), ('A', '712', 7, 'side-chain clash', (104.024, 86.534, 65.548)), ('A', '715', 7, 'side-chain clash', (101.607, 84.075, 70.127)), ('A', '758', 8, 'side-chain clash\nDihedral angle:CA:C', (86.65299999999999, 88.331, 96.088)), ('A', '759', 8, 'side-chain clash\nDihedral angle:N:CA\ncablam Outlier', (88.611, 91.196, 97.583)), ('A', '761', 8, 'smoc Outlier', (91.30499999999999, 85.902, 97.038)), ('A', '812', 8, 'smoc Outlier', (88.94800000000001, 80.24400000000001, 98.647)), ('A', '815', 8, 'smoc Outlier', (87.271, 77.532, 103.079)), ('A', '816', 8, 'side-chain clash', (84.435, 74.097, 101.044)), ('A', '830', 8, 'side-chain clash', (84.435, 74.097, 101.044)), ('A', '606', 9, 'side-chain clash\ncablam Outlier', (84.044, 77.702, 82.495)), ('A', '607', 9, 'cablam Outlier', (80.5, 78.0, 82.7)), ('A', '608', 9, 'cablam Outlier', (81.6, 76.1, 79.6)), ('A', '609', 9, 'side-chain clash', (84.044, 77.702, 82.495)), ('A', '610', 9, 'smoc Outlier', (87.079, 73.537, 77.387)), ('A', '612', 9, 'side-chain clash', (87.294, 71.777, 84.261)), ('A', '805', 9, 'side-chain clash', (87.294, 71.777, 84.261)), ('A', '468', 10, 'side-chain clash', (96.416, 97.455, 79.963)), ('A', '472', 10, 'side-chain clash', (96.416, 97.455, 79.963)), ('A', '474', 10, 'Dihedral angle:CB:CG:CD:OE1', (89.161, 99.896, 79.505)), ('A', '476', 10, 'side-chain clash', (91.193, 96.783, 82.584)), ('A', '696', 10, 'side-chain clash', (91.875, 91.861, 84.719)), ('A', '700', 10, 'side-chain clash', (91.875, 91.861, 84.719)), ('A', '268', 11, 'side-chain clash\nsmoc Outlier', (113.433, 119.819, 96.597)), ('A', '272', 11, 'side-chain clash', (113.08, 124.673, 93.284)), ('A', '274', 11, 'cablam Outlier', (104.9, 124.5, 93.4)), ('A', '275', 11, 'side-chain clash\ncablam Outlier', (110.647, 122.943, 93.424)), ('A', '321', 11, 'smoc Outlier', (111.537, 117.053, 95.17799999999998)), ('A', '322', 11, 'side-chain clash', (113.433, 119.819, 96.597)), ('A', '527', 12, 'side-chain clash', (81.612, 117.471, 101.476)), ('A', '531', 12, 'side-chain clash', (86.243, 116.905, 97.625)), ('A', '533', 12, 'Dihedral angle:CD:NE:CZ:NH1', (84.819, 121.612, 95.503)), ('A', '567', 12, 'side-chain clash', (82.456, 112.829, 100.3)), ('A', '654', 12, 'side-chain clash\nsmoc Outlier', (82.456, 112.829, 100.3)), ('A', '657', 12, 'side-chain clash', (86.243, 116.905, 97.625)), ('A', '572', 13, 'side-chain clash', (79.507, 102.107, 96.627)), ('A', '575', 13, 'smoc Outlier', (77.44500000000001, 101.195, 93.321)), ('A', '576', 13, 'side-chain clash\nsmoc Outlier', (79.507, 102.107, 96.627)), ('A', '578', 13, 'side-chain clash', (74.942, 94.148, 91.822)), ('A', '579', 13, 'smoc Outlier', (78.056, 94.96600000000001, 93.18499999999999)), ('A', '582', 13, 'side-chain clash', (74.942, 94.148, 91.822)), ('A', '125', 14, 'smoc Outlier', (115.277, 95.458, 75.124)), ('A', '128', 14, 'side-chain clash', (110.248, 96.048, 79.605)), ('A', '132', 14, 'side-chain clash', (106.563, 98.434, 78.725)), ('A', '239', 14, 'smoc Outlier', (105.74000000000001, 103.101, 77.23400000000001)), ('A', '240', 14, 'side-chain clash', (106.563, 98.434, 78.725)), ('A', '290', 15, 'side-chain clash', (101.28, 111.035, 77.306)), ('A', '309', 15, 'side-chain clash', (100.511, 107.784, 79.837)), ('A', '311', 15, 'smoc Outlier', (99.44700000000002, 111.349, 87.30799999999999)), ('A', '312', 15, 'smoc Outlier', (101.70100000000001, 108.565, 86.016)), ('A', '466', 15, 'side-chain clash', (100.511, 107.784, 79.837)), ('A', '387', 16, 'smoc Outlier', (108.696, 118.44300000000001, 116.66799999999999)), ('A', '388', 16, 'backbone clash', (110.424, 112.543, 117.074)), ('A', '389', 16, 'backbone clash', (110.424, 112.543, 117.074)), ('A', '390', 16, 'smoc Outlier', (111.455, 108.892, 115.643)), ('A', '393', 16, 'smoc Outlier', (110.896, 103.838, 111.896)), ('A', '488', 17, 'side-chain clash', (73.357, 107.444, 100.468)), ('A', '493', 17, 'side-chain clash', (73.357, 107.444, 100.468)), ('A', '494', 17, 'side-chain clash', (74.52, 102.726, 103.641)), ('A', '573', 17, 'side-chain clash', (74.52, 102.726, 103.641)), ('A', '818', 18, 'backbone clash', (81.313, 68.091, 105.234)), ('A', '820', 18, 'side-chain clash', (78.403, 67.825, 100.575)), ('A', '829', 18, 'side-chain clash', (78.403, 67.825, 100.575)), ('A', '868', 18, 'backbone clash', (81.313, 68.091, 105.234)), ('A', '333', 19, 'side-chain clash', (91.571, 133.026, 105.503)), ('A', '334', 19, 'smoc Outlier', (91.285, 135.251, 111.083)), ('A', '337', 19, 'cablam Outlier', (90.6, 138.4, 115.4)), ('A', '361', 19, 'side-chain clash', (91.571, 133.026, 105.503)), ('A', '145', 20, 'smoc Outlier', (123.90400000000001, 92.26100000000001, 83.08)), ('A', '149', 20, 'side-chain clash', (124.298, 96.418, 79.753)), ('A', '212', 20, 'side-chain clash', (124.298, 96.418, 79.753)), ('A', '615', 21, 'side-chain clash', (94.422, 81.051, 86.844)), ('A', '755', 21, 'side-chain clash', (90.225, 84.168, 86.652)), ('A', '764', 21, 'side-chain clash', (94.422, 81.051, 86.844)), ('A', '200', 22, 'backbone clash\nsmoc Outlier', (111.981, 114.941, 59.185)), ('A', '226', 22, 'smoc Outlier', (111.958, 117.20400000000001, 53.572)), ('A', '230', 22, 'backbone clash', (111.981, 114.941, 59.185)), ('A', '415', 23, 'side-chain clash', (89.662, 75.326, 129.848)), ('A', '416', 23, 'smoc Outlier', (87.479, 78.54, 128.42600000000002)), ('A', '417', 23, 'side-chain clash', (89.662, 75.326, 129.848)), ('A', '420', 24, 'side-chain clash', (88.994, 68.727, 127.408)), ('A', '423', 24, 'smoc Outlier', (86.827, 67.93, 124.462)), ('A', '424', 24, 'side-chain clash', (88.994, 68.727, 127.408)), ('A', '881', 25, 'smoc Outlier', (80.54400000000001, 68.584, 114.61)), ('A', '884', 25, 'side-chain clash', (77.932, 72.114, 119.614)), ('A', '888', 25, 'side-chain clash', (77.932, 72.114, 119.614)), ('A', '723', 26, 'smoc Outlier', (93.76100000000001, 88.864, 68.142)), ('A', '727', 26, 'smoc Outlier', (96.103, 93.757, 70.55)), ('A', '729', 26, 'Dihedral angle:CB:CG:CD:OE1', (98.15499999999999, 97.60199999999999, 67.362)), ('A', '601', 27, 'side-chain clash\nsmoc Outlier', (81.849, 80.443, 90.131)), ('A', '605', 27, 'side-chain clash', (84.126, 81.942, 89.739)), ('A', '756', 27, 'side-chain clash', (84.126, 81.942, 89.739)), ('A', '205', 28, 'side-chain clash', (114.637, 104.343, 69.402)), ('A', '216', 28, 'side-chain clash', (114.637, 104.343, 69.402)), ('A', '136', 29, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1', (114.21100000000001, 82.482, 88.99900000000001)), ('A', '139', 29, 'cablam Outlier', (117.1, 84.8, 85.0)), ('A', '689', 30, 'side-chain clash', (87.569, 96.771, 93.182)), ('A', '693', 30, 'side-chain clash', (87.569, 96.771, 93.182)), ('A', '819', 31, 'side-chain clash', (78.555, 66.017, 92.604)), ('A', '826', 31, 'side-chain clash', (78.555, 66.017, 92.604)), ('A', '413', 32, 'side-chain clash', (92.401, 87.102, 124.867)), ('A', '546', 32, 'side-chain clash', (92.401, 87.102, 124.867)), ('A', '677', 33, 'cablam CA Geom Outlier', (103.7, 106.3, 101.7)), ('A', '678', 33, 'cablam CA Geom Outlier', (100.5, 104.7, 100.3)), ('A', '834', 34, 'smoc Outlier', (88.68799999999999, 72.04, 112.088)), ('A', '836', 34, 'Dihedral angle:CD:NE:CZ:NH1', (90.589, 76.871, 113.495)), ('A', '798', 35, 'smoc Outlier', (100.79700000000001, 79.77499999999999, 98.313)), ('A', '800', 35, 'smoc Outlier', (97.763, 76.25, 93.863)), ('A', '186', 36, 'side-chain clash', (114.582, 104.97, 79.22)), ('A', '241', 36, 'side-chain clash', (114.582, 104.97, 79.22)), ('A', '515', 37, 'side-chain clash', (76.395, 113.832, 112.755)), ('A', '519', 37, 'side-chain clash', (75.817, 116.395, 109.31)), ('A', '254', 38, 'Dihedral angle:CB:CG:CD:OE1\nsmoc Outlier', (118.30499999999999, 115.342, 89.281)), ('A', '259', 38, 'cablam Outlier', (123.0, 117.3, 88.0)), ('A', '602', 39, 'side-chain clash', (85.481, 75.34, 93.3)), ('A', '809', 39, 'side-chain clash', (85.481, 75.34, 93.3)), ('A', '501', 40, 'smoc Outlier', (85.94000000000001, 104.33, 115.436)), ('A', '502', 40, 'smoc Outlier', (85.192, 107.827, 114.14)), ('A', '40', 41, 'smoc Outlier', (101.52499999999999, 92.99900000000001, 59.055)), ('A', '41', 41, 'backbone clash', (102.578, 90.835, 58.11)), ('A', '614', 42, 'side-chain clash\nsmoc Outlier', (91.9, 73.306, 89.988)), ('A', '802', 42, 'side-chain clash', (91.9, 73.306, 89.988)), ('B', '131', 1, 'smoc Outlier', (112.61999999999999, 108.295, 120.607)), ('B', '132', 1, 'side-chain clash', (119.699, 106.348, 122.229)), ('B', '133', 1, 'smoc Outlier', (115.503, 102.573, 120.356)), ('B', '138', 1, 'side-chain clash', (119.699, 106.348, 122.229)), ('B', '142', 1, 'smoc Outlier', (122.326, 112.73700000000001, 121.285)), ('B', '143', 1, 'smoc Outlier', (126.01700000000001, 113.368, 121.895)), ('B', '159', 1, 'side-chain clash', (117.596, 111.949, 126.288)), ('B', '160', 1, 'smoc Outlier', (112.795, 109.346, 130.33800000000002)), ('B', '161', 1, 'side-chain clash', (114.361, 105.34, 128.644)), ('B', '162', 1, 'cablam Outlier', (109.7, 103.7, 128.6)), ('B', '167', 1, 'smoc Outlier', (116.80499999999999, 108.877, 133.83100000000002)), ('B', '182', 1, 'cablam CA Geom Outlier', (114.6, 101.1, 126.0)), ('B', '184', 1, 'side-chain clash', (114.361, 105.34, 128.644)), ('B', '186', 1, 'side-chain clash', (117.596, 111.949, 126.288)), ('B', '103', 2, 'side-chain clash', (99.884, 128.609, 112.112)), ('B', '91', 2, 'side-chain clash\nsmoc Outlier', (92.181, 126.751, 118.678)), ('B', '95', 2, 'side-chain clash', (92.181, 126.751, 118.678)), ('B', '96', 2, 'Dihedral angle:CD:NE:CZ:NH1', (96.903, 129.1, 123.118)), ('B', '98', 2, 'side-chain clash\nsmoc Outlier', (95.937, 126.634, 115.459)), ('B', '106', 3, 'smoc Outlier', (107.52799999999999, 132.095, 108.429)), ('B', '115', 3, 'side-chain clash', (105.534, 126.667, 105.028)), ('B', '119', 3, 'side-chain clash', (105.534, 126.667, 105.028)), ('B', '120', 4, 'side-chain clash', (106.5, 125.656, 112.81)), ('B', '124', 4, 'side-chain clash', (106.5, 125.656, 112.81)), ('B', '125', 4, 'smoc Outlier', (107.921, 124.23700000000001, 117.627)), ('B', '83', 5, 'side-chain clash', (82.077, 119.516, 118.966)), ('B', '87', 5, 'side-chain clash\nsmoc Outlier', (82.077, 119.516, 118.966)), ('C', '10', 1, 'side-chain clash', (102.677, 78.448, 127.649)), ('C', '13', 1, 'side-chain clash', (103.719, 80.651, 132.107)), ('C', '14', 1, 'side-chain clash', (101.876, 84.598, 126.431)), ('C', '17', 1, 'side-chain clash', (104.557, 88.528, 135.563)), ('C', '22', 1, 'side-chain clash', (104.557, 88.528, 135.563)), ('C', '33', 1, 'smoc Outlier', (105.332, 87.627, 125.868)), ('C', '35', 1, 'side-chain clash', (107.307, 79.993, 125.087)), ('C', '36', 1, 'side-chain clash', (101.876, 84.598, 126.431)), ('C', '39', 1, 'side-chain clash', (102.677, 78.448, 127.649)), ('C', '40', 1, 'smoc Outlier', (102.754, 78.7, 121.348)), ('C', '48', 1, 'smoc Outlier', (107.644, 73.865, 125.79400000000001)), ('C', '49', 1, 'side-chain clash', (110.202, 74.569, 131.862)), ('C', '52', 1, 'side-chain clash', (103.064, 77.963, 133.551)), ('C', '53', 1, 'side-chain clash', (110.202, 74.569, 131.862)), ('C', '54', 1, 'side-chain clash', (110.024, 82.957, 134.05)), ('C', '55', 1, 'side-chain clash', (103.719, 80.651, 132.107)), ('C', '58', 1, 'side-chain clash', (110.024, 82.957, 134.05)), ('C', '59', 1, 'smoc Outlier', (105.38499999999999, 84.114, 138.472)), ('C', '28', 2, 'side-chain clash', (102.596, 71.137, 130.44)), ('C', '31', 2, 'side-chain clash', (102.596, 71.137, 130.44)), ('C', '23', 3, 'Dihedral angle:CB:CG:CD:OE1\nsmoc Outlier', (102.76700000000001, 94.692, 131.98600000000002)), ('C', '43', 3, 'smoc Outlier', (106.63799999999999, 71.523, 118.012)), ('D', '147', 1, 'side-chain clash', (123.387, 74.972, 141.171)), ('D', '148', 1, 'smoc Outlier', (120.37299999999999, 71.202, 142.268)), ('D', '154', 1, 'side-chain clash', (123.387, 74.972, 141.171)), ('D', '155', 1, 'smoc Outlier', (127.986, 75.24100000000001, 139.593)), ('D', '156', 1, 'side-chain clash', (127.664, 75.424, 142.642)), ('D', '186', 1, 'side-chain clash', (124.297, 79.056, 144.564)), ('D', '189', 1, 'smoc Outlier', (126.368, 80.37299999999999, 136.506)), ('D', '92', 2, 'side-chain clash', (99.265, 74.923, 138.54)), ('D', '93', 2, 'side-chain clash', (95.67, 69.727, 137.561)), ('D', '94', 2, 'side-chain clash', (98.932, 70.96, 134.886)), ('D', '95', 2, 'side-chain clash', (99.265, 74.923, 138.54)), ('D', '97', 2, 'side-chain clash', (95.67, 69.727, 137.561)), ('D', '98', 2, 'side-chain clash', (102.596, 71.137, 130.44)), ('D', '159', 3, 'side-chain clash', (129.788, 84.984, 148.782)), ('D', '166', 3, 'side-chain clash', (129.788, 84.984, 148.782)), ('D', '168', 3, 'side-chain clash', (133.495, 82.812, 151.723)), ('D', '110', 4, 'side-chain clash', (109.055, 80.265, 145.905)), ('D', '113', 4, 'smoc Outlier', (110.306, 79.85799999999999, 151.17)), ('D', '115', 4, 'side-chain clash', (109.055, 80.265, 145.905)), ('D', '102', 5, 'smoc Outlier', (111.023, 70.573, 136.415)), ('D', '103', 5, 'side-chain clash', (106.63, 73.383, 139.991)), ('D', '107', 5, 'side-chain clash', (106.63, 73.383, 139.991)), ('D', '119', 6, 'smoc Outlier', (114.627, 83.96100000000001, 135.767)), ('D', '120', 6, 'side-chain clash', (115.249, 81.24, 136.816)), ('D', '162', 7, 'side-chain clash', (119.918, 88.047, 153.74)), ('D', '183', 7, 'side-chain clash\ncablam CA Geom Outlier', (119.918, 88.047, 153.74))]
data['probe'] = [(' A 884  TYR  O  ', ' A 888  ILE HD12', -0.762, (77.932, 72.114, 119.614)), (' A 819  LEU HD11', ' A 826  TYR  HB3', -0.731, (78.555, 66.017, 92.604)), (' A 223  ILE  O  ', ' A 223  ILE HG13', -0.716, (110.853, 108.516, 55.29)), (' B 120  ILE  O  ', ' B 124  THR  HB ', -0.714, (106.5, 125.656, 112.81)), (' C  35  LEU HD11', ' C  55  LEU HD13', -0.67, (107.024, 82.819, 129.338)), (' D 103  LEU  O  ', ' D 107  ILE HG13', -0.646, (106.63, 73.383, 139.991)), (' A 149  TYR  HE2', ' A 212  LEU HD13', -0.631, (124.298, 96.418, 79.753)), (' A 272  LYS  HE3', ' A 275  PHE  CE1', -0.625, (110.7, 123.373, 93.597)), (' C  28  LEU HD12', ' C  31  GLN HE21', -0.612, (110.78, 89.691, 133.061)), (' A 858  ARG  O  ', ' A 862  LEU HD12', -0.611, (80.784, 79.711, 117.246)), (' A 606  TYR  CE2', ' A 805  LEU HD22', -0.606, (85.516, 72.538, 87.353)), (' D  92  PHE  HA ', ' D  95  LEU  HB2', -0.601, (99.265, 74.923, 138.54)), (' A 531  THR HG21', ' A 567  THR HG21', -0.6, (83.259, 114.555, 102.12)), (' A 333  ILE HG22', ' A 361  LEU  HA ', -0.59, (91.571, 133.026, 105.503)), (' B 159  VAL HG22', ' B 186  VAL HG22', -0.59, (117.596, 111.949, 126.288)), (' A 290  TRP  HE1', ' A 309  HIS  CE1', -0.586, (101.28, 111.035, 77.306)), (' D 166  ILE HG22', ' D 168  GLN  OE1', -0.584, (133.495, 82.812, 151.723)), (' A 309  HIS  HD2', ' A 466  ILE HG12', -0.581, (100.511, 107.784, 79.837)), (' D  94  MET  O  ', ' D  98  LEU HD12', -0.577, (98.932, 70.96, 134.886)), (' C  49  PHE  O  ', ' C  53  VAL HG23', -0.575, (110.202, 74.569, 131.862)), (' A 601  MET  O  ', ' A 605  VAL HG23', -0.574, (81.849, 80.443, 90.131)), (' C  13  LEU HD22', ' C  52  MET  HE1', -0.568, (103.064, 77.963, 133.551)), (' A 271  LEU  N  ', ' A 271  LEU HD12', -0.562, (110.434, 127.635, 103.084)), (' A 527  LEU  O  ', ' A 531  THR HG23', -0.547, (81.612, 117.471, 101.476)), (' A 605  VAL HG22', ' A 756  MET  HB2', -0.545, (84.126, 81.942, 89.739)), (' C  17  LEU HD22', ' C  22  VAL HG21', -0.539, (104.557, 88.528, 135.563)), (' A 136  GLU  N  ', ' A 136  GLU  OE2', -0.539, (112.406, 83.514, 89.475)), (' A 419  PHE  HA ', ' A 887  TYR  HE2', -0.535, (83.649, 72.569, 126.188)), (' A 660  ALA  O  ', ' A 665  GLU  HB3', -0.531, (94.928, 110.858, 103.703)), (' A 856  ILE  O  ', ' A 860  VAL HG23', -0.528, (75.014, 78.685, 119.661)), (' A 472  VAL  O  ', ' A 476  VAL HG23', -0.525, (91.193, 96.783, 82.584)), (' A 200  GLY  HA2', ' A 230  GLY  N  ', -0.518, (111.977, 115.452, 59.207)), (' A 413  GLY  HA2', ' A 546  TYR  OH ', -0.515, (92.401, 87.102, 124.867)), (' A 380  MET  HA ', ' A 380  MET  HE3', -0.507, (95.577, 124.177, 114.732)), (' A 855  MET  HE2', ' A 859  PHE  CE2', -0.506, (81.309, 78.061, 123.491)), (' A 820  VAL HG21', ' A 829  LEU HD12', -0.504, (78.403, 67.825, 100.575)), (' A 816  HIS  O  ', ' A 830  PRO  HA ', -0.503, (84.435, 74.097, 101.044)), (' A 128  VAL  O  ', ' A 132  ARG  HG3', -0.501, (111.138, 94.633, 81.072)), (' A 380  MET  HE1', ' B  98  LEU HD22', -0.501, (95.937, 126.634, 115.459)), (' A 755  MET  HG2', ' A 764  VAL HG12', -0.498, (90.225, 84.168, 86.652)), (' A 855  MET  HE1', ' A 858  ARG  HD3', -0.498, (82.287, 80.748, 121.733)), (' A 341  VAL HG21', ' B 103  LEU HD21', -0.49, (99.884, 128.609, 112.112)), (' A 567  THR  HB ', ' A 654  ARG HH12', -0.489, (82.456, 112.829, 100.3)), (' A 707  LEU  O  ', ' A 710  THR HG22', -0.488, (101.191, 86.734, 72.204)), (' A 615  MET  HE2', ' A 764  VAL HG21', -0.486, (94.422, 81.051, 86.844)), (' D 186  VAL  O  ', ' D 186  VAL HG12', -0.485, (124.297, 79.056, 144.564)), (' B 161  ASP  HA ', ' B 184  LEU HD23', -0.485, (114.361, 105.34, 128.644)), (' A 128  VAL HG12', ' A 132  ARG  HD3', -0.485, (109.76, 95.468, 79.362)), (' A 848  VAL HG23', ' A 854  LEU  HB3', -0.485, (79.204, 85.654, 124.497)), (' C  54  SER  O  ', ' C  58  VAL HG23', -0.483, (110.024, 82.957, 134.05)), (' A 689  TYR  O  ', ' A 693  VAL HG23', -0.479, (87.569, 96.771, 93.182)), (' D 147  PHE  HB2', ' D 156  ILE HD11', -0.476, (125.178, 74.908, 143.615)), (' A 614  LEU  HB2', ' A 802  GLU  HB3', -0.475, (91.9, 73.306, 89.988)), (' A 710  THR  CG2', ' A 715  ILE HD11', -0.472, (101.476, 84.439, 70.555)), (' A 203  GLY  HA3', ' A 222  PHE  CD1', -0.472, (112.359, 105.574, 60.958)), (' A 420  TYR  O  ', ' A 424  VAL HG22', -0.472, (88.994, 68.727, 127.408)), (' A 468  GLN  O  ', ' A 472  VAL HG23', -0.47, (96.416, 97.455, 79.963)), (' A 330  VAL  HA ', ' A 342  VAL  O  ', -0.47, (96.673, 125.728, 105.379)), (' A 186  LEU HD11', ' A 241  LEU HD21', -0.468, (114.582, 104.97, 79.22)), (' A 419  PHE  HA ', ' A 887  TYR  CE2', -0.467, (83.159, 72.558, 126.092)), (' A 379  ALA  HA ', ' B 117  LEU HD13', -0.467, (98.071, 121.767, 109.303)), (' A 545  LYS  HB2', ' A 557  VAL HG23', -0.466, (92.614, 95.208, 114.183)), (' A 272  LYS  HE3', ' A 275  PHE  CD1', -0.465, (110.647, 122.943, 93.424)), (' A 494  ILE  O  ', ' A 573  GLN  NE2', -0.465, (74.52, 102.726, 103.641)), (' A 192  PHE  HZ ', ' A 219  PHE  HE1', -0.461, (118.834, 106.382, 63.97)), (' A 401  LEU  N  ', ' A 401  LEU HD23', -0.46, (101.333, 115.168, 117.924)), (' A  41  LYS  HD2', ' A  41  LYS  N  ', -0.46, (102.578, 90.835, 58.11)), (' A 367  SER  OG ', ' A 368  PHE  N  ', -0.46, (77.988, 124.99, 111.526)), (' A 818  MET  HE1', ' A 868  PRO  O  ', -0.459, (81.313, 68.091, 105.234)), (' D 120  ILE  N  ', ' D 120  ILE HD12', -0.459, (115.249, 81.24, 136.816)), (' A 268  TRP  CZ3', ' A 272  LYS  HE2', -0.458, (113.08, 124.673, 93.284)), (' C  28  LEU HD12', ' C  31  GLN  NE2', -0.457, (111.482, 89.917, 132.702)), (' A 606  TYR  HE2', ' A 805  LEU HD22', -0.457, (85.418, 71.998, 87.812)), (' D 162  ALA  HB2', ' D 183  PRO  HG2', -0.456, (119.918, 88.047, 153.74)), (' A 372  LEU  HG ', ' A 563  CYS  SG ', -0.453, (83.771, 116.298, 109.906)), (' C   6  VAL HG22', ' D  98  LEU HD23', -0.453, (102.596, 71.137, 130.44)), (' A 887  TYR  O  ', ' A 891  LEU  HG ', -0.452, (76.766, 73.861, 125.389)), (' A 196  MET  HE2', ' A 232  PRO  HB3', -0.446, (112.563, 110.239, 65.475)), (' D 156  ILE  H  ', ' D 156  ILE HD12', -0.446, (127.664, 75.424, 142.642)), (' A 602  LEU  O  ', ' A 606  TYR  HD1', -0.446, (81.664, 76.504, 88.687)), (' A 572  HIS  O  ', ' A 576  LEU  HG ', -0.446, (79.507, 102.107, 96.627)), (' A 531  THR  O  ', ' A 657  ASN  ND2', -0.444, (86.243, 116.905, 97.625)), (' A 415  PHE  CZ ', ' A 417  LYS  HA ', -0.444, (89.662, 75.326, 129.848)), (' D 147  PHE  HB3', ' D 154  TRP  HB2', -0.444, (123.387, 74.972, 141.171)), (' A 200  GLY  HA2', ' A 230  GLY  CA ', -0.442, (111.981, 114.941, 59.185)), (' D 124  THR  O  ', ' D 124  THR HG22', -0.442, (125.372, 82.544, 129.244)), (' D 110  ALA  HB1', ' D 115  VAL HG12', -0.441, (109.055, 80.265, 145.905)), (' A 612  PRO  HG2', ' A 805  LEU  CD1', -0.44, (87.294, 71.777, 84.261)), (' D 159  VAL  O  ', ' D 166  ILE HG12', -0.439, (129.788, 84.984, 148.782)), (' A  98  LYS  O  ', ' A 117  GLN  HB3', -0.439, (130.694, 100.982, 64.005)), (' A 696  ILE  O  ', ' A 700  VAL HG23', -0.438, (91.875, 91.861, 84.719)), (' A 488  ILE HD11', ' A 493  VAL HG22', -0.438, (73.357, 107.444, 100.468)), (' B  83  VAL  O  ', ' B  87  MET  HG3', -0.438, (82.077, 119.516, 118.966)), (' A 515  TYR  O  ', ' A 519  MET  HG3', -0.438, (76.395, 113.832, 112.755)), (' A 887  TYR  CE1', ' A 891  LEU HD21', -0.437, (79.236, 74.553, 126.699)), (' A 710  THR HG23', ' A 715  ILE HD11', -0.437, (101.607, 84.075, 70.127)), (' A 388  LEU HD12', ' A 389  LEU  N  ', -0.436, (110.424, 112.543, 117.074)), (' B 132  ILE HG21', ' B 138  TYR  HB2', -0.432, (119.699, 106.348, 122.229)), (' A 578  SER  O  ', ' A 582  THR HG23', -0.426, (74.942, 94.148, 91.822)), (' C  35  LEU  O  ', ' C  39  ILE HG23', -0.424, (107.307, 79.993, 125.087)), (' C  13  LEU HD23', ' C  55  LEU HD23', -0.424, (103.719, 80.651, 132.107)), (' A 204  VAL HG22', ' A 233  VAL  HB ', -0.424, (107.374, 105.215, 65.482)), (' A 203  GLY  HA3', ' A 222  PHE  HD1', -0.422, (112.253, 105.587, 60.725)), (' A 602  LEU HD21', ' A 809  PRO  HD3', -0.421, (85.481, 75.34, 93.3)), (' A 205  LEU  HB3', ' A 216  TRP  CH2', -0.421, (114.637, 104.343, 69.402)), (' D  93  THR  O  ', ' D  97  LYS  HG3', -0.42, (95.67, 69.727, 137.561)), (' A 478  LYS  HA ', ' A 478  LYS  HD3', -0.42, (82.487, 96.518, 79.99)), (' A 544  LEU HD23', ' A 556  THR HG22', -0.418, (98.443, 97.035, 115.144)), (' C  10  SER  HB2', ' C  39  ILE HD11', -0.414, (103.112, 78.353, 127.557)), (' C  14  LEU HD22', ' C  36  HIS  CG ', -0.413, (101.876, 84.598, 126.431)), (' B  91  LEU  O  ', ' B  95  LEU HD13', -0.413, (92.181, 126.751, 118.678)), (' C  10  SER  CB ', ' C  39  ILE HD11', -0.412, (102.677, 78.448, 127.649)), (' A 758  LEU HD23', ' A 759  SER  H  ', -0.412, (87.149, 89.516, 98.511)), (' B 115  VAL  HB ', ' B 119  ILE HD11', -0.412, (105.534, 126.667, 105.028)), (' A 268  TRP  CD1', ' A 322  PRO  HD3', -0.41, (113.433, 119.819, 96.597)), (' A 128  VAL  CG1', ' A 132  ARG  HD3', -0.408, (110.248, 96.048, 79.605)), (' A 132  ARG HH12', ' A 240  LEU  HA ', -0.407, (106.563, 98.434, 78.725)), (' A 606  TYR  O  ', ' A 609  VAL HG23', -0.403, (84.044, 77.702, 82.495)), (' A  42  VAL HG23', ' A 712  GLY  HA3', -0.401, (104.024, 86.534, 65.548)), (' A 519  MET  HB3', ' A 519  MET  HE2', -0.4, (75.817, 116.395, 109.31))]
data['omega'] = [('A', ' 505 ', 'PRO', None, (90.308, 113.568, 115.66700000000002)), ('B', ' 183 ', 'PRO', None, (112.63000000000002, 101.92399999999998, 124.669))]
data['cablam'] = [('A', '139', 'CYS', 'check CA trace,carbonyls, peptide', ' \nSS-HH', (117.1, 84.8, 85.0)), ('A', '218', 'ASP', 'check CA trace,carbonyls, peptide', ' \nB----', (119.9, 99.5, 62.7)), ('A', '259', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nTTS-T', (123.0, 117.3, 88.0)), ('A', '274', 'ASP', 'check CA trace,carbonyls, peptide', ' \n----H', (104.9, 124.5, 93.4)), ('A', '275', 'PHE', 'check CA trace,carbonyls, peptide', ' \n---HH', (107.7, 122.8, 91.4)), ('A', '337', 'GLY', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (90.6, 138.4, 115.4)), ('A', '553', 'ARG', ' beta sheet', ' \nS----', (101.9, 89.0, 113.7)), ('A', '606', 'TYR', 'check CA trace,carbonyls, peptide', 'helix\nHHHSS', (83.0, 76.7, 85.4)), ('A', '607', 'SER', 'check CA trace,carbonyls, peptide', 'bend\nHHSS-', (80.5, 78.0, 82.7)), ('A', '608', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nHSS-S', (81.6, 76.1, 79.6)), ('A', '759', 'SER', 'check CA trace,carbonyls, peptide', 'bend\nE-SS-', (88.6, 91.2, 97.6)), ('A', '824', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (69.7, 62.5, 94.6)), ('A', '151', 'CYS', 'check CA trace', 'bend\nTTSS-', (126.4, 96.7, 90.0)), ('A', '217', 'TYR', 'check CA trace', ' \n-B---', (121.8, 101.7, 65.2)), ('A', '326', 'PHE', 'check CA trace', ' \nGG-EE', (104.1, 117.6, 100.0)), ('A', '677', 'PRO', 'check CA trace', ' \nE--S-', (103.7, 106.3, 101.7)), ('A', '678', 'GLY', 'check CA trace', 'bend\n--S--', (100.5, 104.7, 100.3)), ('B', '101', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\n--SHH', (105.9, 134.4, 116.6)), ('B', '162', 'ALA', 'check CA trace,carbonyls, peptide', 'turn\nE-TTS', (109.7, 103.7, 128.6)), ('B', '112', 'ASP', 'check CA trace', 'helix-3\nSGGG-', (100.4, 134.0, 98.9)), ('B', '182', 'TRP', 'check CA trace', 'bend\nS-S-E', (114.6, 101.1, 126.0)), ('D', '124', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nSSS--', (124.2, 81.0, 128.1)), ('D', '134', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\nE-TTS', (118.3, 79.6, 157.6)), ('D', '183', 'PRO', 'check CA trace', ' \n-S-EE', (118.5, 84.9, 153.3))]
data['smoc'] = [('A', 40, u'ASP', 0.5147118798336519, (101.52499999999999, 92.99900000000001, 59.055)), ('A', 44, u'GLY', 0.4982913040261678, (104.624, 91.374, 69.922)), ('A', 50, u'LYS', 0.47388002180840966, (118.90100000000001, 85.867, 65.615)), ('A', 86, u'ILE', 0.6348983835062377, (120.20100000000001, 107.143, 56.016999999999996)), ('A', 90, u'LEU', 0.4038590467571994, (122.786, 111.18499999999999, 61.146)), ('A', 97, u'ALA', 0.3903699508471636, (126.909, 104.48400000000001, 66.908)), ('A', 117, u'GLN', 0.4313012428996573, (131.35600000000002, 98.67099999999999, 65.453)), ('A', 125, u'ALA', 0.3874046724086562, (115.277, 95.458, 75.124)), ('A', 145, u'ILE', 0.4819510896729618, (123.90400000000001, 92.26100000000001, 83.08)), ('A', 161, u'ASP', 0.44554423071159976, (116.531, 84.617, 98.208)), ('A', 171, u'ILE', 0.4485418595709737, (118.549, 94.41700000000002, 96.187)), ('A', 179, u'GLY', 0.45601012261740526, (119.906, 104.09, 87.426)), ('A', 193, u'CYS', 0.5027697159948018, (115.362, 112.16799999999999, 67.617)), ('A', 200, u'GLY', 0.4956753576079046, (113.60799999999999, 114.927, 57.864)), ('A', 211, u'ASP', 0.44414794540152724, (122.66799999999999, 99.718, 73.15299999999999)), ('A', 221, u'ASP', 0.5110016727244359, (112.709, 101.056, 58.507)), ('A', 226, u'THR', 0.5561286575644224, (111.958, 117.20400000000001, 53.572)), ('A', 239, u'SER', 0.40880290002004716, (105.74000000000001, 103.101, 77.23400000000001)), ('A', 254, u'GLU', 0.5036040344253058, (118.30499999999999, 115.342, 89.281)), ('A', 268, u'TRP', 0.5818171515162193, (115.756, 123.47, 98.149)), ('A', 311, u'ALA', 0.438289988032753, (99.44700000000002, 111.349, 87.30799999999999)), ('A', 312, u'ASN', 0.33777621054518575, (101.70100000000001, 108.565, 86.016)), ('A', 321, u'PHE', 0.495999408013623, (111.537, 117.053, 95.17799999999998)), ('A', 326, u'PHE', 0.4622308587640784, (104.087, 117.619, 100.036)), ('A', 334, u'PHE', 0.5778011283061917, (91.285, 135.251, 111.083)), ('A', 366, u'LEU', 0.6165707117861818, (81.76100000000001, 129.089, 112.612)), ('A', 369, u'LYS', 0.6103483806193276, (80.395, 122.17199999999998, 109.084)), ('A', 376, u'ALA', 0.5269212460164969, (89.68599999999999, 117.18799999999999, 111.327)), ('A', 382, u'ALA', 0.5345553115443342, (100.88499999999999, 119.627, 113.554)), ('A', 387, u'LEU', 0.5400885326238715, (108.696, 118.44300000000001, 116.66799999999999)), ('A', 390, u'ASP', 0.4623813053467008, (111.455, 108.892, 115.643)), ('A', 393, u'THR', 0.4737840705650116, (110.896, 103.838, 111.896)), ('A', 416, u'ASN', 0.5432046290062298, (87.479, 78.54, 128.42600000000002)), ('A', 423, u'ALA', 0.629932291348129, (86.827, 67.93, 124.462)), ('A', 431, u'GLU', 0.6510902285903731, (98.90400000000001, 62.073, 120.30499999999999)), ('A', 440, u'PHE', 0.4932469143574406, (95.854, 81.26700000000001, 119.459)), ('A', 445, u'ASP', 0.5415839272365917, (104.661, 93.77, 123.745)), ('A', 452, u'ASP', 0.5259644846595097, (104.01400000000001, 96.785, 112.336)), ('A', 453, u'TYR', 0.5162229114827632, (103.621, 100.37899999999999, 111.015)), ('A', 501, u'SER', 0.5105389967909949, (85.94000000000001, 104.33, 115.436)), ('A', 502, u'ALA', 0.4948456036034952, (85.192, 107.827, 114.14)), ('A', 538, u'THR', 0.43565934786741334, (91.93, 113.79700000000001, 107.566)), ('A', 553, u'ARG', 0.5314734585298455, (101.923, 89.049, 113.666)), ('A', 555, u'ARG', 0.48591100524974923, (97.063, 92.586, 112.955)), ('A', 575, u'LEU', 0.5152536116693026, (77.44500000000001, 101.195, 93.321)), ('A', 576, u'LEU', 0.46933565723958026, (78.657, 99.005, 96.193)), ('A', 579, u'ILE', 0.5213452059657465, (78.056, 94.96600000000001, 93.18499999999999)), ('A', 592, u'SER', 0.5301425245028587, (76.298, 83.971, 101.133)), ('A', 601, u'MET', 0.5153784719691146, (79.12299999999999, 80.329, 92.49300000000001)), ('A', 610, u'GLU', 0.6209184108264878, (87.079, 73.537, 77.387)), ('A', 614, u'LEU', 0.5542390684149998, (91.542, 75.474, 88.299)), ('A', 630, u'LEU', 0.4283903498561599, (96.79700000000001, 101.16799999999999, 90.751)), ('A', 651, u'ARG', 0.5049280893447428, (84.846, 113.99700000000001, 89.799)), ('A', 654, u'ARG', 0.5063703686180551, (86.193, 113.722, 94.616)), ('A', 658, u'GLU', 0.45044062813425956, (89.865, 110.251, 98.374)), ('A', 665, u'GLU', 0.4234469522472463, (96.84700000000001, 110.978, 104.851)), ('A', 672, u'SER', 0.4727195029955253, (102.069, 111.13499999999999, 117.27799999999999)), ('A', 673, u'LEU', 0.512818120228384, (101.52, 111.65199999999999, 113.576)), ('A', 703, u'ASN', 0.4985694808525526, (96.824, 87.599, 80.119)), ('A', 706, u'ALA', 0.4996139986935487, (101.16, 86.23, 78.17499999999998)), ('A', 717, u'ASP', 0.5991122804924222, (95.12799999999999, 79.087, 65.383)), ('A', 723, u'LEU', 0.5137817484696147, (93.76100000000001, 88.864, 68.142)), ('A', 727, u'LEU', 0.5146145709558266, (96.103, 93.757, 70.55)), ('A', 742, u'VAL', 0.5910679860076706, (87.47, 95.839, 73.94700000000002)), ('A', 761, u'ASP', 0.42086224046075343, (91.30499999999999, 85.902, 97.038)), ('A', 785, u'VAL', 0.39721722584117425, (103.46700000000001, 90.99400000000001, 86.693)), ('A', 792, u'VAL', 0.4787150205209217, (106.586, 92.085, 95.787)), ('A', 798, u'LYS', 0.5345552502289308, (100.79700000000001, 79.77499999999999, 98.313)), ('A', 800, u'TRP', 0.5498762011848439, (97.763, 76.25, 93.863)), ('A', 812, u'PHE', 0.5238743710792261, (88.94800000000001, 80.24400000000001, 98.647)), ('A', 815, u'GLN', 0.5154467228600709, (87.271, 77.532, 103.079)), ('A', 834, u'PRO', 0.5255027410166142, (88.68799999999999, 72.04, 112.088)), ('A', 857, u'GLU', 0.5141238826522584, (75.24700000000001, 82.048, 120.103)), ('A', 860, u'VAL', 0.478624833105648, (75.835, 77.871, 117.229)), ('A', 865, u'ASP', 0.5052756563181411, (80.356, 76.68599999999999, 110.04400000000001)), ('A', 881, u'PHE', 0.6155554334263121, (80.54400000000001, 68.584, 114.61)), ('B', 87, u'MET', 0.5948756666974457, (85.039, 120.93700000000001, 119.531)), ('B', 91, u'LEU', 0.6052824473943675, (90.13, 124.438, 119.299)), ('B', 98, u'LEU', 0.544840057591136, (99.87299999999999, 127.85499999999999, 118.684)), ('B', 106, u'ILE', 0.591924794094308, (107.52799999999999, 132.095, 108.429)), ('B', 125, u'ALA', 0.5277176294968113, (107.921, 124.23700000000001, 117.627)), ('B', 128, u'LEU', 0.5172227984114035, (111.813, 118.462, 120.455)), ('B', 131, u'VAL', 0.5561749290715673, (112.61999999999999, 108.295, 120.607)), ('B', 133, u'PRO', 0.5820951036654134, (115.503, 102.573, 120.356)), ('B', 142, u'CYS', 0.6011590906926683, (122.326, 112.73700000000001, 121.285)), ('B', 143, u'ASP', 0.5731533975365127, (126.01700000000001, 113.368, 121.895)), ('B', 160, u'VAL', 0.545043759866846, (112.795, 109.346, 130.33800000000002)), ('B', 167, u'VAL', 0.5890640928769886, (116.80499999999999, 108.877, 133.83100000000002)), ('C', 23, u'GLU', 0.5537583863397345, (102.76700000000001, 94.692, 131.98600000000002)), ('C', 33, u'VAL', 0.39596599132648774, (105.332, 87.627, 125.868)), ('C', 40, u'LEU', 0.4129434591209255, (102.754, 78.7, 121.348)), ('C', 43, u'LYS', 0.6095814094593645, (106.63799999999999, 71.523, 118.012)), ('C', 48, u'ALA', 0.5252351197570625, (107.644, 73.865, 125.79400000000001)), ('C', 59, u'LEU', 0.448422132625471, (105.38499999999999, 84.114, 138.472)), ('D', 85, u'SER', 0.45920160312784014, (91.44200000000001, 85.83, 141.99200000000002)), ('D', 102, u'ALA', 0.5140569253197474, (111.023, 70.573, 136.415)), ('D', 113, u'GLY', 0.32751485601067126, (110.306, 79.85799999999999, 151.17)), ('D', 119, u'ILE', 0.4657786355049437, (114.627, 83.96100000000001, 135.767)), ('D', 140, u'ASN', 0.3907495442605981, (118.54400000000001, 68.85499999999999, 149.512)), ('D', 148, u'THR', 0.5435932163109617, (120.37299999999999, 71.202, 142.268)), ('D', 155, u'GLU', 0.5341122053403242, (127.986, 75.24100000000001, 139.593)), ('D', 189, u'LEU', 0.5146181301750639, (126.368, 80.37299999999999, 136.506))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-30209/7bv1/Model_validation_1/validation_cootdata/molprobity_probe7bv1_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)
