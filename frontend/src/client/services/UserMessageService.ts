/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssistantMessage } from '../models/AssistantMessage';
import type { UserMessageRequest } from '../models/UserMessageRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class UserMessageService {
    /**
     * Process the user chat message and send response back from the Model selected, Indentifier = 8
     * @param requestBody
     * @returns AssistantMessage Generates the response from the assistant with a conversation ID
     * @throws ApiError
     */
    public static sendUserMessage(
        requestBody: UserMessageRequest,
    ): CancelablePromise<AssistantMessage> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/send-user-message',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
