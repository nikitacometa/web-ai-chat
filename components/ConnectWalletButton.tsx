'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { PeraWalletConnect } from '@perawallet/connect';
import { Button } from '@/components/ui/button';
import { truncateAddress } from '@/lib/utils';

let peraWallet: PeraWalletConnect | null = null;
if (typeof window !== 'undefined') {
  peraWallet = new PeraWalletConnect({
    shouldShowSignTxnToast: true,
  });
}

export function ConnectWalletButton() {
  const [activeAddress, setActiveAddress] = useState<string | null>(null);

  const connectWallet = useCallback(async () => {
    if (!peraWallet) return;
    try {
      const accounts = await peraWallet.connect();
      if (accounts && accounts.length > 0) {
        setActiveAddress(accounts[0]);
      } else {
        setActiveAddress(null);
      }
    } catch (error) {
      if (
        error instanceof Error &&
        error.message.toLowerCase().includes('modal closed')
      ) {
        console.log('Pera Wallet connection modal closed by user.');
      } else {
        console.error('Error connecting to Pera Wallet:', error);
      }
      setActiveAddress(null);
    }
  }, []);

  const disconnectWallet = useCallback(async () => {
    if (!peraWallet) return;
    try {
      await peraWallet.disconnect();
    } catch (e) {
      console.error('Error disconnecting Pera Wallet:', e);
    } finally {
      setActiveAddress(null);
    }
  }, []);

  useEffect(() => {
    if (!peraWallet) return;
    peraWallet
      .reconnectSession()
      .then((accounts) => {
        if (accounts && accounts.length > 0) {
          setActiveAddress(accounts[0]);
        }
      })
      .catch((error) => {
        if (
          error instanceof Error &&
          (error.message.toLowerCase().includes('no session found') ||
            error.message.toLowerCase().includes('no accounts found'))
        ) {
          console.log(
            'No previous Pera Wallet session or accounts found to reconnect.',
          );
        } else {
          console.error('Error reconnecting Pera Wallet session:', error);
        }
      });

    const handlePeraDisconnect = () => {
      setActiveAddress(null);
    };

    const connector = peraWallet.connector;
    if (connector) {
      connector.on('disconnect', handlePeraDisconnect);
      return () => {
        // Attempt to remove the specific listener if possible, otherwise try a generic off.
        if (typeof connector.off === 'function') {
          try {
            // Try with two arguments first, as it's standard for specific listener removal
            (connector as any).off('disconnect', handlePeraDisconnect);
          } catch (e) {
            // If two args fail, try with one arg (less common for specific removal, but linter complained)
            try {
              (connector as any).off('disconnect');
            } catch (e2) {
              console.warn(
                "Failed to remove 'disconnect' listener via off() method.",
                e2,
              );
            }
          }
        } else if (typeof (connector as any).removeListener === 'function') {
          (connector as any).removeListener('disconnect', handlePeraDisconnect);
        } else {
          console.warn(
            'Connector does not have a recognized method to remove event listeners (off/removeListener).',
          );
        }
      };
    }
  }, []);

  if (activeAddress) {
    return (
      <div className="flex items-center gap-2">
        <span className="text-sm">Pera: {truncateAddress(activeAddress)}</span>
        <Button onClick={disconnectWallet} variant="outline" size="sm">
          Disconnect
        </Button>
      </div>
    );
  }

  return (
    <Button onClick={connectWallet} variant="default" size="sm">
      Connect Pera Wallet
    </Button>
  );
}
