import CostForm from "./CostForm";
import { getRecentOrderResults } from "@/lib/shopify";

export default async function DashboardPage({
  searchParams,
}: {
  searchParams: Promise<{ shop?: string }>;
}) {
  const { shop } = await searchParams;

  if (!shop) {
    return (
      <main className="min-h-screen bg-neutral-950 text-neutral-100 flex items-center justify-center px-6">
        <p className="text-neutral-400">Missing shop parameter.</p>
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
