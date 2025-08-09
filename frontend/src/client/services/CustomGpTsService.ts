/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_addFilesToGpt } from '../models/Body_addFilesToGpt';
import type { CreateOrEditCustomGPTStatus } from '../models/CreateOrEditCustomGPTStatus';
import type { CustomGptToCreateOrEdit } from '../models/CustomGptToCreateOrEdit';
import type { DeleteCustomGPTStatus } from '../models/DeleteCustomGPTStatus';
import type { ExistingCustomGPT } from '../models/ExistingCustomGPT';
import type { StandardResponse } from '../models/StandardResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class CustomGpTsService {
    /**
     * Retreive All Custom Gpts
     * @returns ExistingCustomGPT Successful Response
     * @throws ApiError
     */
    public static retreiveAllCustomGpts(): CancelablePromise<Array<ExistingCustomGPT>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/retreive-all-custom-gpts',
        });
    }
    /**
     * Get Custom Gpt By Id
     * @param gptId
     * @returns ExistingCustomGPT Successful Response
     * @throws ApiError
     */
    public static getCustomGptInfos(
        gptId: number,
    ): CancelablePromise<ExistingCustomGPT> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/get-custom-gpt-infos',
            query: {
                'gpt_id': gptId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Custom Gpt Endpoint
     * @param gptId
     * @returns DeleteCustomGPTStatus Successful Response
     * @throws ApiError
     */
    public static deleteCustomGpt(
        gptId: number,
    ): CancelablePromise<DeleteCustomGPTStatus> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/delete-custom-gpt',
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
     * @returns CreateOrEditCustomGPTStatus Successful Response
     * @throws ApiError
     */
    public static createOrEditCustomGpt(
        requestBody: CustomGptToCreateOrEdit,
    ): CancelablePromise<CreateOrEditCustomGPTStatus> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/create-or-edit-custom-gpt',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Add Files To Gpt
     * @param gptId
     * @param formData
     * @returns StandardResponse Successful Response
     * @throws ApiError
     */
    public static addFilesToGpt(
        gptId: number,
        formData: Body_addFilesToGpt,
    ): CancelablePromise<StandardResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/add-files-to-gpt',
            query: {
                'gpt_id': gptId,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Files
     * @param customGptId
     * @returns string Successful Response
     * @throws ApiError
     */
    public static listFilesToGpt(
        customGptId: number,
    ): CancelablePromise<Array<string>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/gpts/{custom_gpt_id}/files',
            path: {
                'custom_gpt_id': customGptId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
