"use client";
import { useState, useEffect } from "react";
import { askStream, sendFeedback } from "@/lib/api";
import { useRouter } from "next/navigation";
import ChatMessage from "@/components/ChatMessage";

type Msg = {
  role: "user" | "assistant";
  text: string;
  sources?: string[];
  questionId?: number | null;
  feedback?: number;
};

export default function Home() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [token, setToken] = useState("");

  const router = useRouter();

  // Keep the existing login protection.
  useEffect(() => {
    const t = localStorage.getItem("token");

    if (!t) {
      router.replace("/login");
    } else {
      setToken(t);
    }
  }, [router]);

  async function handleFeedback(i: number, value: number) {
    const id = messages[i].questionId;
    if (!id) return;

    try {
      await sendFeedback(id, value, token);

      setMessages((m) =>
        m.map((x, j) =>
          j === i ? { ...x, feedback: value } : x
        )
      );
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function handleSend() {
    const q = input.trim();

    if (!q || loading || !token) return;

    // Add the user's message.
    setMessages((m) => [
      ...m,
      { role: "user", text: q },
    ]);

    setInput("");
    setError("");
    setLoading(true);

    setMessages((m) => [
      ...m,
      { role: "assistant", text: "" },
    ]);

    try {
      const result = await askStream(q, token, (t) => {
        setMessages((m) => {
          const copy = [...m];
          const last = copy[copy.length - 1];

          if (last?.role !== "assistant") return m;

          copy[copy.length - 1] = {
            ...last,
            text: last.text + t,
          };

          return copy;
        });
      });

      setMessages((m) => {
        const copy = [...m];
        const lastIndex = copy.length - 1;

        if (copy[lastIndex]?.role !== "assistant") {
          return m;
        }

        copy[lastIndex] = {
          ...copy[lastIndex],
          sources: result.sources,
          questionId: result.questionId,
        };

        return copy;
      });
    } catch (e) {
      const msg = (e as Error).message;

      if (msg === "SESSION_EXPIRED") {
        localStorage.removeItem("token");
        router.replace("/login");
        return;
      }

      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    localStorage.removeItem("token");
    router.replace("/login");
  }

  return (
    <main className="flex min-h-dvh flex-col bg-slate-50 text-slate-900">

      {/* Top navigation */}
      <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/95 backdrop-blur">
        <div className="mx-auto flex w-full max-w-5xl items-center justify-between px-4 py-4 sm:px-6">

          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 text-lg font-bold text-white shadow-sm">
              M
            </div>

            <div>
              <h1 className="text-base font-semibold tracking-tight">
                ModelBench
              </h1>
              <p className="text-xs text-slate-500">
                Knowledge Assistant
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={handleLogout}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-50 hover:text-slate-900"
          >
            Log out
          </button>

        </div>
      </header>

      {/* Main chat area */}
      <section className="mx-auto flex w-full max-w-4xl flex-1 flex-col px-3 py-5 sm:px-6 sm:py-8">

        <div className="flex flex-1 flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">

          {/* Chat heading */}
          <div className="border-b border-slate-100 px-5 py-4 sm:px-6">
            <h2 className="text-sm font-semibold text-slate-800">
              Conversation
            </h2>
            <p className="mt-1 text-xs text-slate-500">
              Ask questions and explore your knowledge base.
            </p>
          </div>

          {/* Messages */}
          <div
            className="flex-1 space-y-6 overflow-y-auto px-4 py-6 sm:px-6"
            aria-live="polite"
          >
            {messages.length === 0 && (
              <div className="flex min-h-64 flex-1 flex-col items-center justify-center px-4 py-12 text-center">

                <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-50 text-2xl text-blue-600">
                  ✦
                </div>

                <h3 className="text-lg font-semibold tracking-tight">
                  How can I help you?
                </h3>

                <p className="mt-2 max-w-sm text-sm leading-6 text-slate-500">
                  Ask a question to get started. Your assistant will
                  respond using your available knowledge sources.
                </p>
              </div>
            )}

            {messages.map((m, i) => (
              <div key={i} className="min-w-0">

                <ChatMessage role={m.role} text={m.text} />

                {/* Feedback */}
                {m.role === "assistant" && m.questionId && (
                  <div className="mt-3 flex items-center gap-2 pl-1">
                    <span className="mr-1 text-xs text-slate-400">
                      Helpful?
                    </span>

                    <button
                      type="button"
                      aria-label="Helpful response"
                      aria-pressed={m.feedback === 1}
                      onClick={() => handleFeedback(i, 1)}
                      className={`rounded-lg border px-3 py-1.5 text-sm transition ${
                        m.feedback === 1
                          ? "border-blue-200 bg-blue-50"
                          : "border-slate-200 hover:bg-slate-50"
                      }`}
                    >
                      👍
                    </button>

                    <button
                      type="button"
                      aria-label="Not helpful response"
                      aria-pressed={m.feedback === -1}
                      onClick={() => handleFeedback(i, -1)}
                      className={`rounded-lg border px-3 py-1.5 text-sm transition ${
                        m.feedback === -1
                          ? "border-blue-200 bg-blue-50"
                          : "border-slate-200 hover:bg-slate-50"
                      }`}
                    >
                      👎
                    </button>
                  </div>
                )}

                {/* Sources */}
                {m.sources && m.sources.length > 0 && (
                  <div className="mt-3 rounded-xl bg-slate-50 px-3 py-3">
                    <p className="mb-2 text-xs font-semibold text-slate-500">
                      SOURCES
                    </p>

                    <div className="flex flex-wrap gap-2">
                      {m.sources.map((source, j) => (
                        <span
                          key={`${source}-${j}`}
                          className="break-all rounded-md border border-slate-200 bg-white px-2.5 py-1 text-xs text-slate-600"
                        >
                          {source}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}

            {/* Loading */}
            {loading && (
              <div
                className="flex items-center gap-2 text-sm text-slate-500"
                role="status"
              >
                <span className="h-2 w-2 animate-pulse rounded-full bg-blue-500" />
                Thinking...
              </div>
            )}

            {/* Error */}
            {error && (
              <div
                role="alert"
                className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
              >
                Error: {error}
              </div>
            )}
          </div>

          {/* Input area */}
          <div className="border-t border-slate-100 bg-white p-4 sm:p-5">
            <form
              className="flex items-end gap-2 rounded-2xl border border-slate-200 bg-slate-50 p-2 transition focus-within:border-blue-300 focus-within:ring-4 focus-within:ring-blue-50"
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
            >
              <input
                className="min-w-0 flex-1 bg-transparent px-3 py-2.5 text-sm text-slate-800 outline-none placeholder:text-slate-400"
                placeholder="Ask a question..."
                aria-label="Ask a question"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={loading || !token}
              />

              <button
                type="submit"
                disabled={loading || !input.trim() || !token}
                className="shrink-0 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Send
              </button>
            </form>

            <p className="mt-3 text-center text-xs text-slate-400">
              Knowledge Assistant · Verify important information.
            </p>
          </div>

        </div>
      </section>
    </main>
  );
}
