import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = "https://smbkits.com";
  const now = new Date();

  return [{ url: base, lastModified: now, changeFrequency: "weekly", priority: 1.0 }];
}
