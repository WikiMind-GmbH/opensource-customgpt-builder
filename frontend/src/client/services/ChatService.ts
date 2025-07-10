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
     * One Liner summary of all chats in the Chat List.  Identifier = 3
     * @returns ChatSummary List of chats summary in one line with a Chat ID
     * @throws ApiError
     */
    public static getChatSummaries(): CancelablePromise<Array<ChatSummary>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/get-chat-summaries',
        });
    }
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
