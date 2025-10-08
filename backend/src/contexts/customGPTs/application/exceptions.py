# Domain/ Service layer exceptions
class ConversationNonExistentError(RuntimeError):
    "No conversation with this id exists"