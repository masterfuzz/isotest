import pygame.locals
from pygame.locals import (
    KEYDOWN, KEYUP, MOUSEBUTTONDOWN
)
from collections import defaultdict

def _pygame_keys(key):
    # TODO make less gross
    def gen(keys):
        for k in keys:
            if len(k) == 1:
                yield ord(k)
            else:
                yield getattr(pygame.locals, "K_" + k)
    if type(key) != list:
        key = [key]
    return list(gen(key))

class Keybindings:
    def __init__(self, keys):
        self._keys = {
            section: {
                action: _pygame_keys(bindings) for action, bindings in action_list.items()
            } for section, action_list in keys.items()
        }
        self.hooks = defaultdict(lambda: defaultdict(list))
        self.pressed_keys = set()

    def keydown(self, event):
        self.pressed_keys.add(event.key)
        self.run_hooks(event)
    
    def keyup(self, event):
        self.pressed_keys.remove(event.key)

    def keyrepeat(self, event):
        for key in self.pressed_keys:
            kevent = lambda:None
            kevent.key = key
            self.run_hooks(kevent)
    
    def run_hooks(self, key):
        # TODO enable/disable sections
        for section in self._keys:
            _, action = self.filter([section])(key)
            if action:
                for wildcard_hook in self.hooks[section]['*']:
                    wildcard_hook(action)
                for hook in self.hooks[section][action]:
                    hook()

    def hook(self, section, action='*'):
        def decorator(func):
            self.hooks[section][action].append(func)
        return decorator

    def filter(self, sections=None):
        def inner(event):
            if sections:
                section_list = sections
            else:
                section_list = self._keys.keys()
            for section in section_list:
                for action, keys in self._keys[section].items():
                    if event.key in keys:
                        return section, action
            return None, None
        return inner
