#!/usr/bin/env python3
# Copyright (C) 2013-2014 Florian Festi
# Copyright (C) 2022 Bjorn Bringert
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from boxes import *

# Tiny 2040 with 12 mm pushbutton on Sparkfun 08808 1" protoboard
#
# x=26
# y=26
# h=15.5
# outside=False
# usbc_offset_x=1.27
# usbc_offset_y=0.4
# button_count=1
# button_w=10
# button_h=10
# button_margin=0.25
# button_corner_radius=1
# button_offset_x=1.27
# button_offset_y=-2.12
#
# thickness=2.31
# burn=0.14

# RPI2040 + NeoKey Featherwing box:
#
# x=24.2
# y=51.66
# h=15
# outside=False
#
# thickness=2.31
# burn=0.14

class ClosedBoxWithHoles(Boxes):
    """Fully closed box with USB-C connector and button hole"""

    ui_group = "Box"

    description = """."""

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser("x", "y", "h", "outside")
        self.argparser.add_argument(
            "--usbc_angle", action="store", type=float, default=0,
            help="angle of the connector hole (0°=horizontal)")
        self.argparser.add_argument(
            "--usbc_margin", action="store", type=float, default=0.1,
            help="space around the connector (in mm)")
        self.argparser.add_argument(
            "--usbc_offset_x", action="store", type=float, default=-1.27,
            help="USB-C connector hole horizontal offset from center (in mm)")
        self.argparser.add_argument(
            "--usbc_offset_y", action="store", type=float, default=1.5,
            help="USB-C connector hole vertical offset from inside bottom (in mm)")
        self.argparser.add_argument(
            "--button_count", action="store", type=int, default=2,
            help="Number of buttons")
        self.argparser.add_argument(
            "--button_w", action="store", type=float, default=14,
            help="Button width (in mm)")
        self.argparser.add_argument(
            "--button_h", action="store", type=float, default=14,
            help="Button height (in mm)")
        self.argparser.add_argument(
            "--button_margin", action="store", type=float, default=0.05,
            help="Space on each side of the button (in mm)")
        self.argparser.add_argument(
            "--button_corner_radius", action="store", type=float, default=0,
            help="Radius of button corners (in mm)")
        self.argparser.add_argument(
            "--button_offset_x", action="store", type=float, default=1,
            help="Button offset from box center in x dimension (in mm)")
        self.argparser.add_argument(
            "--button_offset_y", action="store", type=float, default=0,
            help="Button offset from box center in y dimension (in mm)")
        self.argparser.add_argument(
            "--button_cc_distance_y", action="store", type=float, default=18.85,
            help="Button center-to-center distance in y dimension (in mm)")

    def render(self):

        x, y, h = self.x, self.y, self.h

        if self.outside:
            x = self.adjustSize(x)
            y = self.adjustSize(y)
            h = self.adjustSize(h)

        t = self.thickness

        def add_usb_hole(side):
          if side == 0:
            hole_x_center = x/2 + self.usbc_offset_x
            self.usbcConnectorHole(hole_x_center, self.usbc_offset_y, self.usbc_margin, self.usbc_angle)

        def add_button_holes(side):
          if side == 0:
            hole_w = self.button_w + 2 * self.button_margin
            hole_h = self.button_h + 2 * self.button_margin
            hole_r = self.button_corner_radius
            hole_cc_dist = self.button_cc_distance_y
            first_hole_center_x = x/2 + self.button_offset_x
            buttons_total_height = (self.button_count - 1) * hole_cc_dist + hole_h
            first_hole_start_y = (y - buttons_total_height)/2 + self.button_offset_y
            for i in range(self.button_count):
                hole_x_center = first_hole_center_x
                hole_y_bottom = first_hole_start_y + i * hole_cc_dist
                self.rectangularHole(hole_x_center, hole_y_bottom, hole_w, hole_h, hole_r, center_x=True, center_y=False)

        self.rectangularWall(x, h, "FFFF", move="right", label="Wall 1", callback=add_usb_hole)
        self.rectangularWall(y, h, "FfFf", move="up", label="Wall 2")
        self.rectangularWall(y, h, "FfFf", label="Wall 4")
        self.rectangularWall(x, h, "FFFF", move="left up", label="Wall 3")

        self.rectangularWall(x, y, "ffff", move="right", label="Top", callback=add_button_holes)
        self.rectangularWall(x, y, "ffff", label="Bottom")

    def usbcConnectorHole(self, x_center, bottom_y, margin, angle=0):
        # Connector measurements. Make these arguments?
        connector_width = 8.94
        connector_height = 3.26
        connector_corner_radius = 1.28

        w = connector_width + 2 * margin
        h = connector_height + 2 * margin
        r = connector_corner_radius + margin

        self.moveTo(x_center, bottom_y, angle)
        self.rectangularHole(0, 0, w, h, r, center_x=True, center_y=False)
