# Domain/ Service layer exceptions
class ConversationNonExistentError(RuntimeError):
    "No conversation with this id exists"

class IsNotATextMessage(RuntimeError):
    "Only Messages with contenttype text are can do this."