import gc
import traceback
import torch

# This iterator returns the extensions in the order specified in the command-line
def iterator():
    state_extensions = {}
    for name in sorted(state_extensions, key=lambda x: state_extensions[x][1]):
        if state_extensions[name][0]:
            yield getattr(extensions, name).script, name