from src.contexts.knowledge.application.ports.cgpt_permissions_port import (
    CgptPermissionCheckerPort,
    UserHasNoPermissionForCgptOrTheyDontExist,
)

# class UserHasNoPermissionForCgptOrTheyDontExist(RuntimeError):
#     def __init__(self, unaccessible_cgpt_ids: list[str]) -> None:
#         message = "The following ids were not accessible" + str(unaccessible_cgpt_ids)
#         super().__init__(message)


# class CgptPermissionCheckerPort(Protocol):
#     def assure_user_has_access_to_cgpts(self, cgpt_ids_to_check: list[str]) -> bool: ...


class FakeCgptPermissionChecker(CgptPermissionCheckerPort):
    def __init__(self, will_raise_error: bool) -> None:
        self._will_raise_error = will_raise_error

    def assure_user_has_access_to_cgpts(self, cgpt_ids_to_check: list[str]) -> None:
        if self._will_raise_error:
            raise UserHasNoPermissionForCgptOrTheyDontExist(
                unaccessible_cgpt_ids=cgpt_ids_to_check
            )
