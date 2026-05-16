import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Brand Responses — SMBkits",
  description: "Every public reply becomes part of the brand. Customer communication that feels intentional, measured, and privately managed.",
};

export default function BrandResponsesPage() {
  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=DM+Sans:wght@300;400&display=swap');
        html { font-size: 16px; }
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        :root {
          --gold: #A8864A; --gold-border: rgba(168,134,74,0.28);
          --bg: #08090C; --bg2: #0C0E13;
          --text: #E4DED4; --muted: #8B92A1; --dim: #5B6272;
          --border: rgba(255,255,255,0.05);
          --font-display: 'Cormorant Garamond', Georgia, serif;
          --font-body: 'DM Sans', sans-serif;
        }
        html { scroll-behavior: smooth; }
        body { background: var(--bg); color: var(--text); font-family: var(--font-body); font-weight: 400; line-height: 1.6; -webkit-font-smoothing: antialiased; overflow-x: hidden; }
        nav { position: fixed; top: 0; left: 0; right: 0; z-index: 100; display: flex; align-items: center; justify-content: space-between; padding: 1.5rem 4rem; background: rgba(8,9,12,0.95); backdrop-filter: blur(24px); border-bottom: 1px solid var(--border); }
        .logo { font-family: var(--font-display); font-size: 1.25rem; font-weight: 300; letter-spacing: 0.12em; text-transform: uppercase; color: var(--text); text-decoration: none; }
        .nav-cta { font-size: 0.72rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--muted); border: 1px solid var(--border); padding: 0.65rem 1.75rem; text-decoration: none; transition: color 0.3s, border-color 0.3s; min-height: 44px; display: flex; align-items: center; }
        .nav-cta:hover { color: var(--text); border-color: var(--gold-border); }
        .nav-cta:focus { outline: 1px solid rgba(168,134,74,0.65); outline-offset: 2px; }

        .tool-hero { padding: 12rem 2rem 7rem; text-align: center; border-bottom: 1px solid var(--border); }
        .tool-hero-inner { max-width: 760px; margin: 0 auto; }
        .tool-kicker { font-size: 0.72rem; letter-spacing: 0.35em; text-transform: uppercase; color: var(--muted); margin-bottom: 2.5rem; }
        .tool-hero h1 { font-family: var(--font-display); font-size: clamp(2.5rem, 5.5vw, 4.5rem); font-weight: 300; line-height: 1.05; letter-spacing: -0.02em; margin-bottom: 2rem; }
        .tool-tagline { font-family: var(--font-display); font-size: clamp(1rem, 1.8vw, 1.25rem); font-style: italic; font-weight: 300; color: var(--muted); margin-bottom: 2rem; line-height: 1.5; }
        .tool-desc { font-size: 1.05rem; color: #A7AFBD; line-height: 1.9; max-width: 600px; margin: 0 auto; }
        .rule { width: 36px; height: 1px; background: var(--gold); opacity: 0.5; margin: 2.5rem auto; }

        .content-wrap { max-width: 680px; margin: 0 auto; padding: 0 2rem; }
        .tool-section { padding: 5rem 2rem; border-bottom: 1px solid var(--border); }
        .tool-section:nth-child(even) { background: var(--bg2); }
        .section-lead { font-family: var(--font-display); font-size: clamp(1.5rem, 2.5vw, 2rem); font-weight: 300; line-height: 1.3; margin-bottom: 2rem; }
        .section-lead em { font-style: italic; color: var(--gold); }
        .tool-section p { font-size: 1.05rem; color: #A7AFBD; line-height: 1.9; margin-bottom: 1.25rem; }
        .tool-section p:last-child { margin-bottom: 0; }
        .qual-list { list-style: none; margin-top: 1.5rem; display: flex; flex-direction: column; gap: 0.75rem; }
        .qual-list li { font-size: 1rem; color: #A7AFBD; padding-left: 1.25rem; position: relative; line-height: 1.7; }
        .qual-list li::before { content: '—'; position: absolute; left: 0; color: var(--gold); opacity: 0.6; }

        .outcome-section { padding: 6rem 2rem; text-align: center; border-bottom: 1px solid var(--border); }
        .outcome-inner { max-width: 560px; margin: 0 auto; }
        .outcome-tag { font-size: 0.72rem; letter-spacing: 0.25em; text-transform: uppercase; color: var(--dim); margin-bottom: 2rem; }
        .outcome-section h2 { font-family: var(--font-display); font-size: clamp(1.5rem, 2.5vw, 2rem); font-weight: 300; line-height: 1.4; margin-bottom: 1.5rem; }
        .outcome-section p { font-size: 1.05rem; color: #A7AFBD; line-height: 1.9; margin-bottom: 0.75rem; }

        .cta-section { padding: 7rem 2rem; text-align: center; }
        .cta-inner { max-width: 480px; margin: 0 auto; }
        .cta-section p { font-size: 1.05rem; color: #A7AFBD; line-height: 1.9; margin-bottom: 2.5rem; }
        .btn-primary { display: inline-flex; align-items: center; font-size: 0.72rem; font-weight: 500; letter-spacing: 0.22em; text-transform: uppercase; color: var(--bg); background: var(--gold); padding: 1rem 3.2rem; text-decoration: none; min-height: 54px; transition: filter 0.25s; }
        .btn-primary:hover { filter: brightness(1.08); }
        .btn-primary:focus { outline: 1px solid rgba(168,134,74,0.65); outline-offset: 2px; }
        .cta-note { font-size: 0.78rem; color: var(--dim); margin-top: 1.25rem; letter-spacing: 0.04em; }

        footer { padding: 2.5rem 4rem; border-top: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
        .footer-brand { font-family: var(--font-display); font-size: 0.85rem; font-weight: 300; letter-spacing: 0.18em; text-transform: uppercase; color: var(--muted); }
        .footer-copy { font-size: 0.78rem; color: var(--muted); }

        @media (max-width: 768px) {
          nav { padding: 1rem 1.25rem; }
          .nav-cta { padding: 0.6rem 1rem; letter-spacing: 0.14em; }
          .tool-hero { padding: 9rem 1.5rem 5rem; }
          .tool-section, .outcome-section, .cta-section { padding: 4rem 1.5rem; }
          footer { flex-direction: column; gap: 0.75rem; text-align: center; padding: 1.5rem; }
        }
      `}</style>

      <nav>
        <a href="/" className="logo">SMBkits</a>
        <a href="/#access" className="nav-cta">Request Private Access</a>
      </nav>

      <main>
        <section className="tool-hero">
          <div className="tool-hero-inner">
            <div className="tool-kicker">Brand Infrastructure</div>
            <h1>Brand<br />Responses</h1>
            <div className="rule" />
            <p className="tool-tagline">
              Every public reply<br />
              becomes part of the brand.
            </p>
            <p className="tool-desc">
              Especially for businesses where perception defines demand.
            </p>
          </div>
        </section>

        <section className="tool-section">
          <div className="content-wrap">
            <h2 className="section-lead">
              Most responses fail<br />
              for one reason.<br />
              <em>They sound operational instead of human.</em>
            </h2>
            <p>Or worse — they sound automated.</p>
            <p>
              SMBkits prepares responses designed around brand sensitivity,
              emotional context, and reputational exposure.
            </p>
          </div>
        </section>

        <section className="tool-section">
          <div className="content-wrap">
            <h2 className="section-lead">
              Different situations require<br />
              different restraint levels.<br />
              <em>Not templates. Judgment.</em>
            </h2>
            <p>A positive review requires acknowledgment.</p>
            <p>A frustrated customer requires composure.</p>
            <p>A critical incident requires executive judgment.</p>
          </div>
        </section>

        <section className="tool-section">
          <div className="content-wrap">
            <h2 className="section-lead">Responses are structured to preserve:</h2>
            <ul className="qual-list">
              <li>dignity</li>
              <li>calmness</li>
              <li>professionalism</li>
              <li>emotional control</li>
              <li>brand alignment</li>
            </ul>
          </div>
        </section>

        <section className="outcome-section">
          <div className="outcome-inner">
            <div className="outcome-tag">Outcome</div>
            <h2>Customer communication that feels intentional, measured, and privately managed.</h2>
            <p>Never reactive.</p>
            <p>Never generic.</p>
          </div>
        </section>

        <section className="cta-section">
          <div className="cta-inner">
            <p>SMBkits operates by private referral.<br />Access is reviewed for brand alignment.</p>
            <a href="/#access" className="btn-primary">Request Private Access</a>
            <p className="cta-note">Independent premium businesses only.</p>
          </div>
        </section>
      </main>

      <footer>
        <div className="footer-brand">SMBkits Reputation Infrastructure</div>
        <div className="footer-copy">© 2026 SMBkits · Private reputation infrastructure for independent brands.</div>
      </footer>
    </>
  );
}
