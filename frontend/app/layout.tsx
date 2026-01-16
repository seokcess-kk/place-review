import "./globals.css";
import Providers from "./providers";

export const metadata = {
  title: "Place Review Analyzer",
  description: "Analyze place reviews with scraping and GPT insights."
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
