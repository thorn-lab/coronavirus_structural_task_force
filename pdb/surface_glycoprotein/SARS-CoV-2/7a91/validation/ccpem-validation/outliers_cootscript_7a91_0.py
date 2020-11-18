
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
data['probe'] = [(' A 578  ASP  OD1', ' A 583  GLU  N  ', -0.734, (199.309, 188.706, 183.131)), (' A 362  VAL HG23', ' A 526  GLY  HA3', -0.638, (197.421, 200.77, 197.281)), (' D 168  TRP  HE1', ' D 502  SER  HB3', -0.602, (211.467, 222.967, 278.512)), (' A 393  THR  O  ', ' A 523  THR  OG1', -0.565, (199.095, 190.342, 201.518)), (' D 269  ASP  OD1', ' D 270  MET  N  ', -0.558, (214.992, 230.299, 273.437)), (' D  85  LEU  O  ', ' D  94  LYS  NZ ', -0.555, (224.727, 188.043, 254.11)), (' D 247  LYS  HB3', ' D 282  THR HG22', -0.543, (227.797, 241.989, 272.311)), (' D 261  CYS  HB2', ' D 488  VAL HG13', -0.532, (228.715, 230.338, 283.339)), (' D  32  PHE  CD1', ' D  76  GLN  HG2', -0.527, (206.797, 193.395, 251.277)), (' A 329  PHE  HE2', ' A 528  LYS  HD3', -0.507, (203.331, 202.846, 192.257)), (' D 402  GLU  HB3', ' D 518  ARG  HD3', -0.503, (220.441, 220.518, 257.63)), (' A 457  ARG  NH1', ' A 467  ASP  OD1', -0.5, (203.999, 181.303, 229.579)), (' A 503  VAL  HA ', ' A 506  GLN HE21', -0.475, (202.945, 211.017, 232.589)), (' D 204  ARG  HD2', ' D 219  ARG  O  ', -0.473, (228.534, 204.597, 268.02)), (' D 187  LYS  HB3', ' D 199  TYR  CD2', -0.466, (215.626, 203.954, 273.684)), (' D 177  ARG  HB3', ' D 178  PRO  HD3', -0.465, (209.983, 213.857, 287.715)), (' D 320  LEU  HB3', ' D 321  PRO  HD2', -0.465, (218.878, 218.401, 237.399)), (' D 457  GLU  HG2', ' D 513  ILE  HB ', -0.464, (224.03, 213.157, 268.103)), (' D 284  PRO  HB3', ' D 594  TRP  CH2', -0.458, (232.263, 243.548, 265.067)), (' D 476  LYS  O  ', ' D 480  MET  HG2', -0.457, (227.544, 217.476, 282.753)), (' A 418  ILE HD13', ' A 422  ASN HD22', -0.448, (205.314, 192.885, 230.61)), (' A 421  TYR  CD1', ' A 457  ARG  HB3', -0.446, (208.989, 185.333, 231.956)), (' D 439  LEU  HA ', ' D 439  LEU HD23', -0.442, (228.88, 235.92, 257.832)), (' D 291  ILE  O  ', ' D 291  ILE HG13', -0.436, (219.823, 241.516, 251.659)), (' D 455  MET  HB3', ' D 455  MET  HE3', -0.436, (225.435, 220.804, 275.204)), (' D 398  GLU  HG3', ' D 514  ARG  HG2', -0.435, (221.069, 212.438, 261.158)), (' D  93  VAL HG12', ' D  97  LEU HD12', -0.435, (218.715, 190.407, 249.791)), (' D 315  PHE  HA ', ' D 318  VAL HG12', -0.43, (220.624, 224.74, 239.111)), (' A 341  VAL HG23', ' A 356  LYS  HZ2', -0.429, (193.117, 197.171, 212.008)), (' D 308  PHE  CZ ', ' D 333  LEU HD22', -0.427, (206.402, 227.776, 246.16)), (' D 336  PRO  HG2', ' D 340  GLN  O  ', -0.425, (192.719, 227.341, 252.929)), (' A 431  GLY  HA3', ' A 513  LEU  O  ', -0.423, (206.102, 196.541, 211.745)), (' D 482  ARG HH21', ' D 489  GLU  CD ', -0.416, (225.168, 226.186, 288.133)), (' D 524  GLN  HG2', ' D 583  PRO  HG2', -0.415, (235.152, 220.818, 254.305)), (' D 230  PHE  HA ', ' D 233  ILE HG22', -0.414, (234.748, 221.413, 267.495)), (' A 409  GLN  OE1', ' A 418  ILE  HB ', -0.412, (209.436, 195.97, 229.013)), (' D 209  VAL HG11', ' D 565  PRO  HB3', -0.412, (230.068, 201.901, 253.297)), (' D 403  ALA  O  ', ' D 407  ILE HG23', -0.409, (224.403, 222.233, 251.382)), (' D  96  GLN  HG2', ' D 391  LEU  HB2', -0.409, (215.427, 198.231, 249.5)), (' D 529  LEU HD21', ' D 554  LEU HD22', -0.407, (226.77, 220.888, 244.536)), (' A 355  ARG  NH2', ' A 398  ASP  OD2', -0.407, (201.812, 190.886, 215.865)), (' A 382  VAL HG11', ' A 387  LEU  HB3', -0.407, (207.749, 200.771, 204.851)), (' D 215  TYR  HE2', ' D 568  LEU HD13', -0.401, (233.771, 204.428, 247.337)), (' D 527  GLU  OE1', ' D 583  PRO  HG3', -0.401, (237.174, 222.953, 252.747))]
data['smoc'] = [('D', 27, u'THR', 0.4425780030995576, (212.33700000000002, 187.202, 243.476)), ('D', 37, u'GLU', 0.5616845682926643, (204.95200000000003, 201.465, 245.683)), ('D', 38, u'ASP', 0.5095546496078511, (201.178, 201.501, 245.38400000000001)), ('D', 45, u'LEU', 0.5107610822167359, (197.845, 211.118, 248.73499999999999)), ('D', 72, u'PHE', 0.5860233664215458, (201.251, 195.434, 255.334)), ('D', 93, u'VAL', 0.5454889844410304, (219.88600000000002, 192.783, 248.11899999999997)), ('D', 101, u'GLN', 0.5801069855774396, (214.626, 192.446, 258.585)), ('D', 141, u'CYS', 0.7459790449486379, (197.859, 231.377, 282.4)), ('D', 161, u'ARG', 0.5570661645187703, (212.954, 236.56, 281.69)), ('D', 164, u'ALA', 0.5169701582218531, (209.71699999999998, 233.038, 282.335)), ('D', 193, u'ALA', 0.6873007976807166, (217.289, 192.66299999999998, 272.59599999999995)), ('D', 198, u'ASP', 0.5725241692801835, (222.298, 200.292, 274.462)), ('D', 199, u'TYR', 0.5062937303104679, (219.78, 202.656, 272.90299999999996)), ('D', 207, u'TYR', 0.6227727192637219, (226.629, 205.94299999999998, 260.43399999999997)), ('D', 208, u'GLU', 0.6401966260904427, (227.748, 202.346, 259.98099999999994)), ('D', 226, u'VAL', 0.4970354828639066, (232.935, 214.08200000000002, 266.949)), ('D', 248, u'LEU', 0.41567029277323303, (226.257, 241.79399999999998, 276.97799999999995)), ('D', 262, u'LEU', 0.5085092973500857, (226.863, 233.80700000000002, 280.743)), ('D', 284, u'PRO', 0.5005127901192494, (229.761, 245.32200000000003, 265.146)), ('D', 291, u'ILE', 0.683514605358393, (220.772, 243.52800000000002, 251.88500000000002)), ('D', 308, u'PHE', 0.657407176491026, (209.661, 229.725, 242.296)), ('D', 315, u'PHE', 0.6559389136173288, (218.65800000000002, 225.136, 239.03)), ('D', 379, u'ILE', 0.6012254176357134, (212.785, 218.477, 245.47)), ('D', 404, u'VAL', 0.5615078188481368, (221.925, 219.813, 249.997)), ('D', 435, u'GLU', 0.5645185101833392, (230.692, 241.74499999999998, 255.232)), ('D', 453, u'THR', 0.5366990407841128, (224.26, 219.914, 270.092)), ('D', 481, u'LYS', 0.5443232170918706, (227.27899999999997, 223.21499999999997, 280.65900000000005)), ('D', 491, u'VAL', 0.5026953199668787, (219.38200000000003, 229.20999999999998, 290.568)), ('D', 508, u'ASN', 0.5678370687899378, (209.57899999999998, 213.489, 271.94599999999997)), ('D', 510, u'TYR', 0.5629294060052933, (214.336, 212.24899999999997, 268.40299999999996)), ('D', 518, u'ARG', 0.5192072374991547, (224.61599999999999, 218.834, 258.802)), ('D', 525, u'PHE', 0.5319388508079984, (230.096, 220.61299999999997, 249.916)), ('D', 529, u'LEU', 0.6544466008272177, (231.757, 223.012, 244.48200000000003)), ('D', 551, u'GLY', 0.7168358098067078, (226.32200000000003, 220.771, 238.75)), ('D', 558, u'LEU', 0.5612973371452419, (222.684, 212.948, 244.185)), ('D', 569, u'ALA', 0.551772759147484, (229.037, 209.171, 248.369)), ('D', 584, u'LEU', 0.6173109606155082, (233.993, 225.676, 258.131)), ('D', 587, u'TYR', 0.6253978087810106, (234.537, 230.319, 255.74099999999999)), ('D', 591, u'LEU', 0.45673906908156525, (235.445, 237.16, 261.21099999999996)), ('D', 606, u'TRP', 0.545145316985936, (235.795, 231.54399999999998, 281.265)), ('A', 525, u'CYS', 0.3644195970217604, (199.687, 197.464, 197.635)), ('A', 541, u'PHE', 0.6605459889892213, (208.258, 199.62800000000001, 184.329)), ('A', 543, u'PHE', 0.6990819310764539, (205.376, 196.068, 188.791)), ('A', 332, u'ILE', 0.6563624943423025, (192.03, 197.222, 194.411)), ('A', 368, u'LEU', 0.6343082412629651, (198.873, 208.316, 209.423)), ('A', 387, u'LEU', 0.7357172512655014, (206.342, 202.36200000000002, 202.53)), ('A', 391, u'CYS', 0.47154724351456123, (203.718, 195.803, 197.975)), ('A', 393, u'THR', 0.533445875694101, (201.692, 190.007, 201.17399999999998)), ('A', 399, u'SER', 0.4982359953719916, (197.631, 196.695, 219.985)), ('A', 406, u'GLU', 0.49784689372651775, (208.64499999999998, 200.638, 229.34)), ('A', 425, u'LEU', 0.6413143204973281, (210.185, 191.069, 218.94299999999998)), ('A', 447, u'GLY', 0.5994931436543732, (193.141, 203.661, 240.237)), ('A', 467, u'ASP', 0.476874813197021, (201.38200000000003, 182.555, 227.032)), ('A', 510, u'VAL', 0.4483784996255777, (201.03, 201.029, 221.56))]
data['rota'] = [('D', ' 432 ', 'ASN', 0.005862268721496897, (234.1710000000001, 245.15699999999995, 254.217)), ('D', ' 474 ', 'MET', 0.08409521220669822, (221.05399999999997, 217.213, 287.25)), ('D', ' 540 ', 'HIS', 0.13170982847020082, (231.63400000000004, 233.8899999999999, 251.813)), ('A', ' 336 ', 'CYS', 0.09684643591754138, (192.26999999999998, 199.52799999999993, 205.039)), ('A', ' 358 ', 'ILE', 0.0, (194.62, 193.38299999999992, 207.231)), ('A', ' 546 ', 'LEU', 0.03229870616423019, (209.809, 196.254, 191.435))]
data['clusters'] = [('D', '315', 1, 'side-chain clash\nsmoc Outlier', (220.624, 224.74, 239.111)), ('D', '318', 1, 'side-chain clash', (220.624, 224.74, 239.111)), ('D', '320', 1, 'side-chain clash', (218.878, 218.401, 237.399)), ('D', '321', 1, 'side-chain clash', (218.878, 218.401, 237.399)), ('D', '402', 1, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1', (219.654, 219.21399999999997, 254.77899999999997)), ('D', '403', 1, 'side-chain clash', (224.403, 222.233, 251.382)), ('D', '404', 1, 'smoc Outlier', (221.925, 219.813, 249.997)), ('D', '406', 1, 'Dihedral angle:CB:CG:CD:OE1', (221.19, 224.499, 252.63)), ('D', '407', 1, 'side-chain clash', (224.403, 222.233, 251.382)), ('D', '432', 1, 'Rotamer', (234.1710000000001, 245.15699999999995, 254.217)), ('D', '435', 1, 'smoc Outlier', (230.692, 241.74499999999998, 255.232)), ('D', '439', 1, 'side-chain clash', (228.88, 235.92, 257.832)), ('D', '518', 1, 'side-chain clash\nDihedral angle:CD:NE:CZ:NH1\nsmoc Outlier', (224.61599999999999, 218.834, 258.802)), ('D', '524', 1, 'side-chain clash', (235.152, 220.818, 254.305)), ('D', '525', 1, 'smoc Outlier', (230.096, 220.61299999999997, 249.916)), ('D', '527', 1, 'side-chain clash', (237.174, 222.953, 252.747)), ('D', '529', 1, 'side-chain clash\nsmoc Outlier', (226.77, 220.888, 244.536)), ('D', '540', 1, 'Rotamer', (231.63400000000004, 233.8899999999999, 251.813)), ('D', '551', 1, 'smoc Outlier', (226.32200000000003, 220.771, 238.75)), ('D', '554', 1, 'side-chain clash', (226.77, 220.888, 244.536)), ('D', '583', 1, 'side-chain clash', (237.174, 222.953, 252.747)), ('D', '584', 1, 'smoc Outlier', (233.993, 225.676, 258.131)), ('D', '587', 1, 'smoc Outlier', (234.537, 230.319, 255.74099999999999)), ('D', '589', 1, 'Dihedral angle:CB:CG:CD:OE1', (238.517, 233.463, 258.638)), ('D', '591', 1, 'smoc Outlier', (235.445, 237.16, 261.21099999999996)), ('D', '245', 2, 'Dihedral angle:CD:NE:CZ:NH1', (229.76899999999998, 238.45100000000002, 276.952)), ('D', '247', 2, 'side-chain clash', (227.797, 241.989, 272.311)), ('D', '248', 2, 'smoc Outlier', (226.257, 241.79399999999998, 276.97799999999995)), ('D', '252', 2, 'Dihedral angle:CA:C', (222.49800000000002, 244.125, 281.97099999999995)), ('D', '253', 2, 'Dihedral angle:N:CA', (224.767, 246.4, 283.99699999999996)), ('D', '261', 2, 'side-chain clash', (228.715, 230.338, 283.339)), ('D', '262', 2, 'smoc Outlier', (226.863, 233.80700000000002, 280.743)), ('D', '282', 2, 'side-chain clash', (227.797, 241.989, 272.311)), ('D', '488', 2, 'side-chain clash', (228.715, 230.338, 283.339)), ('D', '224', 3, 'cablam Outlier', (235.6, 209.8, 267.9)), ('D', '225', 3, 'Dihedral angle:CA:CB:CG:OD1\ncablam Outlier', (235.80800000000002, 212.35600000000002, 265.14900000000006)), ('D', '226', 3, 'smoc Outlier', (232.935, 214.08200000000002, 266.949)), ('D', '227', 3, 'Dihedral angle:CB:CG:CD:OE1', (235.591, 214.95700000000002, 269.546)), ('D', '230', 3, 'side-chain clash', (234.748, 221.413, 267.495)), ('D', '232', 3, 'Dihedral angle:CB:CG:CD:OE1', (239.446, 221.905, 266.546)), ('D', '233', 3, 'side-chain clash', (234.748, 221.413, 267.495)), ('D', '453', 4, 'smoc Outlier', (224.26, 219.914, 270.092)), ('D', '455', 4, 'side-chain clash', (225.435, 220.804, 275.204)), ('D', '476', 4, 'side-chain clash', (227.544, 217.476, 282.753)), ('D', '479', 4, 'Dihedral angle:CB:CG:CD:OE1', (228.935, 220.545, 284.977)), ('D', '480', 4, 'side-chain clash', (227.544, 217.476, 282.753)), ('D', '481', 4, 'smoc Outlier', (227.27899999999997, 223.21499999999997, 280.65900000000005)), ('D', '483', 4, 'Dihedral angle:CB:CG:CD:OE1', (232.916, 223.156, 280.734)), ('D', '423', 5, 'cablam CA Geom Outlier', (216.3, 243.5, 241.9)), ('D', '424', 5, 'cablam Outlier', (219.2, 244.8, 243.9)), ('D', '425', 5, 'Dihedral angle:CA:C', (219.88100000000003, 248.056, 241.947)), ('D', '426', 5, 'Dihedral angle:N:CA', (222.983, 247.686, 239.8)), ('D', '427', 5, 'cablam Outlier', (225.8, 249.8, 241.3)), ('D', '428', 5, 'cablam Outlier', (225.7, 248.8, 245.0)), ('D', '189', 6, 'Dihedral angle:CB:CG:CD:OE1', (216.053, 196.73, 277.075)), ('D', '192', 6, 'Dihedral angle:CD:NE:CZ:NH1', (219.634, 195.262, 274.079)), ('D', '193', 6, 'smoc Outlier', (217.289, 192.66299999999998, 272.59599999999995)), ('D', '198', 6, 'smoc Outlier', (222.298, 200.292, 274.462)), ('D', '215', 7, 'side-chain clash', (233.771, 204.428, 247.337)), ('D', '568', 7, 'side-chain clash', (233.771, 204.428, 247.337)), ('D', '569', 7, 'smoc Outlier', (229.037, 209.171, 248.369)), ('D', '160', 8, 'Dihedral angle:CB:CG:CD:OE1', (210.966, 239.012, 283.789)), ('D', '161', 8, 'smoc Outlier', (212.954, 236.56, 281.69)), ('D', '164', 8, 'smoc Outlier', (209.71699999999998, 233.038, 282.335)), ('D', '269', 9, 'backbone clash', (214.992, 230.299, 273.437)), ('D', '270', 9, 'backbone clash', (214.992, 230.299, 273.437)), ('D', '273', 9, 'Dihedral angle:CD:NE:CZ:NH1', (219.993, 227.003, 271.534)), ('D', '482', 10, 'side-chain clash', (225.168, 226.186, 288.133)), ('D', '489', 10, 'side-chain clash', (225.168, 226.186, 288.133)), ('D', '491', 10, 'smoc Outlier', (219.38200000000003, 229.20999999999998, 290.568)), ('D', '168', 11, 'side-chain clash', (211.467, 222.967, 278.512)), ('D', '169', 11, 'Dihedral angle:CD:NE:CZ:NH1', (212.01899999999998, 224.57399999999998, 284.16)), ('D', '502', 11, 'side-chain clash', (211.467, 222.967, 278.512)), ('D', '206', 12, 'Dihedral angle:CA:CB:CG:OD1', (223.01399999999998, 204.94299999999998, 261.15000000000003)), ('D', '207', 12, 'smoc Outlier', (226.629, 205.94299999999998, 260.43399999999997)), ('D', '208', 12, 'smoc Outlier', (227.748, 202.346, 259.98099999999994)), ('D', '204', 13, 'backbone clash', (228.534, 204.597, 268.02)), ('D', '219', 13, 'backbone clash', (228.534, 204.597, 268.02)), ('D', '336', 14, 'backbone clash', (192.719, 227.341, 252.929)), ('D', '340', 14, 'backbone clash', (192.719, 227.341, 252.929)), ('D', '284', 15, 'side-chain clash\nsmoc Outlier', (232.263, 243.548, 265.067)), ('D', '594', 15, 'side-chain clash', (232.263, 243.548, 265.067)), ('D', '56', 16, 'Dihedral angle:CB:CG:CD:OE1', (186.459, 216.553, 259.16200000000003)), ('D', '57', 16, 'cablam Outlier', (186.3, 213.0, 257.7)), ('D', '375', 17, 'Dihedral angle:CB:CG:CD:OE1', (212.659, 223.48700000000002, 249.399)), ('D', '379', 17, 'smoc Outlier', (212.785, 218.477, 245.47)), ('D', '187', 18, 'side-chain clash', (215.626, 203.954, 273.684)), ('D', '199', 18, 'side-chain clash\nsmoc Outlier', (215.626, 203.954, 273.684)), ('D', '177', 19, 'side-chain clash\nDihedral angle:CD:NE:CZ:NH1', (211.07299999999998, 213.494, 285.869)), ('D', '178', 19, 'side-chain clash', (209.983, 213.857, 287.715)), ('D', '391', 20, 'side-chain clash', (215.427, 198.231, 249.5)), ('D', '96', 20, 'side-chain clash', (215.427, 198.231, 249.5)), ('D', '111', 21, 'Dihedral angle:CA:CB:CG:OD1', (202.577, 193.948, 278.24)), ('D', '115', 21, 'Dihedral angle:CD:NE:CZ:NH1', (203.26999999999998, 200.818, 278.815)), ('D', '398', 22, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1', (220.553, 211.266, 257.765)), ('D', '514', 22, 'side-chain clash', (221.069, 212.438, 261.158)), ('D', '85', 23, 'side-chain clash', (224.727, 188.043, 254.11)), ('D', '94', 23, 'side-chain clash', (224.727, 188.043, 254.11)), ('D', '308', 24, 'side-chain clash\nsmoc Outlier', (206.402, 227.776, 246.16)), ('D', '333', 24, 'side-chain clash', (206.402, 227.776, 246.16)), ('D', '37', 25, 'smoc Outlier', (204.95200000000003, 201.465, 245.683)), ('D', '38', 25, 'smoc Outlier', (201.178, 201.501, 245.38400000000001)), ('D', '32', 26, 'side-chain clash', (206.797, 193.395, 251.277)), ('D', '76', 26, 'side-chain clash', (206.797, 193.395, 251.277)), ('D', '508', 27, 'smoc Outlier', (209.57899999999998, 213.489, 271.94599999999997)), ('D', '510', 27, 'smoc Outlier', (214.336, 212.24899999999997, 268.40299999999996)), ('D', '457', 28, 'side-chain clash', (224.03, 213.157, 268.103)), ('D', '513', 28, 'side-chain clash', (224.03, 213.157, 268.103)), ('D', '209', 29, 'side-chain clash', (230.068, 201.901, 253.297)), ('D', '565', 29, 'side-chain clash', (230.068, 201.901, 253.297)), ('D', '90', 30, 'Bond angle:C', (225.224, 190.74399999999997, 246.146)), ('D', '91', 30, 'Bond angle:N:CA\ncablam Outlier', (225.54, 193.69899999999998, 248.638)), ('D', '93', 31, 'side-chain clash\nsmoc Outlier', (218.715, 190.407, 249.791)), ('D', '97', 31, 'side-chain clash', (218.715, 190.407, 249.791)), ('D', '72', 32, 'smoc Outlier', (201.251, 195.434, 255.334)), ('D', '75', 32, 'Dihedral angle:CB:CG:CD:OE1', (203.54399999999998, 191.282, 257.78)), ('A', '329', 1, 'side-chain clash', (203.331, 202.846, 192.257)), ('A', '362', 1, 'side-chain clash', (197.421, 200.77, 197.281)), ('A', '364', 1, 'Dihedral angle:CA:CB:CG:OD1', (197.617, 205.131, 202.89800000000002)), ('A', '389', 1, 'cablam Outlier', (204.2, 202.9, 197.7)), ('A', '391', 1, 'smoc Outlier', (203.718, 195.803, 197.975)), ('A', '525', 1, 'smoc Outlier', (199.687, 197.464, 197.635)), ('A', '526', 1, 'side-chain clash\ncablam CA Geom Outlier', (197.421, 200.77, 197.281)), ('A', '527', 1, 'cablam CA Geom Outlier', (198.2, 203.7, 196.9)), ('A', '528', 1, 'side-chain clash\ncablam Outlier', (203.331, 202.846, 192.257)), ('A', '336', 2, 'Rotamer', (192.26999999999998, 199.52799999999993, 205.039)), ('A', '341', 2, 'side-chain clash', (193.117, 197.171, 212.008)), ('A', '356', 2, 'side-chain clash', (193.117, 197.171, 212.008)), ('A', '357', 2, 'Dihedral angle:CD:NE:CZ:NH1', (195.524, 190.79899999999998, 209.89600000000002)), ('A', '358', 2, 'Rotamer', (194.62, 193.38299999999992, 207.231)), ('A', '405', 3, 'Dihedral angle:CA:CB:CG:OD1', (208.702, 204.13899999999998, 230.865)), ('A', '406', 3, 'Dihedral angle:CB:CG:CD:OE1\nsmoc Outlier', (208.64499999999998, 200.638, 229.34)), ('A', '409', 3, 'side-chain clash', (209.436, 195.97, 229.013)), ('A', '418', 3, 'side-chain clash', (209.436, 195.97, 229.013)), ('A', '422', 3, 'side-chain clash', (205.314, 192.885, 230.61)), ('A', '541', 4, 'smoc Outlier', (208.258, 199.62800000000001, 184.329)), ('A', '543', 4, 'smoc Outlier', (205.376, 196.068, 188.791)), ('A', '546', 4, 'Rotamer', (209.809, 196.254, 191.435)), ('A', '368', 5, 'smoc Outlier', (198.873, 208.316, 209.423)), ('A', '371', 5, 'cablam CA Geom Outlier', (198.5, 212.8, 212.2)), ('A', '372', 5, 'cablam Outlier', (201.0, 214.2, 214.7)), ('A', '484', 6, 'cablam CA Geom Outlier', (200.0, 180.5, 246.9)), ('A', '485', 6, 'cablam Outlier', (201.6, 181.5, 250.1)), ('A', '486', 6, 'cablam Outlier', (205.3, 181.3, 251.0)), ('A', '578', 7, 'backbone clash', (199.309, 188.706, 183.131)), ('A', '583', 7, 'backbone clash', (199.309, 188.706, 183.131)), ('A', '421', 8, 'side-chain clash', (208.989, 185.333, 231.956)), ('A', '457', 8, 'side-chain clash', (208.989, 185.333, 231.956)), ('A', '393', 9, 'side-chain clash\nsmoc Outlier', (199.095, 190.342, 201.518)), ('A', '523', 9, 'side-chain clash', (199.095, 190.342, 201.518)), ('A', '399', 10, 'smoc Outlier', (197.631, 196.695, 219.985)), ('A', '510', 10, 'smoc Outlier', (201.03, 201.029, 221.56)), ('A', '355', 11, 'side-chain clash', (201.812, 190.886, 215.865)), ('A', '398', 11, 'side-chain clash', (201.812, 190.886, 215.865)), ('A', '503', 12, 'side-chain clash', (202.945, 211.017, 232.589)), ('A', '506', 12, 'side-chain clash', (202.945, 211.017, 232.589)), ('A', '382', 13, 'side-chain clash', (207.749, 200.771, 204.851)), ('A', '387', 13, 'side-chain clash\nsmoc Outlier', (207.749, 200.771, 204.851)), ('A', '431', 14, 'backbone clash', (206.102, 196.541, 211.745)), ('A', '513', 14, 'backbone clash', (206.102, 196.541, 211.745))]
data['omega'] = [('A', ' 527 ', 'PRO', None, (198.933, 203.51299999999992, 198.13)), ('D', ' 146 ', 'PRO', None, (202.41499999999994, 231.39199999999997, 271.655))]
data['cablam'] = [('D', '57', 'GLU', 'check CA trace,carbonyls, peptide', 'bend\n-SSHH', (186.3, 213.0, 257.7)), ('D', '91', 'LEU', 'check CA trace,carbonyls, peptide', 'bend\n-SSSH', (225.5, 193.7, 248.6)), ('D', '144', 'LEU', 'check CA trace,carbonyls, peptide', 'helix-5\nB-III', (204.6, 228.0, 275.4)), ('D', '224', 'GLU', ' alpha helix', 'helix\nTHHHH', (235.6, 209.8, 267.9)), ('D', '225', 'ASP', ' alpha helix', 'helix\nHHHHH', (235.8, 212.4, 265.1)), ('D', '267', 'LEU', 'check CA trace,carbonyls, peptide', 'bend\nGGSSS', (221.3, 233.8, 275.6)), ('D', '303', 'ASP', 'check CA trace,carbonyls, peptide', ' \nT--SS', (203.1, 237.6, 242.4)), ('D', '334', 'THR', 'check CA trace,carbonyls, peptide', 'bend\n--S--', (199.7, 230.1, 248.2)), ('D', '424', 'LEU', 'check CA trace,carbonyls, peptide', 'bend\nS-S-S', (219.2, 244.8, 243.9)), ('D', '427', 'ASP', 'check CA trace,carbonyls, peptide', ' \n-S---', (225.8, 249.8, 241.3)), ('D', '428', 'PHE', 'check CA trace,carbonyls, peptide', ' \nS----', (225.7, 248.8, 245.0)), ('D', '602', 'SER', 'check CA trace,carbonyls, peptide', 'bend\nGGS--', (238.7, 242.0, 277.2)), ('D', '353', 'LYS', 'check CA trace', 'turn\nEETTE', (204.9, 207.3, 241.3)), ('D', '423', 'LEU', 'check CA trace', ' \nSS-S-', (216.3, 243.5, 241.9)), ('A', '372', 'ALA', 'check CA trace,carbonyls, peptide', ' \nHT---', (201.0, 214.2, 214.7)), ('A', '389', 'ASP', 'check CA trace,carbonyls, peptide', 'helix-3\nGGG-E', (204.2, 202.9, 197.7)), ('A', '442', 'ASP', 'check CA trace,carbonyls, peptide', 'helix\nHHH--', (192.0, 205.1, 230.6)), ('A', '477', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n-SSS-', (212.2, 174.1, 246.0)), ('A', '485', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\n--SSS', (201.6, 181.5, 250.1)), ('A', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\n-SSSE', (205.3, 181.3, 251.0)), ('A', '528', 'LYS', 'check CA trace,carbonyls, peptide', ' \n-S---', (199.4, 204.5, 193.4)), ('A', '371', 'SER', 'check CA trace', 'turn\nHHT--', (198.5, 212.8, 212.2)), ('A', '484', 'GLU', 'check CA trace', ' \nT--SS', (200.0, 180.5, 246.9)), ('A', '526', 'GLY', 'check CA trace', ' \nEE-S-', (199.0, 201.2, 197.5)), ('A', '527', 'PRO', 'check CA trace', 'bend\nE-S--', (198.2, 203.7, 196.9))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-11681/7a91/Model_validation_1/validation_cootdata/molprobity_probe7a91_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)
