const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://pjuuem2fn8.execute-api.us-west-2.amazonaws.com/prod";

export const api = {
  async chat(message: string, sessionId?: string, profile?: any) {
    const res = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: sessionId, profile }),
    });
    if (!res.ok) throw new Error("Chat failed");
    return res.json();
  },

  async uploadFile(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    
    const res = await fetch(`${API_URL}/upload`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error("Upload failed");
    return res.json();
  },
};
