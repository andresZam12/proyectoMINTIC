"use client";

import { CSSProperties, useMemo, useState } from "react";
import content from "./content.json";

type Section = (typeof content.sections)[number];

type ThemeStyle = CSSProperties & {
  "--app-bg": string;
  "--app-surface": string;
  "--app-surface-soft": string;
  "--app-border": string;
  "--app-primary": string;
  "--app-accent": string;
  "--app-accent-soft": string;
  "--app-text": string;
  "--app-muted": string;
  "--app-warning": string;
};

// ─── Componente existente: Power BI ───────────────────────────────────────────
function PowerBIView({
  section,
  loadingLabel,
}: {
  section: Section;
  loadingLabel: string;
}) {
  return (
    <article className="w-full overflow-hidden rounded-lg border border-(--app-border) bg-(--app-surface) shadow-2xl shadow-black/40">
      <div className="relative aspect-video w-full bg-(--app-primary) overflow-hidden">
        <div className="absolute inset-0 grid place-items-center bg-[linear-gradient(135deg,var(--app-primary),var(--app-surface))]">
          <span className="rounded-md border border-(--app-border) bg-(--app-surface)/85 px-4 py-2 text-sm font-medium text-(--app-muted) backdrop-blur">
            {loadingLabel}
          </span>
        </div>
        <iframe
          key={section.url}
          className="absolute inset-0 h-full w-full border-0"
          title={section.title}
          src={`${section.url}&navContentPaneEnabled=false`}
          allowFullScreen
        />
      </div>
    </article>
  );
}

