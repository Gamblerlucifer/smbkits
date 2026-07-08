import { NextRequest, NextResponse } from "next/server";
import {
  verifyWebhookHmac,
  getCostConfig,
  computeOrderMargin,
  recordOrderResult,
  ShopifyOrder,
} from "@/lib/shopify";

export async function POST(request: NextRequest) {
  const rawBody = await request.text();
  const hmacHeader = request.headers.get("x-shopify-hmac-sha256");
  const shop = request.headers.get("x-shopify-shop-domain");

  if (!verifyWebhookHmac(rawBody, hmacHeader)) {
    return NextResponse.json({ error: "Invalid HMAC" }, { status: 401 });
  }

  if (!shop) {
    return NextResponse.json({ error: "Missing shop domain header" }, { status: 400 });
  }

  const order = JSON.parse(rawBody) as ShopifyOrder;
  const costConfig = await getCostConfig(shop);
  const result = computeOrderMargin(order, costConfig);
  await recordOrderResult(shop, result);

  return NextResponse.json({ ok: true });
}
