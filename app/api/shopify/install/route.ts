import { NextRequest, NextResponse } from "next/server";
import { randomBytes } from "crypto";
import { isValidShopDomain, buildAuthorizeUrl, errorPage } from "@/lib/shopify";

export async function GET(request: NextRequest) {
  const shop = request.nextUrl.searchParams.get("shop");

  if (!shop || !isValidShopDomain(shop)) {
    return errorPage(
      "This install link is missing your store's address. Please install Profit Guard from the Shopify App Store instead of using this link directly."
    );
  }

  const state = randomBytes(16).toString("hex");
  const authorizeUrl = buildAuthorizeUrl(shop, state);

  const response = NextResponse.redirect(authorizeUrl);
  response.cookies.set("shopify_oauth_state", state, {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    maxAge: 600,
  });
  return response;
}
