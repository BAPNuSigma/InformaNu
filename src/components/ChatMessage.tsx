"use client";

import Image from "next/image";

export type MessageRole = "user" | "assistant";

export interface ChatMessageProps {
  role: MessageRole;
  content: string;
}

const AVATARS: Record<MessageRole, string> = {
  user: "https://i.ibb.co/K9FCHHS/BAP-B-W-Logo.jpg",
  assistant:
    "https://upload.wikimedia.org/wikipedia/en/6/6a/Fairleigh_Dickinson_University_seal.png",
};

const ALTS: Record<MessageRole, string> = {
  user: "BAP Nu Sigma user avatar",
  assistant: "InformaNu assistant avatar",
};

export function ChatMessage({ role, content }: ChatMessageProps) {
  return (
    <div className={`chat-message ${role}`}>
      <div className="avatar">
        <Image
          src={AVATARS[role]}
          alt={ALTS[role]}
          width={48}
          height={48}
          unoptimized
        />
      </div>
      <div className="message-body" style={{ whiteSpace: "pre-wrap" }}>
        {content}
      </div>
    </div>
  );
}
