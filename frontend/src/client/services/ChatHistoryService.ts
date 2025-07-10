/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChatHistory } from '../models/ChatHistory';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ChatHistoryService {
    /**
     * Fetches the history of a particular chat id. Identifier = 5
     * @param chatId
     * @returns ChatHistory retrives the list of messages and Model ID (0: ChatGPT40, -1: Error, 1/custom_gpt_id: CustomGPTName)
     * @throws ApiError
     */
    public static getChatHistoryById(
        chatId: number,
    ): CancelablePromise<ChatHistory> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/chat_history_by_id',
            query: {
                'chat_id': chatId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
