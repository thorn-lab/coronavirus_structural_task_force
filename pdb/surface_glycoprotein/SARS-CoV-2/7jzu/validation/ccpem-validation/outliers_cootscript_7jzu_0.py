
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
data['clusters'] = [('A', '1', 1, 'smoc Outlier', (225.74299999999997, 190.466, 210.267)), ('A', '51', 1, 'smoc Outlier', (224.463, 208.389, 223.448)), ('B', '480', 1, 'smoc Outlier', (207.517, 190.64899999999997, 209.924)), ('B', '481', 1, 'smoc Outlier', (203.935, 189.42800000000003, 209.57399999999998)), ('B', '484', 1, 'cablam Outlier', (207.8, 194.8, 215.1)), ('B', '486', 1, 'cablam Outlier', (214.5, 192.5, 215.1)), ('B', '488', 1, 'smoc Outlier', (211.08800000000002, 195.122, 211.57299999999998)), ('B', '405', 2, 'Dihedral angle:CA:CB:CG:OD1', (218.477, 221.156, 207.98200000000003)), ('B', '406', 2, 'smoc Outlier', (215.975, 219.405, 205.68800000000002)), ('B', '408', 2, 'Dihedral angle:CD:NE:CZ:NH1', (217.39100000000002, 222.171, 201.30800000000002)), ('B', '520', 3, 'side-chain clash', (192.493, 225.133, 180.407)), ('B', '521', 3, 'side-chain clash\ncablam Outlier', (192.493, 225.133, 180.407)), ('B', '522', 3, 'cablam Outlier', (193.8, 229.4, 183.2)), ('B', '362', 4, 'smoc Outlier', (193.40200000000002, 236.17, 191.748)), ('B', '364', 4, 'Dihedral angle:CA:CB:CG:OD1', (198.354, 238.319, 194.74899999999997)), ('B', '366', 4, 'smoc Outlier', (203.394, 240.196, 195.959)), ('B', '456', 5, 'smoc Outlier', (211.88000000000002, 203.431, 206.224)), ('B', '491', 5, 'smoc Outlier', (208.11599999999999, 203.254, 209.18800000000002)), ('B', '444', 6, 'smoc Outlier', (206.564, 222.791, 222.925)), ('B', '497', 6, 'smoc Outlier', (210.632, 219.686, 218.288)), ('B', '379', 7, 'smoc Outlier', (211.4, 229.708, 192.594)), ('B', '432', 7, 'smoc Outlier', (208.065, 228.196, 194.36800000000002)), ('C', '1', 1, 'Bond angle:C8:C7:N2', (199.21699999999998, 234.737, 203.1)), ('C', '2', 1, 'Bond length:C5:O5', (202.934, 240.778, 211.71299999999997))]
data['probe'] = [(' B 520  ALA  HB1', ' B 521  PRO  HD2', -0.467, (192.248, 224.779, 180.641)), (' B 520  ALA  HB1', ' B 521  PRO  CD ', -0.431, (192.493, 225.133, 180.407))]
data['cablam'] = [('B', '484', 'GLU', 'check CA trace,carbonyls, peptide', ' \nT--BT', (207.8, 194.8, 215.1)), ('B', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTE', (214.5, 192.5, 215.1)), ('B', '521', 'PRO', ' beta sheet', 'bend\n-SS--', (191.6, 228.3, 180.2)), ('B', '522', 'ALA', ' beta sheet', ' \nSS--E', (193.8, 229.4, 183.2))]
data['smoc'] = [('A', 1, u'ASP', 0.4474369775490818, (225.74299999999997, 190.466, 210.267)), ('A', 51, u'LEU', 0.5686681336571718, (224.463, 208.389, 223.448)), ('B', 362, u'VAL', 0.5357615778947943, (193.40200000000002, 236.17, 191.748)), ('B', 366, u'SER', 0.6095746135168695, (203.394, 240.196, 195.959)), ('B', 374, u'PHE', 0.5575712089911711, (210.003, 233.864, 205.053)), ('B', 379, u'CYS', 0.573419306790744, (211.4, 229.708, 192.594)), ('B', 398, u'ASP', 0.5400866639935368, (201.632, 221.38800000000003, 199.38100000000003)), ('B', 406, u'GLU', 0.5020681866999858, (215.975, 219.405, 205.68800000000002)), ('B', 417, u'LYS', 0.5585863113196331, (215.282, 211.035, 203.796)), ('B', 422, u'ASN', 0.5528904925242936, (208.424, 211.738, 202.154)), ('B', 432, u'CYS', 0.5904516177241929, (208.065, 228.196, 194.36800000000002)), ('B', 438, u'SER', 0.4406639641909258, (207.959, 228.065, 213.36200000000002)), ('B', 444, u'LYS', 0.5111565932277724, (206.564, 222.791, 222.925)), ('B', 452, u'LEU', 0.5685661459526633, (206.064, 212.537, 211.751)), ('B', 456, u'PHE', 0.5777190827835305, (211.88000000000002, 203.431, 206.224)), ('B', 480, u'CYS', 0.4315869658587042, (207.517, 190.64899999999997, 209.924)), ('B', 481, u'ASN', 0.5091236898162479, (203.935, 189.42800000000003, 209.57399999999998)), ('B', 488, u'CYS', 0.48462083221162194, (211.08800000000002, 195.122, 211.57299999999998)), ('B', 491, u'PRO', 0.5105486556356823, (208.11599999999999, 203.254, 209.18800000000002)), ('B', 497, u'PHE', 0.5164891513719849, (210.632, 219.686, 218.288))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-22574/7jzu/Model_validation_1/validation_cootdata/molprobity_probe7jzu_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)
