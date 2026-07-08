import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms of Service",
  description: "Terms governing use of SMBkits apps, including Profit Guard.",
  alternates: { canonical: "https://smbkits.com/terms" },
  robots: { index: true, follow: true },
};

export default function TermsPage() {
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

      <article className="max-w-2xl mx-auto px-6 py-20">
        <h1 className="text-3xl font-semibold mb-2">Terms of Service</h1>
        <p className="text-sm text-neutral-500 mb-10">Last updated: July 2026</p>

        <div className="space-y-8 text-neutral-300 leading-relaxed">
          <section>
            <h2 className="text-lg font-semibold mb-2 text-neutral-100">
              Using our apps
            </h2>
            <p>
              By installing a SMBkits app on your Shopify store, you agree to
              use it in accordance with Shopify&apos;s Acceptable Use Policy
              and applicable law. Apps are provided to help you operate your
              store more effectively; you remain responsible for decisions
              made using the information they surface.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold mb-2 text-neutral-100">
              Accuracy of calculations
            </h2>
            <p>
              Profit Guard and other SMBkits apps calculate figures such as
              order margin based on the cost data you provide. Accuracy
              depends on that input being correct and kept up to date. We do
              not guarantee that calculated figures match your actual
              accounting records, and our apps are not a substitute for
              professional accounting or tax advice.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold mb-2 text-neutral-100">
              Billing
            </h2>
            <p>
              Paid plans are billed through Shopify&apos;s Billing API on a
              recurring basis. You can cancel a subscription at any time by
              uninstalling the app; charges already billed for the current
              period are non-refundable except where required by law.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold mb-2 text-neutral-100">
              Limitation of liability
            </h2>
            <p>
              SMBkits apps are provided &quot;as is,&quot; without warranty
              of any kind. To the maximum extent permitted by law, SMBkits is
              not liable for indirect, incidental, or consequential damages
              arising from use of the app, including decisions made based on
              its output.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold mb-2 text-neutral-100">Changes</h2>
            <p>
              We may update these terms from time to time. Continued use of
              the app after a change constitutes acceptance of the updated
              terms.
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
