/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DocumentStatusDTO } from '../models/DocumentStatusDTO';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class KnowledgeQueriesService {
    /**
     * Check Status Of Document
     * @param documentId
     * @param cgptId
     * @returns DocumentStatusDTO Successful Response
     * @throws ApiError
     */
    public static checkStatusOfDocument(
        documentId: string,
        cgptId: string,
    ): CancelablePromise<DocumentStatusDTO> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/knowledge/check_status_of_document',
            query: {
                'document_id': documentId,
                'cgpt_id': cgptId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
