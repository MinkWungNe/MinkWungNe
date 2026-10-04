import os
import re

def style_snake_svg(file_path: str, is_dark: bool = True):
    if not os.path.exists(file_path):
        print(f"[SKIP] File not found: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Clean up any previously injected cyber elements (ensures idempotency)
    content = re.sub(r'\s*<defs\s+id="cyber-snake-defs">.*?</defs>', '', content, flags=re.DOTALL)
    content = re.sub(r'\s*<!-- Top HUD Header -->.*?<line[^>]+class="hud-divider"[^>]*>', '', content, flags=re.DOTALL)
    content = re.sub(r'\s*<!-- SHINY LIGHT EFFECT OVERLAY -->.*?class="shine-light"[^>]*/>\s*</g>', '', content, flags=re.DOTALL)
    content = re.sub(r'<rect[^>]+class="cyber-snake-[^"]*"[^>]*>', '', content)
    content = re.sub(r'\s*\.(?:cyber-snake|hud-|status-pill|shine-light)[^{]*\{[^}]*\}', '', content)
    content = re.sub(r'\s*@keyframes\s+(?:cyber-purple-aurora|shine-scroll-snake)[^{]*\{.*?\}\s*\}', '', content, flags=re.DOTALL)

    # 1. Update <svg> tag with expanded viewBox to accommodate top header + neon glow padding
    # Card is 870x246: x from -10 to 860, y from -80 to 166
    # viewBox with 15px padding: -25 -95 900 276
    new_svg_tag = '<svg viewBox="-25 -95 900 276" width="100%" height="276" xmlns="http://www.w3.org/2000/svg">'
    content = re.sub(r'<svg[^>]+>', new_svg_tag, content, count=1)

    # 2. Defs for Shiny Scroll Overlay (Cel-shaded Hoyoverse style)
    defs_markup = """
  <defs id="cyber-snake-defs">
    <clipPath id="snake-card-clip">
      <rect x="-10" y="-80" width="870" height="246" rx="6" />
    </clipPath>
    <linearGradient id="shine-sweep-grad-snake" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0" />
      <stop offset="2%" stop-color="#ffffff" stop-opacity="0" />
      <stop offset="3%" stop-color="#ffffff" stop-opacity="0.22" />
      <stop offset="14%" stop-color="#ffffff" stop-opacity="0.22" />
      <stop offset="15%" stop-color="#ffffff" stop-opacity="0.14" />
      <stop offset="97%" stop-color="#ffffff" stop-opacity="0.14" />
      <stop offset="98%" stop-color="#ffffff" stop-opacity="0" />
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0" />
    </linearGradient>
  </defs>
"""

    # 3. Prepare CSS styles
    shine_style = """
  .shine-light {
    animation: shine-scroll-snake 4.5s cubic-bezier(0.25, 1, 0.4, 1) infinite;
    pointer-events: none;
  }
  @keyframes shine-scroll-snake {
    0% {
      transform: translateX(-400px) skewX(-20deg);
      opacity: 0;
    }
    8% {
      opacity: 1;
    }
    38% {
      transform: translateX(1100px) skewX(-20deg);
      opacity: 1;
    }
    42%, 100% {
      transform: translateX(1100px) skewX(-20deg);
      opacity: 0;
    }
  }
"""

    if is_dark:
        custom_style = """
  .cyber-snake-bg {
    fill: rgba(22, 13, 44, 0.65);
  }
  .cyber-snake-frame {
    stroke: #ffffff;
    stroke-width: 1.5;
    fill: none;
    animation: cyber-purple-aurora 3s ease-in-out infinite;
  }
  .hud-divider {
    stroke: rgba(255, 255, 255, 0.25);
    stroke-width: 1;
    stroke-dasharray: 4 3;
  }
  .hud-tag {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", monospace, sans-serif;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.18em;
    fill: #d28cff;
  }
  .hud-title {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", monospace, sans-serif;
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 0.12em;
    fill: #ffffff;
  }
  .status-pill {
    stroke: #805cf6;
    stroke-width: 1;
    fill: rgba(128, 92, 246, 0.2);
  }
  .status-pill-text {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", monospace, sans-serif;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.12em;
    fill: #e0d4fc;
    text-anchor: middle;
    dominant-baseline: central;
  }
  @keyframes cyber-purple-aurora {
    0%, 100% {
      filter: drop-shadow(0 0 1px #805cf6) drop-shadow(0 0 3px rgba(150, 38, 255, 0.6));
    }
    50% {
      filter: drop-shadow(0 0 1.5px #ffffff) drop-shadow(0 0 4px #6c29e7) drop-shadow(0 0 5.5px rgba(125, 92, 246, 0.94));
    }
  }
""" + shine_style
    else:
        custom_style = """
  .cyber-snake-bg {
    fill: rgba(246, 248, 250, 0.85);
  }
  .cyber-snake-frame {
    stroke: #805cf6;
    stroke-width: 1.5;
    fill: none;
    animation: cyber-purple-aurora-light 3s ease-in-out infinite;
  }
  .hud-divider {
    stroke: rgba(128, 92, 246, 0.25);
    stroke-width: 1;
    stroke-dasharray: 4 3;
  }
  .hud-tag {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", monospace, sans-serif;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.18em;
    fill: #805cf6;
  }
  .hud-title {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", monospace, sans-serif;
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 0.12em;
    fill: #1f2328;
  }
  .status-pill {
    stroke: #805cf6;
    stroke-width: 1;
    fill: rgba(128, 92, 246, 0.12);
  }
  .status-pill-text {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", monospace, sans-serif;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.12em;
    fill: #59229e;
    text-anchor: middle;
    dominant-baseline: central;
  }
  @keyframes cyber-purple-aurora-light {
    0%, 100% {
      filter: drop-shadow(0 0 2px rgba(128, 92, 246, 0.4));
    }
    50% {
      filter: drop-shadow(0 0 4px rgba(176, 38, 255, 0.7));
    }
  }
""" + shine_style

    # Insert defs right after <desc> if present, or right before <style>
    if '<desc>' in content:
        content = re.sub(r'(</desc>)', r'\1' + defs_markup, content, count=1)
    else:
        content = re.sub(r'(<style[^>]*>)', defs_markup + r'\1', content, count=1)

    # Inject custom styles into existing <style> tag
    content = re.sub(r'(<style[^>]*>)', r'\1' + custom_style, content, count=1)

    # 4. Build Graphic Layers
    # A. Background Card (behind cells/snake)
    bg_rect = '<rect x="-10" y="-80" width="870" height="246" rx="6" class="cyber-snake-bg" />'

    # B. Header Elements: Tag, Title, Status Pill, and Dotted Divider Line
    header_elements = """
  <!-- Top HUD Header -->
  <text x="14" y="-58" class="hud-tag">// TELEMETRY HUD // CONTRIBUTION STREAM</text>
  <text x="14" y="-38" class="hud-title">CONTRIBUTION ACTIVITY • SNAKE PROTOCOL</text>

  <!-- Status Pill -->
  <rect x="696" y="-66" width="140" height="20" rx="3" class="status-pill" />
  <text x="766" y="-56" class="status-pill-text">AUTOMATED ENGINE</text>

  <!-- Dotted Divider Separating Header and Snake Grid Area -->
  <line x1="14" y1="-24" x2="836" y2="-24" class="hud-divider" />
"""

    # C. Shiny Light Effect Overlay (glides over card content within card clipPath)
    shine_overlay = """
  <!-- SHINY LIGHT EFFECT OVERLAY -->
  <g clip-path="url(#snake-card-clip)">
    <rect x="-10" y="-90" width="60" height="300" fill="url(#shine-sweep-grad-snake)" class="shine-light" style="pointer-events: none;" />
  </g>
"""

    # D. Outer Glowing Frame (on top)
    frame_rect = '<rect x="-10" y="-80" width="870" height="246" rx="6" class="cyber-snake-frame" />'

    # Insert background rect and header immediately after </style>
    content = re.sub(r'(</style>)', r'\1' + bg_rect + header_elements, content, count=1)

    # Insert shine overlay and outer frame right before </svg>
    content = re.sub(r'(</svg>)', shine_overlay + frame_rect + r'\1', content, count=1)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[OK] Styled {file_path} with Cyberpunk HUD header and shiny scroll.")

def main():
    dark_svg = os.path.join("dist", "github-contribution-grid-snake-dark.svg")
    light_svg = os.path.join("dist", "github-contribution-grid-snake.svg")

    style_snake_svg(dark_svg, is_dark=True)
    style_snake_svg(light_svg, is_dark=False)

if __name__ == "__main__":
    main()
