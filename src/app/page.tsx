import { APP_DESCRIPTION, APP_TITLE } from "@/lib/config";
import { Chat } from "@/components/Chat";

export default function Home() {
  return (
    <main>
      <header>
        <h1>{APP_TITLE}</h1>
        <p>{APP_DESCRIPTION}</p>
      </header>
      <Chat />
    </main>
  );
}
