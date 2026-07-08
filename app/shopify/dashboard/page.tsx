import { redirect } from "next/navigation";
import CostForm from "./CostForm";
import { getRecentOrderResults, isSubscribed } from "@/lib/shopify";

export default async function DashboardPage({
  searchParams,
}: {
  searchParams: Promise<{ shop?: string; billing?: string }>;
}) {
  const { shop, billing } = await searchParams;

  if (!shop) {
    return (
      <main className="min-h-screen bg-neutral-950 text-neutral-100 flex items-center justify-center px-6">
        <p className="text-neutral-400">Missing shop parameter.</p>
      </main>
    );
  }

  const skipBilling = process.env.SHOPIFY_SKIP_BILLING === "true";
  const subscribed = skipBilling || (await isSubscribed(shop));

  if (!subscribed && billing !== "declined") {
    redirect(`/api/shopify/billing?shop=${shop}`);
  }

  if (!subscribed && billing === "declined") {
    return (
      <main className="min-h-screen bg-neutral-950 text-neutral-100 flex items-center justify-center px-6">
        <div className="max-w-sm text-center">
          <h1 className="text-2xl font-semibold mb-4">Trial not started</h1>
          <p className="text-neutral-400 mb-8">
            You didn&apos;t complete the $5/mo plan approval, so Profit Guard
            isn&apos;t active on {shop} yet.
          </p>
          <a
            href={`/api/shopify/billing?shop=${shop}`}
            className="inline-flex items-center justify-center bg-emerald-500 text-neutral-950 font-medium px-8 py-3 rounded-lg hover:bg-emerald-400 transition"
          >
            Start free trial
          </a>
        </div>
      </main>
    );
  }

  const orders = await getRecentOrderResults(shop, 20);
  const lossOrders = orders.filter((o) => o.isLoss);
  const lossTotal = lossOrders.reduce((sum, o) => sum + Math.abs(o.margin), 0);

  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-100">
      {orders.length > 0 && (
        <section className="max-w-2xl mx-auto px-6 pt-16">
          <div className="grid sm:grid-cols-2 gap-4 mb-10">
            <div className="rounded-xl border border-neutral-800 bg-neutral-900/40 px-6 py-5">
              <div className="text-2xl font-semibold text-red-400">
                {lossOrders.length}
              </div>
              <div className="text-sm text-neutral-400">Loss-making orders (recent)</div>
            </div>
            <div className="rounded-xl border border-neutral-800 bg-neutral-900/40 px-6 py-5">
              <div className="text-2xl font-semibold text-red-400">
                −${lossTotal.toFixed(2)}
              </div>
              <div className="text-sm text-neutral-400">Total loss caught</div>
            </div>
          </div>

          <div className="border border-neutral-800 rounded-xl divide-y divide-neutral-800 mb-4 overflow-hidden">
            {orders.slice(0, 10).map((o) => (
              <div
                key={o.orderId}
                className="flex items-center justify-between px-5 py-3 text-sm"
              >
                <span className="font-mono text-neutral-300">{o.orderNumber}</span>
                <span className="text-neutral-400">${o.total.toFixed(2)}</span>
                <span
                  className={`font-medium px-2 py-0.5 rounded-md ${
                    o.isLoss
                      ? "text-red-400 bg-red-500/10"
                      : "text-emerald-400 bg-emerald-500/10"
                  }`}
                >
                  {o.margin >= 0 ? "+" : ""}
                  {o.margin.toFixed(2)}
                </span>
              </div>
            ))}
          </div>
        </section>
      )}

      <CostForm shop={shop} />
    </main>
  );
}
