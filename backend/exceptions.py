class UnpersistedObjectError(RuntimeError):
    """Raised when an operation requires the model to be stored in the DB."""

# app/exceptions.py  (same place as UnpersistedObjectError)
class OpenAIApiUnexpectedAnswerError(RuntimeError):
    """Raised when OpenAI returns a response different than the expected one"""

class UnexpectedSQLEntryStucture(RuntimeError):
    """Unexpected combination of values occured -implement subclasses and further validation maybe"""

