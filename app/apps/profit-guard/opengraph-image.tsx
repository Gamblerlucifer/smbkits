import { ImageResponse } from "next/og";

export const alt = "Profit Guard — Real-Time Shopify Order Profit Calculator";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          background: "#0a0a0a",
          color: "#f5f5f5",
          fontFamily: "sans-serif",
          padding: "80px",
        }}
      >
        <div
          style={{
            fontSize: 28,
            letterSpacing: 4,
            textTransform: "uppercase",
            color: "#34d399",
            marginBottom: 28,
          }}
        >
          SMBkits · Profit Guard
        </div>
        <div
          style={{
            fontSize: 64,
            fontWeight: 700,
            textAlign: "center",
            lineHeight: 1.15,
            maxWidth: 980,
          }}
        >
          Detect Unprofitable Orders Before They Hurt Your Business
        </div>
      </div>
    ),
    { ...size }
  );
}
