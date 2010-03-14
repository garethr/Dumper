import os

def create_or_update(content, filename):
    """
    Given some content and a filename either:
    - create the file and write the content to it if it doesn't exist
    - update the file contents if they differ
    - do nothing if the file hasn't changed
    """
    # work out whether we are creating, updating or doing nothing
    try:
        handle = open(filename, 'r')
        created = False 
        if not content == handle.read():
            updated = True
        else:
            updated = False
    except IOError:
        created = True
        updated = False

    # write the output to the file and close if we have to
    if created or updated:
        handle = open(filename, 'w')
        handle.write(content)
        handle.close()

    return created, updated

def ensure_dir(path):
    "Create directory if it doesn't already exist"
    directory = os.path.dirname("%s/" % path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        return True
    return False
