export const metadata = {
  title: "Profit Guard — Real-Time Order Profitability for Shopify",
};

export default function ProfitGuardPage() {
  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-100">
      <nav className="flex items-center justify-between px-8 py-6 border-b border-neutral-800">
        <a href="/" className="text-lg font-semibold tracking-tight">SMBkits</a>
        <div className="flex items-center gap-6 text-sm text-neutral-400">
          <a href="/apps/profit-guard" className="text-neutral-100">Profit Guard</a>
          <a
            href="https://apps.shopify.com"
            className="hover:text-neutral-100 transition"
          >
            Shopify App Store
          </a>
        </div>
      </nav>

      <section className="max-w-3xl mx-auto px-6 pt-28 pb-20 text-center">
        <p className="text-sm uppercase tracking-widest text-emerald-400 mb-6">
          For Shopify Merchants
        </p>
        <h1 className="text-4xl sm:text-6xl font-semibold tracking-tight leading-tight mb-6">
          Stop shipping orders<br />that lose you money.
        </h1>
        <p className="text-lg text-neutral-400 max-w-xl mx-auto mb-10 leading-relaxed">
          Profit Guard checks every order&apos;s real margin — cost, shipping,
          discounts, and payment fees — the moment it comes in. Know before
          you ship, not after you reconcile.
        </p>
        <a
          href="/api/shopify/install"
          className="inline-flex items-center justify-center bg-emerald-500 text-neutral-950 font-medium px-8 py-3 rounded-lg hover:bg-emerald-400 transition"
        >
          Install on Shopify
        </a>
      </section>

      <section className="max-w-4xl mx-auto px-6 pb-24 grid sm:grid-cols-3 gap-8 text-center">
        <div>
          <div className="text-2xl font-semibold mb-2">Real-time</div>
          <p className="text-neutral-400 text-sm">
            Margin calculated the instant an order is placed, not at month end.
          </p>
        </div>
        <div>
          <div className="text-2xl font-semibold mb-2">No setup cost</div>
          <p className="text-neutral-400 text-sm">
            Enter your costs once. Every future order is checked automatically.
          </p>
        </div>
        <div>
          <div className="text-2xl font-semibold mb-2">Loss alerts</div>
          <p className="text-neutral-400 text-sm">
            Get notified the moment an order is shipping at a loss.
          </p>
        </div>
      </section>

      <footer className="border-t border-neutral-800 px-8 py-6 text-center text-sm text-neutral-500">
        © 2026 SMBkits · Profit Guard
      </footer>
    </main>
  );
}
