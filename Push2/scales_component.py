# uncompyle6 version 3.9.1
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.12.2 (main, Feb  6 2024, 20:19:44) [Clang 15.0.0 (clang-1500.1.0.2.5)]
# Embedded file name: output/Live/mac_universal_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/scales_component.py
# Compiled at: 2024-03-09 01:30:22
# Size of source mod 2**32: 7455 bytes
from __future__ import absolute_import, print_function, unicode_literals
from past.utils import old_div
from collections import namedtuple
from functools import partial
from math import ceil
from ableton.v2.base import clamp, index_if, listenable_property, listens
from ableton.v2.control_surface import Component
from ableton.v2.control_surface.control import ButtonControl, RadioButtonControl, StepEncoderControl, ToggleButtonControl, control_list
from pushbase.melodic_pattern import NOTE_NAMES, ROOT_NOTES, SCALES
Layout = namedtuple("Layout", ('name', 'interval'))

class ScalesComponent(Component):
    navigation_colors = dict(color="Scales.Navigation",
      disabled_color="Scales.NavigationDisabled")
    up_button = ButtonControl(repeat=True, **navigation_colors)
    down_button = ButtonControl(repeat=True, **navigation_colors)
    right_button = ButtonControl(repeat=True, **navigation_colors)
    left_button = ButtonControl(repeat=True, **navigation_colors)
    root_note_buttons = control_list(RadioButtonControl,
      control_count=(len(ROOT_NOTES)),
      checked_color="Scales.OptionOn",
      unchecked_color="Scales.OptionOff")
    in_key_toggle_button = ToggleButtonControl(toggled_color="Scales.OptionOn",
      untoggled_color="Scales.OptionOn")
    fixed_toggle_button = ToggleButtonControl(toggled_color="Scales.OptionOn",
      untoggled_color="Scales.OptionOff")
    scale_encoders = control_list(StepEncoderControl)
    layout_encoder = StepEncoderControl()
    direction_encoder = StepEncoderControl()
    horizontal_navigation = listenable_property.managed(False)
    NUM_DISPLAY_ROWS = 4
    NUM_DISPLAY_COLUMNS = int(ceil(old_div(float(len(SCALES)), NUM_DISPLAY_ROWS)))

    def __init__(self, note_layout=None, *a, **k):
        (super(ScalesComponent, self).__init__)(*a, **k)
        self._note_layout = note_layout
        self._scale_list = list(SCALES)
        self._scale_name_list = [m.name for m in self._scale_list]
        self._selected_scale_index = -1
        self._selected_root_note_index = -1
        self._layouts = (Layout("5ths", 4), Layout("4ths", 3), Layout("3rds", 2), Layout("2nds", 1), Layout("Sequential", None))
        self._selected_layout_index = 0
        self.in_key_toggle_button.connect_property(note_layout, "is_in_key")
        self.fixed_toggle_button.connect_property(note_layout, "is_fixed")
        self._ScalesComponent__on_root_note_changed.subject = self._note_layout
        self._ScalesComponent__on_scale_changed.subject = self._note_layout
        self._ScalesComponent__on_interval_changed.subject = self._note_layout
        self._ScalesComponent__on_root_note_changed(note_layout.root_note)
        self._ScalesComponent__on_scale_changed(note_layout.scale)
        self._ScalesComponent__on_interval_changed(self._note_layout.interval)

    def _set_selected_scale_index(self, index):
        index = clamp(index, 0, len(self._scale_list) - 1)
        self._note_layout.scale = self._scale_list[index]

    @down_button.pressed
    def down_button(self, button):
        self._update_horizontal_navigation()
        self._set_selected_scale_index(self._selected_scale_index + 1)

    @up_button.pressed
    def up_button(self, button):
        self._update_horizontal_navigation()
        self._set_selected_scale_index(self._selected_scale_index - 1)

    @left_button.pressed
    def left_button(self, button):
        self._update_horizontal_navigation()
        self._set_selected_scale_index(self._selected_scale_index - self.NUM_DISPLAY_ROWS)

    @right_button.pressed
    def right_button(self, button):
        self._update_horizontal_navigation()
        self._set_selected_scale_index(self._selected_scale_index + self.NUM_DISPLAY_ROWS)

    @root_note_buttons.pressed
    def root_note_buttons(self, button):
        self._note_layout.root_note = ROOT_NOTES[button.index]

    @listens("root_note")
    def __on_root_note_changed(self, root_note):
        self._selected_root_note_index = list(ROOT_NOTES).index(root_note)
        self.root_note_buttons.checked_index = self._selected_root_note_index
        self.notify_selected_root_note_index()

    @property
    def root_note_names(self):
        return [NOTE_NAMES[note] for note in ROOT_NOTES]

    @listenable_property
    def selected_root_note_index(self):
        return self._selected_root_note_index

    @scale_encoders.value
    def scale_encoders(self, value, encoder):
        self._update_horizontal_navigation()
        self._set_selected_scale_index(self._selected_scale_index + value)

    @property
    def scale_names(self):
        return self._scale_name_list

    @listenable_property
    def selected_scale_index(self):
        return self._selected_scale_index

    @listens("scale")
    def __on_scale_changed(self, scale):
        index = self._scale_list.index(scale) if scale in self._scale_list else -1
        if index != self._selected_scale_index:
            self._selected_scale_index = index
            self.up_button.enabled = index > 0
            self.left_button.enabled = index > 0
            self.down_button.enabled = index < len(self._scale_list) - 1
            self.right_button.enabled = index < len(self._scale_list) - 1
            self.notify_selected_scale_index()

    @layout_encoder.value
    def layout_encoder(self, value, encoder):
        index = clamp(self._selected_layout_index + value, 0, len(self._layouts) - 1)
        self.selected_layout_index = index

    @property
    def layout_names(self):
        return [layout.name for layout in self._layouts]

    @listenable_property
    def selected_layout_index(self):
        return self._selected_layout_index

    @selected_layout_index.setter
    def selected_layout_index(self, index):
        if index != self._selected_layout_index:
            self._selected_layout_index = index
            interval = self._layouts[index].interval
            self._note_layout.interval = interval
            self.notify_selected_layout_index()

    @direction_encoder.value
    def direction_encoder(self, value, encoder):
        self._note_layout.is_horizontal = value < 0

    @property
    def note_layout(self):
        return self._note_layout

    def _update_horizontal_navigation(self):
        self.horizontal_navigation = self.right_button.is_pressed or self.left_button.is_pressed

    @listens("interval")
    def __on_interval_changed(self, interval):
        index = index_if((lambda layout: layout.interval == interval), self._layouts)
        self.selected_layout_index = index


class ScalesEnabler(Component):
    toggle_button = ButtonControl(color="DefaultButton.On")

    def __init__(self, enter_dialog_mode=None, exit_dialog_mode=None, *a, **k):
        (super(ScalesEnabler, self).__init__)(*a, **k)
        self._enable_dialog_mode = partial(enter_dialog_mode, "scales")
        self._exit_dialog_mode = partial(exit_dialog_mode, "scales")

    @toggle_button.pressed
    def toggle_button(self, button):
        self._enable_dialog_mode()

    @toggle_button.released_delayed
    def toggle_button(self, button):
        self._exit_dialog_mode()

    def on_enabled_changed(self):
        super(ScalesEnabler, self).on_enabled_changed()
        if not self.is_enabled():
            self._exit_dialog_mode()
