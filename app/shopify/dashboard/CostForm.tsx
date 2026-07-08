"use client";

import { useEffect, useState } from "react";

interface Product {
  id: number;
  title: string;
  variants: { id: number; price: string }[];
}

export default function CostForm({ shop }: { shop: string }) {
  const [products, setProducts] = useState<Product[]>([]);
  const [shippingCost, setShippingCost] = useState(0);
  const [feePercent, setFeePercent] = useState(0);
  const [productCosts, setProductCosts] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    async function load() {
      const [productsRes, costsRes] = await Promise.all([
        fetch(`/api/shopify/products?shop=${shop}`),
        fetch(`/api/shopify/costs?shop=${shop}`),
      ]);

      if (productsRes.ok) {
        const data = await productsRes.json();
        setProducts(data.products);
      } else {
        setError("Could not load products from Shopify.");
      }

      if (costsRes.ok) {
        const data = await costsRes.json();
        setShippingCost(data.shippingCost ?? 0);
        setFeePercent(data.feePercent ?? 0);
        setProductCosts(data.productCosts ?? {});
      }

      setLoading(false);
    }
    load();
  }, [shop]);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setSaved(false);
    await fetch("/api/shopify/costs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ shop, shippingCost, feePercent, productCosts }),
    });
    setSaving(false);
    setSaved(true);
  }

  if (loading) {
    return <p className="text-neutral-400 text-center py-24">Loading products…</p>;
  }

  return (
    <form onSubmit={handleSave} className="max-w-2xl mx-auto px-6 py-16">
      <h1 className="text-2xl font-semibold mb-2">Cost setup</h1>
      <p className="text-neutral-400 mb-10">
        Connected to {shop}. Set your costs once — every order is checked
        automatically from now on.
      </p>

      {error && <p className="text-red-400 text-sm mb-6">{error}</p>}

      <div className="grid sm:grid-cols-2 gap-6 mb-10">
        <label className="block">
          <span className="text-sm text-neutral-400 mb-2 block">
            Shipping cost per order ($)
          </span>
          <input
            type="number"
            step="0.01"
            min="0"
            value={shippingCost}
            onChange={(e) => setShippingCost(parseFloat(e.target.value) || 0)}
            className="w-full bg-neutral-900 border border-neutral-800 rounded-lg px-4 py-2.5 text-neutral-100 focus:outline-none focus:border-emerald-500"
          />
        </label>
        <label className="block">
          <span className="text-sm text-neutral-400 mb-2 block">
            Payment processing fee (%)
          </span>
          <input
            type="number"
            step="0.01"
            min="0"
            value={feePercent}
            onChange={(e) => setFeePercent(parseFloat(e.target.value) || 0)}
            className="w-full bg-neutral-900 border border-neutral-800 rounded-lg px-4 py-2.5 text-neutral-100 focus:outline-none focus:border-emerald-500"
          />
        </label>
      </div>

      <h2 className="text-lg font-medium mb-4">Product costs</h2>
      <div className="border border-neutral-800 rounded-lg divide-y divide-neutral-800 mb-10">
        {products.length === 0 && (
          <p className="text-neutral-400 text-sm px-4 py-6">
            No products found in this store.
          </p>
        )}
        {products.map((p) => (
          <div key={p.id} className="flex items-center justify-between gap-4 px-4 py-3">
            <div>
              <div className="text-sm">{p.title}</div>
              <div className="text-xs text-neutral-400">
                Sells for ${p.variants[0]?.price ?? "—"}
              </div>
            </div>
            <input
              type="number"
              step="0.01"
              min="0"
              placeholder="Cost ($)"
              value={productCosts[p.id] ?? ""}
              onChange={(e) =>
                setProductCosts((prev) => ({
                  ...prev,
                  [p.id]: parseFloat(e.target.value) || 0,
                }))
              }
              className="w-28 bg-neutral-900 border border-neutral-800 rounded-lg px-3 py-1.5 text-sm text-neutral-100 focus:outline-none focus:border-emerald-500"
            />
          </div>
        ))}
      </div>

      <button
        type="submit"
        disabled={saving}
        className="bg-emerald-500 text-neutral-950 font-medium px-6 py-2.5 rounded-lg hover:bg-emerald-400 transition disabled:opacity-50"
      >
        {saving ? "Saving…" : "Save costs"}
      </button>
      {saved && <span className="ml-4 text-sm text-emerald-400">Saved.</span>}
    </form>
  );
}
