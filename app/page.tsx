const apps = [
  {
    name: "Profit Guard",
    status: "Live",
    href: "/apps/profit-guard",
    desc: "Detects unprofitable orders in real time — cost, shipping, discounts, and fees included.",
    icon: (
      <path d="M12 2l9 4.5v9L12 20l-9-4.5v-9L12 2zM12 12v8" />
    ),
  },
  {
    name: "Ops Connector",
    status: "Coming soon",
    href: null,
    desc: "Syncs live product and order data into Airtable, Monday, or ClickUp — the tools your team already plans in.",
    icon: <path d="M4 4h16v4H4zM4 10h10v4H4zM4 16h7v4H4z" />,
  },
  {
    name: "Ledger Sync",
    status: "Exploring",
    href: null,
    desc: "A Shopify-to-accounting connector that actually reconciles fees, returns, and tax correctly.",
    icon: <path d="M9 2h6l3 5v13a2 2 0 01-2 2H8a2 2 0 01-2-2V7l3-5zM9 12h6M9 16h6" />,
  },
];

const principles = [
  {
    title: "Focused",
    desc:
      "Every SMBkits app is built to solve exactly one operational problem — nothing bundled in that you didn't ask for, and nothing you have to configure away.",
  },
  {
    title: "Fair pricing",
    desc:
      "Every SMBkits app costs about the same as one coffee, once — for a full month of service. No tiers, no per-order fees, no surprise upsells.",
  },
  {
    title: "Built for real problems",
    desc:
      "Each app starts from a specific, verifiable gap in what Shopify merchants can already do — not a feature list copied from a bigger competitor.",
  },
];

const steps = [
  {
    n: "01",
    title: "Install in under a minute",
    desc: "Connect your Shopify store through the standard OAuth flow. No credit card required to start.",
  },
  {
    n: "02",
    title: "Set it up once",
    desc: "Tell the app what it needs to know — product cost, shipping rate, whatever's relevant — a single time.",
  },
  {
    n: "03",
    title: "It runs in the background",
    desc: "From then on, the app does its one job automatically on every order, with no ongoing maintenance.",
  },
];

const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      name: "SMBkits",
      url: "https://smbkits.com",
      description:
        "SMBkits builds narrow, focused Shopify apps that solve one real operational problem each.",
    },
    {
      "@type": "WebSite",
      name: "SMBkits",
      url: "https://smbkits.com",
    },
  ],
};

