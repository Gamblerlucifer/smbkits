import { NextRequest, NextResponse } from "next/server";
import {
  isValidShopDomain,
  getAccessToken,
  activateRecurringCharge,
  storeSubscriptionStatus,
} from "@/lib/shopify";

export async function GET(request: NextRequest) {
  const { searchParams } = request.nextUrl;
  const shop = searchParams.get("shop");
  const chargeId = searchParams.get("charge_id");

  if (!shop || !isValidShopDomain(shop) || !chargeId) {
    return NextResponse.json({ error: "Invalid billing callback params" }, { status: 400 });
  }

  const accessToken = await getAccessToken(shop);
  if (!accessToken) {
    return NextResponse.json({ error: "Store is not installed" }, { status: 404 });
  }

  const charge = await activateRecurringCharge(shop, accessToken, chargeId);
  const active = charge.status === "active";
  await storeSubscriptionStatus(shop, active);

  const dashboardUrl = `${process.env.SHOPIFY_APP_URL}/shopify/dashboard?shop=${shop}`;
  if (!active) {
    return NextResponse.redirect(`${dashboardUrl}&billing=declined`);
  }
  return NextResponse.redirect(dashboardUrl);
}
