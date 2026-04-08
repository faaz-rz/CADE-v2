import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, TrendingDown, FileCheck, BarChart3, ChevronRight, Stethoscope, BadgeIndianRupee, Package, Wrench } from 'lucide-react';

const features = [
    {
        icon: <Shield className="w-6 h-6 text-teal-600" />,
        title: "Vendor Concentration Risk",
        desc: "Identify single-supplier dependencies in medical equipment, pharma, and consumables before they become supply chain failures."
    },
    {
        icon: <TrendingDown className="w-6 h-6 text-emerald-600" />,
        title: "Price Intelligence",
        desc: "Cross-supplier price comparison across every procurement category. Know exactly when you're overpaying."
    },
    {
        icon: <Wrench className="w-6 h-6 text-indigo-600" />,
        title: "AMC Tracker",
        desc: "Track Annual Maintenance Contracts against market rates. Automatic detection of 2%+ overcharges on medical equipment."
    },
    {
        icon: <FileCheck className="w-6 h-6 text-blue-600" />,
        title: "Contract Renewal Engine",
        desc: "Never miss a renewal window. AI-generated negotiation playbooks with competitive quote benchmarks."
    },
    {
        icon: <BarChart3 className="w-6 h-6 text-orange-600" />,
        title: "Board-Ready Reporting",
        desc: "Export CFO-ready procurement intelligence with ₹ amounts, risk heatmaps, and savings opportunities."
    },
    {
        icon: <BadgeIndianRupee className="w-6 h-6 text-purple-600" />,
        title: "India-First Design",
        desc: "Built for Indian hospital procurement. ₹ currency, GST-aware categories, and Indian vendor intelligence."
    }
];

const stats = [
    { value: "₹2.1Cr+", label: "Savings identified per hospital" },
    { value: "10%", label: "Average AMC overcharge detected" },
    { value: "15-20%", label: "Vendor negotiation leverage gained" },
    { value: "90 days", label: "Contract renewal lead time" }
];

