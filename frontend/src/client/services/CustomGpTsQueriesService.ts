/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CustomGPTInfosSchema } from '../models/CustomGPTInfosSchema';
import type { CustomGPTOverviewSchema } from '../models/CustomGPTOverviewSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class CustomGpTsQueriesService {
    /**
     * Retreive All Custom Gpts
     * @returns CustomGPTOverviewSchema Successful Response
     * @throws ApiError
     */
    public static retreiveAllCustomGpts(): CancelablePromise<Array<CustomGPTOverviewSchema>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/customgpts/retreive-all-custom-gpts',
        });
    }
    /**
     * Get Custom Gpt By Id
     * @param customGptId
     * @returns CustomGPTInfosSchema Successful Response
     * @throws ApiError
     */
    public static getCustomGptInfos(
        customGptId: string,
    ): CancelablePromise<CustomGPTInfosSchema> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/customgpts/get-custom-gpt-infos',
            query: {
                'custom_gpt_id': customGptId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
