import { NextRequest, NextResponse } from "next/server";
import {
  isValidShopDomain,
  checkHmac,
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
  const hmacCheck = checkHmac(rawQuery);
  if (!hmacCheck.match) {
    // TEMPORARY: surfaces the verification internals so we can diagnose a
    // signature mismatch. Remove this branch once installs succeed.
    return errorPage(
      `DEBUG — raw: ${rawQuery} | message: ${hmacCheck.message} | digest: ${hmacCheck.digest} | received hmac: ${hmacCheck.hmac}`
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
