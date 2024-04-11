import uuid

from monitorizer.settings import TEMP


def tmp_file(name: str = None):
    return str(TEMP / str(uuid.uuid4()))
