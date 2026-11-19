const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

   export async function login(email: string, password: string): Promise<string> 
   {
     const res = await fetch(`${API_URL}/login`, {
       method: "POST",
       headers: { "Content-Type": "application/json" },
       body: JSON.stringify({ email, password }),
     });
     if (!res.ok) 
     {
       throw new Error(res.status === 401 ? "Invalid email or password" : `Server returned ${res.status}`);
     }
     return (await res.json()).access_token;
   }

   export async function askQuestion(question: string, token: string): Promise<{ answer: string; sources: string[] }>
   {
     const res = await fetch(`${API_URL}/ask`, {
       method: "POST",
       headers: {
         "Content-Type": "application/json",
         Authorization: `Bearer ${token}`,       // proof of identity
       },
       body: JSON.stringify({ question }),
     });
     if (res.status === 401) throw new Error("SESSION_EXPIRED");
     if (!res.ok) throw new Error(`Server returned ${res.status}`);
     return await res.json();
   }

   export async function askStream(
    question: string, token: string, onToken: (t: string) => void
  ): Promise<{ sources: string[]; questionId: number | null }> {
    const res = await fetch(`${API_URL}/ask/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ question }),
    });
    if (res.status === 401) throw new Error("SESSION_EXPIRED");
if (res.status === 429) throw new Error("Too many questions, please wait a minute and try again.");
    if (!res.ok || !res.body) throw new Error(`Server returned ${res.status}`);
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    while (true) 
    {
      const { done, value } = await reader.read();
      if (done) break;
      onToken(decoder.decode(value, { stream: true }));
    }
    const src = res.headers.get("X-Sources") ?? "";
    const qid = res.headers.get("X-Question-Id");
    return { sources: src ? src.split(",") : [], questionId: qid ? Number(qid) : null };
  }

  export async function sendFeedback(id: number, value: number, token: string): Promise<void> {
  const res = await fetch(`${API_URL}/questions/${id}/feedback`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify({ value }),
  });
  if (res.status === 401) throw new Error("SESSION_EXPIRED");
  if (!res.ok) throw new Error(`Server returned ${res.status}`);
}