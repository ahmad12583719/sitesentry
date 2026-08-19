import { Button } from "@/components/ui/button";
import { ArrowUpRight, Check, ChevronRight, FileJson, FileText, LockKeyhole, Moon, Radar, ScanLine, ShieldAlert, Sun, TriangleAlert } from "lucide-react";
import { useEffect, useState } from "react";

/**
 * Aperture Atlas: SiteSentry's proprietary identity. A field-log layout, asymmetric orbital instrument, calibrated indexes, and a Paper/Night theme make security evidence feel physical, inspectable, and uniquely local-first.
 */
const asset = {
  mark: "/manus-storage/sitesentry-scan-aperture-mark_8ea7e204.png",
  tls: "/manus-storage/sitesentry-tls-orbit_6e987370.png",
  ports: "/manus-storage/sitesentry-port-map_fb6f8f53.png",
  files: "/manus-storage/sitesentry-file-inspection_d1aaf3c9.png",
};

const evidence = [
  { id: "01 / TLS", severity: "High", title: "Certificate renewal window is approaching", text: "The certificate has 12 days remaining before expiry. Automated renewal and deployment checks should be confirmed now.", fix: "Renew the certificate and confirm the full chain is served.", icon: TriangleAlert, color: "#c7503d" },
  { id: "02 / HTTP", severity: "Medium", title: "Content-Security-Policy is missing", text: "The final HTTPS response does not send a CSP, leaving browser resource controls unspecified.", fix: "Add a restrictive policy and tune it to the resources your site uses.", icon: ShieldAlert, color: "#c88b26" },
  { id: "03 / PORT", severity: "Medium", title: "Port 3306 is reachable — MySQL", text: "A database service answers on a common public port. Confirm public reachability is intentional.", fix: "Close the port or restrict it with a network allowlist.", icon: Radar, color: "#c88b26" },
  { id: "04 / WEB", severity: "Pass", title: "No public environment file found", text: "The bounded .env probe was not served by the target.", fix: "Keep environment files outside the public web root.", icon: Check, color: "#0b8f83" },
];

function OrbitInstrument({ active }: { active: boolean }) {
  return (
    <div className={`atlas-orbit ${active ? "is-scanning" : ""}`} aria-hidden="true">
      <span className="atlas-grid" />
      <span className="atlas-ring atlas-ring-a" />
      <span className="atlas-ring atlas-ring-b" />
      <span className="atlas-ring atlas-ring-c" />
      <span className="atlas-cursor atlas-cursor-a" />
      <span className="atlas-cursor atlas-cursor-b" />
      <span className="atlas-core"><img src={asset.mark} alt="" /></span>
      <span className="atlas-index atlas-index-top">FIELD / 03</span>
      <span className="atlas-index atlas-index-right">LOCAL / 01</span>
      <span className="atlas-index atlas-index-bottom">EVIDENCE</span>
    </div>
  );
}

function ThemeSwitch({ dark, onToggle }: { dark: boolean; onToggle: () => void }) {
  return <button type="button" onClick={onToggle} aria-pressed={dark} className="inline-flex h-9 items-center gap-2 border px-3 font-mono text-[10px] font-bold uppercase tracking-[.1em] transition-all duration-200 hover:-translate-y-0.5" aria-label="Toggle the dashboard colour theme">{dark ? <Moon className="h-3.5 w-3.5 text-[#83d5c7]" /> : <Sun className="h-3.5 w-3.5 text-[#0b8f83]" />}{dark ? "Night record" : "Paper record"}</button>;
}

