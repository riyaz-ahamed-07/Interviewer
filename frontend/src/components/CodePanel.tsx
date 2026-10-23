import { Highlight, themes } from "prism-react-renderer";

type Props = {
  code: string;
};

export function CodePanel({ code }: Props) {
  return (
    <Highlight theme={themes.nightOwl} code={code} language="python">
      {({ className, style, tokens, getLineProps, getTokenProps }) => (
        <pre className={`code code-hl ${className}`} style={style}>
          {tokens.map((line, i) => (
            <div key={i} {...getLineProps({ line, className: "code-line" })}>
              <span className="code-ln" aria-hidden="true">
                {i + 1}
              </span>
              <span className="code-content">
                {line.map((token, key) => (
                  <span key={key} {...getTokenProps({ token })} />
                ))}
              </span>
            </div>
          ))}
        </pre>
      )}
    </Highlight>
  );
}
