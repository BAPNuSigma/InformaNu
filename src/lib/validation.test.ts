import { describe, expect, it } from "vitest";
import { validateChatRequest } from "./validation";
import { MAX_QUESTION_LENGTH } from "./config";

describe("validateChatRequest", () => {
  it("accepts a valid question", () => {
    const result = validateChatRequest({ question: "What are the membership requirements?" });
    expect(result.valid).toBe(true);
    if (result.valid) {
      expect(result.question).toBe("What are the membership requirements?");
    }
  });

  it("trims whitespace", () => {
    const result = validateChatRequest({ question: "  Hello  " });
    expect(result.valid).toBe(true);
    if (result.valid) {
      expect(result.question).toBe("Hello");
    }
  });

  it("rejects a missing body", () => {
    const result = validateChatRequest(undefined);
    expect(result.valid).toBe(false);
    if (!result.valid) {
      expect(result.error).toBe("Invalid request body.");
    }
  });

  it("rejects a non-string question", () => {
    const result = validateChatRequest({ question: 123 });
    expect(result.valid).toBe(false);
    if (!result.valid) {
      expect(result.error).toBe("A question string is required.");
    }
  });

  it("rejects an empty question", () => {
    const result = validateChatRequest({ question: "   " });
    expect(result.valid).toBe(false);
    if (!result.valid) {
      expect(result.error).toBe("Question cannot be empty.");
    }
  });

  it("rejects an excessively long question", () => {
    const result = validateChatRequest({ question: "a".repeat(MAX_QUESTION_LENGTH + 1) });
    expect(result.valid).toBe(false);
    if (!result.valid) {
      expect(result.error).toContain("maximum length");
    }
  });
});
