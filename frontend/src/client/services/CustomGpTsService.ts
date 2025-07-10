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
     * Dispalys all the custom GPTs created, Indentfier = 4
     * @returns ExistingCustomGPT Returns a list of custom gpts created
     * @throws ApiError
     */
    public static retreiveAllCustomGpTs(): CancelablePromise<Array<ExistingCustomGPT>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/retreive-all-custom-gpts',
        });
    }
    /**
     * User chats with Custom GPT, indetifier = 13
     * @param customGptId
     * @returns ExistingCustomGPT Information of Custom GPT so as to the Navigate to its Chat Page
     * @throws ApiError
     */
    public static getCustomGptInfos(
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
     * delete the existing custom GPT by ID, identifier = 15
     * @param customGptId
     * @returns DeleteCustomGPTStatus Send the status of deleted successfully(true) or failure(false)
     * @throws ApiError
     */
    public static deleteCustomGpt(
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
     * Takes the input from user to create a custom gpt (Name, instruction), Indentfier = 11/ create
     * @param requestBody
     * @returns CreateOrEditCustomGPTStatus Responds the status of custom gpt created successfully(true) or failed(false) with custom_gpt_id
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
}
