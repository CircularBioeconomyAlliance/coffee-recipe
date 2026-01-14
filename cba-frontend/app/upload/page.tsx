"use client";

import { useState, useCallback } from "react";
import { Upload, FileText, ArrowLeft, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";

interface AnalysisResult {
  found: {
    location?: string;
    commodity?: string;
    budget?: string;
  };
  missing: string[];
}

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragging(true);
    } else if (e.type === "dragleave") {
      setIsDragging(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleFile(files[0]);
    }
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (selectedFile: File) => {
    const validTypes = ["application/pdf", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"];
    
    if (!validTypes.includes(selectedFile.type)) {
      alert("Please upload a PDF or Excel file");
      return;
    }

    setFile(selectedFile);
    analyzeFile(selectedFile);
  };

  const analyzeFile = async (file: File) => {
    setIsAnalyzing(true);

    try {
      const { api } = await import("@/lib/api");
      const result = await api.uploadFile(file);
      setAnalysis(result);
    } catch (error) {
      console.error("Upload failed:", error);
      alert("Failed to analyze file");
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-cba-navy-light bg-cba-navy-dark/50 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4 flex items-center gap-4">
          <Link href="/" className="text-gray-400 hover:text-white transition">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-lg font-bold">Upload Project File</h1>
            <p className="text-xs text-gray-400">AI will analyze your document</p>
          </div>
        </div>
      </header>

      <main className="flex-1 container mx-auto px-6 py-12">
        <div className="max-w-4xl mx-auto">
          {/* Upload Area */}
          {!file && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all ${
                isDragging
                  ? "border-cba-gold bg-cba-gold/5"
                  : "border-cba-gold/30 hover:border-cba-gold/50"
              }`}
            >
              <div className="flex flex-col items-center gap-6">
                <div className="w-20 h-20 rounded-full bg-cba-gold/10 flex items-center justify-center">
                  <Upload className="w-10 h-10 text-cba-gold" />
                </div>
                
                <div>
                  <h2 className="text-2xl font-bold mb-2">Drop your file here</h2>
                  <p className="text-gray-400">or click to browse</p>
                </div>

                <input
                  type="file"
                  onChange={handleFileInput}
                  accept=".pdf,.xlsx,.xls"
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />

                <div className="flex gap-4 text-sm text-gray-500">
                  <span>📄 PDF</span>
                  <span>•</span>
                  <span>📊 Excel</span>
                  <span>•</span>
                  <span>Max 10MB</span>
                </div>
              </div>
            </motion.div>
          )}

          {/* File Uploaded */}
          {file && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="space-y-6"
            >
              {/* File Info */}
              <div className="bg-cba-navy-light border border-cba-gold/20 rounded-2xl p-6 flex items-center gap-4">
                <div className="w-12 h-12 rounded-lg bg-cba-gold/10 flex items-center justify-center">
                  <FileText className="w-6 h-6 text-cba-gold" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold">{file.name}</h3>
                  <p className="text-sm text-gray-400">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                {isAnalyzing && (
                  <Loader2 className="w-6 h-6 text-cba-gold animate-spin" />
                )}
              </div>

              {/* Analysis Results */}
              <AnimatePresence>
                {analysis && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-6"
                  >
                    {/* Found Information */}
                    <div className="bg-cba-navy-light border border-green-500/20 rounded-2xl p-6">
                      <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                        <CheckCircle className="w-5 h-5 text-green-500" />
                        Information Found
                      </h3>
                      <div className="grid md:grid-cols-3 gap-4">
                        {Object.entries(analysis.found).map(([key, value]) => (
                          <div key={key} className="bg-cba-navy/50 rounded-lg p-4">
                            <div className="text-xs text-gray-400 mb-1 capitalize">{key}</div>
                            <div className="font-semibold text-green-400">{value}</div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Missing Information */}
                    {analysis.missing.length > 0 && (
                      <div className="bg-cba-navy-light border border-orange-500/20 rounded-2xl p-6">
                        <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                          <AlertCircle className="w-5 h-5 text-orange-500" />
                          Missing Information
                        </h3>
                        <p className="text-gray-300 mb-4">
                          We need a bit more information to recommend the best indicators:
                        </p>
                        <ul className="space-y-2 mb-6">
                          {analysis.missing.map((item, index) => (
                            <li key={index} className="flex items-center gap-2 text-gray-400">
                              <span className="w-1.5 h-1.5 rounded-full bg-orange-500" />
                              {item}
                            </li>
                          ))}
                        </ul>
                        <a
                          href={`/chat?location=${encodeURIComponent(analysis.found.location || "")}&commodity=${encodeURIComponent(analysis.found.commodity || "")}&budget=${encodeURIComponent(analysis.found.budget || "")}`}
                          className="inline-flex items-center gap-2 bg-cba-gold hover:bg-cba-gold-light text-cba-navy font-semibold px-6 py-3 rounded-lg transition"
                        >
                          Complete in Chat
                          <ArrowLeft className="w-4 h-4 rotate-180" />
                        </a>
                      </div>
                    )}

                    {/* All Complete */}
                    {analysis.missing.length === 0 && (
                      <div className="bg-gradient-to-r from-cba-gold/10 to-transparent border border-cba-gold/30 rounded-2xl p-6 text-center">
                        <CheckCircle className="w-12 h-12 text-cba-gold mx-auto mb-4" />
                        <h3 className="text-xl font-bold mb-2">All Set!</h3>
                        <p className="text-gray-300 mb-6">
                          We have all the information needed. Let's find your indicators.
                        </p>
                        <Link
                          href={`/chat?location=${encodeURIComponent(analysis.found.location || "")}&commodity=${encodeURIComponent(analysis.found.commodity || "")}&budget=${encodeURIComponent(analysis.found.budget || "")}`}
                          className="inline-block bg-cba-gold hover:bg-cba-gold-light text-cba-navy font-semibold px-8 py-3 rounded-lg transition"
                        >
                          Get Recommendations
                        </Link>
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )}
        </div>
      </main>
    </div>
  );
}
