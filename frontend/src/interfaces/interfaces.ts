export interface CreateOrEditCustomGPTForm {
  custom_gpt_name: string,
  custom_gpt_description: string,
  custom_gpt_instructions: string,
}

export enum Role{
  USER = 'user',
  CHATBOT_RESPONSE_FOR_USER = 'chatbotResponseForUser',
}

export type CustomGptInfo = {
  customgptIdOrNullIfDefault: number;
  customGptName: string;
};