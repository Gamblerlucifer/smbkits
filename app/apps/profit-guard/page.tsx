import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Profit Guard — Real-Time Order Profitability for Shopify",
  description:
    "Detect unprofitable Shopify orders in real time. Calculate true profit including product cost, shipping, payment fees and taxes before losses accumulate.",
  keywords: [
    "shopify profit app",
    "shopify profit calculator",
    "shopify profit tracker",
    "shopify profit margin",
    "shopify order profit",
    "shopify order margin",
    "shopify cost calculator",
    "shopify product cost",
    "shopify margin calculator",
    "shopify shipping cost calculator",
    "shopify fee calculator",
    "shopify cost of goods",
    "shopify gross margin",
    "real time profit tracking for shopify",
    "shopify detect unprofitable orders",
    "prevent loss making orders shopify",
    "shopify order profitability",
    "shopify profit by product",
    "shopify cost tracking app",
  ],
  alternates: {
    canonical: "https://smbkits.com/apps/profit-guard",
  },
  openGraph: {
    title: "Profit Guard — Real-Time Order Profitability for Shopify",
    description:
      "Detect unprofitable Shopify orders in real time. Calculate true profit including product cost, shipping, payment fees and taxes before losses accumulate.",
    url: "https://smbkits.com/apps/profit-guard",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Profit Guard — Real-Time Order Profitability for Shopify",
    description:
      "Detect unprofitable Shopify orders in real time, before losses accumulate.",
  },
};

const faqs = [
  {
    q: "How do I know if a Shopify order is profitable?",
    a: "An order is profitable when its total revenue exceeds product cost, shipping cost, and payment processing fees combined. Profit Guard calculates this automatically for every order the moment it's placed, using the cost data you set up once.",
  },
  {
    q: "Why is my Shopify store not profitable even with steady sales?",
    a: "Revenue and conversion rate don't show true profit. Discounts, shipping costs, and payment fees can silently turn a sale into a loss. Many stores have a meaningful share of orders that lose money without the owner noticing, because standard Shopify analytics don't surface per-order margin.",
  },
  {
    q: "Does Profit Guard replace profit analytics apps like BeProfit or TrueProfit?",
    a: "No — those tools are built for after-the-fact reporting and dashboards. Profit Guard is focused on one thing: detecting a loss-making order in real time, before it ships, so you can act on it immediately rather than discover it in a monthly report.",
  },
];

const features = [
  {
    icon: (
      <path d="M12 6v6l4 2M12 22a10 10 0 100-20 10 10 0 000 20z" />
    ),
    title: "Real-time",
    desc: "Margin calculated the instant an order is placed, not at month end.",
  },
  {
    icon: <path d="M12 2l9 4.5v9L12 20l-9-4.5v-9L12 2zM12 12v8" />,
    title: "No setup cost",
    desc: "Enter your costs once. Every future order is checked automatically.",
  },
  {
    icon: (
      <path d="M12 9v4m0 4h.01M10.29 3.86l-8.18 14.14A2 2 0 004 21h16a2 2 0 001.89-3l-8.18-14.14a2 2 0 00-3.42 0z" />
    ),
    title: "Loss alerts",
    desc: "Get notified the moment an order is shipping at a loss.",
  },
];

const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      name: "SMBkits",
      url: "https://smbkits.com",
    },
    {
      "@type": "WebSite",
      name: "SMBkits",
      url: "https://smbkits.com",
    },
    {
      "@type": "SoftwareApplication",
      name: "Profit Guard",
      applicationCategory: "BusinessApplication",
      operatingSystem: "Shopify",
      description:
        "Real-time order profitability checker for Shopify. Detects unprofitable orders the moment they're placed, accounting for product cost, shipping, discounts, and payment processing fees.",
      offers: {
        "@type": "Offer",
        priceCurrency: "USD",
        price: "5",
      },
      publisher: {
        "@type": "Organization",
        name: "SMBkits",
        url: "https://smbkits.com",
      },
    },
    {
      "@type": "FAQPage",
      mainEntity: faqs.map((f) => ({
        "@type": "Question",
        name: f.q,
        acceptedAnswer: { "@type": "Answer", text: f.a },
      })),
    },
  ],
};

