import pygame
import Commands


def coords_in_rect(coords, rect):
    return (coords[0] >= rect[0]
            and coords[0] < rect[0] + rect[2]
            and coords[1] >= rect[1]
            and coords[1] < rect[1] + rect[3])


class Input:

    def __init__(self, expression_rect, blocksize):
        self.expression_rect = expression_rect
        self.blocksize = blocksize

    def process_input(self, event, expression):

        commands = []

        # control and shift
        control = pygame.key.get_pressed()[pygame.K_LCTRL] or \
            pygame.key.get_pressed()[pygame.K_RCTRL]
        shift = pygame.key.get_pressed()[pygame.K_LSHIFT] or \
            pygame.key.get_pressed()[pygame.K_RSHIFT]

        if event.type == pygame.KEYDOWN:

            # navigation

            if event.key == pygame.K_RIGHT:
                commands.append(Commands.FrontCycle(False))
                commands.append(Commands.GoDown(False))
            if event.key == pygame.K_LEFT:
                commands.append(Commands.BackCycle(False))
            if event.key == pygame.K_TAB:
                if shift:
                    commands.append(Commands.BackCycle(True))
                    commands.append(Commands.BackCycle(False))
                else:
                    commands.append(Commands.FrontCycle(True))
                    commands.append(Commands.FrontCycle(False))
                    commands.append(Commands.GoDown(True))
                    commands.append(Commands.GoDown(False))

            if event.key == pygame.K_UP:
                if control:
                    commands.append(Commands.GoTop())
                else:
                    commands.append(Commands.GoUp())
            if event.key == pygame.K_DOWN:
                if not shift:
                    commands.append(Commands.GoDown(True))
                commands.append(Commands.GoDown(False))

            # manipulation
            if event.key == pygame.K_RETURN:
                commands.append(Commands.Rotate())
            if event.key == pygame.K_BACKSPACE:
                commands.append(Commands.Rotate(back_only=True))
            if event.key == pygame.K_SPACE:
                commands.append(Commands.Reverse())
                commands.append(Commands.CollapseLet())
            if event.key == pygame.K_x and control:
                commands.append(Commands.Cut())
            if event.key == pygame.K_v and control:
                commands.append(Commands.Paste())

            # special typing
            if event.key == pygame.K_BACKSPACE:
                commands.append(Commands.Backspace())
            if event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                # commands.append(Commands.LetDelete())
                commands.append(Commands.Delete())
            if event.key == pygame.K_SPACE:
                commands.append(Commands.TextCommand())

            # special nodes
            if event.key == pygame.K_SPACE:
                commands.append(Commands.ApplyUpwards(forwards=False))
            if event.key == pygame.K_COMMA and shift:
                commands.append(Commands.ApplyUpwards(forwards=False))
            if event.key == pygame.K_PERIOD and shift:
                commands.append(Commands.ApplyUpwards(forwards=True))
            if event.key == pygame.K_EQUALS:
                commands.append(Commands.AddLet())

            # general typing
            for c in "abcdefghijklmnopqrstuvwxyz0123456789":
                if event.key == pygame.key.key_code(c):
                    visible_c = c
                    if shift:
                        visible_c = c.upper()
                    commands.append(Commands.AddId(visible_c))
                    commands.append(Commands.TypeId(visible_c))

            if event.key == pygame.K_SPACE:
                commands.append(Commands.FrontCycle(True))
                commands.append(Commands.FrontCycle(False))

        elif event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            coords = (pos[0]//self.blocksize, pos[1]//self.blocksize)
            if expression.node_of_coords.valid(*coords):
                commands.append(Commands.SelectNode(
                    expression.node_of_coords.get(*coords)))

        for command in commands:
            if command.allowed(expression):
                return command
        return None
