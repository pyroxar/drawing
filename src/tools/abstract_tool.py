# tools.py
#
# Super-class implemented and extended by all tools.

from gi.repository import Gtk, Gdk
import cairo

from .utilities import utilities_show_overlay_on_context

class ToolTemplate():
	__gtype_name__ = 'ToolTemplate'

	def __init__(self, tool_id, label, icon_name, window, **kwargs):
		self.id = tool_id
		self.implements_panel = False
		self.accept_selection = False
		self.use_color = True
		self.menu_id = 0
		self.label = label
		self.icon_name = icon_name
		self.tool_width = 10
		self.cursor_name = 'cell'
		self.use_size = False
		self.has_ongoing_operation = False # TODO
		self.window = window
		self.build_row()

	# Actions

	def add_tool_action_simple(self, action_name, callback):
		"""Convenient wrapper method adding a stateless action to the window. It
		will be named 'action_name' (string) and activating the action will
		trigger the method 'callback'."""
		self.window.add_action_simple(action_name, callback, None) # XXX shortcut ?

	def add_tool_action_boolean(self, action_name, default):
		self.window.options_manager.add_tool_option_boolean(action_name, default)

	def add_tool_action_enum(self, action_name, default):
		self.window.options_manager.add_tool_option_enum(action_name, default)

	def get_option_value(self, action_name):
		return self.window.options_manager.get_value(action_name)

	def set_action_sensitivity(self, action_name, state):
		self.get_image().set_action_sensitivity(action_name, state)

	def update_actions_state(self):
		pass

	# UI

	def show_error(self, text):
		self.window.prompt_message(True, text)

	def show_panel(self, visibility):
		if self.implements_panel:
			self.window.bottom_panel.set_visible(not visibility)
			self.bottom_panel.set_visible(visibility)
		else:
			self.window.bottom_panel.set_visible(True)

	def add_item_to_menu(self, tools_menu):
		tools_menu.append(self.label, 'win.active_tool::' + self.id)

	def get_options_model(self):
		builder = Gtk.Builder.new_from_resource( \
		       '/com/github/maoschanz/drawing/tools/ui/tool_' + self.id + '.ui')
		return builder.get_object('options-menu')

	def get_options_widget(self):
		return None

	def get_edition_status(self):
		return self.label

	def get_options_label(self):
		return _("No options")

	def build_row(self):
		"""Build the GtkRadioButton for the sidebar. This method stores it as
		'self.row', but does not pack it in the bar, and does not return it."""
		self.row = Gtk.RadioButton(draw_indicator=False, \
		                   tooltip_text=self.label, relief=Gtk.ReliefStyle.NONE)
		self.row.set_detailed_action_name('win.active_tool::' + self.id)
		self.label_widget = Gtk.Label(label=self.label)
		if self.window.decorations == 'csd-eos':
			self.row.set_border_width(6)
		image = Gtk.Image().new_from_icon_name(self.icon_name, Gtk.IconSize.SMALL_TOOLBAR)
		box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
		box.add(image)
		box.add(self.label_widget)
		self.row.add(box)
		self.row.show_all()

	def adapt_to_window_size(self, available_width):
		pass

	# Activation or not

	def on_tool_selected(self):
		pass

	def on_tool_unselected(self):
		pass

	def cancel_ongoing_operation(self):
		pass

	def give_back_control(self, preserve_selection):
		self.restore_pixbuf()
		self.non_destructive_show_modif()

	# History

	def do_tool_operation(self, operation):
		pass

	def apply_operation(self, operation):
		self.do_tool_operation(operation)
		self.non_destructive_show_modif()
		self.apply_to_pixbuf()
		self.get_image().add_operation_to_history(operation)

	# Selection

	def get_selection(self):
		return self.get_image().selection

	def selection_is_active(self):
		return self.get_selection().is_active

	def get_selection_pixbuf(self):
		return self.get_selection().get_pixbuf()

	def set_selection_has_been_used(self, state):
		self.get_selection().has_been_used = state

	def selection_has_been_used(self):
		return self.get_selection().has_been_used

	# Image management

	def get_image(self):
		return self.window.get_active_image()

	def get_surface(self):
		return self.get_image().get_surface()

	def get_main_pixbuf(self):
		return self.get_image().get_main_pixbuf()

	def non_destructive_show_modif(self):
		self.get_image().update()

	def restore_pixbuf(self):
		self.get_image().use_stable_pixbuf()

	def apply_to_pixbuf(self):
		self.get_image().on_tool_finished()

	# Signals handling

	def on_press_on_area(self, area, event, surface, tool_width, lc, rc, e_x, e_y):
		pass

	def on_motion_on_area(self, area, event, surface, event_x, event_y):
		pass

	def on_unclicked_motion_on_area(self, event, surface):
		pass

	def on_release_on_area(self, area, event, surface, event_x, event_y):
		pass

	def on_draw(self, area, cairo_context):
		if not self.accept_selection:
			return
		# Very basic implementation
		if self.selection_is_active():
			Gdk.cairo_set_source_pixbuf(cairo_context, \
			                            self.get_selection_pixbuf(), \
			                            self.get_selection().selection_x, \
			                            self.get_selection().selection_y) # FIXME le scroll ptn
			cairo_context.paint()
			utilities_show_overlay_on_context(cairo_context, \
			                self.get_image().get_dragged_selection_path(), True)


