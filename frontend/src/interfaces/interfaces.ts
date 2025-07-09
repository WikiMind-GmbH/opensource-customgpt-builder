export interface CreateOrEditCustomGPTForm {
  custom_gpt_name: string;
  description: string;
  instruction: string;
}

export enum Role{
  USER = 'user',
  CHATBOT_RESPONSE_FOR_USER = 'chatbotResponseForUser',
}