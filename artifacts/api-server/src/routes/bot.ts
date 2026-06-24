import { Router } from "express";

const router = Router();

const DISCORD_API_BASE = "https://discord.com/api/v10";

function getAuthHeader() {
  const token = process.env.DISCORD_BOT_TOKEN;
  if (!token) throw new Error("DISCORD_BOT_TOKEN is not set");
  return `Bot ${token}`;
}

function buildAvatarUrl(userId: string, avatarHash: string | null): string | null {
  if (!avatarHash) return null;
  const ext = avatarHash.startsWith("a_") ? "gif" : "png";
  return `https://cdn.discordapp.com/avatars/${userId}/${avatarHash}.${ext}?size=256`;
}

function buildBannerUrl(userId: string, bannerHash: string | null): string | null {
  if (!bannerHash) return null;
  const ext = bannerHash.startsWith("a_") ? "gif" : "png";
  return `https://cdn.discordapp.com/banners/${userId}/${bannerHash}.${ext}?size=480`;
}

router.get("/bot/profile", async (req, res) => {
  try {
    const response = await fetch(`${DISCORD_API_BASE}/users/@me`, {
      headers: { Authorization: getAuthHeader() },
    });

    if (!response.ok) {
      const text = await response.text();
      return res.status(response.status).json({ error: `Discord API error: ${text}` });
    }

    const user = (await response.json()) as {
      id: string;
      username: string;
      discriminator: string;
      avatar: string | null;
      banner: string | null;
      accent_color: number | null;
    };

    return res.json({
      id: user.id,
      username: user.username,
      discriminator: user.discriminator,
      avatarUrl: buildAvatarUrl(user.id, user.avatar),
      bannerUrl: buildBannerUrl(user.id, user.banner),
      bannerColor: user.accent_color ? `#${user.accent_color.toString(16).padStart(6, "0")}` : null,
    });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return res.status(500).json({ error: message });
  }
});

router.patch("/bot/avatar", async (req, res) => {
  const { imageDataUri } = req.body as { imageDataUri?: string };

  if (!imageDataUri || !imageDataUri.startsWith("data:image/")) {
    return res.status(400).json({ error: "imageDataUri must be a valid base64 image data URI" });
  }

  try {
    const response = await fetch(`${DISCORD_API_BASE}/users/@me`, {
      method: "PATCH",
      headers: {
        Authorization: getAuthHeader(),
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ avatar: imageDataUri }),
    });

    if (!response.ok) {
      const text = await response.text();
      return res.status(response.status).json({ error: `Discord API error: ${text}` });
    }

    const user = (await response.json()) as {
      id: string;
      username: string;
      discriminator: string;
      avatar: string | null;
      banner: string | null;
      accent_color: number | null;
    };

    return res.json({
      id: user.id,
      username: user.username,
      discriminator: user.discriminator,
      avatarUrl: buildAvatarUrl(user.id, user.avatar),
      bannerUrl: buildBannerUrl(user.id, user.banner),
      bannerColor: user.accent_color ? `#${user.accent_color.toString(16).padStart(6, "0")}` : null,
    });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return res.status(500).json({ error: message });
  }
});

router.patch("/bot/banner", async (req, res) => {
  const { imageDataUri } = req.body as { imageDataUri?: string };

  if (!imageDataUri || !imageDataUri.startsWith("data:image/")) {
    return res.status(400).json({ error: "imageDataUri must be a valid base64 image data URI" });
  }

  try {
    const response = await fetch(`${DISCORD_API_BASE}/users/@me`, {
      method: "PATCH",
      headers: {
        Authorization: getAuthHeader(),
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ banner: imageDataUri }),
    });

    if (!response.ok) {
      const text = await response.text();
      return res.status(response.status).json({ error: `Discord API error: ${text}` });
    }

    const user = (await response.json()) as {
      id: string;
      username: string;
      discriminator: string;
      avatar: string | null;
      banner: string | null;
      accent_color: number | null;
    };

    return res.json({
      id: user.id,
      username: user.username,
      discriminator: user.discriminator,
      avatarUrl: buildAvatarUrl(user.id, user.avatar),
      bannerUrl: buildBannerUrl(user.id, user.banner),
      bannerColor: user.accent_color ? `#${user.accent_color.toString(16).padStart(6, "0")}` : null,
    });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return res.status(500).json({ error: message });
  }
});

export default router;
