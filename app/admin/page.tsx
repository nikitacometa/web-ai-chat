'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { startNewRound } from '@/lib/api';
import { GameRound } from '@/lib/types';

export default function AdminPage() {
  const [leftAvatarUrl, setLeftAvatarUrl] = useState('');
  const [rightAvatarUrl, setRightAvatarUrl] = useState('');
  const [adminToken, setAdminToken] = useState('');
  const [initialMomentum, setInitialMomentum] = useState('50');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<{
    success?: boolean;
    message?: string;
    round?: GameRound;
  }>({});

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setResult({});

    try {
      const momentum = Number.parseInt(initialMomentum, 10);
      if (Number.isNaN(momentum) || momentum < 0 || momentum > 100) {
        setResult({
          success: false,
          message: 'Initial momentum must be a number between 0 and 100.',
        });
        setIsLoading(false);
        return;
      }
      const response = await startNewRound(
        leftAvatarUrl,
        rightAvatarUrl,
        adminToken,
        momentum,
      );
      setResult(response);
    } catch (error) {
      setResult({
        success: false,
        message: `Failed to start new round: ${error instanceof Error ? error.message : String(error)}`,
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
              <Label htmlFor="leftAvatarUrl">Left Avatar URL</Label>
              <Input
                id="leftAvatarUrl"
                type="url"
                placeholder="e.g., https://example.com/avatar1.png"
                value={leftAvatarUrl}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setLeftAvatarUrl(e.target.value)
                }
                required
                data-testid="admin-left-avatar-url-input"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="rightAvatarUrl">Right Avatar URL</Label>
              <Input
                id="rightAvatarUrl"
                type="url"
                placeholder="e.g., https://example.com/avatar2.png"
                value={rightAvatarUrl}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setRightAvatarUrl(e.target.value)
                }
                required
                data-testid="admin-right-avatar-url-input"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="initialMomentum">Initial Momentum (0-100)</Label>
              <Input
                id="initialMomentum"
                type="number"
                placeholder="50"
                value={initialMomentum}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setInitialMomentum(e.target.value)
                }
                min="0"
                max="100"
                required
                data-testid="admin-initial-momentum-input"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="adminToken">Admin Token</Label>
              <Input
                id="adminToken"
                type="password"
                placeholder="Admin API token"
                value={adminToken}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setAdminToken(e.target.value)
                }
                required
                data-testid="admin-token-input"
              />
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={isLoading}
              data-testid="admin-start-round-button"
            >
              {isLoading ? 'Starting...' : 'Start New Round'}
            </Button>
          </form>

          {result.message && (
            <div
              className={`mt-4 p-3 rounded-md ${result.success ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'}`}
              data-testid="admin-result-message"
            >
              <p>{result.message}</p>
              {result.round && (
                <p className="font-mono mt-1">Round ID: {result.round.id}</p>
              )}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
