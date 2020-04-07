import pygame.locals

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
        self.hooks = []
    
    def trigger(self, key_event, active_sections=None):
        pass

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
        return inner
