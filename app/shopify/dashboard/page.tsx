export default async function DashboardPage({
  searchParams,
}: {
  searchParams: Promise<{ shop?: string }>;
}) {
  const { shop } = await searchParams;

  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-100 flex items-center justify-center px-6">
      <div className="max-w-md text-center">
        <h1 className="text-2xl font-semibold mb-4">Profit Guard installed</h1>
        <p className="text-neutral-400">
          {shop ? `Connected to ${shop}.` : "App installed."} Cost setup and
          the profitability dashboard are coming next.
        </p>
      </div>
    </main>
  );
}
