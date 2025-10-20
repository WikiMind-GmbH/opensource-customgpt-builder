# Domain/ Service layer exceptions
class CGPTNonExistentError(RuntimeError):
    "No conversation with this id exists"