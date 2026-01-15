"use client";

import { useState } from "react";
import { Upload, MessageSquare, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";

export default function Home() {
  const [selectedFlow, setSelectedFlow] = useState<"upload" | "chat" | null>(null);

  return (
    <main className="min-h-screen">
      {/* Header */}
      <header className="border-b border-cba-navy-light bg-cba-navy-dark/50 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cba-gold to-cba-gold-dark flex items-center justify-center">
              <span className="text-cba-navy font-bold text-xl">🌍</span>
            </div>
            <div>
              <h1 className="text-xl font-bold">CBA Indicator Selection</h1>
              <p className="text-xs text-gray-400">Circular Bioeconomy Alliance</p>
            </div>
          </div>
          <div className="flex gap-4 text-sm text-gray-400">
            <span>Circular Bioeconomy Alliance</span>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-6 py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center max-w-4xl mx-auto mb-16"
        >
          <h2 className="text-5xl font-bold mb-6">
            Find the Perfect{" "}
            <span className="text-gradient">Indicators</span>
            <br />
            for Your Project
          </h2>
          <p className="text-xl text-gray-300">
            AI-powered recommendations for monitoring & evaluation indicators
            tailored to your sustainable agriculture project
          </p>
        </motion.div>

        {/* Entry Point Cards */}
        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {/* Upload File Card */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="group relative"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-cba-gold/20 to-transparent rounded-2xl blur-xl group-hover:blur-2xl transition-all" />
            <div className="relative bg-cba-navy-light border border-cba-gold/20 rounded-2xl p-8 hover:border-cba-gold/40 transition-all card-glow-hover cursor-pointer">
              <div className="w-16 h-16 rounded-xl bg-cba-gold/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Upload className="w-8 h-8 text-cba-gold" />
              </div>
              <h3 className="text-2xl font-bold mb-3">Upload Project File</h3>
              <p className="text-gray-300 mb-6">
                Have a project document? Upload your PDF file and let AI
                analyze it to recommend the best indicators.
              </p>
              <ul className="space-y-2 mb-8 text-sm text-gray-400">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-cba-gold" />
                  Instant analysis of project details
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-cba-gold" />
                  Identifies missing information
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-cba-gold" />
                  Guided completion process
                </li>
              </ul>
              <a href="/upload" className="w-full bg-cba-gold hover:bg-cba-gold-light text-cba-navy font-semibold py-3 px-6 rounded-lg transition-all flex items-center justify-center gap-2 group-hover:gap-3">
                Upload File
                <ArrowRight className="w-5 h-5" />
              </a>
            </div>
          </motion.div>

          {/* Start from Scratch Card */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="group relative"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-cba-gold/20 to-transparent rounded-2xl blur-xl group-hover:blur-2xl transition-all" />
            <div className="relative bg-cba-navy-light border border-cba-gold/20 rounded-2xl p-8 hover:border-cba-gold/40 transition-all card-glow-hover cursor-pointer">
              <div className="w-16 h-16 rounded-xl bg-cba-gold/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <MessageSquare className="w-8 h-8 text-cba-gold" />
              </div>
              <h3 className="text-2xl font-bold mb-3">Start from Scratch</h3>
              <p className="text-gray-300 mb-6">
                Building a new project? Chat with our AI assistant to define your
                project and get personalized indicator recommendations.
              </p>
              <ul className="space-y-2 mb-8 text-sm text-gray-400">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-cba-gold" />
                  Conversational project builder
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-cba-gold" />
                  Step-by-step guidance
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-cba-gold" />
                  Real-time recommendations
                </li>
              </ul>
              <a href="/chat" className="w-full bg-cba-gold hover:bg-cba-gold-light text-cba-navy font-semibold py-3 px-6 rounded-lg transition-all flex items-center justify-center gap-2 group-hover:gap-3">
                Start Chat
                <ArrowRight className="w-5 h-5" />
              </a>
            </div>
          </motion.div>
        </div>

        {/* Features */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-20 text-center"
        >
          <p className="text-gray-400 mb-6">Powered by</p>
          <div className="flex items-center justify-center gap-8 text-sm text-gray-500">
            <span>Amazon Bedrock</span>
            <span>•</span>
            <span>Claude AI</span>
            <span>•</span>
            <span>801 Methods</span>
            <span>•</span>
            <span>224 Indicators</span>
          </div>
        </motion.div>
      </section>
    </main>
  );
}
