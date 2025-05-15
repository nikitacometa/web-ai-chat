"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { startNewRound } from "@/lib/api";
import { GameRound } from "@/lib/types";

export default function AdminPage() {
  const [leftHandle, setLeftHandle] = useState("");
  const [rightHandle, setRightHandle] = useState("");
  const [adminToken, setAdminToken] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<{ success?: boolean; message?: string; round?: GameRound }>({});

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setResult({});

    try {
      const response = await startNewRound(leftHandle, rightHandle, adminToken);
      setResult(response);
    } catch (error) {
      setResult({ 
        success: false, 
        message: `Failed to start new round: ${error instanceof Error ? error.message : String(error)}` 
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen p-4 md:p-8">
      <div className="w-full max-w-md">
        <h1 className="text-2xl font-bold mb-6 text-center">AlgoFOMO Admin</h1>
        
        <div className="bg-background border border-border rounded-lg p-6 shadow-sm">
          <h2 className="text-xl font-semibold mb-4">Start New Round</h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="leftHandle">Left Twitter Handle</Label>
              <Input
                id="leftHandle"
                placeholder="e.g., elonmusk"
                value={leftHandle}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setLeftHandle(e.target.value)}
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="rightHandle">Right Twitter Handle</Label>
              <Input
                id="rightHandle"
                placeholder="e.g., SBF_FTX"
                value={rightHandle}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setRightHandle(e.target.value)}
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="adminToken">Admin Token</Label>
              <Input
                id="adminToken"
                type="password"
                placeholder="Admin API token"
                value={adminToken}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setAdminToken(e.target.value)}
                required
              />
            </div>
            
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Starting..." : "Start New Round"}
            </Button>
          </form>
          
          {result.message && (
            <div className={`mt-4 p-3 rounded-md ${result.success ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400" : "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400"}`}>
              <p>{result.message}</p>
              {result.round && <p className="font-mono mt-1">Round ID: {result.round.id}</p>}
            </div>
          )}
        </div>
      </div>
    </main>
  );
} 