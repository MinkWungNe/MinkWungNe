const fs = require('fs');
const path = require('path');

const USERNAME = 'MinkWungNe';
const PALETTE = ['#805cf6', '#b026ff', '#3b82f6', '#38bdf8', '#e2e8f0'];

function escapeXml(unsafe) {
  return String(unsafe).replace(/[<>&'"]/g, c => {
    switch (c) {
      case '<': return '&lt;';
      case '>': return '&gt;';
      case '&': return '&amp;';
      case '\'': return '&apos;';
      case '"': return '&quot;';
    }
  });
}

function formatApproxCommits(count) {
  if (count == null) return null;
  if (count < 10) return `${count}`;
  let step = 5;
  if (count >= 1000) step = 100;
  else if (count >= 200) step = 50;
  else if (count >= 50) step = 10;
  const approx = Math.floor(count / step) * step;
  return `${approx}+`;
}

function generateLanguageBarDesktop(languages) {
  const totalBarWidth = 822;
  const barHeight = 8;
  const gap = 2;
  const activeCount = languages.length;
  const totalGaps = (activeCount - 1) * gap;
  const availableWidth = totalBarWidth - totalGaps;

  let currentX = 0;
  const rects = languages.map((lang, idx) => {
    const isFirst = idx === 0;
    const isLast = idx === activeCount - 1;
    const w = isLast ? Math.max(2, totalBarWidth - currentX) : Math.max(2, Math.round((lang.pct / 100) * availableWidth));
    const rx = isFirst || isLast ? 4 : 2;
    const color = PALETTE[idx % PALETTE.length];
    const rect = `<rect x="${currentX}" y="0" width="${w}" height="${barHeight}" rx="${rx}" fill="${color}" />`;
    currentX += w + gap;
    return rect;
  }).join('\n        ');

  const step = Math.floor(totalBarWidth / activeCount);
  const legendItems = languages.map((lang, idx) => {
    const xBase = idx * step;
    const color = PALETTE[idx % PALETTE.length];
    return `          <circle cx="${xBase + 6}" cy="0" class="dot" fill="${color}" />\n          <text x="${xBase + 16}" y="4" class="lang-lbl">${escapeXml(lang.name)} (${lang.pct}%)</text>`;
  }).join('\n\n');

  return `<g id="language-telemetry" transform="translate(24, 138)">
        <!-- Multi-segment bar (Width 822, Height 8) -->
        <rect x="0" y="0" width="822" height="8" rx="4" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.15)" stroke-width="0.8" />
        <!-- Segments -->
        ${rects}

        <!-- Legend -->
        <g transform="translate(0, 24)">
${legendItems}
        </g>
      </g>`;
}

function generateLanguageBarMobile(languages) {
  const totalBarWidth = 368;
  const barHeight = 7;
  const gap = 1.5;
  const activeCount = languages.length;
  const totalGaps = (activeCount - 1) * gap;
  const availableWidth = totalBarWidth - totalGaps;

  let currentX = 0;
  const rects = languages.map((lang, idx) => {
    const isFirst = idx === 0;
    const isLast = idx === activeCount - 1;
    const w = isLast ? Math.max(2, Math.round(totalBarWidth - currentX)) : Math.max(2, Math.round((lang.pct / 100) * availableWidth));
    const rx = isFirst || isLast ? 3.5 : 1.5;
    const color = PALETTE[idx % PALETTE.length];
    const rect = `<rect x="${currentX}" y="0" width="${w}" height="${barHeight}" rx="${rx}" fill="${color}" />`;
    currentX += w + gap;
    return rect;
  }).join('\n      ');

  const row1 = languages.slice(0, 3);
  const row2 = languages.slice(3);

  const row1Svg = row1.map((lang, idx) => {
    const color = PALETTE[idx % PALETTE.length];
    const xBase = idx === 0 ? 0 : (idx === 1 ? 120 : 235);
    return `        <circle cx="${xBase + 5}" cy="0" class="dot" fill="${color}" />\n        <text x="${xBase + 14}" y="3" class="lang-lbl">${escapeXml(lang.name)} (${lang.pct}%)</text>`;
  }).join('\n');

  const row2Svg = row2.map((lang, idx) => {
    const color = PALETTE[(idx + 3) % PALETTE.length];
    const xBase = idx === 0 ? 65 : 190;
    return `        <circle cx="${xBase + 5}" cy="22" class="dot" fill="${color}" />\n        <text x="${xBase + 14}" y="25" class="lang-lbl">${escapeXml(lang.name)} (${lang.pct}%)</text>`;
  }).join('\n');

  return `<g id="language-telemetry" transform="translate(16, 172)">
      <rect x="0" y="0" width="368" height="7" rx="3.5" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.15)" stroke-width="0.8" />
      <!-- Segments -->
      ${rects}

      <!-- Legend in 2 rows -->
      <g transform="translate(0, 20)">
        <!-- Row 1 -->
${row1Svg}

        <!-- Row 2 -->
${row2Svg}
      </g>
    </g>`;
}

