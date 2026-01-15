"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { ArrowLeft, Filter, Grid3x3, List, GitCompare, Download, ChevronDown, ChevronUp, DollarSign, Target, Zap, Loader2, AlertCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { api, Indicator as ApiIndicator } from "@/lib/api";

interface Indicator {
  id: number;
  name: string;
  component: string;
  class: string;
  cost: string;
  accuracy: string;
  ease: string;
  principle: string;
  criterion: string;
  priority: string;
  methods: Method[];
  definition: string;
}

interface Method {
  id: number;
  name: string;
  cost: string;
  accuracy: string;
  ease: string;
}

// Fallback data shown when no recommendations are available
const fallbackIndicators: Indicator[] = [
  {
    id: 47,
    name: "Species Diversity Index",
    component: "Biotic",
    class: "Biodiversity",
    cost: "Medium",
    accuracy: "High",
    ease: "Medium",
    principle: "Principle 2",
    criterion: "Criterion 2.1",
    priority: "Primary",
    definition: "Measures the variety and abundance of species in a given area, providing insights into ecosystem health and biodiversity.",
    methods: [
      { id: 1, name: "Random Walks", cost: "Low", accuracy: "Medium", ease: "High" },
      { id: 2, name: "Transect Sampling", cost: "Medium", accuracy: "High", ease: "Medium" },
      { id: 3, name: "Camera Traps", cost: "High", accuracy: "High", ease: "Low" },
    ],
  },
  {
    id: 89,
    name: "Soil Organic Carbon",
    component: "Abiotic",
    class: "Soil Carbon",
    cost: "Low",
    accuracy: "Medium",
    ease: "High",
    principle: "Principle 1",
    criterion: "Criterion 1.2",
    priority: "Primary",
    definition: "Quantifies the amount of carbon stored in soil, a key indicator of soil health and carbon sequestration potential.",
    methods: [
      { id: 4, name: "Walkley-Black Method", cost: "Low", accuracy: "Medium", ease: "High" },
      { id: 5, name: "Loss on Ignition", cost: "Low", accuracy: "Low", ease: "High" },
      { id: 6, name: "Dry Combustion", cost: "High", accuracy: "High", ease: "Medium" },
    ],
  },
  {
    id: 12,
    name: "Water Quality Index",
    component: "Abiotic",
    class: "Water",
    cost: "High",
    accuracy: "High",
    ease: "Low",
    principle: "Principle 3",
    criterion: "Criterion 3.1",
    priority: "Secondary",
    definition: "Composite measure of water quality based on multiple parameters including pH, dissolved oxygen, and contaminants.",
    methods: [
      { id: 7, name: "Field Test Kits", cost: "Medium", accuracy: "Medium", ease: "High" },
      { id: 8, name: "Laboratory Analysis", cost: "High", accuracy: "High", ease: "Low" },
    ],
  },
  {
    id: 34,
    name: "Crop Yield per Hectare",
    component: "Socioeconomic",
    class: "Productivity",
    cost: "Low",
    accuracy: "High",
    ease: "High",
    principle: "Principle 5",
    criterion: "Criterion 5.2",
    priority: "Primary",
    definition: "Measures agricultural productivity by quantifying crop output per unit area, essential for economic viability assessment.",
    methods: [
      { id: 9, name: "Harvest Weighing", cost: "Low", accuracy: "High", ease: "High" },
      { id: 10, name: "Crop Cutting", cost: "Low", accuracy: "High", ease: "Medium" },
    ],
  },
];

