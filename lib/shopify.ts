import { createHmac, timingSafeEqual } from "crypto";
import { kv } from "@vercel/kv";

const SCOPES = "read_orders,read_products";

export function isValidShopDomain(shop: string): boolean {
  return /^[a-zA-Z0-9][a-zA-Z0-9-]*\.myshopify\.com$/.test(shop);
}

export function buildAuthorizeUrl(shop: string, state: string): string {
  const params = new URLSearchParams({
    client_id: process.env.SHOPIFY_CLIENT_ID!,
    scope: SCOPES,
    redirect_uri: `${process.env.SHOPIFY_APP_URL}/api/shopify/callback`,
    state,
  });
  return `https://${shop}/admin/oauth/authorize?${params.toString()}`;
}

export function verifyHmac(searchParams: URLSearchParams): boolean {
  const hmac = searchParams.get("hmac");
  if (!hmac) return false;

  const message = [...searchParams.entries()]
    .filter(([key]) => key !== "hmac" && key !== "signature")
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([key, value]) => `${key}=${value}`)
    .join("&");

  const digest = createHmac("sha256", process.env.SHOPIFY_CLIENT_SECRET!)
    .update(message)
    .digest("hex");

  const digestBuf = Buffer.from(digest, "utf8");
  const hmacBuf = Buffer.from(hmac, "utf8");
  if (digestBuf.length !== hmacBuf.length) return false;
  return timingSafeEqual(digestBuf, hmacBuf);
}

export async function exchangeCodeForToken(
  shop: string,
  code: string
): Promise<string> {
  const res = await fetch(`https://${shop}/admin/oauth/access_token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      client_id: process.env.SHOPIFY_CLIENT_ID,
      client_secret: process.env.SHOPIFY_CLIENT_SECRET,
      code,
    }),
  });

  if (!res.ok) {
    throw new Error(`Token exchange failed: ${res.status} ${await res.text()}`);
  }

  const data = await res.json();
  return data.access_token as string;
}

export async function storeAccessToken(shop: string, token: string) {
  await kv.set(`shop:${shop}:token`, token);
}

export async function getAccessToken(shop: string): Promise<string | null> {
  return kv.get<string>(`shop:${shop}:token`);
}

export interface CostConfig {
  shippingCost: number;
  feePercent: number;
  productCosts: Record<string, number>;
}

const EMPTY_COST_CONFIG: CostConfig = { shippingCost: 0, feePercent: 0, productCosts: {} };

export async function getCostConfig(shop: string): Promise<CostConfig> {
  const config = await kv.get<CostConfig>(`shop:${shop}:costs`);
  return config ?? EMPTY_COST_CONFIG;
}

export async function saveCostConfig(shop: string, config: CostConfig) {
  await kv.set(`shop:${shop}:costs`, config);
}

export interface ShopifyProduct {
  id: number;
  title: string;
  variants: { id: number; price: string }[];
}

export async function fetchProducts(
  shop: string,
  accessToken: string
): Promise<ShopifyProduct[]> {
  const res = await fetch(
    `https://${shop}/admin/api/2026-07/products.json?limit=50&fields=id,title,variants`,
    { headers: { "X-Shopify-Access-Token": accessToken } }
  );

  if (!res.ok) {
    throw new Error(`Failed to fetch products: ${res.status} ${await res.text()}`);
  }

  const data = await res.json();
  return data.products as ShopifyProduct[];
}

export async function registerOrderWebhook(shop: string, accessToken: string) {
  const res = await fetch(`https://${shop}/admin/api/2026-07/webhooks.json`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Shopify-Access-Token": accessToken,
    },
    body: JSON.stringify({
      webhook: {
        topic: "orders/create",
        address: `${process.env.SHOPIFY_APP_URL}/api/webhooks/orders`,
        format: "json",
      },
    }),
  });

  if (!res.ok) {
    throw new Error(`Failed to register order webhook: ${res.status} ${await res.text()}`);
  }
}

export function verifyWebhookHmac(rawBody: string, hmacHeader: string | null): boolean {
  if (!hmacHeader) return false;

  const digest = createHmac("sha256", process.env.SHOPIFY_CLIENT_SECRET!)
    .update(rawBody, "utf8")
    .digest("base64");

  const digestBuf = Buffer.from(digest, "utf8");
  const hmacBuf = Buffer.from(hmacHeader, "utf8");
  if (digestBuf.length !== hmacBuf.length) return false;
  return timingSafeEqual(digestBuf, hmacBuf);
}

export interface ShopifyOrder {
  id: number;
  name?: string;
  order_number?: number;
  total_price: string;
  line_items: { product_id: number | null; quantity: number; price: string }[];
}

export interface OrderMarginResult {
  orderId: number;
  orderNumber: string;
  total: number;
  cost: number;
  shippingCost: number;
  paymentFee: number;
  margin: number;
  isLoss: boolean;
  createdAt: string;
}

export function computeOrderMargin(
  order: ShopifyOrder,
  costConfig: CostConfig
): OrderMarginResult {
  const total = parseFloat(order.total_price) || 0;

  const cost = order.line_items.reduce((sum, item) => {
    const unitCost = costConfig.productCosts[String(item.product_id)] ?? 0;
    return sum + unitCost * item.quantity;
  }, 0);

  const shippingCost = costConfig.shippingCost;
  const paymentFee = (costConfig.feePercent / 100) * total;
  const margin = Math.round((total - cost - shippingCost - paymentFee) * 100) / 100;

  return {
    orderId: order.id,
    orderNumber: order.name ?? String(order.order_number ?? order.id),
    total,
    cost,
    shippingCost,
    paymentFee,
    margin,
    isLoss: margin < 0,
    createdAt: new Date().toISOString(),
  };
}

const ORDER_HISTORY_LIMIT = 200;

export async function recordOrderResult(shop: string, result: OrderMarginResult) {
  const key = `shop:${shop}:orders`;
  await kv.lpush(key, result);
  await kv.ltrim(key, 0, ORDER_HISTORY_LIMIT - 1);
}

export async function getRecentOrderResults(
  shop: string,
  limit = 20
): Promise<OrderMarginResult[]> {
  const key = `shop:${shop}:orders`;
  const raw = await kv.lrange<OrderMarginResult>(key, 0, limit - 1);
  return raw ?? [];
}
