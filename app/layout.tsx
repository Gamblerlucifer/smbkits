import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "SMBkits — Small, Focused Tools for Shopify Merchants",
    template: "%s | SMBkits",
  },
  description:
    "SMBkits builds narrow, focused Shopify apps that solve one real operational problem each — starting with Profit Guard, a real-time order profitability checker.",
  applicationName: "SMBkits",
  generator: "Next.js",
  category: "Business",
  metadataBase: new URL("https://smbkits.com"),
  keywords: [
    "shopify profit calculator",
    "shopify order profitability app",
    "shopify margin tracker",
    "shopify profit margin app",
    "shopify apps for merchants",
    "shopify unprofitable orders alert",
  ],
  alternates: {
    canonical: "https://smbkits.com",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true, "max-image-preview": "large" },
  },
  openGraph: {
    siteName: "SMBkits",
    title: "SMBkits — Small, Focused Tools for Shopify Merchants",
    description:
      "Narrow, focused Shopify apps that solve one real operational problem each.",
    type: "website",
    url: "https://smbkits.com",
    locale: "en_US",
  },
  twitter: {
    card: "summary",
    title: "SMBkits — Small, Focused Tools for Shopify Merchants",
    description:
      "Narrow, focused Shopify apps that solve one real operational problem each.",
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