// ─── Componente existente: Pantalla de dashboard ──────────────────────────────
function DashboardScreen({
  section,
  index,
}: {
  section: Section;
  index: number;
}) {
  return (
    <section className="grid min-h-[calc(100vh-140px)] gap-10 py-8 lg:grid-cols-[380px_1fr] items-center">
      {/* Columna Izquierda: Información */}
      <div className="flex flex-col rounded-lg border border-(--app-border) bg-(--app-surface) p-6 md:p-7 shadow-xl">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-(--app-accent)">
          {section.kicker}
        </p>
        <h2 className="mt-3 text-2xl font-bold leading-tight text-(--app-text) md:text-3xl">
          {section.title}
        </h2>
        <p className="mt-2 text-sm font-semibold text-(--app-warning)">
          {section.subtitle}
        </p>
        <p className="mt-4 text-xs leading-relaxed text-(--app-muted)">
          {section.description}
        </p>

        <div className="mt-6 space-y-5">
          <div className="rounded-lg border border-(--app-border) bg-(--app-surface-soft) p-4">
            <h3 className="text-xs font-bold text-(--app-text) uppercase tracking-wide">
              {section.pointsTitle}
            </h3>
            <ul className="mt-3 space-y-2 text-xs leading-5 text-(--app-muted)">
              {section.points.map((point) => (
                <li className="flex gap-3" key={point}>
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-(--app-accent)" />
                  <span>{point}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-xs font-bold text-(--app-text) mb-2 uppercase tracking-wide">
              {section.dataTitle}
            </h3>
            <div className="flex flex-wrap gap-2">
              {section.data.map((item) => (
                <span
                  className="rounded-md border border-(--app-border) bg-(--app-bg) px-2.5 py-1 text-[10px] font-bold text-(--app-muted) uppercase tracking-wider"
                  key={item}
                >
                  {item}
                </span>
              ))}
            </div>
          </div>
        </div>

        <a
          className="mt-6 inline-flex h-11 items-center justify-center rounded-md bg-(--app-accent) px-6 text-xs font-bold text-(--app-bg) transition-all hover:brightness-110 active:scale-95 shadow-lg shadow-(--app-accent)/10"
          href={section.url}
          target="_blank"
          rel="noreferrer"
        >
          {content.powerBi.openLabel}
        </a>
      </div>

      {/* Columna Derecha: Reporte Power BI */}
      <div className="flex flex-col w-full max-w-full overflow-hidden">
        <div className="mb-4 flex items-center justify-between px-1">
          <div className="flex items-center gap-3">
            <span className="text-xl font-black text-(--app-accent)">
              {String(index + 1).padStart(2, "0")}
            </span>
            <span className="h-px w-12 bg-(--app-border)" />
            <span className="text-xs font-bold uppercase tracking-widest text-(--app-muted)">
              {section.label}
            </span>
          </div>
          <span className="text-[10px] font-bold text-(--app-muted)/60 uppercase tracking-widest">
            Visualización Interactiva
          </span>
        </div>

        <PowerBIView
          section={section}
          loadingLabel={content.powerBi.loadingLabel}
        />

        <div className="mt-5 border-l-4 border-(--app-accent) bg-(--app-surface) p-4 rounded-r-lg shadow-inner">
          <h3 className="text-[10px] font-bold uppercase tracking-[0.2em] text-(--app-accent)">
            {section.valueTitle}
          </h3>
          <p className="mt-1 text-sm text-(--app-muted) italic leading-relaxed">
            {"\""}{section.value}{"\""}
          </p>
        </div>
      </div>
    </section>
  );
}

// ─── NUEVO: Pantalla ANOVA ────────────────────────────────────────────────────
function AnovaScreen() {
  const a = content.anova;

  return (
    <section className="min-h-[calc(100vh-140px)] py-8 space-y-8">

      {/* Header de sección */}
      <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-(--app-accent)">
            {a.kicker}
          </p>
          <h2 className="mt-2 text-2xl font-bold text-(--app-text) md:text-3xl">
            {a.title}
          </h2>
          <p className="mt-1 text-sm font-semibold text-(--app-warning)">
            {a.subtitle}
          </p>
        </div>
        <a
          href={a.source.url}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-2 rounded-md border border-(--app-border) bg-(--app-surface) px-4 py-2 text-[10px] font-bold uppercase tracking-wider text-(--app-muted) hover:border-(--app-accent) hover:text-(--app-accent) transition-colors"
        >
          <span className="h-1.5 w-1.5 rounded-full bg-(--app-accent)" />
          {a.source.name}
        </a>
      </div>

      {/* Descripción + Hipótesis */}
      <div className="grid gap-4 lg:grid-cols-[1fr_1fr]">
        <div className="rounded-lg border border-(--app-border) bg-(--app-surface) p-5">
          <h3 className="text-[10px] font-bold uppercase tracking-[0.2em] text-(--app-muted) mb-3">
            Descripción
          </h3>
          <p className="text-xs leading-relaxed text-(--app-muted)">{a.description}</p>
          <div className="mt-4 flex flex-wrap gap-2">
            {a.data.map((item) => (
              <span
                key={item}
                className="rounded-md border border-(--app-border) bg-(--app-bg) px-2.5 py-1 text-[10px] font-bold text-(--app-muted) uppercase tracking-wider"
              >
                {item}
              </span>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-(--app-border) bg-(--app-surface) p-5 space-y-3">
          <h3 className="text-[10px] font-bold uppercase tracking-[0.2em] text-(--app-muted)">
            Hipótesis
          </h3>
          <div className="rounded-md border border-(--app-border) bg-(--app-surface-soft) p-3">
            <p className="text-[10px] font-bold text-(--app-warning) uppercase tracking-wider mb-1">H₀ — Hipótesis nula</p>
            <p className="text-xs text-(--app-muted) leading-relaxed">{a.hypothesis.null}</p>
          </div>
          <div className="rounded-md border border-(--app-accent)/30 bg-(--app-accent-soft) p-3">
            <p className="text-[10px] font-bold text-(--app-accent) uppercase tracking-wider mb-1">H₁ — Hipótesis alternativa</p>
            <p className="text-xs text-(--app-muted) leading-relaxed">{a.hypothesis.alt}</p>
          </div>
        </div>
      </div>

      {/* Estadística descriptiva + Banco Mundial */}
      <div className="grid gap-4 lg:grid-cols-[1fr_1fr]">

        {/* Tabla descriptiva */}
        <div className="rounded-lg border border-(--app-border) bg-(--app-surface) overflow-hidden">
          <div className="px-5 py-3 border-b border-(--app-border) bg-(--app-surface-soft)">
            <h3 className="text-[10px] font-bold uppercase tracking-[0.2em] text-(--app-accent)">
              Estadística descriptiva por grupo
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-(--app-border)">
                  {["Grupo", "n", "Media (%)", "Std", "Mín", "Máx"].map((h) => (
                    <th key={h} className="px-4 py-2.5 text-left text-[10px] font-bold uppercase tracking-wider text-(--app-muted)">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {a.descriptive.map((row, i) => (
                  <tr key={i} className="border-b border-(--app-border) last:border-0 hover:bg-(--app-surface-soft) transition-colors">
                    <td className="px-4 py-3 font-medium text-(--app-text)">{row.group}</td>
                    <td className="px-4 py-3 text-(--app-muted)">{row.n}</td>
                    <td className="px-4 py-3 font-bold text-(--app-accent)">{row.media}%</td>
                    <td className="px-4 py-3 text-(--app-muted)">{row.std}</td>
                    <td className="px-4 py-3 text-(--app-muted)">{row.min}</td>
                    <td className="px-4 py-3 text-(--app-muted)">{row.max}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Dataset Banco Mundial */}
        <div className="rounded-lg border border-(--app-border) bg-(--app-surface) overflow-hidden">
          <div className="px-5 py-3 border-b border-(--app-border) bg-(--app-surface-soft)">
            <h3 className="text-[10px] font-bold uppercase tracking-[0.2em] text-(--app-accent)">
              Dataset externo — Banco Mundial Colombia
            </h3>
            <p className="text-[9px] text-(--app-muted) mt-0.5">{a.source.indicator}</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-(--app-border)">
                  <th className="px-4 py-2.5 text-left text-[10px] font-bold uppercase tracking-wider text-(--app-muted)">Año</th>
                  <th className="px-4 py-2.5 text-left text-[10px] font-bold uppercase tracking-wider text-(--app-muted)">Tasa Desempleo (%)</th>
                  <th className="px-4 py-2.5 text-left text-[10px] font-bold uppercase tracking-wider text-(--app-muted)">Fuente</th>
                </tr>
              </thead>
              <tbody>
                {a.bancoMundial.map((row) => (
                  <tr key={row.anio} className="border-b border-(--app-border) last:border-0 hover:bg-(--app-surface-soft) transition-colors">
                    <td className="px-4 py-2.5 text-(--app-text) font-medium">{row.anio}</td>
                    <td className="px-4 py-2.5 font-bold" style={{ color: row.tasa > 12 ? "#f87171" : row.tasa > 10 ? "#facc15" : "#42f59e" }}>
                      {row.tasa}%
                    </td>
                    <td className="px-4 py-2.5 text-(--app-muted) text-[10px]">Banco Mundial</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Resultado ANOVA */}
      <div className="rounded-lg border border-(--app-border) bg-(--app-surface) overflow-hidden">
        <div className="px-5 py-3 border-b border-(--app-border) bg-(--app-surface-soft) flex items-center justify-between">
          <h3 className="text-[10px] font-bold uppercase tracking-[0.2em] text-(--app-accent)">
            Tabla ANOVA de un factor
          </h3>
          <div className="flex gap-3">
            <span className="rounded-md bg-(--app-accent-soft) border border-(--app-accent)/40 px-3 py-1 text-[10px] font-bold text-(--app-accent)">
              F = {a.anovaResult.f}
            </span>
            <span className="rounded-md bg-(--app-accent-soft) border border-(--app-accent)/40 px-3 py-1 text-[10px] font-bold text-(--app-accent)">
              p = {a.anovaResult.p}
            </span>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-(--app-border)">
                {["Fuente de variación", "Suma de cuadrados", "Grados de libertad", "Media cuadrática", "F", "p-valor"].map((h) => (
                  <th key={h} className="px-4 py-2.5 text-left text-[10px] font-bold uppercase tracking-wider text-(--app-muted)">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {a.anovaResult.rows.map((row, i) => (
                <tr key={i} className="border-b border-(--app-border) last:border-0 hover:bg-(--app-surface-soft) transition-colors">
                  <td className="px-4 py-3 font-medium text-(--app-text)">{row.fuente}</td>
                  <td className="px-4 py-3 text-(--app-muted)">{row.sc}</td>
                  <td className="px-4 py-3 text-(--app-muted)">{row.gl}</td>
                  <td className="px-4 py-3 text-(--app-muted)">{row.mc}</td>
                  <td className="px-4 py-3 font-bold text-(--app-accent)">{row.f}</td>
                  <td className="px-4 py-3 font-bold text-(--app-accent)">{row.p}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="px-5 py-3 border-t border-(--app-border) bg-(--app-accent-soft)">
          <p className="text-xs font-bold text-(--app-accent)">
            ✓ {a.anovaResult.conclusion}
          </p>
        </div>
      </div>

      {/* Post-hoc Tukey */}
      <div className="rounded-lg border border-(--app-border) bg-(--app-surface) overflow-hidden">
        <div className="px-5 py-3 border-b border-(--app-border) bg-(--app-surface-soft)">
          <h3 className="text-[10px] font-bold uppercase tracking-[0.2em] text-(--app-accent)">
            Post-hoc Tukey HSD — Comparación de pares
          </h3>
          <p className="text-[9px] text-(--app-muted) mt-0.5">
            Identifica entre cuáles grupos existe la diferencia real (α = 0.05)
          </p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-(--app-border)">
                {["Grupo 1", "Grupo 2", "Diferencia media (pp)", "p ajustado", "¿Significativo?"].map((h) => (
                  <th key={h} className="px-4 py-2.5 text-left text-[10px] font-bold uppercase tracking-wider text-(--app-muted)">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {a.tukey.map((row, i) => (
                <tr key={i} className="border-b border-(--app-border) last:border-0 hover:bg-(--app-surface-soft) transition-colors">
                  <td className="px-4 py-3 text-(--app-text) font-medium">{row.g1}</td>
                  <td className="px-4 py-3 text-(--app-text) font-medium">{row.g2}</td>
                  <td className="px-4 py-3 text-(--app-muted)">{row.diff}</td>
                  <td className="px-4 py-3 text-(--app-muted)">{row.p}</td>
                  <td className="px-4 py-3">
                    <span className={`rounded-md px-2.5 py-1 text-[10px] font-bold ${
                      row.sig
                        ? "bg-(--app-accent-soft) text-(--app-accent) border border-(--app-accent)/40"
                        : "bg-(--app-surface-soft) text-(--app-muted) border border-(--app-border)"
                    }`}>
                      {row.sig ? "SÍ ✓" : "NO"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Conclusión final */}
      <div className="border-l-4 border-(--app-accent) bg-(--app-surface) p-5 rounded-r-lg shadow-inner">
        <h3 className="text-[10px] font-bold uppercase tracking-[0.2em] text-(--app-accent) mb-2">
          {a.valueTitle}
        </h3>
        <p className="text-sm text-(--app-muted) italic leading-relaxed">
          &quot;{a.value}&quot;
        </p>
        <div className="mt-4 flex flex-wrap gap-3">
          {a.points.map((p) => (
            <div key={p} className="flex items-start gap-2 text-xs text-(--app-muted)">
              <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-(--app-accent)" />
              <span>{p}</span>
            </div>
          ))}
        </div>
      </div>

    </section>
  );
}

// ─── Componente principal ─────────────────────────────────────────────────────
export default function Home() {
  const [activeId, setActiveId] = useState(content.sections[0].id);

  const isAnova = activeId === "anova";

  const activeIndex = useMemo(
    () =>
      Math.max(
        content.sections.findIndex((section) => section.id === activeId),
        0,
      ),
    [activeId],
  );

  const activeSection = content.sections[activeIndex];

  const themeStyle: ThemeStyle = {
    "--app-bg": content.theme.background,
    "--app-surface": content.theme.surface,
    "--app-surface-soft": content.theme.surfaceSoft,
    "--app-border": content.theme.border,
    "--app-primary": content.theme.primary,
    "--app-accent": content.theme.accent,
    "--app-accent-soft": content.theme.accentSoft,
    "--app-text": content.theme.text,
    "--app-muted": content.theme.muted,
    "--app-warning": content.theme.warning,
  } as ThemeStyle;

  // Todas las secciones de nav: las 4 existentes + ANOVA
  const allNavItems = [
    ...content.sections,
    { id: content.anova.id, label: content.anova.label },
  ];

  return (
    <main
      className="min-h-screen bg-(--app-bg) text-(--app-text) selection:bg-(--app-accent) selection:text-(--app-bg)"
      style={themeStyle}
    >
      <header className="sticky top-0 z-50 border-b border-(--app-border) bg-(--app-bg)/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-400 flex-col gap-4 px-6 py-4 lg:flex-row lg:items-center lg:justify-between lg:px-10">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.3em] text-(--app-accent)">
              {content.project.eyebrow}
            </p>
            <h1 className="mt-0.5 text-xl font-bold tracking-tight">
              {content.project.name}
            </h1>
          </div>

          <nav
            className="flex flex-wrap gap-2 sm:grid sm:grid-cols-2 lg:flex xl:grid-cols-5"
            aria-label={content.navigation.dashboardLabel}
          >
            {allNavItems.map((section) => {
              const isActive = section.id === activeId;
              const isAnovaBtn = section.id === "anova";

              return (
                <button
                  className="inline-flex min-h-10 items-center justify-center rounded-md border px-4 text-center text-xs font-bold transition-all active:scale-95"
                  key={section.id}
                  onClick={() => setActiveId(section.id)}
                  style={{
                    background: isActive
                      ? "var(--app-accent-soft)"
                      : "transparent",
                    borderColor: isActive
                      ? "var(--app-accent)"
                      : isAnovaBtn
                      ? "var(--app-accent)30"
                      : "var(--app-border)",
                    color: isActive
                      ? "var(--app-accent)"
                      : isAnovaBtn
                      ? "var(--app-accent)99"
                      : "var(--app-muted)",
                  }}
                  type="button"
                >
                  {section.label}
                </button>
              );
            })}
          </nav>
        </div>
      </header>

      <div className="mx-auto max-w-400 px-6 lg:px-10">
        {isAnova ? (
          <AnovaScreen />
        ) : (
          <DashboardScreen section={activeSection} index={activeIndex} />
        )}
      </div>
    </main>
  );
}