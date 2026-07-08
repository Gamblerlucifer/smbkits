import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy Policy",
  description: "How SMBkits collects, uses, and protects merchant data.",
  alternates: { canonical: "https://smbkits.com/privacy" },
  robots: { index: true, follow: true },
};

export default function PrivacyPage() {
  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-100">
      <nav className="flex items-center justify-between px-6 sm:px-8 py-5 border-b border-neutral-800/80">
        <a href="/" className="text-lg font-semibold tracking-tight">
          SMBkits
        </a>
        <a href="/apps/profit-guard" className="text-sm text-neutral-400 hover:text-neutral-100 transition">
          Profit Guard
        </a>
      </nav>

      <article className="max-w-2xl mx-auto px-6 py-20 prose prose-invert prose-neutral">
        <h1 className="text-3xl font-semibold mb-2">Privacy Policy</h1>
        <p className="text-sm text-neutral-500 mb-10">Last updated: July 2026</p>

        <div className="space-y-8 text-neutral-300 leading-relaxed">
          <section>
            <h2 className="text-lg font-semibold mb-2 text-neutral-100">
              What we collect
            </h2>
            <p>
              When you install a SMBkits app on your Shopify store, we access
              only the data required for that specific app to function —
              typically order and product information needed to calculate
              order-level metrics. We do not access customer personal data
              beyond what is strictly necessary to process an order (such as
              order totals and line items), and we never sell merchant or
              customer data.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold mb-2 text-neutral-100">
              How we use it
            </h2>
            <p>
              Data is used exclusively to power the app&apos;s core function
              — for example, Profit Guard uses order and product cost data
              solely to calculate order profitability. We do not use
              merchant or customer data for advertising, and we do not share
              it with third parties except infrastructure providers strictly
              necessary to run the service (such as our hosting and data
              storage providers).
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold mb-2 text-neutral-100">
              Data retention
            </h2>
            <p>
              We retain store data for as long as the app remains installed.
              If you uninstall an app, associated store data is deleted from
              our systems within 30 days, in line with Shopify&apos;s data
              protection requirements for apps.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold mb-2 text-neutral-100">
              Your rights
            </h2>
            <p>
              You can request access to, correction of, or deletion of your
              store&apos;s data at any time by uninstalling the app or
              contacting us directly. Shopify also provides merchants and
              their customers standard data request and erasure mechanisms
              that we honor as required.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold mb-2 text-neutral-100">Contact</h2>
            <p>
              Questions about this policy can be sent to the contact address
              listed on our Shopify Partner profile.
            </p>
          </section>
        </div>
      </article>

      <footer className="border-t border-neutral-800 px-8 py-6 text-center text-sm text-neutral-400">
        <a href="/" className="hover:text-neutral-100 transition">
          ← Back to SMBkits
        </a>
      </footer>
    </main>
  );
}
