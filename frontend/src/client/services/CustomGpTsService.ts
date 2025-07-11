/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreateOrEditCustomGPTStatus } from '../models/CreateOrEditCustomGPTStatus';
import type { CustomGptToCreateOrEdit } from '../models/CustomGptToCreateOrEdit';
import type { DeleteCustomGPTStatus } from '../models/DeleteCustomGPTStatus';
import type { ExistingCustomGPT } from '../models/ExistingCustomGPT';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class CustomGpTsService {
    /**
     * Retreive All Custom Gpts
     * @returns ExistingCustomGPT Successful Response
     * @throws ApiError
     */
    public static retreiveAllCustomGptsRetreiveAllCustomGptsGet(): CancelablePromise<Array<ExistingCustomGPT>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/retreive-all-custom-gpts',
        });
    }
    /**
     * Get Custom Gpt By Id
     * @param customGptId
     * @returns ExistingCustomGPT Successful Response
     * @throws ApiError
     */
    public static getCustomGptByIdGetCustomGptInfosGet(
        customGptId: number,
    ): CancelablePromise<ExistingCustomGPT> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/get-custom-gpt-infos',
            query: {
                'custom_gpt_id': customGptId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Custom Gpt Endpoint
     * @param customGptId
     * @returns DeleteCustomGPTStatus Successful Response
     * @throws ApiError
     */
    public static deleteCustomGptEndpointDeleteCustomGptDelete(
        customGptId: number,
    ): CancelablePromise<DeleteCustomGPTStatus> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/delete-custom-gpt',
            query: {
                'custom_gpt_id': customGptId,
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
    public static createCustomGptCreateOrEditCustomGptPost(
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
}
