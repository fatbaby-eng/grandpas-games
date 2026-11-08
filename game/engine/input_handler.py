"""Routes pygame events through a stack of layers; the first layer to consume an
event stops propagation. Layers are objects with `handle_event(event) -> bool`."""
import pygame


class InputHandler:
    def __init__(self):
        self.mouse_pos = (0, 0)
        self.quit_requested = False

    def poll(self, layers) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_requested = True
                continue
            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
                # Everyone may see motion events (hover highlighting), nothing consumes them.
                for layer in layers:
                    if layer is not None:
                        layer.handle_event(event)
                continue
            for layer in layers:
                if layer is not None and layer.handle_event(event):
                    break
