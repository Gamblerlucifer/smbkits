import { NextRequest, NextResponse } from "next/server";
import { isValidShopDomain, getAccessToken, createRecurringCharge } from "@/lib/shopify";

export async function GET(request: NextRequest) {
  const shop = request.nextUrl.searchParams.get("shop");

  if (!shop || !isValidShopDomain(shop)) {
    return NextResponse.json({ error: "Missing or invalid shop parameter" }, { status: 400 });
  }

  const accessToken = await getAccessToken(shop);
  if (!accessToken) {
    return NextResponse.json({ error: "Store is not installed" }, { status: 404 });
  }

  const charge = await createRecurringCharge(shop, accessToken);
  return NextResponse.redirect(charge.confirmation_url);
}
