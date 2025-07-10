/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreateCustomGPTResponse } from '../models/CreateCustomGPTResponse';
import type { CustomGPTInfos } from '../models/CustomGPTInfos';
import type { ExistingCustomGPT } from '../models/ExistingCustomGPT';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class CustomGptService {
    /**
     * Dispalys all the custom GPTs created
     * @returns ExistingCustomGPT Returns a list of custom gpts created
     * @throws ApiError
     */
    public static displayAllCustomGptsDisplayAllCustomGptsGet(): CancelablePromise<Array<ExistingCustomGPT>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/display-all-custom-gpts',
        });
    }
    /**
     * Takes the input from user to create a custom gpt (Name, instruction)
     * @param requestBody
     * @returns CreateCustomGPTResponse Responds the status of custom gpt created successfully(true) or failure(false) with custom_gpt_id
     * @throws ApiError
     */
    public static createCustomGptCreateCustomGptPost(
        requestBody: CustomGPTInfos,
    ): CancelablePromise<CreateCustomGPTResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/create_custom_gpt',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
