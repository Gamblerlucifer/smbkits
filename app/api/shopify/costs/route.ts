import { NextRequest, NextResponse } from "next/server";
import { isValidShopDomain, getCostConfig, saveCostConfig, CostConfig } from "@/lib/shopify";

export async function GET(request: NextRequest) {
  const shop = request.nextUrl.searchParams.get("shop");

  if (!shop || !isValidShopDomain(shop)) {
    return NextResponse.json({ error: "Missing or invalid shop parameter" }, { status: 400 });
  }

  const config = await getCostConfig(shop);
  return NextResponse.json(config);
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  const shop = body.shop as string | undefined;

  if (!shop || !isValidShopDomain(shop)) {
    return NextResponse.json({ error: "Missing or invalid shop parameter" }, { status: 400 });
  }

  const config: CostConfig = {
    shippingCost: Number(body.shippingCost) || 0,
    feePercent: Number(body.feePercent) || 0,
    productCosts:
      typeof body.productCosts === "object" && body.productCosts !== null
        ? body.productCosts
        : {},
  };

  await saveCostConfig(shop, config);
  return NextResponse.json({ ok: true });
}
