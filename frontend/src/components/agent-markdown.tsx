import Markdown from "react-markdown";

export function AgentMarkdown({ text }: { text: string }) {
  return (
    <div className="text-sm leading-relaxed [&_p]:mb-2 [&_p:last-child]:mb-0 [&_ul]:mb-2 [&_ul]:list-disc [&_ul]:pl-5 [&_code]:rounded [&_code]:bg-muted [&_code]:px-1">
      <Markdown>{text}</Markdown>
    </div>
  );
}
