import { NextRequest, NextResponse } from "next/server";
import { randomBytes } from "crypto";
import { isValidShopDomain, buildAuthorizeUrl } from "@/lib/shopify";

export async function GET(request: NextRequest) {
  const shop = request.nextUrl.searchParams.get("shop");

  if (!shop || !isValidShopDomain(shop)) {
    return NextResponse.json(
      { error: "Missing or invalid shop parameter" },
      { status: 400 }
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
