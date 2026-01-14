"use client";

import { useState } from "react";
import { ArrowLeft, Filter, Grid3x3, List, GitCompare, Download, ChevronDown, ChevronUp, DollarSign, Target, Zap } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";

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

// Mock data
const mockIndicators: Indicator[] = [
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

export default function ResultsPage() {
  const [indicators] = useState<Indicator[]>(mockIndicators);
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [selectedForCompare, setSelectedForCompare] = useState<number[]>([]);
  const [filters, setFilters] = useState({
    component: "all",
    cost: "all",
    ease: "all",
  });

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

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-cba-navy-light bg-cba-navy-dark/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/chat" className="text-gray-400 hover:text-white transition">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="text-lg font-bold">Recommended Indicators</h1>
              <p className="text-xs text-gray-400">{filteredIndicators.length} indicators found</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex gap-2">
              <button
                onClick={() => setViewMode("grid")}
                className={`p-2 rounded-lg transition ${
                  viewMode === "grid" ? "bg-cba-gold text-cba-navy" : "text-gray-400 hover:text-white"
                }`}
              >
                <Grid3x3 className="w-5 h-5" />
              </button>
              <button
                onClick={() => setViewMode("list")}
                className={`p-2 rounded-lg transition ${
                  viewMode === "list" ? "bg-cba-gold text-cba-navy" : "text-gray-400 hover:text-white"
                }`}
              >
                <List className="w-5 h-5" />
              </button>
            </div>
            {selectedForCompare.length > 0 && (
              <Link
                href={`/compare?ids=${selectedForCompare.join(",")}`}
                className="flex items-center gap-2 bg-cba-gold hover:bg-cba-gold-light text-cba-navy font-semibold px-4 py-2 rounded-lg transition"
              >
                <GitCompare className="w-4 h-4" />
                Compare ({selectedForCompare.length})
              </Link>
            )}
            <button className="flex items-center gap-2 text-gray-400 hover:text-white transition">
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
}: {
  indicator: Indicator;
  isExpanded: boolean;
  isSelected: boolean;
  onToggleExpand: () => void;
  onToggleCompare: () => void;
  viewMode: "grid" | "list";
}) {
  return (
    <motion.div
      layout
      className={`bg-cba-navy-light border rounded-2xl overflow-hidden transition-all ${
        isSelected ? "border-cba-gold" : "border-cba-gold/20 hover:border-cba-gold/40"
      }`}
    >
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
            className={`px-4 py-2 rounded-lg transition text-sm font-semibold ${
              isSelected
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
