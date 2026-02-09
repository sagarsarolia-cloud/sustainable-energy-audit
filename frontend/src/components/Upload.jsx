import React, { useState, useCallback } from 'react';
import { Upload as UploadIcon, FileUp, AlertCircle, Loader2, Zap, Leaf, IndianRupee } from 'lucide-react';
import axios from 'axios';

const Upload = ({ onAuditComplete, loading, setLoading }) => {
    const [error, setError] = useState('');
    const [dragActive, setDragActive] = useState(false);

    const handleDrag = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    }, []);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    }, []);

    const handleChange = (e) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
    };

    const handleFile = async (file) => {
        if (!file.type.startsWith('image/')) {
            setError("Please upload an image file.");
            return;
        }
        setError("");
        setLoading(true);

        const formData = new FormData();
        formData.append('file', file);

        try {
            // Use environment variable for API URL or default to localhost
            const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

            const response = await axios.post(`${API_BASE_URL}/audit`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                }
            });
            onAuditComplete(response.data);
        } catch (err) {
            console.error("Upload error:", err);
            setError("Failed to analyze image. Ensure backend is running.");
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex flex-col items-center justify-center p-4 relative overflow-hidden">
            {/* Background Texture */}
            <div className="absolute inset-0 z-0 opacity-20">
                <div className="absolute top-0 left-0 w-96 h-96 bg-brand-green blur-[128px] rounded-full mix-blend-screen"></div>
                <div className="absolute bottom-0 right-0 w-96 h-96 bg-brand-accent blur-[128px] rounded-full mix-blend-screen"></div>
            </div>

            <div className="relative z-10 w-full max-w-4xl mx-auto space-y-12">

                {/* Hero Section */}
                <div className="text-center space-y-4">
                    <div className="inline-flex items-center px-3 py-1 rounded-full bg-brand-green/20 text-brand-light text-xs font-semibold uppercase tracking-wider mb-2">
                        <Leaf className="w-3 h-3 mr-2" /> Sustainable Energy Auditor
                    </div>
                    <h1 className="text-5xl md:text-6xl font-bold text-white tracking-tight">
                        Stop Wasting <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-green to-brand-light">Energy</span>
                    </h1>
                    <p className="text-lg text-gray-400 max-w-xl mx-auto">
                        Upload a photo of your room or appliance. Our AI detects inefficiencies and creates an instant action plan to save you money.
                    </p>
                </div>

                {/* Upload Area */}
                <div
                    className={`relative group w-full max-w-2xl mx-auto p-12 border-2 border-dashed rounded-3xl transition-all duration-300 transform hover:scale-[1.01] ${dragActive
                        ? "border-brand-green bg-brand-green/10 shadow-[0_0_32px_rgba(16,185,129,0.2)]"
                        : "border-gray-700 bg-brand-card/50 hover:border-brand-green/50 hover:bg-brand-card"
                        }`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                >
                    <input
                        type="file"
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-20"
                        onChange={handleChange}
                        accept="image/*"
                        disabled={loading}
                    />

                    <div className="flex flex-col items-center justify-center text-center space-y-6 relative z-10">
                        {loading ? (
                            <>
                                <div className="relative">
                                    <div className="absolute inset-0 bg-brand-green/20 blur-xl rounded-full animate-pulse"></div>
                                    <Loader2 className="w-16 h-16 text-brand-green animate-spin relative z-10" />
                                </div>
                                <div className="space-y-2">
                                    <p className="text-xl font-bold text-white">Analyzing Thermal Profile...</p>
                                    <p className="text-sm text-gray-400">Detecting insulation gaps & inefficiency...</p>
                                </div>
                            </>
                        ) : (
                            <>
                                <div className="p-6 bg-brand-dark rounded-full border border-gray-700 group-hover:border-brand-green/50 transition-colors shadow-2xl">
                                    <UploadIcon className="w-12 h-12 text-brand-light group-hover:scale-110 transition-transform" />
                                </div>
                                <div>
                                    <p className="text-2xl font-bold text-white mb-2">Drop your image here</p>
                                    <p className="text-gray-400">or click to browse</p>
                                </div>
                            </>
                        )}
                    </div>
                </div>

                {/* Features Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto pt-8">
                    <div className="bg-brand-card p-6 rounded-2xl border border-white/5 hover:border-brand-green/30 transition-colors">
                        <div className="w-10 h-10 bg-brand-dark rounded-lg flex items-center justify-center mb-4 text-brand-light">
                            <Zap className="w-6 h-6" />
                        </div>
                        <h3 className="font-bold text-white mb-2">Instant Analysis</h3>
                        <p className="text-sm text-gray-400">AI identifies appliances and structural issues in seconds.</p>
                    </div>
                    <div className="bg-brand-card p-6 rounded-2xl border border-white/5 hover:border-brand-green/30 transition-colors">
                        <div className="w-10 h-10 bg-brand-dark rounded-lg flex items-center justify-center mb-4 text-brand-light">
                            <IndianRupee className="w-6 h-6" />
                        </div>
                        <h3 className="font-bold text-white mb-2">Cost Savings</h3>
                        <p className="text-sm text-gray-400">Get estimated monthly savings and ROI calculation.</p>
                    </div>
                    <div className="bg-brand-card p-6 rounded-2xl border border-white/5 hover:border-brand-green/30 transition-colors">
                        <div className="w-10 h-10 bg-brand-dark rounded-lg flex items-center justify-center mb-4 text-brand-light">
                            <Leaf className="w-6 h-6" />
                        </div>
                        <h3 className="font-bold text-white mb-2">Eco Impact</h3>
                        <p className="text-sm text-gray-400">Track your reduced carbon footprint and impact.</p>
                    </div>
                </div>

                {error && (
                    <div className="mx-auto max-w-md flex items-center p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-200">
                        <AlertCircle className="w-5 h-5 mr-3 shrink-0" />
                        {error}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Upload;
