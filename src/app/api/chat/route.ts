import { NextResponse } from "next/server";
import {
  MAX_OUTPUT_TOKENS,
  OPENAI_MODEL_DEFAULT,
  SYSTEM_PROMPT,
} from "@/lib/config";
import { getKnowledgeContext, hasKnowledgeEntries } from "@/lib/knowledge";
import { getOpenAIClient } from "@/lib/openai";
import { validateChatRequest } from "@/lib/validation";

export const runtime = "nodejs";

export async function POST(request: Request) {
  let body: unknown;

  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body." }, { status: 400 });
  }

  const validation = validateChatRequest(body);

  if (!validation.valid) {
    return NextResponse.json({ error: validation.error }, { status: 400 });
  }

  if (!hasKnowledgeEntries()) {
    return NextResponse.json(
      { error: "The knowledge base is currently unavailable." },
      { status: 503 }
    );
  }

  let openai;
  try {
    openai = getOpenAIClient();
  } catch {
    return NextResponse.json(
      { error: "The assistant is not configured correctly." },
      { status: 500 }
    );
  }

  const model = process.env.OPENAI_MODEL || OPENAI_MODEL_DEFAULT;
  const context = getKnowledgeContext();
  const input = `Context from knowledge base:\n${context}\n\nUser question: ${validation.question}`;

  try {
    const stream = openai.responses.stream({
      model,
      instructions: SYSTEM_PROMPT,
      input,
      max_output_tokens: MAX_OUTPUT_TOKENS,
    });

    const encoder = new TextEncoder();

    const readable = new ReadableStream({
      async start(controller) {
        try {
          for await (const event of stream) {
            if (event.type === "response.output_text.delta") {
              const delta = (event as { delta?: string }).delta;
              if (delta) {
                controller.enqueue(encoder.encode(delta));
              }
            }
          }
          controller.close();
        } catch (error) {
          controller.error(error);
        }
      },
    });

    return new NextResponse(readable, {
      headers: {
        "Content-Type": "text/plain; charset=utf-8",
      },
    });
  } catch {
    return NextResponse.json(
      { error: "The assistant encountered an error. Please try again." },
      { status: 500 }
    );
  }
}
