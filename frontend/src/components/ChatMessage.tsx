// ChatMessage.tsx: one chat bubble
type Props = {
  role: "user" | "assistant";
  text: string;
};

export default function ChatMessage({ role, text }: Props) {
  const isUser = role === "user";

  return (
    <div className={`flex w-full ${isUser ? "justify-end" : "justify-start"}`}>
      <p
        className={`max-w-[85%] whitespace-pre-wrap break-words rounded-2xl px-4 py-3 text-sm leading-7 shadow-sm ${
          isUser
            ? "rounded-br-md bg-blue-600 text-white"
            : "rounded-bl-md border border-gray-200 bg-white text-gray-800"
        }`}
      >
        {text}
      </p>
    </div>
  );
}
