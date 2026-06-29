/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DocumentStatus } from '../models/DocumentStatus';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class KnowledgeQueriesService {
    /**
     * Check Status Of Document
     * @param cgptId
     * @returns DocumentStatus Successful Response
     * @throws ApiError
     */
    public static checkStatusOfDocument(
        cgptId: string,
    ): CancelablePromise<DocumentStatus> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/knowledge/check_status_of_document',
            query: {
                'cgpt_id': cgptId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
