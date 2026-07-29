current_action = None



def set_action(action):

    global current_action

    current_action = action




def get_action():

    return current_action




def clear_action():

    global current_action

    current_action = None