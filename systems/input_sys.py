import pygame as pg


class InputState:
    def __init__(self):
        self.events = {
            'quit': _EventInfo(pg.QUIT, False),
            'left': _EventInfo(pg.K_LEFT),
            'right': _EventInfo(pg.K_RIGHT),
            'down': _EventInfo(pg.K_DOWN),
            'up': _EventInfo(pg.K_UP),
            'space': _EventInfo(pg.K_SPACE),
            'mouse1': _MouseEventInfo(1),
            'z': _EventInfo(pg.K_z),
        }


    def update_just_pressed(self):
        """Makes just_pressed and just_released things just pressed."""
        for ekey in self.events:
            # Make sure just_pressed things are JUST pressed
            if self.events[ekey].just_pressed:
                self.events[ekey].just_pressed = False
            if self.events[ekey].just_released:
                self.events[ekey].just_released = False


    def update_input(self, event):
        for ekey in self.events:
            # Check event stuff for every non key thing in the thing
            if event.type == self.events[ekey].eventtype and (
                    event.type != pg.MOUSEBUTTONDOWN
                    and event.type != pg.MOUSEBUTTONUP
                    ):
                self.events[ekey].just_pressed = True

            # Do the keys
            if event.type == pg.KEYDOWN:
                if event.key == self.events[ekey].eventtype:
                    self.events[ekey].held = True
                    self.events[ekey].just_pressed = True
            if event.type == pg.KEYUP:
                if event.key == self.events[ekey].eventtype:
                    self.events[ekey].held = False
                    self.events[ekey].just_released = True

            if event.type == pg.MOUSEBUTTONDOWN:
                if hasattr(self.events[ekey], 'button'):
                    if event.button == self.events[ekey].button:
                        self.events[ekey].held = True
                        self.events[ekey].just_pressed = True
            if event.type == pg.MOUSEBUTTONUP:
                if hasattr(self.events[ekey], 'button'):
                    if event.button == self.events[ekey].button:
                        self.events[ekey].held = False
                        self.events[ekey].just_released = True


class _EventInfo:
    def __init__(self, eventtype, key=True) -> None:
        self.held = False
        self.just_pressed = False
        self.just_released = False
        self.eventtype = eventtype


class _MouseEventInfo(_EventInfo):
    def __init__(self, button) -> None:
        super().__init__(pg.MOUSEBUTTONDOWN, False)
        self.button = button
