"use client";

import { useState, useRef, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Send, Loader2, ArrowLeft, FileText, MapPin, DollarSign, Target } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ProjectProfile {
  location?: string;
  commodity?: string;
  budget?: string;
  outcomes?: string;
  capacity?: string;
}

function ChatPageContent() {
  const searchParams = useSearchParams();
  
  // Pre-fill from URL params (from upload page)
  const initialProfile: ProjectProfile = {
    location: searchParams.get("location") || undefined,
    commodity: searchParams.get("commodity") || undefined,
    budget: searchParams.get("budget") || undefined,
  };

  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: initialProfile.location 
        ? `I see you uploaded a file! I found: Location: ${initialProfile.location}, Commodity: ${initialProfile.commodity}, Budget: ${initialProfile.budget}. Now, what are your main expected outcomes? What do you want to measure or improve?`
        : "Hello! I'll help you find the perfect indicators for your project. Let's start by understanding your project. Where is your project located?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [profile, setProfile] = useState<ProjectProfile>(initialProfile);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);

    try {
      const { api } = await import("@/lib/api");
      const response = await api.chat(userMessage, searchParams.get("session_id") || undefined, profile);
      
      // Update profile based on response
      updateProfile(userMessage);
      
      setMessages((prev) => [...prev, { role: "assistant", content: response.response }]);
    } catch (error) {
      console.error("Chat failed:", error);
      setMessages((prev) => [...prev, { role: "assistant", content: "Sorry, I encountered an error. Please try again." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const updateProfile = (userMessage: string) => {
    // Profile extraction is handled by the agent's backend tools
    // (set_project_location, set_project_commodity, etc.)
    // This function is kept for future manual profile updates if needed
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const profileComplete = Object.keys(profile).length;
  const profileTotal = 4;
  // Only complete if we have 4 required fields AND either have capacity or explicitly skipped it
  const isComplete = profileComplete >= profileTotal && (profile.capacity !== undefined);

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-cba-navy-light bg-cba-navy-dark/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="text-gray-400 hover:text-white transition">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="text-lg font-bold">Build Your Project</h1>
              <p className="text-xs text-gray-400">Chat with AI Assistant</p>
            </div>
          </div>
          <div className="text-sm text-gray-400">
            {profileComplete}/4 required fields
          </div>
        </div>
      </header>

      <div className="flex-1 flex">
        {/* Sidebar - Project Profile */}
        <aside className="w-80 border-r border-cba-navy-light bg-cba-navy-dark/30 p-6">
          <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5 text-cba-gold" />
            Project Profile
          </h2>
          
          <div className="space-y-4">
            <ProfileField
              icon={<MapPin className="w-4 h-4" />}
              label="Location"
              value={profile.location}
            />
            <ProfileField
              icon={<span className="text-lg">🌾</span>}
              label="Commodity"
              value={profile.commodity}
            />
            <ProfileField
              icon={<DollarSign className="w-4 h-4" />}
              label="Budget"
              value={profile.budget}
            />
            <ProfileField
              icon={<Target className="w-4 h-4" />}
              label="Outcomes"
              value={profile.outcomes}
            />
            <ProfileField
              icon={<span className="text-lg">⚙️</span>}
              label="Capacity (Optional)"
              value={profile.capacity}
            />
          </div>

          {/* Progress Bar */}
          <div className="mt-8">
            <div className="flex justify-between text-xs text-gray-400 mb-2">
              <span>Progress</span>
              <span>{Math.round((profileComplete / 4) * 100)}%</span>
            </div>
            <div className="h-2 bg-cba-navy-light rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-cba-gold to-cba-gold-light"
                initial={{ width: 0 }}
                animate={{ width: `${(profileComplete / 4) * 100}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>
        </aside>

        {/* Chat Area */}
        <main className="flex-1 flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            <AnimatePresence>
              {messages.map((message, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-2xl rounded-2xl px-6 py-4 ${
                      message.role === "user"
                        ? "bg-cba-gold text-cba-navy"
                        : "bg-cba-navy-light border border-cba-gold/20"
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex justify-start"
              >
                <div className="bg-cba-navy-light border border-cba-gold/20 rounded-2xl px-6 py-4">
                  <Loader2 className="w-5 h-5 text-cba-gold animate-spin" />
                </div>
              </motion.div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-cba-navy-light bg-cba-navy-dark/30 p-6">
            {isComplete ? (
              <div className="max-w-4xl mx-auto text-center">
                <div className="bg-gradient-to-r from-cba-gold/10 to-transparent border border-cba-gold/30 rounded-2xl p-6 mb-4">
                  <h3 className="text-lg font-bold mb-2">Profile Complete! 🎉</h3>
                  <p className="text-gray-300 mb-4">
                    All information gathered. Ready to find your indicators.
                  </p>
                  <Link
                    href="/results"
                    className="inline-flex items-center gap-2 bg-cba-gold hover:bg-cba-gold-light text-cba-navy font-semibold px-8 py-3 rounded-lg transition"
                  >
                    View Recommendations
                    <ArrowLeft className="w-4 h-4 rotate-180" />
                  </Link>
                </div>
              </div>
            ) : (
              <div className="max-w-4xl mx-auto flex gap-4">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your answer..."
                  className="flex-1 bg-cba-navy-light border border-cba-gold/20 rounded-xl px-6 py-4 focus:outline-none focus:border-cba-gold/40 transition"
                  disabled={isLoading}
                />
                <button
                  onClick={handleSend}
                  disabled={!input.trim() || isLoading}
                  className="bg-cba-gold hover:bg-cba-gold-light disabled:opacity-50 disabled:cursor-not-allowed text-cba-navy font-semibold px-8 py-4 rounded-xl transition flex items-center gap-2"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

function ProfileField({ icon, label, value }: { icon: React.ReactNode; label: string; value?: string }) {
  return (
    <div className="bg-cba-navy-light/50 rounded-lg p-4 border border-cba-gold/10">
      <div className="flex items-center gap-2 text-xs text-gray-400 mb-2">
        {icon}
        <span>{label}</span>
      </div>
      <div className="text-sm font-medium">
        {value ? (
          <span className="text-white">{value}</span>
        ) : (
          <span className="text-gray-500 italic">Pending...</span>
        )}
      </div>
    </div>
  );
}


export default function ChatPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-gradient-to-br from-[#031f35] to-[#042d4a] flex items-center justify-center text-white">Loading...</div>}>
      <ChatPageContent />
    </Suspense>
  );
}
