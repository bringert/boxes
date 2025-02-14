#!/usr/bin/env python3
# Copyright (C) 2013-2014 Florian Festi
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
import math, copy

class BinFrontEdge(edges.BaseEdge):
    char = "B"
    def __call__(self, length, **kw):
        f = self.settings.front
        # a1: the angle of the straight edge where the hole is
        a1 = math.degrees(math.atan(math.tan(math.radians(self.angle)) * f/(1-f)))
        # a2: the angle between the extension of the straight edge and
        # the front finger joint edge
        a2 = self.angle + a1
        self.corner(-a1)
        for i, l in enumerate(self.settings.sy):
            # Distance to corner at upper edge of front wall
            el = l * (1 - f) / math.cos(math.radians(a1))
            if self.curved:
                # Relative depth of the cutaway
                c1 = 2.0
                # Size of the opening
                c2 = 0.5
                ep = el * math.tan(math.radians(a1))
                # Curved edge for the hole part
                self.curveTo(c1 * el, c1 * ep, c2 * el, 0, el, 0)
            else:
                # The straight edge for the hole part
                self.edges["e"](el)

            self.corner(a2)
            # The finger joint edge holding the front wall
            self.edges["f"](l * f / math.cos(math.radians(self.angle)))
            if i < len(self.settings.sy)-1:
                if self.char == "B":
                    # Inner wall, add a slot for the shelf
                    self.polyline(
                        # Turn to horizontal to start the slot
                        0, 90 - self.angle,
                        0.5*self.settings.hi, -90,
                        self.thickness, -90,
                        0.5*self.settings.hi, 90-a1)
                else:
                    # Outer wall, add a slot for the shelf
                    self.polyline(0, -self.angle, self.thickness, -a1)
            else:
                # Finished the last section, turn back to vertical
                self.corner(-self.angle)

    def curveToDebug(self, x1, y1, x2, y2, x3, y3):
      self.circle(0, 0, 2)
      self.circle(x1, y1, 2)
      self.circle(x2, y2, 2)
      self.circle(x3, y3, 2)
      self.curveTo(x1, y1, x2, y2, x3, y3)

    def margin(self):
        hf = self.settings.front * math.tan(math.radians(self.angle))
        # Add thickness to cover finger length when angle is small
        return max(self.settings.sy) * hf + self.settings.thickness

class BinFrontSideEdge(BinFrontEdge):
    char = 'b'

class MagazineRack(Boxes):
    """A wall mounted rack for laptops, magazines or documents"""

    ui_group = "Shelf"

    def __init__(self):
        Boxes.__init__(self)
        self.buildArgParser(sx="100*2", sy="70*3", h="20", outside=False)
        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=0.5)
        self.argparser.add_argument(
            "--front", action="store", type=float, default=0.7,
            help="fraction of bin height covert with slope")
        self.argparser.add_argument(
            "--angle", action="store", type=float, default=20,
            help="angle of the front walls")
        self.argparser.add_argument(
            "--curved", action="store", type=boolarg, default=True,
            help="curved side walls around opening")
        self.argparser.add_argument(
            "--curve_depth", action="store", type=float, default=2.0,
            help="depth of the cutaway in the curved side walls, relative to the opening size")
        self.argparser.add_argument(
            "--curve_width", action="store", type=float, default=0.5,
            help="width of the cutaway in the curved side walls, relative to the opening size")

    def xSlots(self):
        posx = -0.5 * self.thickness
        for x in self.sx[:-1]:
            posx += x + self.thickness
            posy = 0
            for y in self.sy:
                self.fingerHolesAt(posx, posy, y)
                posy += y + self.thickness

    def ySlots(self):
        posy = -0.5 * self.thickness
        for y in self.sy[:-1]:
            posy += y + self.thickness
            posx = 0
            for x in self.sx:
                self.fingerHolesAt(posy, posx, x)
                posx += x + self.thickness

    def xHoles(self):
        posx = -0.5 * self.thickness
        for x in self.sx[:-1]:
            posx += x + self.thickness
            self.fingerHolesAt(posx, 0, self.hi)

    def frontHoles(self, i):
        def CB():
            posx = -0.5 * self.thickness
            for x in self.sx[:-1]:
                posx += x + self.thickness
                self.fingerHolesAt(posx, 0, self.sy[i]*self.front*2**0.5)
        return CB

    def yHoles(self):
        posy = -0.5 * self.thickness
        for y in reversed(self.sy[1:]):
            posy += y + self.thickness
            self.fingerHolesAt(posy, 0, self.hi)

    def render(self):
        if self.outside:
            self.sx = self.adjustSize(self.sx)
            self.sy = self.adjustSize(self.sy)
            self.h = self.adjustSize(self.h, e2=False)

        x = sum(self.sx) + self.thickness * (len(self.sx) - 1)
        y = sum(self.sy) + self.thickness * (len(self.sy) - 1)
        h = self.h
        hi = self.hi = h
        t = self.thickness
        self.front = min(self.front, 0.999)

        self.addPart(BinFrontEdge(self, self))
        self.addPart(BinFrontSideEdge(self, self))

        angledsettings = copy.deepcopy(self.edges["f"].settings)
        angledsettings.setValues(self.thickness, True, angle=90 + self.angle)
        angledsettings.edgeObjects(self, chars="gGH")

        # outer walls
        e = ["F", "f", edges.SlottedEdge(self, self.sx[::-1], "G"), "f"]

        self.rectangularWall(x, h, e, callback=[self.xHoles], move="right", label="Bottom")
        self.rectangularWall(y, h, "FFbF", callback=[self.yHoles, ], move="up", label="Side wall")
        self.rectangularWall(y, h, "FFbF", callback=[self.yHoles, ], label="Side wall")
        self.rectangularWall(x, h, "Ffef", callback=[self.xHoles, ], move="left", label="Top")
        self.rectangularWall(y, h, "FFBF", move="up only")

        self.rectangularWall(x, y, "ffff", callback=[self.xSlots, self.ySlots],move="right", label="Rear wall")
        # Inner walls
        for i in range(len(self.sx) - 1):
            e = [edges.SlottedEdge(self, self.sy, "f"), "f", "B", "f"]
            self.rectangularWall(y, hi, e, move="up", label="Inner wall")

        for i in range(len(self.sy) - 1):
            e = [edges.SlottedEdge(self, self.sx, "f", slots=0.5 * hi), "f",
                 edges.SlottedEdge(self, self.sx[::-1], "G"), "f"]
            self.rectangularWall(x, hi, e, move="up", label="Internal shelf bottom")

        # Front walls
        for i in range(len(self.sy)):
            e = [edges.SlottedEdge(self, self.sx, "g"), "F", "e", "F"]
            self.rectangularWall(x, self.sy[i]*self.front*2**0.5, e, callback=[self.frontHoles(i)], move="up", label="Shelf front")
