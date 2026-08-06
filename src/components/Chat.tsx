"use client";

import { useEffect, useRef, useState } from "react";
import { ChatMessage, MessageRole } from "./ChatMessage";

interface Message {
  role: MessageRole;
  content: string;
}

function createErrorMessage(error: string): Message {
  return { role: "assistant", content: `⚠️ ${error}` };
}

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  async function handleSubmit(event?: React.FormEvent) {
    event?.preventDefault();

    const question = input.trim();
    if (!question || isLoading) {
      return;
    }

    setInput("");
    setError(null);
    setIsLoading(true);

    const userMessage: Message = { role: "user", content: question };
    const assistantPlaceholder: Message = { role: "assistant", content: "" };
    setMessages((prev) => [...prev, userMessage, assistantPlaceholder]);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      if (!response.ok) {
        let errorMessage = "The assistant could not answer your question.";
        try {
          const data = (await response.json()) as { error?: string };
          if (data.error) {
            errorMessage = data.error;
          }
        } catch {
          // Keep default error message.
        }
        throw new Error(errorMessage);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("The assistant response could not be read.");
      }

      const decoder = new TextDecoder();
      let done = false;

      while (!done) {
        const { value, done: streamDone } = await reader.read();
        done = streamDone;
        if (value) {
          const chunk = decoder.decode(value, { stream: !done });
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last && last.role === "assistant") {
              last.content += chunk;
            }
            return updated;
          });
        }
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Something went wrong.";
      setError(message);
      setMessages((prev) => {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        if (last && last.role === "assistant" && last.content.length === 0) {
          updated[updated.length - 1] = createErrorMessage(message);
        } else {
          updated.push(createErrorMessage(message));
        }
        return updated;
      });
    } finally {
      setIsLoading(false);
    }
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void handleSubmit();
    }
  }

  return (
    <>
      <div className="chat-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            Ask your first question below to start the conversation.
          </div>
        ) : (
          <div className="messages">
            {messages.map((message, index) => (
              <ChatMessage
                key={index}
                role={message.role}
                content={message.content}
              />
            ))}
          </div>
        )}
        {isLoading && (
          <div className="loading">
            <span>InformaNu is thinking…</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {error && <div className="error">{error}</div>}

      <form className="input-form" onSubmit={handleSubmit}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask me anything about Beta Alpha Psi: Nu Sigma Chapter..."
          rows={1}
          disabled={isLoading}
          aria-label="Question"
        />
        <button type="submit" disabled={isLoading || !input.trim()}>
          Send
        </button>
      </form>
    </>
  );
}
