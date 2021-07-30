def root_path():
    '''
    Path to root directory
    '''
    from pathlib import Path
    file_path = __file__
    return str(Path(file_path).parents[2]) # go up two levels

def child_path(*child_path_list, root_path=root_path()):
    '''
    Path to child directories, ["childA", "child of childA"] etc
    '''
    import os
    final_absolute_path = os.path.join(root_path, *child_path_list)
    return final_absolute_path
