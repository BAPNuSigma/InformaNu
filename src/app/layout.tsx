import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "InformaNu — Beta Alpha Psi Nu Sigma Q&A",
  description:
    "Ask InformaNu anything about the Beta Alpha Psi Nu Sigma chapter, events, requirements, or history.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