export default function Home() {
  const [dark, setDark] = useState(false);
  const [scanning, setScanning] = useState(false);
  useEffect(() => { setDark(localStorage.getItem("sitesentry-preview-theme") === "dark"); }, []);
  const toggleTheme = () => setDark((value) => { const next = !value; localStorage.setItem("sitesentry-preview-theme", next ? "dark" : "light"); return next; });
  const runPreview = () => { setScanning(true); window.setTimeout(() => setScanning(false), 1900); };
  const ink = dark ? "text-[#edf8f4]" : "text-[#102724]";
  const muted = dark ? "text-[#9dbbb4]" : "text-[#52706a]";
  const line = dark ? "border-[#2c4945]" : "border-[#b6cbc4]";
  const surface = dark ? "bg-[#0b1719]" : "bg-[#edf5f2]";

  return (
    <div className={`min-h-screen font-['IBM_Plex_Sans'] transition-colors duration-500 ${dark ? "bg-[#081315]" : "bg-[#edf5f2]"}`}>
      <div className="grid min-h-screen lg:grid-cols-[228px_minmax(0,1fr)]">
        <aside className="relative hidden h-screen overflow-hidden bg-[#071719] px-5 py-7 text-[#d9e9e4] lg:sticky lg:top-0 lg:flex lg:flex-col">
          <div className="absolute left-0 top-0 h-32 w-px bg-[#0b8f83]" />
          <div className="flex items-center gap-3"><img src={asset.mark} alt="" className="h-10 w-10 object-contain" /><div><p className="font-['Space_Grotesk'] text-[22px] font-bold leading-none tracking-[-.08em]">SiteSentry</p><p className="mt-1 font-mono text-[8px] uppercase tracking-[.18em] text-[#72c8bb]">Local security inspection</p></div></div>
          <nav className="mt-20 grid gap-2" aria-label="Field-log navigation">{[["00", "Launch"], ["01", "Posture"], ["02", "Evidence"], ["03", "Protocol"]].map(([number, label], index) => <a key={label} href={`#${label.toLowerCase()}`} className={`grid grid-cols-[32px_1fr] items-center border-l px-3 py-3 font-mono text-[11px] uppercase tracking-[.1em] transition-all ${index === 0 ? "border-[#0b8f83] bg-[#14393a] text-white" : "border-transparent text-[#88a8a1] hover:border-[#4fa99b] hover:bg-[#0d292b] hover:text-white"}`}><span className="text-[9px] text-[#55998e]">{number}</span>{label}</a>)}</nav>
          <div className="mt-auto border-t border-[#274441] pt-5"><div className="flex items-center gap-3"><span className="relative flex h-2 w-2"><span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#44c4b1] opacity-50" /><span className="relative inline-flex h-2 w-2 rounded-full bg-[#0b8f83]" /></span><p className="text-xs leading-snug text-[#8ca9a3]">Private workstation<br /><strong className="font-semibold text-[#e8f3ef]">Local mode active</strong></p></div></div>
        </aside>

        <main className={`min-w-0 ${surface} transition-colors duration-500`}>
          <header className={`flex min-h-20 items-center justify-between gap-4 border-b px-6 sm:px-[6vw] ${line}`}><div className="flex items-center gap-3"><span className="h-2 w-2 rounded-full bg-[#0b8f83] shadow-[0_0_0_5px_#0b8f8320]" /><p className="font-mono text-[10px] font-bold uppercase tracking-[.15em] text-[#0b8f83]">Private field record <span className={muted}>/ local-only</span></p></div><ThemeSwitch dark={dark} onToggle={toggleTheme} /></header>

          <section id="launch" className="relative min-h-[535px] overflow-hidden bg-[#071d20] px-6 py-16 text-[#eefaf6] sm:px-[8vw] sm:py-[8vw]">
            <div className="absolute inset-0 opacity-35" style={{ backgroundImage: "repeating-linear-gradient(90deg, transparent 0, transparent 61px, rgba(117,213,197,.12) 62px, transparent 63px), repeating-linear-gradient(0deg, transparent 0, transparent 61px, rgba(117,213,197,.09) 62px, transparent 63px)" }} />
            <div className="relative z-10 max-w-xl"><p className="font-mono text-[10px] font-bold uppercase tracking-[.15em] text-[#76cfc0]">Target vector / 01</p><h1 className="mt-5 font-['Space_Grotesk'] text-4xl font-bold leading-[.94] tracking-[-.075em] sm:text-5xl">Open the aperture.<br /><span className="text-[#8bdbce]">Read the perimeter.</span></h1><p className="mt-7 max-w-lg text-[17px] leading-relaxed text-[#bdd8d1]">A private instrument for turning a site’s exposed configuration into a traceable field log—without telemetry, cloud accounts, or black-box scores.</p>
              <div className="mt-10 border border-[#71b7ad] bg-[#edf8f5] p-4 text-[#102724] shadow-[13px_13px_0_#020a0b66] sm:p-5"><div className="flex items-center justify-between"><p className="font-mono text-[9px] font-bold uppercase tracking-[.15em] text-[#0b8f83]">Instrument input</p><p className="font-mono text-[9px] text-[#52706a]">PUBLIC TARGET ONLY</p></div><div className="mt-3 flex flex-col gap-3 sm:flex-row"><div className="flex min-h-12 flex-1 items-center border border-[#aec6bf] bg-white px-4 font-mono text-sm text-[#5a766f]">example.com</div><Button onClick={runPreview} className="h-12 rounded-none bg-[#0b8f83] px-5 font-bold hover:bg-[#08786e]">{scanning ? <><ScanLine className="mr-2 h-4 w-4 animate-pulse" />Vectoring…</> : <>Read perimeter <ArrowUpRight className="ml-2 h-4 w-4" /></>}</Button></div><p className="mt-3 flex items-center gap-2 text-xs text-[#58736c]"><LockKeyhole className="h-3.5 w-3.5 text-[#0b8f83]" />Your consent is a reminder: inspect only targets you are authorized to assess.</p></div>
            </div>
            <OrbitInstrument active={scanning} />
          </section>

          <section id="posture" className={`px-6 py-14 sm:px-[8vw] sm:py-[6vw] ${surface}`}><div className={`grid gap-8 border-y-2 py-8 lg:grid-cols-[1fr_auto_auto] ${dark ? "border-y-[#c3e6df]" : "border-y-[#102724]"}`}><div><p className="font-mono text-[10px] font-bold uppercase tracking-[.14em] text-[#0b8f83]">Posture register / target 01</p><h2 className={`mt-4 font-['Space_Grotesk'] text-4xl font-bold tracking-[-.07em] sm:text-5xl ${ink}`}>example.com</h2><p className={`mt-1 text-xs ${muted}`}>Visual preview · fixed ruleset · no data leaves this device</p><p className={`mt-5 max-w-md text-sm leading-relaxed ${muted}`}>Three open observations are recorded below. The grade is an explicit weighted sum, not a predictive score.</p></div><div className="flex items-center gap-5"><div className="relative grid h-36 w-36 place-items-center rounded-[42%_58%_48%_52%] border-[13px] border-[#0b8f83] bg-white font-['Space_Grotesk'] text-[90px] font-bold leading-none tracking-[-.14em] text-[#102724] shadow-[0_0_0_1px_#0b8f83,0_0_0_16px_#0b8f8314] before:absolute before:inset-[-25px] before:rounded-full before:border before:border-dashed before:border-[#5fa196]"><span className="relative">B</span></div><div><p className={`text-sm ${muted}`}><strong className={`font-['Space_Grotesk'] text-4xl tracking-[-.07em] ${ink}`}>82</strong>/100</p><p className={`mt-1 max-w-[145px] text-xs leading-relaxed ${muted}`}>Measured controls are present. Review the record.</p></div></div><div className="flex items-center gap-2"><Button variant="outline" className={`h-10 rounded-none px-3 font-mono text-[9px] font-bold tracking-[.08em] ${dark ? "border-[#3c5e58] bg-[#102225] text-[#e4f2ed] hover:bg-[#1b3535]" : "border-[#a7c0b9] bg-white text-[#17312e]"}`}><FileJson className="mr-1 h-3.5 w-3.5" />JSON</Button><Button variant="outline" className={`h-10 rounded-none px-3 font-mono text-[9px] font-bold tracking-[.08em] ${dark ? "border-[#3c5e58] bg-[#102225] text-[#e4f2ed] hover:bg-[#1b3535]" : "border-[#a7c0b9] bg-white text-[#17312e]"}`}><FileText className="mr-1 h-3.5 w-3.5" />REPORT</Button></div></div>
            <div className="mt-7 grid gap-3 border-b pb-8 sm:grid-cols-[135px_1fr] sm:items-start"><p className={`mt-2 font-mono text-[10px] font-bold uppercase tracking-[.12em] ${muted}`}>Signal register</p><div className="flex flex-wrap gap-2"><span className="border border-[#b94c3b] bg-[#f9e2de] px-3 py-2 font-mono text-[10px] font-bold uppercase tracking-[.09em] text-[#a5382c]">00 critical</span><span className="border border-[#b94c3b] bg-[#f9e2de] px-3 py-2 font-mono text-[10px] font-bold uppercase tracking-[.09em] text-[#a5382c]">01 high</span><span className="border border-[#b78327] bg-[#fff0d8] px-3 py-2 font-mono text-[10px] font-bold uppercase tracking-[.09em] text-[#8b5e16]">02 medium</span><span className="border border-[#3a8e81] bg-[#dff3ed] px-3 py-2 font-mono text-[10px] font-bold uppercase tracking-[.09em] text-[#256e64]">07 observed</span></div></div>
          </section>

          <section id="evidence" className={`px-6 pb-20 pt-6 sm:px-[8vw] sm:pb-[7vw] ${surface}`}><div className="flex items-end justify-between gap-5"><div><p className="font-mono text-[10px] font-bold uppercase tracking-[.14em] text-[#0b8f83]">Evidence sequence / four records</p><h2 className={`mt-4 font-['Space_Grotesk'] text-4xl font-bold leading-[.92] tracking-[-.075em] sm:text-6xl ${ink}`}>Signals, not scare tactics.</h2></div><p className={`hidden max-w-[175px] text-right text-xs leading-relaxed sm:block ${muted}`}>Severity, consequence, and one clear next move.</p></div>
            <div className={`mt-8 border-t-2 ${dark ? "border-[#c4e5df]" : "border-[#102724]"}`}>{evidence.map((entry) => { const Icon = entry.icon; return <article className={`group grid gap-4 border-b py-6 transition-all duration-200 hover:translate-x-1 lg:grid-cols-[82px_16px_minmax(0,1fr)_230px] ${line}`} key={entry.title}><p className={`font-mono text-[10px] font-bold tracking-[.1em] ${muted}`}>{entry.id}</p><span className="mt-1.5 h-2 w-2 rounded-sm" style={{ background: entry.color }} /><div><p className={`font-mono text-[10px] font-bold uppercase tracking-[.09em] ${muted}`}>{entry.severity} / direct observation</p><h3 className={`mt-2 flex items-center gap-2 text-[17px] font-bold tracking-[-.025em] ${ink}`}><Icon className="h-4 w-4" style={{ color: entry.color }} />{entry.title}</h3><p className={`mt-2 max-w-2xl text-sm leading-relaxed ${muted}`}>{entry.text}</p></div><div className={`border-l pl-4 text-sm leading-relaxed ${dark ? "border-[#34534f]" : "border-[#c4d5cf]"}`}><p className="font-bold text-[#0b8f83]">Next move <ChevronRight className="inline h-4 w-4" /></p><p className={`mt-2 ${muted}`}>{entry.fix}</p></div></article>; })}</div>
          </section>

          <section id="protocol" className={`grid gap-10 border-t px-6 py-20 sm:px-[8vw] sm:py-[8vw] lg:grid-cols-[.76fr_1fr] lg:gap-[9vw] ${dark ? "border-[#294641] bg-[#102427]" : "border-[#a8c2ba] bg-[#dcebe6]"}`}><div><p className="font-mono text-[10px] font-bold uppercase tracking-[.14em] text-[#0b8f83]">Protocol annex / deterministic</p><h2 className={`mt-4 font-['Space_Grotesk'] text-4xl font-bold leading-[.92] tracking-[-.075em] sm:text-5xl ${ink}`}>Fixed checks.<br />Local evidence.</h2><p className={`mt-6 max-w-sm border-l-2 border-[#0b8f83] pl-4 text-sm leading-relaxed ${muted}`}>The scanner stays intentionally narrow: a documented set of direct observations, never a cloud reputation score or a broad network sweep.</p><button className="mt-7 inline-flex items-center gap-2 font-mono text-[10px] font-bold uppercase tracking-[.1em] text-[#0b8f83]">Read the local workflow <ArrowUpRight className="h-4 w-4" /></button></div><div className={`border-y-2 ${dark ? "border-y-[#5c837c]" : "border-y-[#315a54]"}`}>{[["A-01", "Transport lens", "Certificate expiry, negotiated protocol, issuer, and key strength.", "diagram-transport"], ["A-02", "Response lens", "Security headers and final response behavior.", "diagram-http"], ["A-03", "Surface lens", "Fixed common-port list and bounded public exposure checks.", "diagram-surface"]].map(([id, title, text, diagram]) => <article className={`group grid grid-cols-[64px_1fr_88px] items-center gap-3 border-b py-5 last:border-b-0 sm:grid-cols-[82px_1fr_126px] ${line}`} key={title}><p className="font-mono text-[9px] font-bold tracking-[.1em] text-[#0b8f83]">{id}</p><div><p className={`font-mono text-[8px] uppercase tracking-[.12em] ${muted}`}>Observe / explain / repair</p><h3 className={`mt-1 font-bold tracking-[-.03em] ${ink}`}>{title}</h3><p className={`mt-1 text-sm ${muted}`}>{text}</p></div><div className={`mini-diagram ${diagram}`}><span /></div></article>)}</div></section>
          <footer className="flex flex-col justify-between gap-4 bg-[#071719] px-6 py-9 text-[#b9d1ca] sm:flex-row sm:px-[8vw]"><div className="flex items-center gap-3"><img src={asset.mark} alt="" className="h-9 w-9" /><p className="font-['Space_Grotesk'] text-sm font-semibold">SiteSentry <span className="font-mono text-[9px] uppercase tracking-[.14em] text-[#74cbbb]">Private local inspection</span></p></div><p className="max-w-sm text-xs leading-relaxed sm:text-right">The preview illustrates the local report interface. The installed Flask tool records only scans you authorize and run from your device.</p></footer>
        </main>
      </div>
    </div>
  );
}
