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
    const previous = document.title;
    document.title = 'About OpenPath RPI';
    heading.current?.focus();
    return () => {
      document.title = previous;
    };
  }, []);

  return (
    <div className="about-page">
      <main className="about-main">
        <a className="about-back" href="#/">← Back to the map</a>
        <h1 ref={heading} tabIndex={-1}>About OpenPath RPI</h1>

        <p>
          OpenPath RPI is a mobile-friendly web app for finding accessible routes across the RPI
          campus. Unlike regular navigation apps, it takes accessibility needs into account, such
          as stairs, entrances and steep paths. You choose a starting point, a destination and your
          accessibility preferences, and you get a route on an interactive map with written
          directions.
        </p>
        <p>
          The site is built to support keyboard navigation, screen readers, mobile devices and
          enlarged text. Our long-term goal is reliable accessible navigation across the whole
          campus.
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