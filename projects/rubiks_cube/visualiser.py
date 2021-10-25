import random
import re

import vpython as vp

"""

Numbering the cube:

    Imagine the cube is made of three layers from top to bottom.
    White is on top and green is in front.
    The cubie positions are numbered by:

    Layer 1 (White face):
    0  1  2
    3  4  5
    6  7  8

    Layer 2 (middle layer):
    9  10 11
    12 13 14
    15 16 17

    Layer 3 (yellow face (viewed from top)):
    18 19 20
    21 22 23
    24 25 26

"""


# Constants for which number represents which face / direction
# May be used to represent a face of a cube / cubie
# or the direction of a cube / cubie rotation
HIDDEN = 0
UP = 1
DOWN = 2
LEFT = 3
RIGHT = 4
FRONT = 5
BACK = 6
MIDDLE = 7
EQUATORIAL = 8
STANDING = 9

WHITE = 1
YELLOW = 2
ORANGE = 3
RED = 4
GREEN = 5
BLUE = 6

COLOUR_TO_LETTER = {WHITE: "W", YELLOW: "Y", ORANGE: "O", RED: "R", GREEN: "G", BLUE: "B"}
FACE_TO_LETTER = {UP: "U", DOWN: "D", LEFT: "L", RIGHT: "R", FRONT: "F", BACK: "B"}

LETTER_TO_COLOUR = {"W": WHITE, "Y": YELLOW, "O": ORANGE, "R": RED, "G": GREEN, "B": BLUE}

ALL_FACES = {UP, DOWN, LEFT, RIGHT, FRONT, BACK}


class Cube:
    def __init__(
        self,
        *,
        visual=False,
        colours={
            UP: "WWWWWWWWW",
            DOWN: "YYYYYYYYY",
            FRONT: "GGGGGGGGG",
            RIGHT: "RRRRRRRRR",
            BACK: "BBBBBBBBB",
            LEFT: "OOOOOOOOO",
        },
        size=3,
        tps=0,
    ):

        self.visual = visual
        self.tps = tps

        if visual:
            self.init_canvas()

        if visual:
            self.cubies = [
                Cubie((x, y, z))
                for y in range(1, -2, -1)
                for z in range(-1, 2, 1)
                for x in range(-1, 2, 1)
            ]
        else:
            self.cubies = [Cubie() for i in range(size * size * size)]

        self.create_faces()

        self.input_colours(colours)

    def create_faces(self):
        self.up = Face(self, UP, self.visual)
        self.down = Face(self, DOWN, self.visual)
        self.left = Face(self, LEFT, self.visual)
        self.right = Face(self, RIGHT, self.visual)
        self.front = Face(self, FRONT, self.visual)
        self.back = Face(self, BACK, self.visual)
        self.middle = Slice(self, MIDDLE, self.visual)
        self.equatorial = Slice(self, EQUATORIAL, self.visual)
        self.standing = Slice(self, STANDING, self.visual)

        self.faces = [self.up, self.front, self.right, self.back, self.left, self.down]
        self.move_dict = {
            "U": self.up,
            "D": self.down,
            "L": self.left,
            "R": self.right,
            "F": self.front,
            "B": self.back,
            "M": self.middle,
            "E": self.equatorial,
            "S": self.standing,
        }

    def move(self, moves, tps=-1):

        if tps == -1:
            tps = self.tps

        split_moves = re.findall(r"[a-zA-Z][^a-zA-Z ]*", moves)
        print(split_moves)
        for split in split_moves:
            move = split[0]

            if split[1:]:
                if split[1:] == "'":
                    turns = -1
                elif split[1:] == "2":
                    turns = 2
                else:
                    raise ValueError(f"Invalid turns for move {split}")
            else:
                turns = 1

            # Rotates the correct face
            if move in self.move_dict:
                self.move_dict[move].rotate(turns, tps)
            elif move == "x":
                self.left.rotate(-turns, tps)
                self.middle.rotate(-turns, tps)
                self.right.rotate(turns, tps)
            else:
                raise ValueError(f"Invalid move {move}")

    def input_colours(self, colours={}):
        if not colours:
            colours = {
                face.face: re.findall(
                    r"[a-zA-Z]", input(f"Input for face {FACE_TO_LETTER[face.face]}: ")
                )
                for face in self.faces
            }

        for cubie in self.cubies:
            cubie.clear()

        for face in self.faces:
            face.input_colours(colours[face.face])

        if self.visual:
            for cubie in self.cubies:
                cubie.draw_visual()

    def display(self):
        """Displays the cube as a net"""
        for face in self.faces:
            print(FACE_TO_LETTER[face.face])
            state = list(map(lambda x: COLOUR_TO_LETTER[x], face.state))
            print(state[1:4])
            print([state[8], state[0], state[4]])
            print(state[7:4:-1])

    @staticmethod
    def init_canvas():
        scene = vp.canvas(x=0, y=0, width=600, height=600, autoscale=False, userpan=False)
        # scene = vp.canvas(
        #     x=0,
        #     y=0,
        #     width=600,
        #     height=600,
        #     autoscale=False,
        #     userpan=False,
        #     userzoom=False,
        # )
        # scene.range = 12
        scene.background = vp.color.white
        scene.lights = []
        scene.ambient = vp.color.white
        scene.userspin = True
        scene.select()


