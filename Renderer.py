import pygame
import math

pygame.init()


class Renderer:

    blocksize = 30  # in pixels

    # in blocks
    screen_width = 30
    screen_height = 20
    expression_rect = (2, 1, 15, 15)
    context_rect = (18, 1, 10, 15)
    goal_rect = (2, 17, 15, 2)
    type_rect = (18, 17, 10, 2)

    near_sight_border = 1
    far_sight_border = 5

    font = pygame.font.SysFont('courier', 20, bold=True)
    colors = {
        "background": (0, 0, 0),
        "syntax": (150, 200, 250),
        "hole": (200, 150, 250),
        "hole_highlight": (200, 200, 250),
        "text_highlight": (100, 100, 150),
        "block_highlight": (200, 200, 250),
        "frame": (100, 100, 100),
    }

    # in pixels
    syntax_thickness = 2
    highlight_thickness = 2
    frame_thickness = 4

    # in blocks
    paren_width = 0.3
    arrow_wideness = 0.3
    anchor_radius = 0.3
    hole_radius = 0.4
    hole_highlight_radius = 0.2
    ellipsis_radius = 0.2
    colon_wideness = 0.4
    colon_radius = 0.1

    let_supported = True

    def __init__(self):
        self.screen = pygame.display.set_mode((
            self.blocksize * self.screen_width, self.blocksize * self.screen_height))
        self.background = pygame.Surface(self.screen.get_size())
        self.background.fill(self.colors["background"])
        self.background = self.background.convert()
        self.draw_background()

        self.expression_offsetx = 0
        self.expression_offsety = 0

        self.arrow_tile = self.compute_arrow(backwards=False)
        self.backwards_arrow_tile = self.compute_arrow(backwards=True)

        self.pipeline_tile = self.compute_pipeline(backwards=False)
        self.backwards_pipeline_tile = self.compute_pipeline(backwards=True)

        self.hole_tile = self.compute_hole(active=False)
        self.active_hole_tile = self.compute_hole(active=True)

    def scale_pair(self, x, y):
        return (x*self.blocksize, y*self.blocksize)

    def scale_rect(self, r):
        return (r[0]*self.blocksize, r[1]*self.blocksize, r[2]*self.blocksize, r[3]*self.blocksize)

    def flip(self):
        pygame.display.flip()

    def calibrate(self, expression):
        focusx, focusy = expression.active_node.coordinate_rect[
            0], expression.active_node.coordinate_rect[1]

        self.expression_offsetx = self.near_sight_border
        self.expression_offsety = self.near_sight_border

        if (focusx + self.expression_offsetx < self.near_sight_border):
            self.expression_offsetx = self.near_sight_border - focusx
        elif (focusx + self.expression_offsetx + 1 > self.expression_rect[2] - self.far_sight_border):
            self.expression_offsetx = self.expression_rect[2] - \
                self.far_sight_border - focusx - 1
        if (focusy + self.expression_offsety < self.near_sight_border):
            self.expression_offsety = self.near_sight_border - focusy
        elif (focusy + self.expression_offsety + 1 > self.expression_rect[3] - self.far_sight_border):
            self.expression_offsety = self.expression_rect[3] - \
                self.far_sight_border - focusy - 1

    def render_expression(self, expression):

        scaled_expression_rect = self.scale_rect(self.expression_rect)

        expression.set_coordinates(self, 0, 0)
        expression.go_up_if_invisible()

        self.calibrate(expression)

        expression.set_coordinates(self,
                                   self.expression_rect[0] +
                                   self.expression_offsetx,
                                   self.expression_rect[1] +
                                   self.expression_offsety)

        expression_tile = pygame.Surface(
            (scaled_expression_rect[2], scaled_expression_rect[2]))

        expression.head.render(self, expression_tile,
                               self.expression_offsetx, self.expression_offsety)

        self.screen.blit(
            expression_tile, (scaled_expression_rect[0], scaled_expression_rect[1]))

        pygame.draw.rect(
            self.screen, self.colors["frame"], scaled_expression_rect, self.frame_thickness)

    def render(self, expression):
        self.render_expression(expression)
        self.flip()

    def draw_background(self):
        self.screen.blit(self.background, (0, 0))

    def draw_exact_dot(self, tile, color, x, y, radius):
        center = self.scale_pair(x, y)
        pygame.draw.circle(tile, color, center, self.blocksize*radius)

    def draw_centered_dot(self, tile, color, x, y, radius):
        self.draw_exact_dot(tile, color, x+0.5, y+0.5, radius)

    def draw_centered_circle(self, tile, color, x, y, radius):
        self.draw_centered_dot(tile, color, x, y, radius)
        self.draw_centered_dot(
            tile, self.colors["background"], x, y, radius - self.syntax_thickness/self.blocksize)

    def draw_anchor(self, tile, x, y):
        self.draw_centered_circle(
            tile, self.colors["syntax"], x, y, self.anchor_radius)

    anchor_width = 1

    def draw_exact_line(self, tile, x1, y1, x2, y2):
        position1 = self.scale_pair(x1, y1)
        position2 = self.scale_pair(x2, y2)
        pygame.draw.line(
            tile, self.colors["syntax"],
            position1, position2, self.syntax_thickness)

    def draw_centered_line(self, tile, x1, y1, x2, y2):
        self.draw_exact_line(tile, x1+0.5, y1+0.5, x2+0.5, y2+0.5)

    def compute_arrow(self, backwards):
        tile = pygame.Surface((self.blocksize, self.blocksize))
        line_start = (0.5*int(backwards), 0.5)
        line_end = (1 - 0.5*int(not backwards), 0.5)
        self.draw_exact_line(tile, *line_start, *line_end)
        trianglepoint1 = self.scale_pair(0.5, 0.5 - self.arrow_wideness)
        trianglepoint2 = self.scale_pair(0.5, 0.5 + self.arrow_wideness)
        trianglepoint3 = self.scale_pair(int(not backwards), 0.5)
        pygame.draw.polygon(
            tile, self.colors["syntax"], (trianglepoint1, trianglepoint2, trianglepoint3))
        return tile

    def draw_arrow(self, tile, x, y, backwards=False):
        image = None
        if not backwards:
            image = self.arrow_tile
        else:
            image = self.backwards_arrow_tile

        tile.blit(image, (self.blocksize*x, self.blocksize*y))

    arrow_width = 1

    def compute_pipeline(self, backwards=False):

        tile = pygame.Surface((self.blocksize, self.blocksize))

        x1, x2 = 0.5, 0.5

        if backwards:
            x1 += 0.25
            x2 -= 0.25
        else:
            x1 -= 0.25
            x2 += 0.25

        trianglepoint1 = self.scale_pair(x1, 0.5 - self.arrow_wideness)
        trianglepoint2 = self.scale_pair(x1, 0.5 + self.arrow_wideness)
        trianglepoint3 = self.scale_pair(x2, 0.5)
        pygame.draw.polygon(
            tile, self.colors["syntax"], (trianglepoint1, trianglepoint2, trianglepoint3), self.syntax_thickness)

        return tile

    def draw_pipeline_cached(self, tile, x, y, backwards=False):
        image = None
        if not backwards:
            image = self.pipeline_tile
        else:
            image = self.backwards_pipeline_tile

        tile.blit(image, (self.blocksize*x, self.blocksize*y))

    def draw_pipeline(self, tile, x, y, backwards=False):
        x1, x2 = x+0.5, x+0.5

        if backwards:
            x1 += 0.25
            x2 -= 0.25
        else:
            x1 -= 0.25
            x2 += 0.25

        trianglepoint1 = self.scale_pair(x1, y+0.5 - self.arrow_wideness)
        trianglepoint2 = self.scale_pair(x1, y+0.5 + self.arrow_wideness)
        trianglepoint3 = self.scale_pair(x2, y+0.5)
        pygame.draw.polygon(
            tile, self.colors["syntax"], (trianglepoint1, trianglepoint2, trianglepoint3), self.syntax_thickness)

    pipeline_width = 1

    def draw_colon(self, tile, x, y):
        self.draw_exact_dot(
            tile, self.colors["syntax"], x+0.5, y + 0.5 + self.colon_wideness/2, self.colon_radius)
        self.draw_exact_dot(
            tile, self.colors["syntax"], x+0.5, y + 0.5 - self.colon_wideness/2, self.colon_radius)

    colon_width = 1

    def draw_parens(self, tile, x1, y1, x2, y2):
        r1 = self.scale_rect((x1, y1, 2*self.paren_width, 1))
        r2 = self.scale_rect((x2, y2, 2*self.paren_width, 1))
        pygame.draw.arc(
            tile, self.colors["syntax"], r1, math.pi*0.5, math.pi*1.5, self.syntax_thickness)
        pygame.draw.arc(
            tile, self.colors["syntax"], r2, math.pi*1.5, math.pi*2.5, self.syntax_thickness)

    def draw_ellipsis(self, tile, x, y):
        self.draw_centered_dot(
            tile, self.colors["syntax"], x, y, self.ellipsis_radius)

    ellipsis_width = 1

    def compute_hole(self, active):
        tile = pygame.Surface((self.blocksize, self.blocksize))
        self.draw_centered_circle(
            tile, self.colors["hole"],
            0, 0, self.hole_radius)
        if active:
            self.draw_centered_dot(
                tile, self.colors["hole_highlight"],
                0, 0, self.hole_highlight_radius)
        return tile

    def draw_hole_cached(self, tile, x, y, active=False):
        image = None
        if active:
            image = self.active_hole_tile
        else:
            image = self.hole_tile
        tile.blit(image, (self.blocksize*x, self.blocksize*y))

    def draw_hole(self, tile, x, y, active=False):
        self.draw_centered_circle(
            tile, self.colors["hole"],
            x, y, self.hole_radius)
        if active:
            self.draw_centered_dot(
                tile, self.colors["hole_highlight"],
                x, y, self.hole_highlight_radius)

    hole_width = 1

    def draw_string(self, tile, x, y, string, active=False):
        highlight_color = self.colors["background"]
        if active:
            highlight_color = self.colors["text_highlight"]

        text = self.font.render(string, True, (255, 255, 255), highlight_color)
        textRect = text.get_rect()

        textRect.center = (self.blocksize*(x + self.string_width(string,
                                                                 rect=textRect)*0.5), self.blocksize * (y + 0.5))
        tile.blit(text, textRect)

    def string_width(self, string, rect=None):
        if rect is None:
            text = self.font.render(string, True, (0, 0, 0))
            rect = text.get_rect()
        return math.ceil(rect[2]/self.blocksize)

    def draw_selection_rect(self, tile, x, y, w, h):
        rect = self.scale_rect((x, y, w, h))
        pygame.draw.rect(
            tile, self.colors["block_highlight"], rect, self.highlight_thickness)
