import os
import glob
import shutil

from ..util import safe_mmkdir


def _scaffold_directories_and_notebooks(base_dir):
    #!!! FIXME: Check to see if the directory already exists. If it does, refuse with:
    # `great_expectations/` already exists.
    # If you're certain you want to re-initialize Great Expectations within this project,
    # please delete the whole `great_expectations/` directory and run `great_expectations init` again.

    safe_mmkdir(base_dir, exist_ok=True)
    notebook_dir_name = "notebooks"

    open(os.path.join(base_dir, ".gitignore"), 'w').write("""uncommitted/""")

    for directory in [notebook_dir_name, "expectations", "datasources", "uncommitted", "plugins", "fixtures"]:
        safe_mmkdir(os.path.join(base_dir, directory), exist_ok=True)

    for uncommitted_directory in ["validations", "credentials", "samples"]:
        safe_mmkdir(os.path.join(base_dir, "uncommitted",
                                 uncommitted_directory), exist_ok=True)

    for notebook in glob.glob(script_relative_path("../init_notebooks/*.ipynb")):
        notebook_name = os.path.basename(notebook)
        shutil.copyfile(notebook, os.path.join(
            base_dir, notebook_dir_name, notebook_name))


def script_relative_path(file_path):
    '''
    Useful for testing with local files. Use a path relative to where the
    test resides and this function will return the absolute path
    of that file. Otherwise it will be relative to script that
    ran the test

    Note this is expensive performance wise so if you are calling this many
    times you may want to call it once and cache the base dir.
    '''
    # from http://bit.ly/2snyC6s

    import inspect
    scriptdir = inspect.stack()[1][1]
    return os.path.join(os.path.dirname(os.path.abspath(scriptdir)), file_path)