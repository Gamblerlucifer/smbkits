"use client";

import { useState } from "react";

function normalizeShopDomain(input: string): string | null {
  const trimmed = input.trim().toLowerCase();
  if (!trimmed) return null;
  const withoutProtocol = trimmed.replace(/^https?:\/\//, "");
  const domain = withoutProtocol.includes(".myshopify.com")
    ? withoutProtocol
    : `${withoutProtocol.replace(/\.myshopify\.com$/, "")}.myshopify.com`;
  return /^[a-zA-Z0-9][a-zA-Z0-9-]*\.myshopify\.com$/.test(domain) ? domain : null;
}

export default function InstallForm({
  buttonLabel = "Install on Shopify",
  fullWidth = false,
}: {
  buttonLabel?: string;
  fullWidth?: boolean;
}) {
  const [value, setValue] = useState("");
  const [error, setError] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const shop = normalizeShopDomain(value);
    if (!shop) {
      setError("Enter your store's .myshopify.com address");
      return;
    }
    window.location.href = `/api/shopify/install?shop=${shop}`;
  }

  return (
    <form
      onSubmit={handleSubmit}
      className={`flex flex-col ${fullWidth ? "" : "sm:flex-row"} gap-3 w-full`}
    >
      <input
        type="text"
        value={value}
        onChange={(e) => {
          setValue(e.target.value);
          if (error) setError("");
        }}
        placeholder="your-store.myshopify.com"
        className="flex-1 bg-neutral-900 border border-neutral-800 rounded-lg px-4 py-3 text-neutral-100 placeholder:text-neutral-600 focus:outline-none focus:border-emerald-500"
      />
      <button
        type="submit"
        className={`inline-flex items-center justify-center bg-emerald-500 text-neutral-950 font-medium px-8 py-3 rounded-lg hover:bg-emerald-400 transition whitespace-nowrap shadow-[0_0_0_1px_rgba(52,211,153,0.4),0_8px_30px_-8px_rgba(52,211,153,0.5)] ${
          fullWidth ? "w-full" : ""
        }`}
      >
        {buttonLabel}
      </button>
      {error && <p className="text-red-400 text-xs text-left">{error}</p>}
    </form>
  );
}