export default function ProfitGuardPage() {
  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-100">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <nav className="sticky top-0 z-20 flex items-center justify-between px-6 sm:px-8 py-5 border-b border-neutral-800/80 bg-neutral-950/80 backdrop-blur-md">
        <a href="/" className="text-lg font-semibold tracking-tight">
          SMBkits
        </a>
        <div className="flex items-center gap-6 text-sm text-neutral-400">
          <a href="/apps/profit-guard" className="text-neutral-100">
            Profit Guard
          </a>
          <a href="https://apps.shopify.com" className="hover:text-neutral-100 transition">
            Shopify App Store
          </a>
        </div>
      </nav>

      {/* HERO */}
      <section className="relative overflow-hidden">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-x-0 -top-40 h-[560px]"
          style={{
            background:
              "radial-gradient(60% 55% at 50% 0%, rgba(52,211,153,0.16) 0%, transparent 70%)",
          }}
        />
        <div className="relative max-w-3xl mx-auto px-6 pt-24 sm:pt-32 pb-16 text-center">
          <span className="inline-flex items-center gap-2 text-xs font-medium uppercase tracking-widest text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 rounded-full px-4 py-1.5 mb-8">
            Order Loss Prevention for Shopify
          </span>
          <h1 className="text-4xl sm:text-6xl font-semibold tracking-tight leading-[1.05] mb-6">
            Detect unprofitable orders
            <br />
            <span className="text-emerald-400">before</span> they hurt your business.
          </h1>
          <p className="text-lg text-neutral-400 max-w-xl mx-auto mb-10 leading-relaxed">
            Profit Guard calculates every order&apos;s true profit — product
            cost, shipping, discounts, and payment fees — the moment it comes
            in. Know before you ship, not after you reconcile.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <a
              href="/api/shopify/install"
              className="inline-flex items-center justify-center bg-emerald-500 text-neutral-950 font-medium px-8 py-3 rounded-lg hover:bg-emerald-400 transition shadow-[0_0_0_1px_rgba(52,211,153,0.4),0_8px_30px_-8px_rgba(52,211,153,0.5)]"
            >
              Install on Shopify
            </a>
            <span className="text-xs text-neutral-400">
              $5/mo — less than a coffee, for the whole month
            </span>
          </div>
        </div>

        {/* PRODUCT PREVIEW — mock order feed */}
        <div className="relative max-w-2xl mx-auto px-6 pb-24">
          <div className="rounded-2xl border border-neutral-800 bg-neutral-900/60 shadow-2xl overflow-hidden">
            <div className="flex items-center gap-2 px-5 py-3 border-b border-neutral-800 bg-neutral-900">
              <span className="w-2.5 h-2.5 rounded-full bg-neutral-700" />
              <span className="w-2.5 h-2.5 rounded-full bg-neutral-700" />
              <span className="w-2.5 h-2.5 rounded-full bg-neutral-700" />
              <span className="ml-3 text-xs text-neutral-400">Live orders</span>
            </div>
            <div className="divide-y divide-neutral-800/80">
              {[
                { id: "#1042", total: "$68.00", margin: "+$21.40", loss: false },
                { id: "#1043", total: "$24.00", margin: "−$3.10", loss: true },
                { id: "#1044", total: "$112.00", margin: "+$38.90", loss: false },
              ].map((o) => (
                <div key={o.id} className="flex items-center justify-between px-5 py-3.5 text-sm">
                  <span className="text-neutral-300 font-mono">{o.id}</span>
                  <span className="text-neutral-400">{o.total}</span>
                  <span
                    className={`font-medium px-2 py-0.5 rounded-md ${
                      o.loss
                        ? "text-red-400 bg-red-500/10"
                        : "text-emerald-400 bg-emerald-500/10"
                    }`}
                  >
                    {o.margin}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section className="max-w-4xl mx-auto px-6 pb-24">
        <h2 className="text-sm uppercase tracking-widest text-neutral-400 text-center mb-12">
          Know your true profit before losses pile up
        </h2>
        <div className="grid sm:grid-cols-3 gap-10">
          {features.map((f) => (
            <div key={f.title} className="text-center">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth={1.5}
                className="w-9 h-9 mx-auto mb-4 text-emerald-400"
              >
                {f.icon}
              </svg>
              <h3 className="text-lg font-semibold mb-2">{f.title}</h3>
              <p className="text-neutral-400 text-sm leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* COMPARISON */}
      <section className="max-w-3xl mx-auto px-6 pb-24">
        <h2 className="text-2xl font-semibold mb-4 text-center">
          Profit Guard vs. traditional profit trackers
        </h2>
        <p className="text-neutral-400 text-center max-w-xl mx-auto mb-10 leading-relaxed">
          Apps like BeProfit, Lifetimely, and TrueProfit are built for
          after-the-sale reporting — dashboards you check at the end of the
          week or month. Profit Guard is built for the moment an order is
          placed, so you can act while it still matters.
        </p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm border border-neutral-800 rounded-xl overflow-hidden">
            <thead>
              <tr className="bg-neutral-900 text-left">
                <th className="px-5 py-3 font-medium text-neutral-300">Capability</th>
                <th className="px-5 py-3 font-medium text-neutral-300">
                  Traditional profit trackers
                </th>
                <th className="px-5 py-3 font-medium text-emerald-400">Profit Guard</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-800">
              <tr>
                <td className="px-5 py-3.5 text-neutral-300">When you see margin</td>
                <td className="px-5 py-3.5 text-neutral-400">
                  End of day, week, or month
                </td>
                <td className="px-5 py-3.5 text-neutral-200">The instant an order is placed</td>
              </tr>
              <tr>
                <td className="px-5 py-3.5 text-neutral-300">Loss-making orders</td>
                <td className="px-5 py-3.5 text-neutral-400">
                  Surface in a monthly report
                </td>
                <td className="px-5 py-3.5 text-neutral-200">Flagged in real time</td>
              </tr>
              <tr>
                <td className="px-5 py-3.5 text-neutral-300">Primary use case</td>
                <td className="px-5 py-3.5 text-neutral-400">Analytics &amp; dashboards</td>
                <td className="px-5 py-3.5 text-neutral-200">Loss prevention</td>
              </tr>
              <tr>
                <td className="px-5 py-3.5 text-neutral-300">Setup</td>
                <td className="px-5 py-3.5 text-neutral-400">
                  Ad spend + channel integrations
                </td>
                <td className="px-5 py-3.5 text-neutral-200">
                  Product cost, shipping, and fees — once
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p className="text-xs text-neutral-500 mt-4 text-center">
          Hidden costs — shipping, discounts, and payment processing fees —
          are a common source of order-level losses. See Shopify&apos;s own{" "}
          <a
            href="https://help.shopify.com/en/manual/payments/shopify-payments/fees"
            target="_blank"
            rel="noopener noreferrer"
            className="text-neutral-400 underline hover:text-neutral-300"
          >
            payment processing fee schedule
          </a>{" "}
          for a sense of how much fees alone can erode a thin-margin order.
        </p>
      </section>

      {/* PRICING */}
      <section className="max-w-md mx-auto px-6 pb-24 text-center">
        <h2 className="text-2xl font-semibold mb-3">Pricing</h2>
        <p className="text-neutral-400 mb-8 leading-relaxed">
          One coffee, once — for a full month of order-loss protection.
        </p>
        <div className="rounded-2xl border border-emerald-500/30 bg-neutral-900/40 px-8 py-10">
          <div className="text-5xl font-semibold mb-1">
            $5<span className="text-lg text-neutral-400 font-normal">/mo</span>
          </div>
          <p className="text-sm text-neutral-400 mb-6">7-day free trial · cancel anytime</p>
          <a
            href="/api/shopify/install"
            className="inline-flex items-center justify-center w-full bg-emerald-500 text-neutral-950 font-medium px-8 py-3 rounded-lg hover:bg-emerald-400 transition"
          >
            Start free trial
          </a>
        </div>
      </section>

      {/* FAQ */}
      <section className="max-w-2xl mx-auto px-6 pb-28">
        <h2 className="text-2xl font-semibold mb-10 text-center">
          Frequently asked questions
        </h2>
        <div className="space-y-3">
          {faqs.map((f) => (
            <div
              key={f.q}
              className="border border-neutral-800 rounded-xl px-6 py-5 bg-neutral-900/40"
            >
              <h3 className="font-medium mb-2 flex items-start gap-2">
                <span className="text-emerald-400">Q.</span>
                {f.q}
              </h3>
              <p className="text-sm text-neutral-400 leading-relaxed pl-5">{f.a}</p>
            </div>
          ))}
        </div>
      </section>

      {/* FINAL CTA */}
      <section className="max-w-2xl mx-auto px-6 pb-28 text-center">
        <h2 className="text-2xl sm:text-3xl font-semibold mb-4">
          Stop finding out at month end.
        </h2>
        <p className="text-neutral-400 mb-8">
          Install Profit Guard and see today&apos;s order margins immediately.
        </p>
        <a
          href="/api/shopify/install"
          className="inline-flex items-center justify-center bg-emerald-500 text-neutral-950 font-medium px-8 py-3 rounded-lg hover:bg-emerald-400 transition"
        >
          Install on Shopify
        </a>
      </section>

      <footer className="border-t border-neutral-800 px-8 py-6 text-center text-sm text-neutral-400">
        <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 mb-3">
          <a href="/" className="hover:text-neutral-100 transition">
            SMBkits
          </a>
          <a href="/privacy" className="hover:text-neutral-100 transition">
            Privacy Policy
          </a>
          <a href="/terms" className="hover:text-neutral-100 transition">
            Terms of Service
          </a>
        </div>
        © 2026 SMBkits · Profit Guard
      </footer>
    </main>
  );
}
