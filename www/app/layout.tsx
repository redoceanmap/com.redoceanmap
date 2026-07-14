import type { Metadata } from "next";
import "./globals.css";
import TopNav from "@/components/seoul/TopNav";
import AuthModal from "@/components/seoul/AuthModal";
import AuthProvider from "@/components/seoul/AuthProvider";
import Providers from "./providers";


export const metadata: Metadata = {
  title: "redoceanmap — 서울 상권 분석",
  description: "예산이랑 업종만 알려주세요. 괜찮은 동네 골라드릴게요.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" className="h-full antialiased">
      <body className="min-h-full flex flex-col">
        <Providers>
          <AuthProvider />
          <TopNav />
          <main className="flex-1 flex flex-col min-h-0">{children}</main>
          <AuthModal />
        </Providers>
      </body>
    </html>
  );
}
