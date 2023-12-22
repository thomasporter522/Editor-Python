import pygame

from Expression import Expression
from HoleNode import HoleNode
from Input import Input
from Renderer import Renderer


def run():

    expression = Expression()
    renderer = Renderer()
    input = Input(renderer.expression_rect, renderer.blocksize)

    mainloop = True
    command = None
    rerender = True

    while mainloop:

        command = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainloop = False
            elif command is None:
                command = input.process_input(event, expression)
                renderer.flip()

        if command is not None:
            command.do(expression)
            rerender = True

        if rerender:
            renderer.render(expression)

            # expression.head.x.compute_context([])
            # expression.head.x.compute_inferred_type()
            # expression.head.x.goal = HoleNode()
            # expression.head.x.compute_goal()
            # goal = expression.active_node.goal
            # icon = ":("
            # if expression.active_node.happy:
            #     icon = ":)"
            # print(icon, goal.to_ocaml())
            # print(", ".join([lc.to_ocaml()
            #      for lc in expression.active_node.context]))

            rerender = False

    pygame.quit()


if __name__ == "__main__":
    run()
