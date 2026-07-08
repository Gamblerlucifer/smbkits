import { NextRequest, NextResponse } from "next/server";
import {
  isValidShopDomain,
  verifyHmac,
  exchangeCodeForToken,
  storeAccessToken,
  registerOrderWebhook,
} from "@/lib/shopify";

export async function GET(request: NextRequest) {
  const { searchParams } = request.nextUrl;
  const shop = searchParams.get("shop");
  const code = searchParams.get("code");
  const state = searchParams.get("state");
  const cookieState = request.cookies.get("shopify_oauth_state")?.value;

  if (!shop || !isValidShopDomain(shop) || !code) {
    return NextResponse.json({ error: "Invalid callback params" }, { status: 400 });
  }

  if (!state || !cookieState || state !== cookieState) {
    return NextResponse.json({ error: "State mismatch (possible CSRF)" }, { status: 403 });
  }

  if (!verifyHmac(searchParams)) {
    return NextResponse.json({ error: "Invalid HMAC signature" }, { status: 403 });
  }

  const accessToken = await exchangeCodeForToken(shop, code);
  await storeAccessToken(shop, accessToken);
  await registerOrderWebhook(shop, accessToken);

  const response = NextResponse.redirect(
    `${process.env.SHOPIFY_APP_URL}/shopify/dashboard?shop=${shop}`
  );
  response.cookies.delete("shopify_oauth_state");
  return response;
}
