import { useEffect, useRef } from 'react';

function ExternalLink({ href, children }) {
  return (
    <a href={href} target="_blank" rel="noopener noreferrer">
      {children}
      <span className="visually-hidden"> (opens in a new tab)</span>
    </a>
  );
}

export default function AboutPage() {
  const heading = useRef(null);

  useEffect(() => {
    heading.current?.focus();
  }, []);

  return (
    <div className="about-page">
      <main className="about-main">
        <a className="about-back" href="#/">← Back to the map</a>
        <h1 ref={heading} tabIndex={-1}>About OpenPath RPI</h1>

        <p>
          OpenPath RPI is a pilot campus navigation app. It can route only along connections
          recorded in the shared campus data. That graph is incomplete, and its paths and
          accessibility details have not been verified on site. Do not rely on it for travel.
          You can choose entrances and avoid recorded stairs when a route is available.
        </p>
        <p>
          The map has text route information and keyboard controls. Our long-term goal is reliable,
          verified accessible navigation across campus.
        </p>

        <h2>An RCOS project</h2>
        <p>
          OpenPath RPI is built by students as part of the{' '}
          <ExternalLink href="https://rcos.io">
            Rensselaer Center for Open Source (RCOS)
          </ExternalLink>
          . This semester we are building a working pilot in the area around 86&apos; Field.
        </p>

        <h2>Accessibility</h2>
        <p>
          We use Section 508 and the Web Content Accessibility Guidelines (WCAG) 2 as our guide. If
          something doesn&apos;t work for you, please{' '}
          <ExternalLink href="https://github.com/veronica-michelle/OpenPath-RPI/issues">
            report it on GitHub
          </ExternalLink>
          .
        </p>

        <h2>Open source</h2>
        <p>
          The code is open source under the MIT license, and contributions are welcome.{' '}
          <ExternalLink href="https://github.com/veronica-michelle/OpenPath-RPI">
            OpenPath RPI on GitHub
          </ExternalLink>
          .
        </p>
      </main>
    </div>
  );
}
