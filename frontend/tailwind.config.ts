import type { Config } from "tailwindcss";

// Design System Specification (prompt §13.6): 12-col grid via default
// Tailwind, 8px spacing baseline, 6-8px radius, 1px borders, restrained
// blue accent, calm neutral surfaces. All semantic color usage must go
// through these tokens - pages must not invent ad-hoc colors.
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: {
          DEFAULT: "#ffffff",
          sunken: "#f5f6f8",
          raised: "#ffffff",
          overlay: "#ffffff",
        },
        border: {
          DEFAULT: "#e2e5ea",
          strong: "#c7cdd6",
        },
        ink: {
          DEFAULT: "#1a1f29",
          muted: "#5b6472",
          // WCAG AA text contrast (4.5:1 on surface/surface-sunken); the
          // prior #8b93a1 measured ~3.1:1 (axe color-contrast, all pages).
          // #6b7280 measured 4.47:1 on surface-sunken and #66707d measured
          // 4.43:1 on accent-soft badges (both just short) in real renders,
          // hence the extra margin here.
          faint: "#616b78",
        },
        accent: {
          DEFAULT: "#2f6fed",
          soft: "#eaf1ff",
          strong: "#1d4fc4",
        },
        state: {
          neutral: "#5b6472",
          active: "#2f6fed",
          // Darkened for WCAG AA text contrast on their paired bg-*-50
          // badge backgrounds (axe color-contrast: success ~4.1:1, caution
          // ~3.7:1 measured on real rendered StatusBadge instances; stale
          // shares the same bg-amber-50 pairing and was below threshold by
          // the same formula, extended here for consistency).
          success: "#047857",
          caution: "#92400e",
          risk: "#c0392f",
          blocked: "#8b93a1",
          stale: "#92400e",
          unavailable: "#8b93a1",
        },
      },
      fontFamily: {
        sans: [
          "Inter",
          "-apple-system",
          "Segoe UI",
          "PingFang SC",
          "Microsoft YaHei",
          "sans-serif",
        ],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "Consolas", "monospace"],
      },
      borderRadius: {
        sm: "6px",
        DEFAULT: "8px",
      },
      spacing: {
        "4.5": "18px",
      },
      boxShadow: {
        overlay: "0 8px 24px rgba(20, 24, 32, 0.12)",
      },
    },
  },
  plugins: [],
} satisfies Config;
