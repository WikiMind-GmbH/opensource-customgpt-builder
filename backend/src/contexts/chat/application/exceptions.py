# Domain/ Service layer exceptions
class ConversationNonExistentError(RuntimeError):
    "No conversation with this id exists"

class IsNotATextMessage(RuntimeError):
    "Only Messages with contenttype text can do this."

class SysPromptMustBeInitializedBeforeAddingMessages(RuntimeError):
    "The SystemPrompt must be initialized before messages can be added/ a conversation started"