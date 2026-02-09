import React, { useState } from 'react';
import { ArrowLeft, Save, Zap, Thermometer, Leaf, RefreshCw, Sun, AlertTriangle } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

const AuditDashboard = ({ data, onReset }) => {
    const [showHeatmap, setShowHeatmap] = useState(true);

    // Normalized Data from Backend (or fallback for older audits)
    const score = data.analysis.energy_score || (data.analysis.overall_score ? data.analysis.overall_score * 10 : 50);
    const weather = data.analysis.weather_context || "Unknown";
    const opportunities = data.analysis.opportunities || [];

    // Fallback map if backend returns old format detected items
    const displayItems = opportunities.length > 0 ? opportunities : (data.analysis.detections || []).map(d => ({
        title: `Inefficient ${d.label}`,
        description: d.recommendation,
        savings_monthly_inr: (d.watts * d.estimated_hours * 30 / 1000 * 7).toFixed(0), // Rough calc
        fix_action: "Check efficiency rating",
        box_2d: d.box_2d
    }));

    const totalSavings = data.analysis.total_monthly_savings_inr || displayItems.reduce((acc, curr) => acc + parseFloat(curr.savings_monthly_inr || 0), 0);
    const trees = data.analysis.trees_planted_equivalent || (totalSavings / 100).toFixed(1); // Rough calc

    // Gauge Chart Data
    const gaugeData = [
        { name: 'Score', value: score },
        { name: 'Remaining', value: 100 - score },
    ];
    const COLORS = [score > 70 ? '#10B981' : score > 40 ? '#F59E0B' : '#EF4444', '#1F2937'];

    return (
        <div className="animate-fade-in max-w-7xl mx-auto p-4 md:p-8">
            <div className="flex items-center justify-between mb-8">
                <button
                    onClick={onReset}
                    className="flex items-center text-gray-400 hover:text-white transition-colors group"
                >
                    <ArrowLeft className="w-4 h-4 mr-2 group-hover:-translate-x-1 transition-transform" />
                    Back to Upload
                </button>

                <div className="flex items-center text-brand-light font-bold text-lg tracking-tight opacity-80">
                    <Leaf className="w-5 h-5 mr-2" />
                    Sustainable Energy Auditor
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* Left Col: Image & Context (7 cols) */}
                <div className="lg:col-span-7 space-y-6">

                    {/* Weather & Location Banner */}
                    <div className="flex items-center justify-between bg-gradient-to-r from-brand-card to-brand-dark p-6 rounded-2xl border border-white/5 relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-brand-green/10 blur-3xl rounded-full"></div>
                        <div className="flex items-center space-x-4 relative z-10">
                            <div className="p-3 bg-brand-dark rounded-xl border border-white/10">
                                <Sun className="w-8 h-8 text-brand-accent" />
                            </div>
                            <div>
                                <div className="text-xs text-brand-light uppercase tracking-wider font-semibold mb-1">Current Conditions</div>
                                <div className="text-xl font-bold text-white">Jaipur • {weather}</div>
                            </div>
                        </div>
                    </div>

                    {/* Main Visual */}
                    <div className="bg-brand-card/50 rounded-2xl border border-white/10 relative group shadow-2xl h-[600px] flex items-center justify-center overflow-hidden">
                        {/* Background Blur for aesthetics if image doesn't fill */}
                        <div
                            className="absolute inset-0 opacity-20 blur-3xl scale-125"
                            style={{
                                backgroundImage: `url(${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/${data.heatmap_image})`,
                                backgroundSize: 'cover',
                                backgroundPosition: 'center'
                            }}
                        ></div>

                        <img
                            src={showHeatmap
                                ? `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/${data.heatmap_image}`
                                : `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/${data.original_image}`
                            }
                            alt="Audit Analysis"
                            className="relative z-10 max-w-full max-h-full object-contain shadow-2xl rounded-lg"
                        />

                        {/* Floating Toggle */}
                        <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 bg-brand-dark/90 backdrop-blur-md p-1.5 rounded-full flex items-center shadow-xl border border-white/10 z-20">
                            <button
                                onClick={() => setShowHeatmap(false)}
                                className={`px-5 py-2 text-sm rounded-full transition-all font-medium ${!showHeatmap ? 'bg-white text-brand-dark' : 'text-gray-400 hover:text-white'}`}
                            >
                                Original
                            </button>
                            <button
                                onClick={() => setShowHeatmap(true)}
                                className={`px-5 py-2 text-sm rounded-full transition-all font-medium ${showHeatmap ? 'bg-gradient-to-r from-brand-green to-brand-light text-brand-dark shadow-lg font-bold' : 'text-gray-400 hover:text-white'}`}
                            >
                                Thermal View
                            </button>
                        </div>
                    </div>
                </div>

                {/* Right Col: Score & Actions (5 cols) */}
                <div className="lg:col-span-5 space-y-6 flex flex-col h-full">

                    {/* Score Card */}
                    <div className="bg-brand-card rounded-2xl p-6 border border-white/10 relative overflow-hidden shadow-xl shrink-0">
                        <div className="absolute top-0 right-0 w-40 h-40 bg-brand-green/10 rounded-full blur-3xl -mr-10 -mt-10"></div>
                        <h3 className="text-gray-400 text-xs font-bold uppercase tracking-widest mb-4">Energy Efficiency Score</h3>

                        <div className="flex items-center justify-between">
                            <div className="relative w-28 h-28">
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart>
                                        <Pie
                                            data={gaugeData}
                                            cx="50%"
                                            cy="50%"
                                            innerRadius={28}
                                            outerRadius={38}
                                            startAngle={180}
                                            endAngle={0}
                                            paddingAngle={0}
                                            dataKey="value"
                                            stroke="none"
                                        >
                                            {gaugeData.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                            ))}
                                        </Pie>
                                    </PieChart>
                                </ResponsiveContainer>
                                <div className="absolute inset-0 flex flex-col items-center justify-center pt-6">
                                    <span className="text-3xl font-bold text-white">{score}</span>
                                    <span className="text-[10px] text-gray-500 font-medium">/100</span>
                                </div>
                            </div>

                            <div className="flex-1 pl-6 border-l border-white/10">
                                <div className="mb-3">
                                    <div className="text-gray-400 text-xs mb-1 font-medium">Potential Savings</div>
                                    <div className="text-3xl font-bold text-brand-light">₹ {totalSavings}</div>
                                    <div className="text-[10px] text-gray-500 mt-0.5">per month</div>
                                </div>
                                <div className="flex items-center space-x-2 text-[10px] font-bold text-brand-green bg-brand-green/10 px-2.5 py-1 rounded-lg w-fit border border-brand-green/20">
                                    <Leaf className="w-3 h-3" />
                                    <span>{trees} Trees / yr</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Opportunities List - Fixed Height to match image container */}
                    <div className="flex-1 flex flex-col min-h-0 bg-brand-card/50 rounded-2xl border border-white/5 overflow-hidden h-[600px]">
                        <div className="flex items-center justify-between p-4 border-b border-white/5 bg-brand-card/80 backdrop-blur-sm sticky top-0 z-10 shrink-0">
                            <h3 className="text-md font-bold text-white flex items-center">
                                <Zap className="w-4 h-4 text-brand-accent mr-2" />
                                Top Opportunities
                            </h3>
                            <span className="text-[10px] bg-brand-accent/10 text-brand-accent px-2 py-0.5 rounded-full font-bold border border-brand-accent/20">{displayItems.length} Issues</span>
                        </div>

                        <div className="overflow-y-auto p-4 space-y-3 scrollbar-thin scrollbar-thumb-brand-gray-700 hover:scrollbar-thumb-brand-gray-500 flex-1">
                            {displayItems.length === 0 && (
                                <div className="flex flex-col items-center justify-center h-full text-gray-500 text-sm">
                                    <p>No issues found. Great job!</p>
                                </div>
                            )}
                            {displayItems.map((item, idx) => (
                                <div key={idx} className="bg-brand-card p-4 rounded-xl border border-white/5 hover:border-brand-green/30 transition-all group hover:bg-brand-card/80 shrink-0">
                                    <div className="flex justify-between items-start mb-2">
                                        <h4 className="font-bold text-white text-sm pr-2 leading-tight">
                                            {item.title}
                                        </h4>
                                        <span className="shrink-0 text-brand-light font-bold text-xs bg-brand-light/10 px-1.5 py-0.5 rounded border border-brand-light/20">₹{item.savings_monthly_inr}</span>
                                    </div>
                                    <p className="text-xs text-gray-400 mb-2 leading-relaxed line-clamp-2">{item.description}</p>
                                    <div className="text-[10px] text-gray-300 font-medium bg-brand-dark/50 px-2 py-1.5 rounded-lg border border-white/5 flex items-start">
                                        <span className="text-brand-accent mr-1.5">FIX:</span> {item.fix_action}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AuditDashboard;
