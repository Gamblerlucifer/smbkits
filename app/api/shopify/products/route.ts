import { NextRequest, NextResponse } from "next/server";
import { isValidShopDomain, getAccessToken, fetchProducts } from "@/lib/shopify";

export async function GET(request: NextRequest) {
  const shop = request.nextUrl.searchParams.get("shop");

  if (!shop || !isValidShopDomain(shop)) {
    return NextResponse.json({ error: "Missing or invalid shop parameter" }, { status: 400 });
  }

  const accessToken = await getAccessToken(shop);
  if (!accessToken) {
    return NextResponse.json({ error: "Store is not installed" }, { status: 404 });
  }

  const products = await fetchProducts(shop, accessToken);
  return NextResponse.json({ products });
}
