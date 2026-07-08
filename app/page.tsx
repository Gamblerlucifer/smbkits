const apps = [
  {
    name: "Profit Guard",
    status: "Live",
    href: "/apps/profit-guard",
    desc: "Flags unprofitable orders in real time — cost, shipping, discounts, and fees included.",
  },
  {
    name: "Ops Connector",
    status: "Coming soon",
    href: null,
    desc: "Syncs live product and order data into Airtable, Monday, or ClickUp — the tools your team already plans in.",
  },
  {
    name: "Ledger Sync",
    status: "Exploring",
    href: null,
    desc: "A Shopify-to-accounting connector that actually reconciles fees, returns, and tax correctly.",
  },
];

export default function Home() {
  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-100">
      <nav className="flex items-center justify-between px-8 py-6 border-b border-neutral-800">
        <span className="text-lg font-semibold tracking-tight">SMBkits</span>
        <div className="flex items-center gap-6 text-sm text-neutral-400">
          {apps
            .filter((a) => a.href)
            .map((a) => (
              <a key={a.name} href={a.href!} className="hover:text-neutral-100 transition">
                {a.name}
              </a>
            ))}
        </div>
      </nav>

      <section className="max-w-3xl mx-auto px-6 pt-28 pb-16 text-center">
        <p className="text-sm uppercase tracking-widest text-emerald-400 mb-6">
          Small, Focused Tools for Shopify Merchants
        </p>
        <h1 className="text-4xl sm:text-6xl font-semibold tracking-tight leading-tight mb-6">
          One job, done well.<br />No bloat.
        </h1>
        <p className="text-lg text-neutral-400 max-w-xl mx-auto leading-relaxed">
          We build narrow Shopify apps that solve one real operational problem
          — not another all-in-one dashboard. Each app does one job merchants
          actually pay to have solved.
        </p>
      </section>

      <section className="max-w-3xl mx-auto px-6 pb-28">
        <div className="border border-neutral-800 divide-y divide-neutral-800 rounded-xl overflow-hidden">
          {apps.map((app) => {
            const Wrapper = app.href ? "a" : "div";
            return (
              <Wrapper
                key={app.name}
                {...(app.href ? { href: app.href } : {})}
                className="flex items-center justify-between gap-6 px-6 py-5 hover:bg-neutral-900 transition"
              >
                <div>
                  <div className="flex items-center gap-3 mb-1">
                    <span className="font-medium">{app.name}</span>
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full border ${
                        app.status === "Live"
                          ? "text-emerald-400 border-emerald-800"
                          : "text-neutral-500 border-neutral-700"
                      }`}
                    >
                      {app.status}
                    </span>
                  </div>
                  <p className="text-sm text-neutral-400">{app.desc}</p>
                </div>
                {app.href && <span className="text-neutral-600">→</span>}
              </Wrapper>
            );
          })}
        </div>
      </section>

      <footer className="border-t border-neutral-800 px-8 py-6 text-center text-sm text-neutral-500">
        © 2026 SMBkits
      </footer>
    </main>
  );
}
