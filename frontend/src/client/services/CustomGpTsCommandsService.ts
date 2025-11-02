/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CommandResult } from '../models/CommandResult';
import type { CustomGptToCreate } from '../models/CustomGptToCreate';
import type { CustomGptToEdit } from '../models/CustomGptToEdit';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class CustomGpTsCommandsService {
    /**
     * Delete Custom Gpt Endpoint
     * @param gptId
     * @returns CommandResult Successful Response
     * @throws ApiError
     */
    public static deleteCustomGpt(
        gptId: string,
    ): CancelablePromise<CommandResult> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/customgpts/delete-custom-gpt',
            query: {
                'gpt_id': gptId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Custom Gpt
     * @param requestBody
     * @returns CommandResult Successful Response
     * @throws ApiError
     */
    public static createOrEditCustomGpt(
        requestBody: CustomGptToCreate,
    ): CancelablePromise<CommandResult> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/customgpts/create-custom-gpt',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Edit Custom Gpt
     * @param requestBody
     * @returns CommandResult Successful Response
     * @throws ApiError
     */
    public static createOrEditCustomGpt1(
        requestBody: CustomGptToEdit,
    ): CancelablePromise<CommandResult> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/customgpts/edit-custom-gpt',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
