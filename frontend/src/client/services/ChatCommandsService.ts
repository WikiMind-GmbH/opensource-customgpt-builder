/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssistantMessage } from '../models/AssistantMessage';
import type { ContinueChatRequest } from '../models/ContinueChatRequest';
import type { NewChatRequest } from '../models/NewChatRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ChatCommandsService {
    /**
     * Send User Message
     * @param requestBody
     * @returns AssistantMessage Successful Response
     * @throws ApiError
     */
    public static sendUserMessage(
        requestBody: (NewChatRequest | ContinueChatRequest),
    ): CancelablePromise<AssistantMessage> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/chat/send-user-message',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
