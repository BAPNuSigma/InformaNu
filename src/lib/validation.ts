import { MAX_QUESTION_LENGTH } from "./config";

export interface ChatRequest {
  question: string;
}

export function validateChatRequest(body: unknown): { valid: true; question: string } | { valid: false; error: string } {
  if (typeof body !== "object" || body === null) {
    return { valid: false, error: "Invalid request body." };
  }

  const { question } = body as Record<string, unknown>;

  if (typeof question !== "string") {
    return { valid: false, error: "A question string is required." };
  }

  const trimmed = question.trim();

  if (trimmed.length === 0) {
    return { valid: false, error: "Question cannot be empty." };
  }

  if (trimmed.length > MAX_QUESTION_LENGTH) {
    return {
      valid: false,
      error: `Question exceeds the maximum length of ${MAX_QUESTION_LENGTH} characters.`,
    };
  }

  return { valid: true, question: trimmed };
}