class Face:

    positions_dict = {
        UP: [4, 0, 1, 2, 5, 8, 7, 6, 3],
        DOWN: [22, 24, 25, 26, 23, 20, 19, 18, 21],
        LEFT: [12, 0, 3, 6, 15, 24, 21, 18, 9],
        RIGHT: [14, 8, 5, 2, 11, 20, 23, 26, 17],
        FRONT: [16, 6, 7, 8, 17, 26, 25, 24, 15],
        BACK: [10, 2, 1, 0, 9, 18, 19, 20, 11],
    }

    rotation_vector_dict = {
        UP: vp.vec(0, -1, 0),
        DOWN: vp.vec(0, 1, 0),
        LEFT: vp.vec(1, 0, 0),
        RIGHT: vp.vec(-1, 0, 0),
        FRONT: vp.vec(0, 0, -1),
        BACK: vp.vec(0, 0, 1),
    }

    def __init__(self, cube, face, visual):
        self.cube = cube
        self.face = face
        self.visual = visual
        self.positions = self.positions_dict[face]
        self.rotation_vector = self.rotation_vector_dict[face]

    def rotate(self, turns=1, tps=0):
        """Rotates the face 90 * `turns` degrees clockwise.
        Each cubie in that face is also rotated."""

        for position in self.positions:
            cubie = self.cube.cubies[position]
            cubie.rotate(self.face, turns)

        if self.visual:
            self.rotate_visual(turns, tps)

        self.update_postitions(turns)

    def update_postitions(self, turns):
        # The first position is the centre piece so doesn't move
        # The positions are arranged in a clockwise fashion
        # Each position after the fist one is shifted along
        new_positions = [self.positions[0]] + shift_list(self.positions[1:], turns * 2)
        all_cubies = self.cube.cubies[:]

        # Now updates the positions of the cubies in the cube
        for new_pos, old_pos in zip(new_positions, self.positions):
            all_cubies[new_pos] = self.cube.cubies[old_pos]
        self.cube.cubies = all_cubies[:]

    def rotate_visual(self, turns, tps=0):
        cubies = [self.cube.cubies[position] for position in self.positions]

        if tps > 0:
            fps = 30
            tps = fps / (fps // tps)  # Makes sure fps is divisible by tps
            # tps /= abs(turns)  # Takes twice as long to make a double turn
            mini_turns = int(fps // tps)  # Amount of mini-turns to make

            for _ in range(mini_turns):
                vp.rate(fps)
                for cubie in cubies:
                    cubie.rotate_visual(
                        angle=(turns * vp.pi / 2) / mini_turns,
                        axis=self.rotation_vector,
                        origin=vp.vec(0, 0, 0),
                    )

        else:
            for cubie in cubies:
                cubie.rotate_visual(
                    angle=turns * vp.pi / 2,
                    axis=self.rotation_vector,
                    origin=vp.vec(0, 0, 0),
                )

    def input_colours(self, colours):
        cubies = [self.cube.cubies[pos] for pos in self.positions]
        input_order = cubies[1:4] + [cubies[8], cubies[0], cubies[4]] + cubies[7:4:-1]
        for cubie, colour in zip(input_order, colours):
            cubie.set_face_colour(self.face, LETTER_TO_COLOUR[colour])

    @property
    def state(self):
        return [
            self.cube.cubies[position].get_colour(self.face)
            for position in self.positions
        ]


class Slice(Face):
    positions_dict = {
        MIDDLE: [13, 1, 4, 7, 16, 25, 22, 19, 10],
        EQUATORIAL: [13, 15, 16, 17, 14, 11, 10, 9, 12],
        STANDING: [13, 3, 4, 5, 14, 23, 22, 21, 12],
    }

    rotation_vector_dict = {
        MIDDLE: vp.vec(1, 0, 0),
        EQUATORIAL: vp.vec(0, 1, 0),
        STANDING: vp.vec(0, 0, -1),
    }


class Cubie:

    face_rotation_info_dict = {
        UP: {"axis": vp.vec(0, 0, 0), "angle": 0},
        DOWN: {"axis": vp.vec(1, 0, 0), "angle": vp.pi},
        LEFT: {"axis": vp.vec(0, 0, 1), "angle": vp.pi / 2},
        RIGHT: {"axis": vp.vec(0, 0, -1), "angle": vp.pi / 2},
        FRONT: {"axis": vp.vec(1, 0, 0), "angle": vp.pi / 2},
        BACK: {"axis": vp.vec(-1, 0, 0), "angle": vp.pi / 2},
    }

    # Position of the stickers (inner colour), borders (black border)
    # and corners (outer corners of face) on the y = 1 plane.
    face_sticker_vecs = [
        vp.vec(-0.9, 1, -0.9),
        vp.vec(0.9, 1, -0.9),
        vp.vec(0.9, 1, 0.9),
        vp.vec(-0.9, 1, 0.9),
    ]
    face_borders_vecs = [
        [vp.vec(-1, 1, -0.9), vp.vec(1, 1, -0.9), vp.vec(1, 1, -1), vp.vec(-1, 1, -1)],
        [vp.vec(-1, 1, 1), vp.vec(1, 1, 1), vp.vec(1, 1, 0.9), vp.vec(-1, 1, 0.9)],
        [
            vp.vec(-1, 1, 0.9),
            vp.vec(-0.9, 1, 0.9),
            vp.vec(-0.9, 1, -0.9),
            vp.vec(-1, 1, -0.9),
        ],
        [
            vp.vec(0.9, 1, 0.9),
            vp.vec(1, 1, 0.9),
            vp.vec(1, 1, -0.9),
            vp.vec(0.9, 1, -0.9),
        ],
    ]
    face_corner_vecs = [
        vp.vec(-1, 1, -1),
        vp.vec(1, 1, -1),
        vp.vec(1, 1, 1),
        vp.vec(-1, 1, 1),
    ]

    colour_to_vp_color = {
        WHITE: vp.color.white,
        YELLOW: vp.color.yellow,
        ORANGE: vp.color.orange,
        RED: vp.color.red,
        GREEN: vp.color.green,
        BLUE: vp.color.blue,
    }

    # Keeps track of which rotations affect which faces
    # They are in a specific order. They are shifted left with a
    # standard 1 turn rotation.
    rotation_faces = {
        UP: [FRONT, RIGHT, BACK, LEFT],
        DOWN: [FRONT, LEFT, BACK, RIGHT],
        LEFT: [UP, BACK, DOWN, FRONT],
        RIGHT: [UP, FRONT, DOWN, BACK],
        FRONT: [UP, LEFT, DOWN, RIGHT],
        BACK: [UP, RIGHT, DOWN, LEFT],
        MIDDLE: [UP, BACK, DOWN, FRONT],
        EQUATORIAL: [FRONT, LEFT, BACK, RIGHT],
        STANDING: [UP, LEFT, DOWN, RIGHT],
    }

    def __init__(self, pos=(), length=2):

        self.visual = bool(pos)
        if self.visual:
            self.length = length
            self.size = vp.vec(length, length, length)
            self.pos = vp.vec(*pos) * length

        self.face_colours = {face: HIDDEN for face in ALL_FACES}

    def rotate(self, direction, turns):
        old_orientations = self.rotation_faces[direction]
        new_orientations = shift_list(old_orientations, turns)

        new_face = {
            old: self.face_colours[new]
            for old, new in zip(old_orientations, new_orientations)
        }
        self.face_colours = {**self.face_colours, **new_face}

    def rotate_visual(self, **kwargs):
        self.visual_cubie.rotate(**kwargs)
        self.pos = self.visual_cubie.pos

    def get_colour(self, face):
        return self.face_colours[face]

    def set_face_colour(self, face, colour):
        self.face_colours[face] = colour

    def clear(self):
        self.face_colours = {face: HIDDEN for face in ALL_FACES}
        if self.visual and hasattr(self, "visual_cubie"):
            self.visual_cubie.visible = False
            del self.visual_cubie

    def draw_visual(self):

        face_quads = []
        for face in ALL_FACES:
            colour = self.face_colours[face]
            face_quads.extend(
                self.create_face(
                    face,
                    self.colour_to_vp_color[colour]
                    if colour is not HIDDEN
                    else vp.color.black,
                    visible=colour is not HIDDEN,
                )
            )

        self.visual_cubie = vp.compound(face_quads)
        self.visual_cubie.size = self.size
        self.visual_cubie.pos = self.pos

    def create_face(self, face, colour, visible=True):
        """Creates each face of a cubie. If the face is visible, it is created
        by drawing the inner sticker and black boarder quads on the y=1 plane.
        Each quad object is then rotated to the position of the cubie.
        If the face is not visible, then one black quad the full size of the
        face is created."""

        rotation_info = self.face_rotation_info_dict[face]

        if visible:
            sticker = vp.quad(
                vs=[
                    self.create_vertex(vec, colour, rotation_info)
                    for vec in self.face_sticker_vecs
                ]
            )

            borders = [
                vp.quad(
                    vs=[
                        self.create_vertex(vec, vp.color.black, rotation_info)
                        for vec in border
                    ]
                )
                for border in self.face_borders_vecs
            ]
            quads = [sticker] + borders

        else:
            quads = [
                vp.quad(
                    vs=[
                        self.create_vertex(vec, colour, rotation_info)
                        for vec in self.face_corner_vecs
                    ]
                )
            ]

        return quads

    @staticmethod
    def create_vertex(vector, colour, rotation_info={}):
        if rotation_info:
            vertex = vp.vertex(pos=vector.rotate(**rotation_info), color=colour)
        else:
            vertex = vp.vertex(pos=vector, color=colour)
        return vertex


def shift_list(list_, moves):
    """Shifts the list leftwards by `moves`.
    Wraps items at the start of the list to the end."""
    moves = moves % len(list_)
    return list_[moves:] + list_[:moves]


if __name__ == "__main__":

    cube = Cube(visual=True)
    # cube.move("RULBF'U2", 2)

    random.seed(1)
    s = " ".join(
        [random.choice("UDLRFBMES") + random.choice(["", "'", "2"]) for _ in range(100)]
    )
    print(s)
    cube.move(s, 2)
