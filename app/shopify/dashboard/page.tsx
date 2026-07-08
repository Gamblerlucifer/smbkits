import CostForm from "./CostForm";

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

  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-100">
      <CostForm shop={shop} />
    </main>
  );
}