async function fetchAllStats(headers) {
  let reposCount = null;
  let starsCount = null;
  let commitCount = null;
  let viewCount = null;
  let languages = null;

  try {
    const [userRes, reposRes, commitsRes, viewsRes] = await Promise.allSettled([
      fetch(`https://api.github.com/users/${USERNAME}`, { headers }),
      fetch(`https://api.github.com/users/${USERNAME}/repos?per_page=100`, { headers }),
      fetch(`https://api.github.com/search/commits?q=author:${USERNAME}`, { headers }),
      fetch(`https://komarev.com/ghpvc/?username=${USERNAME}`, { headers: { 'User-Agent': 'Mozilla/5.0' } })
    ]);

    if (userRes.status === 'fulfilled' && userRes.value.ok) {
      const data = await userRes.value.json();
      reposCount = data.public_repos;
    }

    let nonForkRepos = [];
    if (reposRes.status === 'fulfilled' && reposRes.value.ok) {
      const reposData = await reposRes.value.json();
      if (Array.isArray(reposData)) {
        nonForkRepos = reposData.filter(r => !r.fork);
        const totalStars = nonForkRepos.reduce((acc, r) => acc + (r.stargazers_count || 0), 0);
        starsCount = totalStars > 0 ? `★ ${totalStars}` : '★ ACTIVE';
      }
    }

    if (commitsRes.status === 'fulfilled' && commitsRes.value.ok) {
      const commitData = await commitsRes.value.json();
      if (commitData.total_count != null) {
        commitCount = formatApproxCommits(commitData.total_count);
      }
    }

    if (viewsRes.status === 'fulfilled' && viewsRes.value.ok) {
      const komarevSvg = await viewsRes.value.text();
      const matches = [...komarevSvg.matchAll(/>([0-9,]+)<\/text>/g)];
      if (matches.length > 0) {
        viewCount = matches[matches.length - 1][1];
      }
    }

    // Tự động thu thập tỷ số ngôn ngữ lập trình từ tất cả public repos
    if (nonForkRepos.length > 0) {
      const langResponses = await Promise.allSettled(
        nonForkRepos.map(r => fetch(r.languages_url, { headers }).then(res => res.json()))
      );

      const langTotals = {};
      for (const res of langResponses) {
        if (res.status === 'fulfilled' && typeof res.value === 'object' && res.value !== null) {
          for (const [lang, bytes] of Object.entries(res.value)) {
            langTotals[lang] = (langTotals[lang] || 0) + bytes;
          }
        }
      }

      const sortedLangs = Object.entries(langTotals).sort((a, b) => b[1] - a[1]);
      const totalBytes = sortedLangs.reduce((sum, [, bytes]) => sum + bytes, 0);

      if (totalBytes > 0) {
        const top4 = sortedLangs.slice(0, 4);
        const otherBytes = sortedLangs.slice(4).reduce((sum, [, bytes]) => sum + bytes, 0);

        const items = top4.map(([name, bytes]) => ({
          name,
          pct: Math.round((bytes / totalBytes) * 100),
          bytes
        }));

        if (otherBytes > 0) {
          items.push({
            name: 'Other',
            pct: Math.round((otherBytes / totalBytes) * 100),
            bytes: otherBytes
          });
        }

        languages = items;
      }
    }
  } catch (err) {
    console.error('Error fetching stats:', err);
  }

  return { reposCount, starsCount, commitCount, viewCount, languages };
}

module.exports = async function handler(req, res) {
  const isMobile = req.query && (req.query.view === 'mobile' || req.query.mobile === 'true');
  const svgFileName = isMobile ? 'stats-card-mobile.svg' : 'stats-card.svg';
  const svgPath = path.join(process.cwd(), 'svg', '04_stats', svgFileName);

  let svgContent = '';
  try {
    svgContent = fs.readFileSync(svgPath, 'utf8');
  } catch (err) {
    return res.status(500).send('SVG template not found');
  }

  const token = process.env.GH_TOKEN || process.env.GITHUB_TOKEN;
  const headers = {
    'User-Agent': 'Mozilla/5.0',
    ...(token && { Authorization: `token ${token}` })
  };

  const { reposCount, starsCount, commitCount, viewCount, languages } = await fetchAllStats(headers);

  // Điền 4 chỉ số chính
  if (commitCount) {
    svgContent = svgContent.replace(/(<text id="stat-commits"[^>]*>)[^<]*(<\/text>)/, `$1${commitCount}$2`);
  }
  if (reposCount !== null) {
    svgContent = svgContent.replace(/(<text id="stat-repos"[^>]*>)[^<]*(<\/text>)/, `$1${reposCount}$2`);
  }
  if (starsCount) {
    svgContent = svgContent.replace(/(<text id="stat-stars"[^>]*>)[^<]*(<\/text>)/, `$1${starsCount}$2`);
  }
  if (viewCount) {
    svgContent = svgContent.replace(/(<text id="stat-views"[^>]*>)[^<]*(<\/text>)/, `$1${viewCount}$2`);
  }

  // Điền thanh ngôn ngữ thời gian thực (nếu thu thập thành công)
  if (languages && languages.length > 0) {
    const dynamicBar = isMobile
      ? generateLanguageBarMobile(languages)
      : generateLanguageBarDesktop(languages);

    svgContent = svgContent.replace(/<!-- LANGUAGE_BAR_START -->[\s\S]*?<!-- LANGUAGE_BAR_END -->/, () => {
      return `<!-- LANGUAGE_BAR_START -->\n      ${dynamicBar}\n      <!-- LANGUAGE_BAR_END -->`;
    });
  }

  res.setHeader('Content-Type', 'image/svg+xml; charset=utf-8');
  res.setHeader('Cache-Control', 'public, max-age=30, s-maxage=30, stale-while-revalidate=60');
  return res.status(200).send(svgContent);
};
