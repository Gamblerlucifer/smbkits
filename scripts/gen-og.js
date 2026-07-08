const sharp = require("sharp");
const path = require("path");
const fs = require("fs");

const dir = path.join(__dirname, "..", "public", "og");
if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

// Gold: #A8864A  BG: #08090C  Text: #E4DED4  Muted: #8B92A1
const pages = [
  {
    slug: "main",
    title: "Reputation Infrastructure",
    subtitle: "Private brand-safe reputation management\nfor independent premium businesses.",
  },
  {
    slug: "reputation-response",
    title: "Reputation Response",
    subtitle: "Protecting brand perception\nbefore public damage compounds.",
  },
  {
    slug: "social-presence",
    title: "Social Presence",
    subtitle: "Consistency creates trust\nbefore customers ever arrive.",
  },
  {
    slug: "local-positioning",
    title: "Local Positioning",
    subtitle: "Understand why customers\nchoose nearby competitors.",
  },
  {
    slug: "reputation-recovery",
    title: "Reputation Recovery",
    subtitle: "Trust rarely disappears instantly.\nIt erodes quietly.",
  },
  {
    slug: "brand-voice",
    title: "Brand Voice Library",
    subtitle: "The right tone should never\ndepend on who is typing.",
  },
  {
    slug: "visibility-intelligence",
    title: "Visibility Intelligence",
    subtitle: "Visibility without context\ncreates expensive assumptions.",
  },
  {
    slug: "brand-responses",
    title: "Brand Responses",
    subtitle: "Every public reply\nbecomes part of the brand.",
  },
];

function makeSvg(title, subtitle) {
  // Split subtitle into two lines
  const lines = subtitle.split("\n");
  const line1 = lines[0] || "";
  const line2 = lines[1] || "";

  return `<svg width="1200" height="630" xmlns="http://www.w3.org/2000/svg">
  <!-- Background gradient overlay -->
  <defs>
    <linearGradient id="grad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0C0E13"/>
      <stop offset="100%" stop-color="#08090C"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="630" fill="url(#grad)"/>

  <!-- Left gold accent bar -->
  <rect x="72" y="120" width="2" height="390" fill="#A8864A" opacity="0.5"/>

  <!-- Top border line -->
  <rect x="72" y="72" width="1056" height="1" fill="#A8864A" opacity="0.2"/>
  <!-- Bottom border line -->
  <rect x="72" y="557" width="1056" height="1" fill="#A8864A" opacity="0.2"/>

  <!-- SMBkits wordmark -->
  <text
    x="104"
    y="126"
    font-family="Georgia, serif"
    font-size="18"
    font-weight="300"
    letter-spacing="8"
    fill="#8B92A1"
    text-anchor="start">SMBKITS</text>

  <!-- Gold rule -->
  <rect x="104" y="198" width="40" height="1" fill="#A8864A" opacity="0.6"/>

  <!-- Main title -->
  <text
    x="104"
    y="310"
    font-family="Georgia, serif"
    font-size="68"
    font-weight="300"
    fill="#E4DED4"
    text-anchor="start"
    letter-spacing="-1">${title}</text>

  <!-- Subtitle line 1 -->
  <text
    x="104"
    y="378"
    font-family="Georgia, serif"
    font-size="26"
    font-weight="300"
    font-style="italic"
    fill="#8B92A1"
    text-anchor="start">${line1}</text>

  <!-- Subtitle line 2 -->
  <text
    x="104"
    y="414"
    font-family="Georgia, serif"
    font-size="26"
    font-weight="300"
    font-style="italic"
    fill="#8B92A1"
    text-anchor="start">${line2}</text>

  <!-- Bottom label -->
  <text
    x="104"
    y="534"
    font-family="Georgia, serif"
    font-size="14"
    letter-spacing="4"
    fill="#5B6272"
    text-anchor="start">PRIVATE REPUTATION INFRASTRUCTURE</text>
</svg>`;
}

async function generate() {
  for (const page of pages) {
    const svg = makeSvg(page.title, page.subtitle);
    const svgBuf = Buffer.from(svg);

    await sharp({
      create: {
        width: 1200,
        height: 630,
        channels: 3,
        background: { r: 8, g: 9, b: 12 },
      },
    })
      .composite([{ input: svgBuf, top: 0, left: 0 }])
      .jpeg({ quality: 90 })
      .toFile(path.join(dir, `${page.slug}.jpg`));

    console.log(`✓ ${page.slug}.jpg`);
  }
  console.log("\nDone — all OG images created with branding.");
}

generate().catch(console.error);
