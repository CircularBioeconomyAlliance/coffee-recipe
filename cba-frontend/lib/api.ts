// API URL from environment variable with fallback for development
const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://pjuuem2fn8.execute-api.us-west-2.amazonaws.com/prod";

if (!process.env.NEXT_PUBLIC_API_URL && typeof window !== 'undefined') {
  console.warn("NEXT_PUBLIC_API_URL not set, using fallback. Set this in production.");
}

export interface Indicator {
  id: number;
  name: string;
  definition: string;
  component: string;
  class: string;
  cost: string;
  accuracy: string;
  ease: string;
  principle: string;
  criterion: string;
  priority: string;
  methods: Array<{
    id: number;
    name: string;
    cost: string;
    accuracy: string;
    ease: string;
  }>;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  has_recommendations?: boolean;
}

export interface UploadResponse {
  found: {
    location?: string;
    commodity?: string;
    budget?: string;
  };
  missing: string[];
  s3_uri?: string;
}

export interface RecommendationsResponse {
  indicators: Indicator[];
  session_id?: string;
  message?: string;
}

export const api = {
  async chat(message: string, sessionId?: string, profile?: any): Promise<ChatResponse> {
    const res = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: sessionId, profile }),
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({ error: "Chat failed" }));
      throw new Error(error.error || "Chat failed");
    }
    return res.json();
  },

  async uploadFile(file: File): Promise<UploadResponse> {
    // Convert file to base64 for Lambda compatibility
    const buffer = await file.arrayBuffer();
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    const base64 = btoa(binary);

    const res = await fetch(`${API_URL}/upload`, {
      method: "POST",
      headers: {
        "Content-Type": "application/octet-stream",
      },
      body: base64,
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({ error: "Upload failed" }));
      throw new Error(error.error || "Upload failed");
    }
    return res.json();
  },

  async getRecommendations(sessionId: string): Promise<RecommendationsResponse> {
    const res = await fetch(`${API_URL}/recommendations?session_id=${encodeURIComponent(sessionId)}`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({ error: "Failed to fetch recommendations" }));
      throw new Error(error.error || "Failed to fetch recommendations");
    }
    return res.json();
  },
};
