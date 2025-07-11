/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssistantMessage } from '../models/AssistantMessage';
import type { ChatHistory } from '../models/ChatHistory';
import type { ChatSummary } from '../models/ChatSummary';
import type { UserMessageRequest } from '../models/UserMessageRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ChatService {
    /**
     * Get Chat History
     * @param chatId
     * @returns ChatHistory Successful Response
     * @throws ApiError
     */
    public static chatHistoryById(
        chatId: number,
    ): CancelablePromise<ChatHistory> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/chat-history-by-id',
            query: {
                'chat_id': chatId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Chat Summaries
     * @returns ChatSummary Successful Response
     * @throws ApiError
     */
    public static getChatSummaries(): CancelablePromise<Array<ChatSummary>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/get-chat-summaries',
        });
    }
    /**
     * Send User Message
     * @param requestBody
     * @returns AssistantMessage Successful Response
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
