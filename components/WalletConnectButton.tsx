'use client';

import React from 'react';
import { Button } from '@/components/ui/button';
import { truncateAddress } from '@/lib/utils';
import { LogOut, Wallet } from 'lucide-react';
import { usePeraWallet } from '@/contexts/PeraWalletContext'; // Import the hook

// Removed props interface, will use context
// interface WalletConnectButtonProps {
//   activeAddress: string | null;
//   isConnecting: boolean;
//   onConnect: () => Promise<void>;
//   onDisconnect: () => Promise<void>;
//   peraWalletAvailable: boolean;
// }

export function WalletConnectButton() {
  // Use state from context
  const {
    activeAddress,
    isPeraConnecting,
    handlePeraConnect,
    handlePeraDisconnect,
    peraWalletAvailable,
  } = usePeraWallet();

  if (activeAddress) {
    return (
      <div className="flex items-center gap-2">
        <span className="text-sm font-mono bg-muted px-2 py-1 rounded">
          {truncateAddress(activeAddress)}
        </span>
        <Button
          variant="outline"
          size="sm"
          onClick={handlePeraDisconnect}
          title="Disconnect Wallet"
        >
          <LogOut className="h-4 w-4 mr-1 sm:mr-2" />
          <span className="hidden sm:inline">Disconnect</span>
        </Button>
      </div>
    );
  }

  if (!peraWalletAvailable) {
    return (
      <Button
        variant="outline"
        size="sm"
        disabled
        title="Pera Wallet extension not found. Please install it."
      >
        <Wallet className="h-4 w-4 mr-1 sm:mr-2 text-muted-foreground" />
        <span className="text-muted-foreground">Pera Wallet Not Found</span>
      </Button>
    );
  }

  return (
    <Button
      onClick={handlePeraConnect}
      disabled={isPeraConnecting}
      variant="outline"
      size="sm"
    >
      <Wallet className="h-4 w-4 mr-1 sm:mr-2" />
      {isPeraConnecting ? 'Connecting...' : 'Connect Pera Wallet'}
    </Button>
  );
}