export const HospitalLanding: React.FC = () => {
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-teal-50/30">
            {/* Header */}
            <nav className="px-6 py-4 flex items-center justify-between border-b border-gray-100 bg-white/80 backdrop-blur-sm">
                <div className="flex items-center gap-3">
                    <Stethoscope className="w-7 h-7 text-teal-600" />
                    <div className="flex flex-col">
                        <span className="text-xl font-bold text-gray-900">CADE</span>
                        <span className="text-[10px] text-gray-400 -mt-1 uppercase tracking-wider">Hospital Procurement Intelligence</span>
                    </div>
                </div>
                <Link
                    to="/"
                    className="bg-teal-600 hover:bg-teal-700 text-white font-medium px-5 py-2 rounded-lg shadow-sm transition-colors text-sm"
                >
                    Log In →
                </Link>
            </nav>

            {/* Hero */}
            <section className="max-w-5xl mx-auto px-6 pt-20 pb-16 text-center">
                <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-teal-50 text-teal-700 rounded-full text-sm font-medium mb-6 border border-teal-100">
                    <Stethoscope className="w-4 h-4" />
                    Hospital Procurement Intelligence
                </div>
                <h1 className="text-5xl font-bold text-gray-900 leading-tight mb-6">
                    Stop overpaying vendors.<br />
                    <span className="text-teal-600">Start saving ₹2Cr+ annually.</span>
                </h1>
                <p className="text-lg text-gray-600 max-w-2xl mx-auto mb-10 leading-relaxed">
                    CADE analyzes your hospital's vendor spend, detects concentration risks,
                    tracks AMC overcharges, and generates board-ready procurement intelligence —
                    all from a single transaction upload.
                </p>
                <div className="flex items-center justify-center gap-4">
                    <Link
                        to="/"
                        className="bg-teal-600 hover:bg-teal-700 text-white font-semibold px-8 py-3 rounded-xl shadow-lg shadow-teal-600/20 transition-all hover:shadow-teal-600/30 hover:-translate-y-0.5 text-base flex items-center gap-2"
                    >
                        Get Started <ChevronRight className="w-4 h-4" />
                    </Link>
                    <a
                        href="mailto:hello@capitalrisk.app"
                        className="bg-white border border-gray-200 hover:border-gray-300 text-gray-700 font-semibold px-8 py-3 rounded-xl shadow-sm transition-colors text-base"
                    >
                        Request Demo
                    </a>
                </div>
            </section>

            {/* Stats band */}
            <section className="bg-white border-y border-gray-100">
                <div className="max-w-5xl mx-auto px-6 py-8 grid grid-cols-2 md:grid-cols-4 gap-6">
                    {stats.map((stat, i) => (
                        <div key={i} className="text-center">
                            <div className="text-2xl font-bold text-teal-600 mb-1">{stat.value}</div>
                            <div className="text-sm text-gray-500">{stat.label}</div>
                        </div>
                    ))}
                </div>
            </section>

            {/* Features */}
            <section className="max-w-5xl mx-auto px-6 py-16">
                <div className="text-center mb-12">
                    <h2 className="text-3xl font-bold text-gray-900 mb-3">Built for Hospital CFOs</h2>
                    <p className="text-gray-600 max-w-xl mx-auto">
                        Every feature designed around the unique challenges of hospital procurement
                        in India — from pharma price volatility to equipment AMC negotiations.
                    </p>
                </div>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {features.map((f, i) => (
                        <div
                            key={i}
                            className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow group"
                        >
                            <div className="p-3 bg-gray-50 rounded-lg inline-block mb-4 group-hover:bg-teal-50 transition-colors">
                                {f.icon}
                            </div>
                            <h3 className="text-base font-bold text-gray-900 mb-2">{f.title}</h3>
                            <p className="text-sm text-gray-600 leading-relaxed">{f.desc}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* How it works */}
            <section className="bg-gray-50 border-y border-gray-100">
                <div className="max-w-5xl mx-auto px-6 py-16">
                    <h2 className="text-3xl font-bold text-gray-900 mb-10 text-center">How it works</h2>
                    <div className="grid md:grid-cols-3 gap-8">
                        {[
                            { step: "01", title: "Upload vendor data", desc: "Export your transaction ledger as CSV or Excel. CADE maps it automatically to procurement categories." },
                            { step: "02", title: "Get instant analysis", desc: "7 rule-based checks run in seconds: concentration risk, AMC overcharges, price trends, renewal windows, and more." },
                            { step: "03", title: "Act on decisions", desc: "Approve or reject each recommendation. Export board-ready evidence packages for your procurement committee." }
                        ].map((item, i) => (
                            <div key={i} className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                                <div className="text-3xl font-bold text-teal-200 mb-3">{item.step}</div>
                                <h3 className="text-base font-bold text-gray-900 mb-2">{item.title}</h3>
                                <p className="text-sm text-gray-600 leading-relaxed">{item.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA */}
            <section className="max-w-5xl mx-auto px-6 py-16 text-center">
                <div className="bg-gradient-to-br from-teal-600 to-teal-700 rounded-2xl p-10 shadow-xl shadow-teal-600/10">
                    <Package className="w-10 h-10 text-teal-100 mx-auto mb-4" />
                    <h2 className="text-3xl font-bold text-white mb-3">Ready to optimize your hospital procurement?</h2>
                    <p className="text-teal-100 mb-8 max-w-lg mx-auto">
                        Join hospitals across India using CADE to save 12-18% on vendor spend annually.
                    </p>
                    <Link
                        to="/"
                        className="inline-flex items-center gap-2 bg-white text-teal-700 font-semibold px-8 py-3 rounded-xl shadow-lg hover:bg-teal-50 transition-colors text-base"
                    >
                        Start Free Trial <ChevronRight className="w-4 h-4" />
                    </Link>
                </div>
            </section>

            {/* Footer */}
            <footer className="border-t border-gray-100 py-6 text-center text-sm text-gray-400">
                © 2026 CADE — Capital Allocation Decision Engine. Built for Indian Healthcare.
            </footer>
        </div>
    );
};
