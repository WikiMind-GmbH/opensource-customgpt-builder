/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_uploadFiles } from '../models/Body_uploadFiles';
import type { CommandResult } from '../models/CommandResult';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class KnowledgeCommandsService {
    /**
     * Delete Files Endpoint
     * @param requestBody
     * @returns CommandResult Successful Response
     * @throws ApiError
     */
    public static deleteFiles(
        requestBody: Array<string>,
    ): CancelablePromise<Array<CommandResult>> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/knowledge/delete-files',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Upload File
     * @param formData
     * @returns CommandResult Successful Response
     * @throws ApiError
     */
    public static uploadFiles(
        formData: Body_uploadFiles,
    ): CancelablePromise<CommandResult> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/knowledge/upload-files',
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
