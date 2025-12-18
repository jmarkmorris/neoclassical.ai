# QR Code Reference

## Use Case
- Generate custom QR codes (PNG for crisp raster output, or SVG/PDF when vector scaling is needed) that can be overlaid on still images or inserted into video frames without relying on third-party hosting tools.
- Keep the encoded data short enough that the finder pattern stays clean even after export/compression, since videos and social-image formats tend to soften contrast.
- Include descriptive text near each QR code so viewers know why they should scan it and what to expect once the reader opens the link or data payload.

## QR Code Definition
QR stands for “Quick Response,” and the codes were invented by Denso Wave in 1994 to let scanners read encoded data faster than the 1D barcodes that preceded them. The format is standardized in ISO/IEC 18004, which defines the module layout, finder/alignment patterns, timing, error correction, and encoding modes for versions 1 through 40. Each version increases the symbol size (from 21×21 modules in version 1 up to 177×177 modules in version 40), enabling more data and finer control over redundancy. Modern implementations also support structured append, mirroring, and micro QR variants for very small footprints.

## Specifications for Encoded Data
- Versions 1–40 dictate the number of modules and, together with the error-correction level (L, M, Q, H), determine the usable capacity in numeric, alphanumeric, binary/byte, or Kanji mode. At the maximum (version 40, level L), a QR code can encode up to 7,089 numeric characters, 4,296 alphanumeric characters, or about 2,953 bytes of binary data. The practical limit for links is much lower (~300–500 characters) because denser codes require larger print sizes and more contrast.
- Always account for error correction needs: higher levels (Q/H) add redundancy so the code survives partial occlusion or compression artifacts—useful in videos where motion blur can happen—but they also increase the number of modules. Keep the encoded payload lean for simple graphics, or split large payloads across multiple codes or a landing page.
- QR codes can hold structured data beyond plain text URLs: vCards/contact info, geo coordinates, Wi‑Fi access parameters, SMS templates, email drafts, Bitcoin addresses, calendar events, and custom “universal” data types (e.g., `SMSTO:`, `MATMSG:`). Use the appropriate prefix so readers auto-detect the intent, and test on the devices you expect to support.

## Python Libraries for Generation
- `qrcode` (https://github.com/lincolnloop/python-qrcode): Simple API that works with Pillow to create PNG, JPEG, or BMP files. Handy for quick scripting and supports error levels, box size, border width, and QR version hints.
- `segno` (https://github.com/heuer/segno): Generates clean SVG or PNG output without Pillow, supports micro QR, structured append, and adherence to ISO/IEC 18004. Offers an offline CLI plus options to embed logos or add decorative modules.
- `PyQRCode` (https://github.com/mnooner256/pyqrcode): Pure Python generator producing scalable SVG or EPS along with raster export via `pypng`. Good for workflows that favor vector output first.
- `qrcodegen` by Nayuki (https://github.com/nayuki/QR-Code-generator): Portable, compact library (Python, Java, C++, etc.) that lets you manually control masks, segments, and error correction to produce highly optimized codes for long URLs or binary payloads.
- Complement any of these libraries with `Pillow` or `cairosvg` to layer QR codes onto custom imagery, then export as PNG for compositing or as high-resolution stills for video frames.

## Limitations and Platform Rules
- **General guidance for images/videos:** Keep QR codes readable—avoid placing them in low-contrast spots, limit size so they are scannable once published, and provide a static dwell time in video (e.g., remain visible on screen for several seconds). Compression-heavy codecs (YouTube, Instagram, TikTok) can blur module edges, so allow for some margin by choosing a lower version with higher error correction.
- **YouTube:** No explicit ban, but QR codes in thumbnails or ads should not mislead viewers (per the community guidelines and ad policies). Codes that direct viewers to policy-violating content or phishing pages may trigger takedowns or demonetization. For video overlays, avoid QR codes that cover essential content or violate the "deceptive practice" rules.
- **Reddit:** Many subreddits forbid purely promotional content, so embedding QR codes there may be considered spam if it links to external products or services. Also follow each subreddit’s media rules (e.g., thumbnails vs. posts) and ensure the QR code doesn’t obstruct policy-sensitive imagery like faces or forbidden symbols.
- **X (formerly Twitter):** QR codes themselves are allowed, but links they encode must comply with the platform’s behavior policies (no malicious redirect, no impersonation). Avoid rapid, repeated posting of similar codes across accounts, which can look like spam. Within videos, keep the code legible and unobtrusive, since X often promotes native video previews.
- **Facebook/Instagram:** Business or ad posts that include QR codes should still observe advertising standards—no misleading claims, prohibited content, or banned industries. Ads that rely solely on QR interaction might be scrutinized more closely for transparency. In organic posts, ensure the QR code doesn't dominate landscape or cover ID-verified content, as the platform can flag suspicious overlays.

## Functional Area by Device
- **Mobile phones:** The smallest screens but also the most common QR readers, so codes can be compact (roughly 1.5–2 cm per side for printed material scaled to screen pixels) while still filling enough of the camera preview to be scanned quickly. When appearing in a video, keep the code centered for a few seconds with a minimum of ~200×200 pixels on the exported frame to stay reliable across most smartphones.
- **Laptops/desktops:** Users tend to use secondary devices to scan, so the code must be large enough to occupy a readable portion of the screen (at least 300×300 pixels in the captured frame). If displaying on a web page, avoid scaling down below 150 pixels per side and ensure adequate contrast, since webcams often have lower resolution than mobile cameras.
- **4K TVs downscaled to 1080p outputs:** The QR area must survive both the rendering pipeline and the lower-resolution capture by a phone or camera. Aim for a large, high-contrast block (400–600 pixels wide before the downscale) and a steady on-screen duration; broadcasting at 1080p means the effective module width is approximately half of what it was at 4K, so err on the side of fewer modules (e.g., version ≤10) and higher error correction.

## Display Area Summary
Assuming high error correction (Q or H) for resilience, the following guidance expresses the ideal QR-code area per device as a percentage of that device’s vertical and horizontal screen real estate. Use these rows to balance readability with the goal of keeping the QR minimally intrusive.

| Use Case | Payload | Mobile (V% × H%) | Laptop (V% × H%) | 4K TV→1080p (V% × H%) | Notes |
| --- | --- | --- | --- | --- | --- |
| 1a. Optimal link to `https://neoclassical.ai` | Single HTTPS URL, high error correction, minimal modules | 18% × 30% | 15% × 25% | 20% × 30% | Clean link, no additional text; iOS Camera/Photos and third-party readers auto-open the URL quickly. |
| 1b. Standard web-link presentation | Same URL with slightly lower pixel budget to stay subtle | 12% × 20% | 10% × 18% | 12% × 22% | Works on YouTube/Reddit thumbnails when contrast is solid; keep surrounding art simple. |
| 2. Link plus paragraph (short descriptive blurb) | `https://neoclassical.ai` plus ~100 characters of plain text | 25% × 35% | 20% × 30% | 25% × 35% | Readers (including iOS Camera/Photos) list the text payload but may show only the first line; keep the paragraph short and consider hosting the full copy on the linked page. |

## Unique QR codes
- neoclassical.ai
- youtube channel
- discord
- any other social media
