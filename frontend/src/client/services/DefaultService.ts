/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssistantMessage } from '../models/AssistantMessage';
import type { ChatHistory } from '../models/ChatHistory';
import type { CreateCustomGPTResponse } from '../models/CreateCustomGPTResponse';
import type { CustomGPTInfos } from '../models/CustomGPTInfos';
import type { ExistingCustomGPT } from '../models/ExistingCustomGPT';
import type { ModelName } from '../models/ModelName';
import type { RetreiveChatHistory } from '../models/RetreiveChatHistory';
import type { StatusOfStandardResponse } from '../models/StatusOfStandardResponse';
import type { UserMessageRequest } from '../models/UserMessageRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DefaultService {
    /**
     * Root
     * @returns any Successful Response
     * @throws ApiError
     */
    public static rootGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/',
        });
    }
    /**
     * Get Chat History
     * @param requestBody
     * @returns ChatHistory Successful Response
     * @throws ApiError
     */
    public static getChatHistoryChatHistoryByIdPost(
        requestBody: RetreiveChatHistory,
    ): CancelablePromise<ChatHistory> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/chat_history_by_id',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Chats One Liner
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getChatsOneLinerChatsListByOneLinerGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/chats_list_by_one_liner',
        });
    }
    /**
     * Get Model Name
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getModelNameGetModelNameGet(
        requestBody: ModelName,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/get_model_name',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Send User Message
     * @param requestBody
     * @returns AssistantMessage Successful Response
     * @throws ApiError
     */
    public static sendUserMessageSendUserMessagePost(
        requestBody: UserMessageRequest,
    ): CancelablePromise<AssistantMessage> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/send_user_message',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Read Custom Gpt By Id
     * @param id
     * @returns ExistingCustomGPT Successful Response
     * @throws ApiError
     */
    public static readCustomGptByIdRetrieveCustomGptByIdGet(
        id: number,
    ): CancelablePromise<ExistingCustomGPT> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/retrieve_custom_gpt_by_id',
            query: {
                'id': id,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Edit Custom Gpt
     * @param requestBody
     * @returns StatusOfStandardResponse Successful Response
     * @throws ApiError
     */
    public static editCustomGptEditCustomGptPost(
        requestBody: ExistingCustomGPT,
    ): CancelablePromise<StatusOfStandardResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/edit_custom_gpt',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Custom Gpt
     * @param requestBody
     * @returns CreateCustomGPTResponse Successful Response
     * @throws ApiError
     */
    public static createCustomGptCreateCustomGptPost(
        requestBody: CustomGPTInfos,
    ): CancelablePromise<CreateCustomGPTResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/create_custom_gpt',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
