/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChatSummary } from '../models/ChatSummary';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ChatSummaryService {
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
}
