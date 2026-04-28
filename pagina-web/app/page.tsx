import landingContent from "@/content/landing-content.json";
import { themeColors } from "@/theme/colors";

type KpiCard = {
  label: string;
  value: string;
  trend: string;
  description: string;
};

const iconByIndex = [
  "01",
  "02",
  "03",
] as const;

// Pega aqui la URL "Embed" de Power BI cuando la tengas disponible.
const powerBiEmbedUrl = "";

export default function Home() {
  const { navigation, hero, kpis, dashboard, footer } = landingContent;

  return (
    <main
      className="min-h-screen overflow-hidden"
      style={{
        background: themeColors.pageBackground,
        color: themeColors.textPrimary,
      }}
    >
      <div className="relative">
        <div
          aria-hidden="true"
          className="absolute inset-x-0 top-0 h-[34rem] blur-3xl"
          style={{
            background: `radial-gradient(circle at top, ${themeColors.accentSoft} 0%, transparent 65%)`,
          }}
        />

        <section className="relative mx-auto flex min-h-screen w-full max-w-7xl flex-col px-6 py-6 lg:px-10">
          <header
            className="sticky top-4 z-20 mb-8 rounded-full border px-5 py-4 backdrop-blur-xl"
            style={{
              backgroundColor: themeColors.surfaceOverlay,
              borderColor: themeColors.borderStrong,
              boxShadow: `0 20px 50px ${themeColors.shadow}`,
            }}
          >
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p
                  className="text-xs font-semibold uppercase tracking-[0.35em]"
                  style={{ color: themeColors.textMuted }}
                >
                  {navigation.badge}
                </p>
                <h1 className="text-lg font-semibold tracking-tight">
                  {navigation.projectName}
                </h1>
              </div>

              <nav className="flex flex-wrap gap-3 text-sm">
                {navigation.links.map((link) => (
                  <a
                    key={link.label}
                    href={link.href}
                    className="rounded-full px-4 py-2 transition-transform duration-200 hover:-translate-y-0.5"
                    style={{
                      color: themeColors.textSecondary,
                      backgroundColor: themeColors.surfaceSubtle,
                    }}
                  >
                    {link.label}
                  </a>
                ))}
              </nav>
            </div>
          </header>

          <section
            id="hero"
            className="grid gap-10 rounded-[2rem] border px-6 py-10 md:px-10 md:py-12 lg:grid-cols-[1.2fr_0.8fr]"
            style={{
              background: themeColors.heroGradient,
              borderColor: themeColors.borderSoft,
              boxShadow: `0 30px 70px ${themeColors.shadow}`,
            }}
          >
            <div className="space-y-8">
              <div
                className="inline-flex rounded-full border px-4 py-2 text-xs font-semibold uppercase tracking-[0.3em]"
                style={{
                  backgroundColor: themeColors.badgeBackground,
                  borderColor: themeColors.borderSoft,
                  color: themeColors.badgeText,
                }}
              >
                {hero.eyebrow}
              </div>

              <div className="space-y-5">
                <h2 className="max-w-3xl text-4xl font-semibold tracking-tight md:text-5xl lg:text-6xl">
                  {hero.title}
                </h2>
                <p
                  className="max-w-2xl text-base leading-8 md:text-lg"
                  style={{ color: themeColors.textSecondary }}
                >
                  {hero.description}
                </p>
              </div>

              <div className="flex flex-wrap gap-4">
                <a
                  href={hero.primaryAction.href}
                  className="rounded-full px-6 py-3 text-sm font-semibold transition-transform duration-200 hover:-translate-y-0.5"
                  style={{
                    backgroundColor: themeColors.primaryButton,
                    color: themeColors.primaryButtonText,
                  }}
                >
                  {hero.primaryAction.label}
                </a>
                <a
                  href={hero.secondaryAction.href}
                  className="rounded-full border px-6 py-3 text-sm font-semibold transition-transform duration-200 hover:-translate-y-0.5"
                  style={{
                    borderColor: themeColors.borderStrong,
                    color: themeColors.textPrimary,
                    backgroundColor: themeColors.surfaceOverlay,
                  }}
                >
                  {hero.secondaryAction.label}
                </a>
              </div>
            </div>

            <aside
              className="grid gap-4 rounded-[1.75rem] border p-5"
              style={{
                backgroundColor: themeColors.surfaceCard,
                borderColor: themeColors.borderSoft,
              }}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p
                    className="text-sm font-medium"
                    style={{ color: themeColors.textMuted }}
                  >
                    {hero.summary.title}
                  </p>
                  <p className="mt-2 text-3xl font-semibold">
                    {hero.summary.value}
                  </p>
                </div>
                <div
                  className="rounded-2xl px-4 py-3 text-right"
                  style={{ backgroundColor: themeColors.surfaceSubtle }}
                >
                  <p
                    className="text-xs uppercase tracking-[0.3em]"
                    style={{ color: themeColors.textMuted }}
                  >
                    Corte
                  </p>
                  <p className="mt-1 text-sm font-semibold">{hero.summary.period}</p>
                </div>
              </div>

              <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-1">
                {hero.summary.highlights.map((item) => (
                  <div
                    key={item.label}
                    className="rounded-2xl border p-4"
                    style={{
                      borderColor: themeColors.borderSoft,
                      backgroundColor: themeColors.surfaceSubtle,
                    }}
                  >
                    <p
                      className="text-xs uppercase tracking-[0.25em]"
                      style={{ color: themeColors.textMuted }}
                    >
                      {item.label}
                    </p>
                    <p className="mt-3 text-2xl font-semibold">{item.value}</p>
                    <p
                      className="mt-2 text-sm leading-6"
                      style={{ color: themeColors.textSecondary }}
                    >
                      {item.note}
                    </p>
                  </div>
                ))}
              </div>
            </aside>
          </section>

          <section id="kpis" className="mt-10">
            <div className="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
              <div>
                <p
                  className="text-sm font-semibold uppercase tracking-[0.28em]"
                  style={{ color: themeColors.textMuted }}
                >
                  {kpis.sectionEyebrow}
                </p>
                <h3 className="mt-2 text-3xl font-semibold tracking-tight">
                  {kpis.sectionTitle}
                </h3>
              </div>
              <p
                className="max-w-2xl text-sm leading-7 md:text-base"
                style={{ color: themeColors.textSecondary }}
              >
                {kpis.sectionDescription}
              </p>
            </div>

            <div className="grid gap-5 lg:grid-cols-3">
              {kpis.items.map((item, index) => (
                <KpiItem key={item.label} item={item} index={index} />
              ))}
            </div>
          </section>

          <section
            id="dashboard"
            className="mt-10 rounded-[2rem] border p-6 md:p-8"
            style={{
              backgroundColor: themeColors.surfaceCard,
              borderColor: themeColors.borderSoft,
              boxShadow: `0 24px 70px ${themeColors.shadow}`,
            }}
          >
            <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <p
                  className="text-sm font-semibold uppercase tracking-[0.28em]"
                  style={{ color: themeColors.textMuted }}
                >
                  {dashboard.eyebrow}
                </p>
                <h3 className="mt-2 text-3xl font-semibold tracking-tight">
                  {dashboard.title}
                </h3>
              </div>
              <p
                className="max-w-2xl text-sm leading-7 md:text-base"
                style={{ color: themeColors.textSecondary }}
              >
                {dashboard.description}
              </p>
            </div>

            <div
              className="mt-8 rounded-[1.75rem] border p-4 md:p-6"
              style={{
                borderColor: themeColors.borderStrong,
                backgroundColor: themeColors.surfaceSubtle,
              }}
            >
              <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-lg font-semibold">{dashboard.embedTitle}</p>
                  <p
                    className="mt-1 text-sm"
                    style={{ color: themeColors.textSecondary }}
                  >
                    {dashboard.embedHelp}
                  </p>
                </div>
                <div
                  className="rounded-full px-4 py-2 text-xs font-semibold uppercase tracking-[0.25em]"
                  style={{
                    backgroundColor: themeColors.badgeBackground,
                    color: themeColors.badgeText,
                  }}
                >
                  Power BI
                </div>
              </div>

              <div
                className="relative min-h-[420px] overflow-hidden rounded-[1.5rem] border md:min-h-[560px]"
                style={{
                  borderColor: themeColors.borderSoft,
                  background: `linear-gradient(135deg, ${themeColors.embedBackgroundStart} 0%, ${themeColors.embedBackgroundEnd} 100%)`,
                }}
              >
                {/*
                  ESPACIO PRINCIPAL PARA POWER BI

                  Opcion 1:
                  Pega la URL embed en la constante powerBiEmbedUrl para que el iframe se active automaticamente.

                  Opcion 2:
                  Reemplaza el bloque completo por el iframe oficial que entrega Power BI.

                  Ejemplo:
                  <iframe
                    title="Dashboard Power BI"
                    src="AQUI_VA_EL_EMBED_URL_DE_POWER_BI"
                    className="h-full min-h-[420px] w-full"
                    allowFullScreen
                  />
                */}

                {powerBiEmbedUrl ? (
                  <iframe
                    title="Dashboard Power BI"
                    src={powerBiEmbedUrl}
                    className="h-full min-h-[420px] w-full"
                    allowFullScreen
                  />
                ) : (
                  <div className="flex h-full min-h-[420px] flex-col items-center justify-center px-6 py-12 text-center md:min-h-[560px]">
                    <div
                      className="rounded-3xl border px-5 py-3 text-xs font-semibold uppercase tracking-[0.3em]"
                      style={{
                        borderColor: themeColors.borderSoft,
                        backgroundColor: themeColors.surfaceOverlay,
                        color: themeColors.textMuted,
                      }}
                    >
                      Zona de integracion
                    </div>
                    <h4 className="mt-6 text-2xl font-semibold tracking-tight md:text-3xl">
                      {dashboard.placeholderTitle}
                    </h4>
                    <p
                      className="mt-4 max-w-2xl text-sm leading-7 md:text-base"
                      style={{ color: themeColors.textSecondary }}
                    >
                      {dashboard.placeholderDescription}
                    </p>
                    <div className="mt-8 w-full max-w-3xl rounded-[1.5rem] border border-dashed p-5 text-left">
                      <p className="font-mono text-xs md:text-sm">
                        {dashboard.codeHint}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </section>

          <footer
            className="mt-10 rounded-[2rem] border px-6 py-6"
            style={{
              borderColor: themeColors.borderSoft,
              backgroundColor: themeColors.surfaceCard,
            }}
          >
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="text-lg font-semibold">{footer.title}</p>
                <p
                  className="mt-1 text-sm leading-7"
                  style={{ color: themeColors.textSecondary }}
                >
                  {footer.description}
                </p>
              </div>
              <a
                href={footer.action.href}
                className="inline-flex rounded-full px-5 py-3 text-sm font-semibold transition-transform duration-200 hover:-translate-y-0.5"
                style={{
                  backgroundColor: themeColors.primaryButton,
                  color: themeColors.primaryButtonText,
                }}
              >
                {footer.action.label}
              </a>
            </div>
          </footer>
        </section>
      </div>
    </main>
  );
}

function KpiItem({ item, index }: { item: KpiCard; index: number }) {
  return (
    <article
      className="rounded-[1.75rem] border p-6"
      style={{
        backgroundColor: themeColors.surfaceCard,
        borderColor: themeColors.borderSoft,
        boxShadow: `0 20px 50px ${themeColors.shadow}`,
      }}
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <p
            className="text-sm font-semibold uppercase tracking-[0.25em]"
            style={{ color: themeColors.textMuted }}
          >
            {item.label}
          </p>
          <p className="mt-4 text-4xl font-semibold tracking-tight">{item.value}</p>
        </div>
        <div
          className="rounded-2xl px-4 py-3 text-sm font-semibold"
          style={{
            backgroundColor: themeColors.badgeBackground,
            color: themeColors.badgeText,
          }}
        >
          {iconByIndex[index] ?? "04"}
        </div>
      </div>

      <div className="mt-8 flex items-center justify-between gap-4">
        <span
          className="rounded-full px-4 py-2 text-sm font-semibold"
          style={{
            backgroundColor: themeColors.surfaceSubtle,
            color: themeColors.success,
          }}
        >
          {item.trend}
        </span>
      </div>

      <p
        className="mt-5 text-sm leading-7 md:text-base"
        style={{ color: themeColors.textSecondary }}
      >
        {item.description}
      </p>
    </article>
  );
}
