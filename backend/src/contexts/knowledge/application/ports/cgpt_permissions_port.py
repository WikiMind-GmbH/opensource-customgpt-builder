from typing import Protocol


class UserHasNoPermissionForCgptOrTheyDontExist(RuntimeError):
    def __init__(self, unaccessible_cgpt_ids: list[str]) -> None:
        message = "The following ids were not accessible" + str(unaccessible_cgpt_ids)
        super().__init__(message)


class EmptyListToCheckPassedError(RuntimeError):
    "The list to check must not be empty, as we want to avoid false-positive-esque assertions"


class CgptPermissionCheckerPort(Protocol):
    def assure_user_has_access_to_cgpts(self, cgpt_ids_to_check: list[str]) -> None: ...

    """
    Raises `UserHasNoPermissionForCgptOrTheyDontExist` if there is at least one cgpt in `cgpt_ids_to_check` which the user has no authorization to access.
    """
