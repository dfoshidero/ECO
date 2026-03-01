"""Helper to resolve data paths by trainer version (inferred from folder name)."""
import os


def get_data_version():
    """Infer trainer version from parent folder (e.g. trainers/v1/ -> v1)."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.basename(current_dir)


def get_data_version_from_prep(caller_file):
    """Infer trainer version when called from prep/ subfolder (e.g. trainers/v1/prep/ -> v1)."""
    parent = os.path.dirname(os.path.dirname(os.path.abspath(caller_file)))
    return os.path.basename(parent)
