import { describe, expect, it } from "vitest";
import { getKnowledgeContext, hasKnowledgeEntries, knowledgeEntries } from "./knowledge";

describe("knowledge base", () => {
  it("has loaded entries from the generated artifact", () => {
    expect(hasKnowledgeEntries()).toBe(true);
    expect(knowledgeEntries.length).toBeGreaterThan(0);
  });

  it("includes expected source files", () => {
    const names = knowledgeEntries.map((entry) => entry.fileName);
    expect(names).toContain("spring_2026_schedule.md");
  });

  it("does not silently omit document text", () => {
    for (const entry of knowledgeEntries) {
      expect(entry.text.length).toBeGreaterThan(0);
    }
  });

  it("produces a non-empty context string", () => {
    const context = getKnowledgeContext();
    expect(context.length).toBeGreaterThan(0);
    expect(context).toContain("spring_2026_schedule.md");
  });
});
