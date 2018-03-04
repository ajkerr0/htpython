

class CondorpyBaseException(Exception):
    pass

class NoExecutable(CondorpyBaseException):
    pass

class HTCondorError(CondorpyBaseException):
    pass