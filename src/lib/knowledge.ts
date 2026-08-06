import knowledgeArtifact from "@/data/knowledge-base.json";
import { MAX_CONTEXT_CHARS } from "./config";

export interface KnowledgeEntry {
  fileName: string;
  text: string;
}

export interface KnowledgeArtifact {
  generatedAt: string;
  sourceDirectory: string;
  entryCount: number;
  entries: KnowledgeEntry[];
}

const artifact = knowledgeArtifact as KnowledgeArtifact;

export const knowledgeEntries = artifact.entries;

export function getKnowledgeContext(): string {
  const chunks = knowledgeEntries.map(
    (entry) => `--- ${entry.fileName} ---\n${entry.text}`
  );
  const fullContext = chunks.join("\n\n");

  if (fullContext.length > MAX_CONTEXT_CHARS) {
    return fullContext.slice(0, MAX_CONTEXT_CHARS);
  }

  return fullContext;
}

export function hasKnowledgeEntries(): boolean {
  return knowledgeEntries.length > 0;
}
