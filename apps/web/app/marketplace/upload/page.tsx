"use client";

import { useState } from "react";
import { Upload, FileJson, DollarSign, Wallet, Tag, CheckCircle, AlertCircle } from "lucide-react";

export default function UploadAgent() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<any>(null);
  const [price, setPrice] = useState<string>("");
  const [description, setDescription] = useState<string>("");
  const [wallet, setWallet] = useState<string>("");
  const [tags, setTags] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string>("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError("");
      
      // Preview
      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const data = JSON.parse(event.target?.result as string);
          setPreview(data);
          // Auto-suggest price based on estimated value
          if (data.estimated_market_value) {
            setPrice(Math.round(data.estimated_market_value * 1.2).toString());
          }
        } catch (e) {
          setError("Invalid JSON file");
        }
      };
      reader.readAsText(selectedFile);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a file");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("price", price);
      formData.append("description", description);
      formData.append("seller_wallet", wallet);
      formData.append("tags", tags);

      const res = await fetch("http://localhost:8000/marketplace/upload", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      
      if (data.success) {
        setResult(data);
      } else {
        setError(data.message || "Upload failed");
      }
    } catch (e) {
      setError("Network error. Is the API running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg border overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white">
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Upload className="w-6 h-6" />
              List Agent on Marketplace
            </h1>
            <p className="mt-2 opacity-90">
              Upload your trained agent and set your price
            </p>
          </div>

          <div className="p-6">
            {result ? (
              /* Success State */
              <div className="text-center py-8">
                <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  Agent Listed Successfully!
                </h2>
                <p className="text-gray-600 mb-4">
                  Your agent is now available on the marketplace
                </p>
                <div className="bg-gray-50 p-4 rounded-lg inline-block text-left">
                  <p><strong>Listing ID:</strong> {result.agent_id}</p>
                  <p><strong>Estimated Value:</strong> ${result.estimated_value}</p>
                </div>
                <div className="mt-6 flex gap-4 justify-center">
                  <a
                    href="/marketplace"
                    className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 transition"
                  >
                    View Marketplace
                  </a>
                  <button
                    onClick={() => {
                      setResult(null);
                      setFile(null);
                      setPreview(null);
                      setPrice("");
                    }}
                    className="bg-gray-200 text-gray-800 px-6 py-2 rounded hover:bg-gray-300 transition"
                  >
                    List Another
                  </button>
                </div>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* File Upload */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Agent Export File (JSON)
                  </label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition">
                    <input
                      type="file"
                      accept=".json"
                      onChange={handleFileChange}
                      className="hidden"
                      id="agent-file"
                    />
                    <label htmlFor="agent-file" className="cursor-pointer">
                      <FileJson className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                      <p className="text-gray-600">
                        {file ? file.name : "Click to upload agent JSON file"}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        Generated by arli-export-skill
                      </p>
                    </label>
                  </div>
                </div>

                {/* Preview */}
                {preview && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h3 className="font-semibold text-blue-900 mb-2">Agent Preview</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div>
                        <p className="text-xs text-gray-600">Name</p>
                        <p className="font-medium">{preview.name}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600">Level</p>
                        <p className="font-medium">{preview.level} ({preview.tier})</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600">XP</p>
                        <p className="font-medium">{preview.xp}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600">Est. Value</p>
                        <p className="font-medium text-green-600">
                          ${preview.estimated_market_value}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Price */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <DollarSign className="w-4 h-4 inline mr-1" />
                    Price (USD)
                  </label>
                  <input
                    type="number"
                    value={price}
                    onChange={(e) => setPrice(e.target.value)}
                    placeholder="100"
                    min="1"
                    step="0.01"
                    className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
                    required
                  />
                  {preview?.estimated_market_value && (
                    <p className="text-xs text-gray-500 mt-1">
                      Suggested: ${Math.round(preview.estimated_market_value * 1.2)} 
                      (20% above estimated value)
                    </p>
                  )}
                </div>

                {/* Description */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Describe your agent's capabilities and what makes it special..."
                    rows={3}
                    className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>

                {/* Wallet */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Wallet className="w-4 h-4 inline mr-1" />
                    Your ICP Wallet Address
                  </label>
                  <input
                    type="text"
                    value={wallet}
                    onChange={(e) => setWallet(e.target.value)}
                    placeholder="rdmx6-jaaaa-aaaaa-aaadq-cai"
                    className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Where you'll receive payments
                  </p>
                </div>

                {/* Tags */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Tag className="w-4 h-4 inline mr-1" />
                    Tags (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={tags}
                    onChange={(e) => setTags(e.target.value)}
                    placeholder="trading, crypto, analysis, automation"
                    className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>

                {/* Error */}
                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded flex items-center gap-2">
                    <AlertCircle className="w-5 h-5" />
                    {error}
                  </div>
                )}

                {/* Submit */}
                <button
                  type="submit"
                  disabled={loading || !file}
                  className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? "Uploading..." : "List on Marketplace"}
                </button>
              </form>
            )}
          </div>
        </div>

        {/* Instructions */}
        <div className="mt-8 bg-white rounded-lg shadow border p-6">
          <h2 className="font-semibold text-lg mb-4">How to Export Your Agent</h2>
          <div className="space-y-3 text-sm text-gray-600">
            <p>1. Install arli-export-skill in your agent</p>
            <p>2. Run: <code className="bg-gray-100 px-2 py-1 rounded">agent.export_to_arli()</code></p>
            <p>3. Upload the generated JSON file here</p>
            <p>4. Set your price and list!</p>
          </div>
        </div>
      </div>
    </div>
  );
}
