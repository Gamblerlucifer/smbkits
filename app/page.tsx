"use client";

export default function Home() {
  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=DM+Sans:wght@300;400&display=swap');

        html { font-size: 16px; }
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        :root {
          --gold: #A8864A;
          --gold-border: rgba(168,134,74,0.28);
          --gold-hover: rgba(168,134,74,0.24);
          --bg: #08090C;
          --bg2: #0C0E13;
          --bg3: #111318;
          --text: #E4DED4;
          --muted: #8B92A1;
          --dim: #5B6272;
          --border: rgba(255,255,255,0.05);
          --font-display: 'Cormorant Garamond', Georgia, serif;
          --font-body: 'DM Sans', sans-serif;
        }

        html { scroll-behavior: smooth; }
        body {
          background: var(--bg);
          color: var(--text);
          font-family: var(--font-body);
          font-weight: 400;
          line-height: 1.6;
          overflow-x: hidden;
          -webkit-font-smoothing: antialiased;
          text-rendering: optimizeLegibility;
        }

        /* NAV */
        nav {
          position: fixed; top: 0; left: 0; right: 0; z-index: 100;
          display: flex; align-items: center; justify-content: space-between;
          padding: 1.5rem 4rem;
          background: rgba(8,9,12,0.95);
          backdrop-filter: blur(24px);
          border-bottom: 1px solid var(--border);
        }
        .logo {
          font-family: var(--font-display);
          font-size: 1.25rem; font-weight: 300;
          letter-spacing: 0.12em; text-transform: uppercase;
          color: var(--text); text-decoration: none;
        }
        .nav-cta {
          font-size: 0.72rem; font-weight: 400;
          letter-spacing: 0.2em; text-transform: uppercase;
          color: var(--muted);
          border: 1px solid var(--border);
          padding: 0.65rem 1.75rem; text-decoration: none;
          transition: color 0.3s, border-color 0.3s;
        }
        .nav-cta:hover { color: var(--text); border-color: var(--gold-border); }

        /* HERO */
        .hero {
          min-height: 92vh;
          display: flex; flex-direction: column;
          align-items: center; justify-content: center;
          text-align: center;
          padding: 10rem 2rem 8rem;
          position: relative;
        }
        .hero::before {
          content: '';
          position: absolute; inset: 0;
          background: radial-gradient(ellipse 50% 55% at 50% 0%, rgba(168,134,74,0.045) 0%, transparent 65%);
          pointer-events: none;
        }
        .kicker {
          font-size: 0.72rem; font-weight: 400;
          letter-spacing: 0.35em; text-transform: uppercase;
          color: var(--muted); margin-bottom: 2.5rem;
        }
        .hero-philosophy {
          font-family: var(--font-display);
          font-size: clamp(0.95rem, 1.5vw, 1.1rem);
          font-weight: 300; font-style: italic;
          color: var(--muted); margin-bottom: 2rem;
          letter-spacing: 0.02em;
        }
        .hero h1 {
          font-family: var(--font-display);
          font-size: clamp(2.75rem, 6.5vw, 5.5rem);
          font-weight: 300; line-height: 1.02;
          max-width: 860px; margin-bottom: 1rem;
          letter-spacing: -0.03em;
        }
        .hero h1 em { font-style: italic; color: var(--gold); }
        .rule { width: 36px; height: 1px; background: var(--gold); opacity: 0.5; margin: 2.5rem auto; }
        .hero-sub {
          font-size: 1.15rem; font-weight: 300;
          color: #A7AFBD; max-width: 540px;
          margin: 0 auto 3.5rem; line-height: 1.9;
        }
        .hero-sub strong { color: var(--text); font-weight: 400; }
        .btn-primary {
          display: inline-block;
          font-size: 0.72rem; font-weight: 500;
          letter-spacing: 0.22em; text-transform: uppercase;
          color: var(--bg); background: var(--gold);
          padding: 1rem 3.2rem; text-decoration: none;
          min-height: 54px; line-height: 1;
          display: inline-flex; align-items: center;
          transition: opacity 0.25s, filter 0.25s;
        }
        .btn-primary:hover { opacity: 1; filter: brightness(1.08); }
        .btn-ghost {
          display: inline-block;
          font-size: 0.72rem; letter-spacing: 0.15em;
          text-transform: uppercase; color: #A7AFBD;
          padding: 1rem 2rem; text-decoration: none;
          transition: color 0.25s; margin-left: 1.25rem;
        }
        .btn-ghost:hover { color: #FFFFFF; }

        /* MARQUEE */
        .marquee-wrap {
          overflow: hidden;
          border-top: 1px solid var(--border);
          border-bottom: 1px solid var(--border);
          padding: 0.9rem 0; background: var(--bg2);
        }
        .marquee-inner {
          display: flex; gap: 5rem;
          animation: marquee 65s linear infinite;
          white-space: nowrap;
          opacity: 0.7;
        }
        .marquee-inner span {
          font-size: 0.72rem; letter-spacing: 0.18em;
          text-transform: uppercase; color: #CEC6BA; flex-shrink: 0;
        }
        .marquee-inner span em { font-style: normal; opacity: 0.7; }
        @keyframes marquee {
          from { transform: translateX(0); }
          to { transform: translateX(-50%); }
        }

        /* STATEMENT */
        .statement {
          padding: 7rem 2rem;
          text-align: center;
          border-bottom: 1px solid var(--border);
        }
        .statement-inner { max-width: 680px; margin: 0 auto; }
        .statement h2 {
          font-family: var(--font-display);
          font-size: clamp(1.75rem, 3.5vw, 2.75rem);
          font-weight: 300; line-height: 1.25;
          color: var(--text); margin-bottom: 1.5rem;
        }
        .statement h2 em { font-style: italic; color: var(--gold); }
        .statement p { font-size: 1.05rem; color: var(--muted); line-height: 1.9; }

        /* CORE */
        .core-section {
          padding: 8rem 4rem; max-width: 1200px; margin: 0 auto;
          display: grid; grid-template-columns: 1fr 1fr;
          gap: 6rem; align-items: start;
        }
        .section-tag {
          font-size: 0.72rem; letter-spacing: 0.18em;
          text-transform: uppercase; color: var(--muted); margin-bottom: 1.75rem;
        }
        .core-left h2 {
          font-family: var(--font-display);
          font-size: clamp(1.75rem, 3vw, 2.75rem);
          font-weight: 300; line-height: 1.25; margin-bottom: 1.75rem;
        }
        .core-left h2 em { font-style: italic; color: var(--gold); }
        .core-left p { font-size: 1.05rem; color: var(--muted); line-height: 1.9; margin-bottom: 2.5rem; }
        .core-right { padding-top: 0.5rem; }
        .core-right-label {
          font-size: 0.72rem; letter-spacing: 0.25em;
          text-transform: uppercase; color: var(--dim); margin-bottom: 1.75rem;
          padding-bottom: 1rem; border-bottom: 1px solid var(--border);
        }
        .t-row {
          padding: 1.5rem 0;
          border-bottom: 1px solid var(--border);
        }
        .t-row:last-child { border-bottom: none; }
        .t-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.4rem; }
        .t-name {
          font-size: 1rem; font-weight: 400;
          color: var(--text); letter-spacing: 0.02em;
        }
        .t-tag {
          font-size: 0.72rem; letter-spacing: 0.15em;
          text-transform: uppercase; padding: 0.2rem 0.65rem;
          border: 1px solid;
        }
        .tag-a { color: #4A7059; border-color: rgba(74,112,89,0.25); }
        .tag-r { color: var(--muted); border-color: var(--dim); }
        .tag-x { color: #6B4040; border-color: rgba(107,64,64,0.25); }
        .t-desc { font-size: 1rem; color: var(--muted); line-height: 1.8; }
        .t-sub { font-size: 0.9rem; color: var(--muted); margin-top: 0.25rem; }

        /* ECO */
        .eco-section {
          border-top: 1px solid var(--border);
          background: var(--bg2);
          padding: 7rem 4rem;
        }
        .eco-header { margin-bottom: 3rem; text-align: center; }
        .eco-header h2 {
          font-family: var(--font-display);
          font-size: clamp(1.5rem, 3vw, 2.5rem);
          font-weight: 300; margin-bottom: 0.75rem;
        }
        .eco-header p { font-size: 1.05rem; color: var(--muted); max-width: 560px; line-height: 1.9; margin: 0 auto; }
        .service-list {
          border: 1px solid var(--border);
        }
        .service-item {
          display: grid;
          grid-template-columns: 1fr auto;
          gap: 2.5rem;
          padding: 2rem 2.5rem;
          border-bottom: 1px solid var(--border);
          text-decoration: none; color: inherit;
          transition: background 0.2s ease;
          align-items: start;
        }
        .service-item:last-child { border-bottom: none; }
        .service-item:hover { background: rgba(255,255,255,0.025); }
        .service-item:hover .service-arrow { color: var(--gold); }
        .service-tag-inline {
          font-size: 0.6rem; letter-spacing: 0.22em;
          text-transform: uppercase; color: var(--gold);
          display: block; margin-bottom: 0.5rem;
        }
        .service-name {
          font-size: 1.05rem; font-weight: 400;
          color: var(--text); margin-bottom: 0.5rem;
          letter-spacing: 0.01em;
        }
        .service-core .service-name {
          font-family: var(--font-display);
          font-size: 1.25rem; font-weight: 300;
        }
        .service-desc {
          font-size: 1rem; color: #A7AFBD; line-height: 1.8;
        }
        .service-arrow {
          font-size: 0.7rem; color: var(--dim);
          transition: color 0.2s; padding-top: 0.3rem;
        }

        /* CONCIERGE / WAITLIST */
        .concierge-section {
          padding: 8rem 2rem;
          text-align: center;
          border-top: 1px solid var(--border);
        }
        .concierge-inner { max-width: 500px; margin: 0 auto; }
        .concierge-inner h2 {
          font-family: var(--font-display);
          font-size: clamp(1.75rem, 3.5vw, 2.75rem);
          font-weight: 300; line-height: 1.2; margin-bottom: 1rem;
        }
        .concierge-inner h2 em { font-style: italic; color: var(--gold); }
        .concierge-inner p {
          font-size: 1.05rem; color: var(--muted);
          margin-bottom: 2rem; line-height: 1.9;
        }
        .quote-block {
          border-left: 1px solid var(--gold-border);
          padding: 1.25rem 1.5rem;
          margin-bottom: 2.5rem;
          text-align: left;
          background: rgba(255,255,255,0.01);
        }
        .quote-text {
          font-family: var(--font-display);
          font-size: 1.05rem; font-style: italic; font-weight: 300;
          color: var(--muted); line-height: 1.8; margin-bottom: 0.6rem;
        }
        .quote-attr { font-size: 0.78rem; color: var(--muted); letter-spacing: 0.08em; }
        .email-form { display: flex; border: 1px solid var(--border); }
        .invite-form {
          display: flex; flex-direction: column; gap: 0;
          border: 1px solid var(--border);
          background: rgba(255,255,255,0.01);
        }
        .invite-input {
          background: transparent; border: none; border-bottom: 1px solid var(--border);
          outline: none; padding: 1rem 1.25rem; color: var(--text);
          font-family: var(--font-body); font-size: 1rem; width: 100%; min-height: 58px;
          transition: border-color 0.2s, background 0.2s;
        }
        .invite-input:focus { border-color: var(--gold); background: rgba(255,255,255,0.015); }
        .invite-input:last-of-type { border-bottom: none; }
        .invite-input::placeholder { color: #788191; }
        .invite-submit { width: 100%; border-top: 1px solid var(--border); }
        .email-submit {
          background: var(--gold); border: none; color: var(--bg);
          font-family: var(--font-body); font-size: 0.72rem; font-weight: 500;
          letter-spacing: 0.2em; text-transform: uppercase;
          padding: 1rem 1.75rem; cursor: pointer; min-height: 54px;
          transition: opacity 0.25s, filter 0.25s; white-space: nowrap;
        }
        .email-submit:hover { opacity: 1; filter: brightness(1.08); }
        .scarcity-note {
          font-size: 0.8rem; color: var(--muted);
          margin-top: 1.1rem; line-height: 1.65; letter-spacing: 0.03em;
        }
        .access-note {
          font-size: 0.65rem; color: var(--dim);
          margin-top: 0.5rem; letter-spacing: 0.06em;
        }

        /* FOOTER */
        footer {
          padding: 2.5rem 4rem;
          border-top: 1px solid var(--border);
          display: flex; align-items: center; justify-content: space-between;
        }
        .footer-brand {
          font-family: var(--font-display);
          font-size: 0.85rem; font-weight: 300;
          letter-spacing: 0.18em; text-transform: uppercase; color: var(--muted);
        }
        .footer-copy { font-size: 0.78rem; color: var(--muted); letter-spacing: 0.05em; }

        .statement p,
        .core-left p,
        .concierge-inner p,
        .eco-header p,
        .service-desc,
        .t-desc { color: #A7AFBD; }

        .t-sub,
        .quote-attr,
        .footer-copy,
        .scarcity-note { color: #929CAD; }

        .kicker,
        .section-tag,
        .core-right-label,
        .eco-feat-tag { letter-spacing: 0.22em; }

        @media (max-width: 900px) {
          nav { padding: 1.25rem 1.5rem; }
          .core-section { grid-template-columns: 1fr; gap: 3rem; padding: 5rem 1.5rem; }
          .eco-section { padding: 5rem 1.5rem; }
          .service-item { gap: 1.5rem; padding: 1.5rem; }
          footer { flex-direction: column; gap: 0.75rem; text-align: center; padding: 1.5rem; }
          .email-form { flex-direction: column; }
          .invite-form { width: 100%; }
          .email-submit { width: 100%; }
        }

        /* FINAL PRODUCTION POLISH */

        .btn-primary:focus,
        .btn-ghost:focus,
        .nav-cta:focus,
        .email-submit:focus,
        .invite-input:focus {
          outline: 1px solid rgba(168,134,74,0.65);
          outline-offset: 2px;
        }

        .service-item:hover { background: rgba(255,255,255,0.03); }
        .service-item:hover .service-name { color: #F1EBDF; }

        .hero-sub,
        .statement p,
        .core-left p,
        .concierge-inner p,
        .service-desc,
        .t-desc { font-weight: 400; }

        .service-desc { max-width: 720px; }

        @media (max-width: 768px) {
          .hero { padding-top: 8rem; padding-bottom: 6rem; }
          .hero h1 { font-size: clamp(2.5rem, 12vw, 4rem); line-height: 1.06; }
          .hero-sub br { display: none; }
          .hero-sub { max-width: 92%; font-size: 0.98rem; line-height: 1.85; }
          .service-item { grid-template-columns: 1fr; gap: 0.75rem; }
          .service-arrow { display: none; }
          .btn-primary, .btn-ghost, .email-submit { width: 100%; justify-content: center; }
          .btn-ghost { margin-left: 0; margin-top: 1rem; display: block; }
          .marquee-inner { animation-duration: 90s; }
        }

        .hero-sub { font-weight: 400; }

        .btn-primary:hover,
        .email-submit:hover { filter: brightness(1.05); }

        @media (max-width: 768px) {
          nav { padding: 1rem 1.25rem; }
          .nav-cta { padding: 0.6rem 1rem; letter-spacing: 0.14em; }
        }
      `}</style>

      {/* NAV */}
      <nav>
        <a href="/" className="logo">SMBkits</a>
        <a href="#access" className="nav-cta">Request Private Access</a>
      </nav>

      {/* HERO */}
      <section className="hero">
        <div className="kicker">Brand Intelligence · Reputation Protection</div>
        <p className="hero-philosophy">A single customer experience can define an entire brand.</p>
        <h1>
          Reputation,<br />
          once damaged,<br />
          <em>rarely recovers.</em>
        </h1>
        <div className="rule" />
        <p className="hero-sub">
          Built for independent premium businesses<br />
          where <strong>reputation defines demand.</strong>
        </p>
        <div>
          <a href="#access" className="btn-primary">Request Private Access</a>
          <a href="#platform" className="btn-ghost">View Brand System →</a>
        </div>
      </section>

      {/* MARQUEE */}
      <div className="marquee-wrap">
        <div className="marquee-inner">
          {Array(2).fill(null).map((_, i) => (
            <div key={i} style={{ display: "flex", gap: "5rem", flexShrink: 0 }}>
              <span>Michelin Guide <em>★★★</em></span>
              <span>World&apos;s 50 Best</span>
              <span>World&apos;s 50 Best Bars</span>
              <span>Forbes 5-Star Spa</span>
              <span>SCA Certified</span>
              <span>Decanter <em>95+</em></span>
              <span>Tabelog</span>
            </div>
          ))}
        </div>
      </div>

      {/* STATEMENT */}
      <section className="statement">
        <div className="statement-inner">
          <h2>
            Your reputation is not<br />
            a marketing asset.<br />
            <em>It is the business itself.</em>
          </h2>
          <div className="rule" />
          <p>
            One unresolved interaction<br />
            can erode years of trust.
          </p>
        </div>
      </section>

      {/* CORE */}
      <section className="core-section">
        <div className="core-left">
          <div className="section-tag">Private Infrastructure · Core Layer</div>
          <h2>
            Brand-safe<br />
            reputation<br />
            <em>orchestration.</em>
          </h2>
          <p>
            Every customer experience is monitored with context, urgency, and brand sensitivity.
            Exceptional experiences are acknowledged immediately.
            Critical feedback is held for personal review — nothing is published without your approval.
          </p>
          <a href="#access" className="btn-primary" style={{ display: "inline-block" }}>Request Private Access</a>
        </div>
        <div className="core-right">
          <div className="core-right-label">Reputation Response Flow</div>
          <div className="t-row">
            <div className="t-header">
              <span className="t-name">Exceptional Experience</span>
              <span className="t-tag tag-a">Acknowledged</span>
            </div>
            <div className="t-desc">Response crafted to brand standard and published without friction.</div>
            <div className="t-sub">Maintains brand consistency at scale.</div>
          </div>
          <div className="t-row">
            <div className="t-header">
              <span className="t-name">Requires Attention</span>
              <span className="t-tag tag-r">Personal Review</span>
            </div>
            <div className="t-desc">Draft prepared and held for executive approval before any action.</div>
            <div className="t-sub">Reviewed, refined, and approved before publication.</div>
          </div>
          <div className="t-row">
            <div className="t-header">
              <span className="t-name">Critical Recovery</span>
              <span className="t-tag tag-x">Immediate Attention</span>
            </div>
            <div className="t-desc">Immediate notification to leadership. Personal response required. Nothing is published.</div>
            <div className="t-sub">Brand protection at the highest sensitivity</div>
          </div>
        </div>
      </section>

      {/* PLATFORM */}
      <section className="eco-section" id="platform">
        <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
        <div className="eco-header">
          <div className="section-tag">Brand Infrastructure</div>
          <h2>A private brand infrastructure for independent premium businesses.</h2>
          <p>Every layer operates with shared brand standards.</p>
        </div>
        <div className="service-list">
          <a href="/reputation-response" className="service-item service-core">
            <div>
              <span className="service-tag-inline">Core · Primary</span>
              <div className="service-name">Reputation Response</div>
              <div className="service-desc">
                Brand-safe reputation management. Positive customer interactions prepared in your brand tone for review.
                Critical feedback reserved for personal response.
                Brand-safe response orchestration — nothing is published outside your brand standards.
              </div>
            </div>
            <span className="service-arrow">→</span>
          </a>
          {[
            { name: "Social Presence", href: "/social-presence", desc: "Maintain a consistent tone across every customer touchpoint — dining, bar, studio, or spa." },
            { name: "Local Positioning", href: "/local-positioning", desc: "Understand what customers say about your closest competitors." },
            { name: "Reputation Recovery", href: "/reputation-recovery", desc: "Encourage satisfied customers to share their experience naturally." },
            { name: "Brand Voice Library", href: "/brand-voice", desc: "Descriptions that reflect your culinary or service vision — from wine list to treatment menu." },
            { name: "Visibility Intelligence", href: "/visibility-intelligence", desc: "Understand why customers choose competing premium businesses nearby." },
            { name: "Brand Responses", href: "/brand-responses", desc: "The right words for every customer interaction, every time." },
          ].map((item) => (
            <a key={item.name} href={item.href} className="service-item">
              <div>
                <div className="service-name">{item.name}</div>
                <div className="service-desc">{item.desc}</div>
              </div>
              <span className="service-arrow">→</span>
            </a>
          ))}
        </div>
        </div>
      </section>

      {/* CONCIERGE ACCESS */}
      <section className="concierge-section" id="access">
        <div className="concierge-inner">
          <div className="section-tag">Private Access</div>
          <h2>
            Private systems<br />
            for brands that cannot afford<br />
            <em>public mistakes.</em>
          </h2>
          <div className="rule" />
          <p>
            SMBkits operates by private referral.
          </p>

          <div className="quote-block">
            <p className="quote-text">
              &ldquo;Finally, a system that protects brand tone without sounding automated.&rdquo;
            </p>
            <p className="quote-attr">— Independent restaurant owner</p>
          </div>

          <div className="invite-form">
            <input type="text" className="invite-input" placeholder="Business Name" />
            <input type="text" className="invite-input" placeholder="Your Role" />
            <input type="email" className="invite-input" placeholder="Business Email" />
            <button type="button" className="email-submit invite-submit">Request Private Access</button>
          </div>

          <p className="scarcity-note">
            Access remains intentionally limited<br />
            to maintain brand alignment.
          </p>
        </div>
      </section>

      {/* FOOTER */}
      <footer>
        <div className="footer-brand">SMBkits Reputation Infrastructure</div>
        <div className="footer-copy">© 2026 SMBkits · Private reputation infrastructure for independent brands.</div>
      </footer>
    </>
  );
}
