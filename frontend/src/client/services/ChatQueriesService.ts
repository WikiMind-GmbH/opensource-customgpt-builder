/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChatHistory } from '../models/ChatHistory';
import type { ChatSummary } from '../models/ChatSummary';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ChatQueriesService {
    /**
     * Get Chat Summaries
     * @returns ChatSummary Successful Response
     * @throws ApiError
     */
    public static getChatSummaries(): CancelablePromise<Array<ChatSummary>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/chat/get-chat-summaries',
        });
    }
    /**
     * Get Chat History
     * @param chatId
     * @returns ChatHistory Successful Response
     * @throws ApiError
     */
    public static chatHistoryById(
        chatId: string,
    ): CancelablePromise<ChatHistory> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/chat/chat-history-by-id',
            query: {
                'chat_id': chatId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
