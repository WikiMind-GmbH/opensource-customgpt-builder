# @app.post(
#     "/add-files-to-gpt",
#     tags=["customGPTs"],
#     response_model=StandardResponse,
#     operation_id="addFilesToGpt",
# )
# async def add_files_to_gpt(
#     validated_custom_gpt_id: int = Depends(validateGptExistsQuery),
#     validated_files: list[UploadFileFileFormatValidated] = Depends(validateFileFormat),
#     session: Session = Depends(get_session),
# ) -> StandardResponse:
#     res: StandardResponse = await add_files_to_gpt_helper(
#         validated_custom_gpt_id=validated_custom_gpt_id,
#         validated_files=validated_files,
#         session=session
#     )
#     return res

# TODO:
# async def add_files_to_gpt_helper(
#     validated_custom_gpt_id: int,
#     validated_files: list[UploadFileFileFormatValidated],
#     session: Session,
# )-> StandardResponse:
#     max_size: int = int(require_env("UPLOAD_MAX_FILE_SIZE"))

#     customGpt: ExistingCustomGPT = retrieve_custom_gpt_by_id(custom_gpt_id=validated_custom_gpt_id, session=session)
#     files: list[UploadFile] = [file.uploadFile for file in validated_files]
#     if not files:
#         raise HTTPException(status.HTTP_400_BAD_REQUEST, "No files supplied")
#     for f in files:
#         contents = await f.read()
#         if len(contents) > max_size:
#             raise HTTPException(
#                 status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
#                 f"{f.filename} exceeds 10 MB limit",
#             )
#         if f.filename is None:      # should be impossible
#             raise RuntimeError("Invariant violated: value cannot be None here")
#         base_dir = Path(require_env("LOADED_FILES_PATH")) / str(customGpt.custom_gpt_id)
#         base_dir.mkdir(parents=True, exist_ok=True)
#         file_path:str = os.path.join(base_dir, f.filename)
#         async with aiofiles.open(file_path, "wb") as out:
#             await out.write(contents)

#     return StandardResponse(res=StatusOfStandardResponse.success)

