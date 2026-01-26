# @app.get("/gpts/{custom_gpt_id}/files", response_model=list[str], tags=["customGPTs"], operation_id="listFilesToGpt",)
# async def get_files(custom_gpt_id: int):
#     return list_loaded_files(custom_gpt_id)


# def list_loaded_files(custom_gpt_id: int) -> list[str]:
#     """
#     Ensure the folder for this GPT exists and return a sorted list of file names in it.
#     If the folder is empty, returns [].
#     """
#     base_dir = Path(require_env("LOADED_FILES_PATH")) / str(custom_gpt_id)
#     base_dir.mkdir(parents=True, exist_ok=True)  # create if missing

#     # list only regular files (ignore subfolders)
#     try:
#         files = [p.name for p in base_dir.iterdir() if p.is_file()]
#     except FileNotFoundError:
#         # extremely rare (e.g., race condition on network FS); treat as empty
#         return []

#     return sorted(files)
