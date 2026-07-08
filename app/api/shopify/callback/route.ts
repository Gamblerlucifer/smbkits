import { NextRequest, NextResponse } from "next/server";
import {
  isValidShopDomain,
  verifyHmac,
  exchangeCodeForToken,
  storeAccessToken,
  registerOrderWebhook,
  errorPage,
} from "@/lib/shopify";

export async function GET(request: NextRequest) {
  const { searchParams } = request.nextUrl;
  const shop = searchParams.get("shop");
  const code = searchParams.get("code");
  const state = searchParams.get("state");
  const cookieState = request.cookies.get("shopify_oauth_state")?.value;

  if (!shop || !isValidShopDomain(shop) || !code) {
    return errorPage("This installation link looks incomplete. Please try installing again.");
  }

  if (!state || !cookieState || state !== cookieState) {
    return errorPage(
      "Your installation session expired or was started from a different browser. Please try installing again."
    );
  }

  const rawQuery = request.nextUrl.search.replace(/^\?/, "");
  if (!verifyHmac(rawQuery)) {
    return errorPage(
      "We couldn't verify this request came from Shopify. Please try installing again from your Shopify admin."
    );
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
