/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreateOrEditCustomGPTResponse } from '../models/CreateOrEditCustomGPTResponse';
import type { CustomGptToCreate } from '../models/CustomGptToCreate';
import type { CustomGptToEdit } from '../models/CustomGptToEdit';
import type { ExistingCustomGPT } from '../models/ExistingCustomGPT';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class CustomGptService {
    /**
     * Dispalys all the custom GPTs created, Indentfier = 4
     * @returns ExistingCustomGPT Returns a list of custom gpts created
     * @throws ApiError
     */
    public static dispalyAllCustomGpTs(): CancelablePromise<Array<ExistingCustomGPT>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/display-all-custom-gpts',
        });
    }
    /**
     * User chats with Custom GPT, indetifier = 13
     * @param customGptId
     * @returns ExistingCustomGPT Information of Custom GPT so as to the Navigate to its Chat Page
     * @throws ApiError
     */
    public static chatWithCustomGpt(
        customGptId: number,
    ): CancelablePromise<ExistingCustomGPT> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/chat-with-custom-gpt',
            query: {
                'custom_gpt_id': customGptId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Edit the existing custom GPT by navigating to CreateGPT Page with Existing Custom GPT Info, identifier: 14
     * @param customGptId
     * @returns ExistingCustomGPT Send the information about Existing GPT
     * @throws ApiError
     */
    public static navigateToEditCustomGpt(
        customGptId: number,
    ): CancelablePromise<ExistingCustomGPT> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/navigate-to-edit-custom-gpt',
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
     * @returns boolean Send the status of deleted successfully(true) or failure(false)
     * @throws ApiError
     */
    public static deleteExistingCustomGpt(
        customGptId: number,
    ): CancelablePromise<boolean> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/delete-custom-gpt-by-id',
            query: {
                'custom_gpt_id': customGptId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Edit the information of existing Custom GPT, identifier = 11/update
     * @param requestBody
     * @returns CreateOrEditCustomGPTResponse Responds the status of custom gpt updated successfully(true) or failed(false) with custom gpt id
     * @throws ApiError
     */
    public static updateExistingCustomGpt(
        requestBody: CustomGptToEdit,
    ): CancelablePromise<CreateOrEditCustomGPTResponse> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/update-custom-gpt',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Takes the input from user to create a custom gpt (Name, instruction), Indentfier = 11/ create
     * @param requestBody
     * @returns CreateOrEditCustomGPTResponse Responds the status of custom gpt created successfully(true) or failed(false) with custom_gpt_id
     * @throws ApiError
     */
    public static createNewCustomGpt(
        requestBody: CustomGptToCreate,
    ): CancelablePromise<CreateOrEditCustomGPTResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/create-custom-gpt',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
