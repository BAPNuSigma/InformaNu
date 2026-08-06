import { describe, expect, it } from "vitest";
import { OPENAI_MODEL_DEFAULT, SYSTEM_PROMPT } from "./config";

describe("configuration", () => {
  it("restricts answers to the supplied knowledge-base context", () => {
    expect(SYSTEM_PROMPT).toContain("ONLY the supplied knowledge-base context");
    expect(SYSTEM_PROMPT).toContain("Not answer unrelated questions using general model knowledge");
    expect(SYSTEM_PROMPT).toContain("do not have that information in the InformaNu knowledge base");
  });

  it("names the assistant and chapter", () => {
    expect(SYSTEM_PROMPT).toContain("InformaNu");
    expect(SYSTEM_PROMPT).toContain("Beta Alpha Psi Nu Sigma");
  });

  it("uses a current cost-efficient default model", () => {
    expect(OPENAI_MODEL_DEFAULT).toContain("gpt-4o-mini");
  });
});