function ResultsContent() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session_id");

  const [indicators, setIndicators] = useState<Indicator[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [usingFallback, setUsingFallback] = useState(false);
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [selectedForCompare, setSelectedForCompare] = useState<number[]>([]);
  const [filters, setFilters] = useState({
    component: "all",
    cost: "all",
    ease: "all",
  });

  // Fetch recommendations from API
  useEffect(() => {
    async function fetchRecommendations() {
      if (!sessionId) {
        // No session ID - use fallback data
        setIndicators(fallbackIndicators);
        setUsingFallback(true);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const response = await api.getRecommendations(sessionId);

        if (response.indicators && response.indicators.length > 0) {
          // Transform API indicators to match our interface
          const transformedIndicators: Indicator[] = response.indicators.map((ind: ApiIndicator) => ({
            id: ind.id,
            name: ind.name,
            component: ind.component || "Unknown",
            class: ind.class || "Unknown",
            cost: ind.cost || "Medium",
            accuracy: ind.accuracy || "Medium",
            ease: ind.ease || "Medium",
            principle: ind.principle || "",
            criterion: ind.criterion || "",
            priority: ind.priority || "Primary",
            definition: ind.definition || "",
            methods: ind.methods || [],
          }));
          setIndicators(transformedIndicators);
          setUsingFallback(false);
        } else {
          // No recommendations found - use fallback
          setIndicators(fallbackIndicators);
          setUsingFallback(true);
        }
      } catch (err) {
        console.error("Failed to fetch recommendations:", err);
        setError(err instanceof Error ? err.message : "Failed to load recommendations");
        // Use fallback on error
        setIndicators(fallbackIndicators);
        setUsingFallback(true);
      } finally {
        setLoading(false);
      }
    }

    fetchRecommendations();
  }, [sessionId]);

  const toggleExpand = (id: number) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const toggleCompare = (id: number) => {
    setSelectedForCompare((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const filteredIndicators = indicators.filter((ind) => {
    if (filters.component !== "all" && ind.component !== filters.component) return false;
    if (filters.cost !== "all" && ind.cost !== filters.cost) return false;
    if (filters.ease !== "all" && ind.ease !== filters.ease) return false;
    return true;
  });

  // Show loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-cba-gold animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading recommendations...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      {/* Error/Warning Banner */}
      {error && (
        <div className="bg-red-900/50 border-b border-red-700 px-6 py-3">
          <div className="container mx-auto flex items-center gap-2 text-red-200">
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
          </div>
        </div>
      )}

      {usingFallback && !error && (
        <div className="bg-amber-600 border-b-2 border-amber-400 px-6 py-4">
          <div className="container mx-auto flex items-center gap-3 text-white">
            <div className="bg-amber-800 rounded-full p-2">
              <AlertCircle className="w-5 h-5" />
            </div>
            <div>
              <p className="font-bold text-lg">Showing Example Data</p>
              <p className="text-amber-100 text-sm">These are sample indicators for demonstration. Complete a chat conversation to get personalized recommendations for your project.</p>
            </div>
            <Link
              href="/chat"
              className="ml-auto bg-white text-amber-700 hover:bg-amber-50 font-semibold px-4 py-2 rounded-lg transition whitespace-nowrap"
            >
              Start Chat
            </Link>
          </div>
        </div>
      )}

      {/* Header */}
      <header className="border-b border-cba-navy-light bg-cba-navy-dark/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/chat" className="text-gray-400 hover:text-white transition">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="text-lg font-bold flex items-center gap-2">
                {usingFallback ? "Example Indicators" : "Recommended Indicators"}
                {usingFallback && (
                  <span className="text-xs font-normal bg-amber-600 text-white px-2 py-0.5 rounded-full">
                    DEMO DATA
                  </span>
                )}
              </h1>
              <p className="text-xs text-gray-400">
                {filteredIndicators.length} {usingFallback ? "example indicators shown" : "indicators found"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex gap-2">
              <button
                onClick={() => setViewMode("grid")}
                className={`p-2 rounded-lg transition ${viewMode === "grid" ? "bg-cba-gold text-cba-navy" : "text-gray-400 hover:text-white"
                  }`}
              >
                <Grid3x3 className="w-5 h-5" />
              </button>
              <button
                onClick={() => setViewMode("list")}
                className={`p-2 rounded-lg transition ${viewMode === "list" ? "bg-cba-gold text-cba-navy" : "text-gray-400 hover:text-white"
                  }`}
              >
                <List className="w-5 h-5" />
              </button>
            </div>
            {selectedForCompare.length > 0 && (
              <Link
                href={`/compare?ids=${selectedForCompare.join(",")}${sessionId ? `&session_id=${sessionId}` : ""}`}
                className="flex items-center gap-2 bg-cba-gold hover:bg-cba-gold-light text-cba-navy font-semibold px-4 py-2 rounded-lg transition"
              >
                <GitCompare className="w-4 h-4" />
                Compare ({selectedForCompare.length})
              </Link>
            )}
            <button
              className="flex items-center gap-2 text-gray-500 cursor-not-allowed opacity-60"
              disabled
              title="Export coming soon"
            >
              <Download className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Filters Sidebar */}
        <aside className="w-64 border-r border-cba-navy-light bg-cba-navy-dark/30 p-6">
          <h2 className="text-lg font-bold mb-6 flex items-center gap-2">
            <Filter className="w-5 h-5 text-cba-gold" />
            Filters
          </h2>

          <div className="space-y-6">
            <FilterSection
              label="Component"
              value={filters.component}
              onChange={(val) => setFilters({ ...filters, component: val })}
              options={["all", "Biotic", "Abiotic", "Socioeconomic"]}
            />
            <FilterSection
              label="Cost"
              value={filters.cost}
              onChange={(val) => setFilters({ ...filters, cost: val })}
              options={["all", "Low", "Medium", "High"]}
            />
            <FilterSection
              label="Ease of Use"
              value={filters.ease}
              onChange={(val) => setFilters({ ...filters, ease: val })}
              options={["all", "Low", "Medium", "High"]}
            />
          </div>

          <button
            onClick={() => setFilters({ component: "all", cost: "all", ease: "all" })}
            className="w-full mt-6 text-sm text-gray-400 hover:text-white transition"
          >
            Reset Filters
          </button>
        </aside>

        {/* Indicators Grid/List */}
        <main className="flex-1 p-6">
          <div className={viewMode === "grid" ? "grid md:grid-cols-2 gap-6" : "space-y-4"}>
            {filteredIndicators.map((indicator) => (
              <IndicatorCard
                key={indicator.id}
                indicator={indicator}
                isExpanded={expandedId === indicator.id}
                isSelected={selectedForCompare.includes(indicator.id)}
                onToggleExpand={() => toggleExpand(indicator.id)}
                onToggleCompare={() => toggleCompare(indicator.id)}
                viewMode={viewMode}
                isMockData={usingFallback}
              />
            ))}
          </div>
        </main>
      </div>
    </div>
  );
}

function FilterSection({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (val: string) => void;
  options: string[];
}) {
  return (
    <div>
      <label className="text-sm font-semibold text-gray-300 mb-3 block">{label}</label>
      <div className="space-y-2">
        {options.map((option) => (
          <label key={option} className="flex items-center gap-2 cursor-pointer group">
            <input
              type="radio"
              name={label}
              checked={value === option}
              onChange={() => onChange(option)}
              className="w-4 h-4 text-cba-gold"
            />
            <span className="text-sm text-gray-400 group-hover:text-white transition capitalize">
              {option}
            </span>
          </label>
        ))}
      </div>
    </div>
  );
}

function IndicatorCard({
  indicator,
  isExpanded,
  isSelected,
  onToggleExpand,
  onToggleCompare,
  viewMode,
  isMockData = false,
}: {
  indicator: Indicator;
  isExpanded: boolean;
  isSelected: boolean;
  onToggleExpand: () => void;
  onToggleCompare: () => void;
  viewMode: "grid" | "list";
  isMockData?: boolean;
}) {
  return (
    <motion.div
      layout
      className={`bg-cba-navy-light border rounded-2xl overflow-hidden transition-all relative ${isSelected ? "border-cba-gold" : isMockData ? "border-amber-600/40 hover:border-amber-600/60" : "border-cba-gold/20 hover:border-cba-gold/40"
        }`}
    >
      {/* Mock Data Ribbon */}
      {isMockData && (
        <div className="absolute top-0 right-0 bg-amber-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-bl-lg">
          EXAMPLE
        </div>
      )}
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-mono text-gray-400">#{indicator.id}</span>
              <span className="text-xs px-2 py-1 rounded-full bg-cba-gold/10 text-cba-gold">
                {indicator.component}
              </span>
            </div>
            <h3 className="text-xl font-bold mb-1">{indicator.name}</h3>
            <p className="text-sm text-gray-400">{indicator.class}</p>
          </div>
        </div>

        {/* Attributes */}
        <div className="flex gap-4 mb-4">
          <AttributeBadge icon={<DollarSign className="w-3 h-3" />} label="Cost" value={indicator.cost} />
          <AttributeBadge icon={<Target className="w-3 h-3" />} label="Accuracy" value={indicator.accuracy} />
          <AttributeBadge icon={<Zap className="w-3 h-3" />} label="Ease" value={indicator.ease} />
        </div>

        {/* Mapping */}
        <div className="text-xs text-gray-400 mb-4">
          {indicator.principle} • {indicator.criterion} • {indicator.priority}
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={onToggleExpand}
            className="flex-1 bg-cba-navy hover:bg-cba-navy-dark text-white px-4 py-2 rounded-lg transition flex items-center justify-center gap-2 text-sm"
          >
            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            {isExpanded ? "Hide" : "View"} Methods ({indicator.methods.length})
          </button>
          <button
            onClick={onToggleCompare}
            className={`px-4 py-2 rounded-lg transition text-sm font-semibold ${isSelected
              ? "bg-cba-gold text-cba-navy"
              : "bg-cba-navy hover:bg-cba-navy-dark text-white"
              }`}
          >
            {isSelected ? "Selected" : "Compare"}
          </button>
        </div>

        {/* Expanded Content */}
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="mt-4 pt-4 border-t border-cba-gold/20"
            >
              <p className="text-sm text-gray-300 mb-4">{indicator.definition}</p>
              <h4 className="text-sm font-semibold mb-3">Available Methods:</h4>
              <div className="space-y-2">
                {indicator.methods.map((method) => (
                  <div
                    key={method.id}
                    className="bg-cba-navy/50 rounded-lg p-3 flex items-center justify-between"
                  >
                    <span className="text-sm font-medium">{method.name}</span>
                    <div className="flex gap-2 text-xs">
                      <span className="text-gray-400">💰 {method.cost}</span>
                      <span className="text-gray-400">📊 {method.accuracy}</span>
                      <span className="text-gray-400">🎯 {method.ease}</span>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}

function AttributeBadge({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  const colorMap: Record<string, string> = {
    Low: "text-green-400",
    Medium: "text-yellow-400",
    High: "text-red-400",
  };

  return (
    <div className="flex items-center gap-1.5 text-xs">
      <div className="text-gray-400">{icon}</div>
      <span className="text-gray-500">{label}:</span>
      <span className={`font-semibold ${colorMap[value] || "text-gray-300"}`}>{value}</span>
    </div>
  );
}

// Export with Suspense boundary for useSearchParams
export default function ResultsPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-cba-gold animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    }>
      <ResultsContent />
    </Suspense>
  );
}
