import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "SMBkits — Small, Focused Tools for Shopify Merchants",
    template: "%s | SMBkits",
  },
  description:
    "SMBkits builds narrow, focused Shopify apps that solve one real operational problem each — starting with Profit Guard, real-time order profitability checking.",
  applicationName: "SMBkits",
  generator: "Next.js",
  category: "Business",
  metadataBase: new URL("https://smbkits.com"),
  robots: {
    index: true,
    follow: true,
  },
  icons: {
    icon: "/favicon.ico",
    other: { rel: "icon", url: "/icon.png" },
  },
};

export const viewport = {
  themeColor: "#0A0A0A",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
