import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "SMBkits Profit Guard — Real-Time Order Profitability for Shopify",
    template: "%s | SMBkits Profit Guard",
  },
  description:
    "Catch unprofitable orders before they ship. SMBkits Profit Guard checks every Shopify order's margin in real time — costs, shipping, and fees included.",
  applicationName: "SMBkits Profit Guard",
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
