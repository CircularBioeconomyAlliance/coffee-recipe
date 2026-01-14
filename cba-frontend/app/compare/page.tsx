"use client";

import { useSearchParams } from "next/navigation";
import { ArrowLeft, Download, X } from "lucide-react";
import { motion } from "framer-motion";
import Link from "next/link";
import { Suspense } from "react";

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
  methods: number;
  definition: string;
}

// Mock data (same as results page)
const mockIndicators: Record<number, Indicator> = {
  47: {
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
    methods: 3,
    definition: "Measures the variety and abundance of species in a given area.",
  },
  89: {
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
    methods: 3,
    definition: "Quantifies the amount of carbon stored in soil.",
  },
  12: {
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
    methods: 2,
    definition: "Composite measure of water quality based on multiple parameters.",
  },
  34: {
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
    methods: 2,
    definition: "Measures agricultural productivity by quantifying crop output per unit area.",
  },
};

function ComparePageContent() {
  const searchParams = useSearchParams();
  const ids = searchParams.get("ids")?.split(",").map(Number) || [];
  const indicators = ids.map((id) => mockIndicators[id]).filter(Boolean);

  if (indicators.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-400 mb-4">No indicators selected for comparison</p>
          <Link href="/results" className="text-cba-gold hover:text-cba-gold-light">
            Go back to results
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-cba-navy-light bg-cba-navy-dark/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/results" className="text-gray-400 hover:text-white transition">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="text-lg font-bold">Compare Indicators</h1>
              <p className="text-xs text-gray-400">{indicators.length} indicators selected</p>
            </div>
          </div>
          <button className="flex items-center gap-2 bg-cba-gold hover:bg-cba-gold-light text-cba-navy font-semibold px-4 py-2 rounded-lg transition">
            <Download className="w-4 h-4" />
            Export Comparison
          </button>
        </div>
      </header>

      {/* Comparison Table */}
      <main className="container mx-auto px-6 py-8">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr>
                <th className="sticky left-0 bg-cba-navy-dark z-10 p-4 text-left text-sm font-semibold text-gray-400 border-b border-cba-gold/20">
                  Attribute
                </th>
                {indicators.map((indicator) => (
                  <th
                    key={indicator.id}
                    className="p-4 text-left border-b border-cba-gold/20 min-w-[250px]"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <div className="text-xs font-mono text-gray-400 mb-1">#{indicator.id}</div>
                        <div className="font-bold text-white">{indicator.name}</div>
                      </div>
                      <Link
                        href={`/results?remove=${indicator.id}`}
                        className="text-gray-400 hover:text-red-400 transition"
                      >
                        <X className="w-4 h-4" />
                      </Link>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              <ComparisonRow
                label="Component"
                values={indicators.map((i) => i.component)}
                renderValue={(val) => (
                  <span className="px-2 py-1 rounded-full bg-cba-gold/10 text-cba-gold text-xs">
                    {val}
                  </span>
                )}
              />
              <ComparisonRow label="Class" values={indicators.map((i) => i.class)} />
              <ComparisonRow
                label="Cost"
                values={indicators.map((i) => i.cost)}
                renderValue={(val) => <CostBadge value={val} />}
              />
              <ComparisonRow
                label="Accuracy"
                values={indicators.map((i) => i.accuracy)}
                renderValue={(val) => <AccuracyBadge value={val} />}
              />
              <ComparisonRow
                label="Ease of Use"
                values={indicators.map((i) => i.ease)}
                renderValue={(val) => <EaseBadge value={val} />}
              />
              <ComparisonRow
                label="Methods Available"
                values={indicators.map((i) => `${i.methods} methods`)}
              />
              <ComparisonRow label="Principle" values={indicators.map((i) => i.principle)} />
              <ComparisonRow label="Criterion" values={indicators.map((i) => i.criterion)} />
              <ComparisonRow
                label="Priority"
                values={indicators.map((i) => i.priority)}
                renderValue={(val) => (
                  <span
                    className={`px-2 py-1 rounded-full text-xs ${
                      val === "Primary"
                        ? "bg-green-500/10 text-green-400"
                        : "bg-yellow-500/10 text-yellow-400"
                    }`}
                  >
                    {val}
                  </span>
                )}
              />
              <ComparisonRow
                label="Definition"
                values={indicators.map((i) => i.definition)}
                renderValue={(val) => <span className="text-sm text-gray-300">{val}</span>}
              />
            </tbody>
          </table>
        </div>

        {/* Actions */}
        <div className="mt-8 flex gap-4 justify-center">
          <Link
            href="/results"
            className="bg-cba-navy-light hover:bg-cba-navy text-white font-semibold px-6 py-3 rounded-lg transition"
          >
            Back to Results
          </Link>
          <button className="bg-cba-gold hover:bg-cba-gold-light text-cba-navy font-semibold px-6 py-3 rounded-lg transition">
            Select These Indicators
          </button>
        </div>
      </main>
    </div>
  );
}

function ComparisonRow({
  label,
  values,
  renderValue,
}: {
  label: string;
  values: string[];
  renderValue?: (val: string) => React.ReactNode;
}) {
  return (
    <tr className="border-b border-cba-gold/10 hover:bg-cba-navy-light/30 transition">
      <td className="sticky left-0 bg-cba-navy-dark z-10 p-4 text-sm font-semibold text-gray-300">
        {label}
      </td>
      {values.map((value, index) => (
        <td key={index} className="p-4">
          {renderValue ? renderValue(value) : <span className="text-white">{value}</span>}
        </td>
      ))}
    </tr>
  );
}

function CostBadge({ value }: { value: string }) {
  const colors = {
    Low: "text-green-400",
    Medium: "text-yellow-400",
    High: "text-red-400",
  };
  return <span className={`font-semibold ${colors[value as keyof typeof colors]}`}>💰 {value}</span>;
}

function AccuracyBadge({ value }: { value: string }) {
  const colors = {
    Low: "text-red-400",
    Medium: "text-yellow-400",
    High: "text-green-400",
  };
  return <span className={`font-semibold ${colors[value as keyof typeof colors]}`}>📊 {value}</span>;
}

function EaseBadge({ value }: { value: string }) {
  const colors = {
    Low: "text-red-400",
    Medium: "text-yellow-400",
    High: "text-green-400",
  };
  return <span className={`font-semibold ${colors[value as keyof typeof colors]}`}>🎯 {value}</span>;
}


export default function ComparePage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-gradient-to-br from-[#031f35] to-[#042d4a] flex items-center justify-center text-white">Loading...</div>}>
      <ComparePageContent />
    </Suspense>
  );
}
