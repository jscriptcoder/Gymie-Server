#####################
# Custom Exceptions #
#####################

class InstanceNotFound(Exception):
    """Instance is not found in the dictionary where environments are stored"""
    pass

class EnvironmentMalformed(Exception):
    """Environment ID is not correct"""
    pass

class EnvironmentNotFound(Exception):
    """Environment ID is not registered as environment"""
    pass

class WrongAction(Exception):
    """There was a problem executing the action on the environment"""
    pass