export default function Home() {
  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-100">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <nav className="sticky top-0 z-20 flex items-center justify-between px-6 sm:px-8 py-5 border-b border-neutral-800/80 bg-neutral-950/80 backdrop-blur-md">
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

      {/* HERO */}
      <section className="relative overflow-hidden">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-x-0 -top-40 h-[520px]"
          style={{
            background:
              "radial-gradient(60% 55% at 50% 0%, rgba(52,211,153,0.14) 0%, transparent 70%)",
          }}
        />
        <div className="relative max-w-3xl mx-auto px-6 pt-24 sm:pt-32 pb-20 text-center">
          <span className="inline-flex items-center gap-2 text-xs font-medium uppercase tracking-widest text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 rounded-full px-4 py-1.5 mb-8">
            Small, Focused Tools for Shopify Merchants
          </span>
          <h1 className="text-4xl sm:text-6xl font-semibold tracking-tight leading-[1.05] mb-6">
            One job, done well.
            <br />
            No bloat.
          </h1>
          <p className="text-lg text-neutral-400 max-w-xl mx-auto leading-relaxed">
            We build narrow Shopify apps that solve one real operational
            problem — not another all-in-one dashboard. Each app does one job
            merchants actually pay to have solved.
          </p>
        </div>
      </section>

      {/* APPS */}
      <section className="max-w-3xl mx-auto px-6 pb-24">
        <h2 className="text-sm uppercase tracking-widest text-neutral-400 text-center mb-8">
          Apps
        </h2>
        <div className="grid gap-4">
          {apps.map((app) => {
            const Wrapper = app.href ? "a" : "div";
            return (
              <Wrapper
                key={app.name}
                {...(app.href ? { href: app.href } : {})}
                className={`flex items-center gap-5 px-6 py-6 rounded-2xl border border-neutral-800 bg-neutral-900/40 transition ${
                  app.href ? "hover:border-emerald-500/40 hover:bg-neutral-900" : "opacity-70"
                }`}
              >
                <div className="shrink-0 w-11 h-11 rounded-xl bg-neutral-800 flex items-center justify-center">
                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth={1.5}
                    className="w-5 h-5 text-emerald-400"
                  >
                    {app.icon}
                  </svg>
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1">
                    <span className="font-medium">{app.name}</span>
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full border ${
                        app.status === "Live"
                          ? "text-emerald-400 border-emerald-800"
                          : "text-neutral-400 border-neutral-600"
                      }`}
                    >
                      {app.status}
                    </span>
                  </div>
                  <p className="text-sm text-neutral-400">{app.desc}</p>
                </div>
                {app.href && <span className="text-neutral-600 text-lg">→</span>}
              </Wrapper>
            );
          })}
        </div>
      </section>

      {/* WHY NARROW APPS */}
      <section className="max-w-3xl mx-auto px-6 pb-24">
        <h2 className="text-2xl sm:text-3xl font-semibold text-center mb-6">
          Why we build narrow apps
        </h2>
        <p className="text-neutral-400 text-center max-w-xl mx-auto mb-14 leading-relaxed">
          Most Shopify tooling bundles unrelated features into one
          subscription — analytics, marketing, chat, upsells, reports —
          hoping something in the bundle sticks. Merchants end up paying for
          a dozen capabilities they never open, and configuring away the
          ones that get in the way. SMBkits takes the opposite approach:
          every app we ship solves exactly one problem, is priced for that
          problem alone, and otherwise stays out of your way.
        </p>
        <div className="grid sm:grid-cols-3 gap-8">
          {principles.map((p) => (
            <div key={p.title}>
              <h3 className="font-semibold mb-2">{p.title}</h3>
              <p className="text-sm text-neutral-400 leading-relaxed">{p.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* WHO IT'S FOR */}
      <section className="max-w-3xl mx-auto px-6 pb-24">
        <h2 className="text-2xl sm:text-3xl font-semibold text-center mb-6">
          Who SMBkits is for
        </h2>
        <p className="text-neutral-400 text-center max-w-xl mx-auto leading-relaxed mb-6">
          SMBkits apps are built for merchants running a Shopify store on
          their own, or with a small team — the kind of business where the
          owner is still involved in day-to-day margins, shipping decisions,
          and product pricing, not just looking at a monthly summary someone
          else prepared. If you've ever discovered a problem in your store's
          numbers weeks after it started, that's the gap we're building for.
        </p>
        <p className="text-neutral-400 text-center max-w-xl mx-auto leading-relaxed">
          We&apos;re not trying to be the last app you&apos;ll ever need to
          install. We&apos;d rather be the one app in a specific category
          that you never think about uninstalling, because it quietly keeps
          doing its one job correctly, order after order, without asking you
          to configure a dashboard or learn a new interface.
        </p>
      </section>

      {/* HOW IT WORKS */}
      <section className="max-w-3xl mx-auto px-6 pb-28">
        <h2 className="text-2xl sm:text-3xl font-semibold text-center mb-14">
          How it works
        </h2>
        <div className="grid sm:grid-cols-3 gap-10">
          {steps.map((s) => (
            <div key={s.n}>
              <div className="text-emerald-400 font-mono text-sm mb-3">{s.n}</div>
              <h3 className="font-semibold mb-2">{s.title}</h3>
              <p className="text-sm text-neutral-400 leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
        <p className="text-center mt-14">
          <a
            href="/apps/profit-guard"
            className="inline-flex items-center justify-center bg-emerald-500 text-neutral-950 font-medium px-8 py-3 rounded-lg hover:bg-emerald-400 transition"
          >
            See Profit Guard →
          </a>
        </p>
      </section>

      <footer className="border-t border-neutral-800 px-8 py-6 text-center text-sm text-neutral-400">
        <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 mb-3">
          <a href="/apps/profit-guard" className="hover:text-neutral-100 transition">
            Profit Guard
          </a>
          <a href="/privacy" className="hover:text-neutral-100 transition">
            Privacy Policy
          </a>
          <a href="/terms" className="hover:text-neutral-100 transition">
            Terms of Service
          </a>
        </div>
        © 2026 SMBkits
      </footer>
    </main>
  );
}
