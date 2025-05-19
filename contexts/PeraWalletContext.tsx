'use client';

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from 'react';
import { PeraWalletConnect } from '@perawallet/connect';

interface IPeraWalletContext {
  peraWallet: PeraWalletConnect | null;
  activeAddress: string | null;
  isPeraConnecting: boolean;
  peraWalletAvailable: boolean;
  handlePeraConnect: () => Promise<void>;
  handlePeraDisconnect: () => Promise<void>;
}

const PeraWalletContext = createContext<IPeraWalletContext | undefined>(
  undefined,
);

export function usePeraWallet() {
  const context = useContext(PeraWalletContext);
  if (context === undefined) {
    throw new Error('usePeraWallet must be used within a PeraWalletProvider');
  }
  return context;
}

interface PeraWalletProviderProps {
  children: ReactNode;
}

export function PeraWalletProvider({ children }: PeraWalletProviderProps) {
  const [peraWallet, setPeraWallet] = useState<PeraWalletConnect | null>(null);
  const [activeAddress, setActiveAddress] = useState<string | null>(null);
  const [isPeraConnecting, setIsPeraConnecting] = useState(false);
  const [peraWalletAvailable, setPeraWalletAvailable] = useState(true); // Assume available

  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        const instance = new PeraWalletConnect({
          shouldShowSignTxnToast: true,
        });
        setPeraWallet(instance);

        instance
          .reconnectSession()
          .then((accounts) => {
            if (accounts.length > 0) {
              setActiveAddress(accounts[0]);
              // Listen for disconnects after session is established
              instance.connector?.on('disconnect', () => {
                setActiveAddress(null);
              });
            }
          })
          .catch((e) => {
            console.warn('Pera reconnect error or no prior session:', e);
            // This can happen if Pera extension is not installed or no session exists
            // If PeraWalletConnect constructor itself fails, it might indicate no extension
          });
      } catch (e) {
        console.error(
          'PeraWalletConnect could not be initialized (likely no extension):',
          e,
        );
        setPeraWalletAvailable(false);
      }
    } else {
      setPeraWalletAvailable(false); // Cannot be available on server
    }
  }, []);

  const handlePeraConnect = useCallback(async () => {
    if (!peraWallet) {
      console.warn('PeraWallet instance not available for connect');
      return;
    }
    setIsPeraConnecting(true);
    try {
      // Ensure any previous connection modal is closed or handled by Pera
      // await peraWallet.disconnect(); // Optional: Force disconnect if issues with stale sessions
      const newAccounts = await peraWallet.connect();
      if (newAccounts.length > 0) {
        setActiveAddress(newAccounts[0]);
        peraWallet.connector?.on('disconnect', () => {
          // Re-attach listener on new session
          setActiveAddress(null);
        });
      }
    } catch (error: any) {
      // Catch as any to inspect properties
      // Check if the error is due to the user closing the connection modal
      if (error?.data?.type === 'CONNECT_MODAL_CLOSED') {
        console.info('Pera Wallet connect modal was closed by the user.');
      } else if (
        error instanceof Error &&
        error.message.includes('Connect modal is already open')
      ) {
        // Modal is already open, do nothing
        console.info('Pera Wallet connect modal is already open.');
      } else if (
        error instanceof Error &&
        error.message.includes('PopupBlocked')
      ) {
        console.error('Pera Wallet popup was blocked. Please allow popups.');
        // Potentially set a state here to show a message to the user
      } else {
        console.error('Error connecting to Pera Wallet:', error);
      }
    } finally {
      setIsPeraConnecting(false);
    }
  }, [peraWallet]);

  const handlePeraDisconnect = useCallback(async () => {
    if (!peraWallet) return;
    try {
      await peraWallet.disconnect();
    } catch (error) {
      console.error('Error disconnecting Pera Wallet:', error);
    }
    setActiveAddress(null); // Clear active address on manual disconnect
  }, [peraWallet]);

  const value = {
    peraWallet,
    activeAddress,
    isPeraConnecting,
    peraWalletAvailable,
    handlePeraConnect,
    handlePeraDisconnect,
  };

  return (
    <PeraWalletContext.Provider value={value}>
      {children}
    </PeraWalletContext.Provider>
  );
}
