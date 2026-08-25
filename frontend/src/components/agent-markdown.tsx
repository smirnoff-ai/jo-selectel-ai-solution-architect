import Markdown from "react-markdown";

export function AgentMarkdown({ text }: { text: string }) {
  return (
    <div className="text-sm leading-relaxed [&_h2]:mt-1 [&_h2]:mb-2 [&_h2]:font-serif [&_h2]:text-base [&_h2]:font-semibold [&_h3]:mt-3 [&_h3]:mb-1.5 [&_h3]:text-[11px] [&_h3]:font-semibold [&_h3]:tracking-[0.12em] [&_h3]:text-muted-foreground [&_h3]:uppercase [&_p]:mb-2 [&_p:last-child]:mb-0 [&_ul]:mb-2 [&_ul]:list-disc [&_ul]:pl-5 [&_ol]:mb-2 [&_ol]:list-decimal [&_ol]:pl-5 [&_li]:mb-0.5 [&_strong]:font-semibold [&_code]:rounded [&_code]:bg-muted [&_code]:px-1">
      <Markdown>{text}</Markdown>
    </div>
  );
}
