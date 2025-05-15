'use client';

import * as React from 'react';
import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Sword,
  Coins,
  Rocket,
  Bolt,
  AlertCircle,
  CheckCircle2,
} from 'lucide-react';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { BetRequest } from '@/lib/types';

interface BetDrawerProps {
  roundId: number;
  walletAddress: string;
  leftSideLabel: string;
  rightSideLabel: string;
  minimumBet: number;
  onPlaceBet?: (betData: BetRequest) => Promise<void>;
  className?: string;
}

export function BetDrawer({
  roundId,
  walletAddress,
  leftSideLabel,
  rightSideLabel,
  minimumBet,
  onPlaceBet,
  className = '',
}: BetDrawerProps) {
  const [selectedSide, setSelectedSide] = useState<'left' | 'right' | ''>('');
  const [spellText, setSpellText] = useState<string>('');
  const [betAmount, setBetAmount] = useState<string>(minimumBet.toString());
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [wordCount, setWordCount] = useState(0);
  const [feedbackMessage, setFeedbackMessage] = useState<{
    type: 'success' | 'error';
    message: string;
  } | null>(null);

  const handleSpellChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const text = e.target.value;
    setSpellText(text);
    const words = text
      .trim()
      .split(/\s+/)
      .filter((word) => word.length > 0);
    setWordCount(words.length);
  };

  const handleAmountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    if (/^\d*\.?\d*$/.test(value)) {
      setBetAmount(value);
    }
  };

  const handleSubmit = async () => {
    if (!selectedSide || !spellText.trim() || isSubmitting || !betAmount)
      return;

    const amountNumber = Number.parseFloat(betAmount);
    if (Number.isNaN(amountNumber) || amountNumber < minimumBet) {
      setFeedbackMessage({
        type: 'error',
        message: `Amount must be at least ${minimumBet}.`,
      });
      return;
    }
    if (wordCount > 10) {
      setFeedbackMessage({ type: 'error', message: 'Spell exceeds 10 words.' });
      return;
    }

    setIsSubmitting(true);
    setFeedbackMessage(null);

    const betData: BetRequest = {
      round_id: roundId,
      side: selectedSide,
      amount: amountNumber,
      spell: spellText.trim(),
      wallet_address: walletAddress,
    };

    try {
      await onPlaceBet?.(betData);
      setFeedbackMessage({
        type: 'success',
        message: 'Bet placed successfully!',
      });
    } catch (error) {
      console.error('Error placing bet:', error);
      let errorMessage = 'Failed to place bet. Please try again.';
      if (error instanceof Error) {
        // Attempt to parse if the error.message is a JSON string from the API
        try {
          const parsedError = JSON.parse(error.message);
          if (parsedError?.detail) {
            errorMessage =
              typeof parsedError.detail === 'string'
                ? parsedError.detail
                : JSON.stringify(parsedError.detail);
          } else {
            errorMessage = error.message; // Fallback to original error message if no detail
          }
        } catch (parseError) {
          // If parsing fails, it's likely not a JSON string from our API, use the raw message
          errorMessage = error.message;
        }
      } else if (typeof error === 'string') {
        errorMessage = error;
      }
      setFeedbackMessage({ type: 'error', message: errorMessage });
    } finally {
      setIsSubmitting(false);
    }
  };

  const getWordCountColor = () => {
    if (wordCount > 10) return 'text-red-500';
    if (wordCount >= 7) return 'text-amber-500';
    return 'text-muted-foreground';
  };

  return (
    <Card className={`overflow-hidden ${className}`}>
      <CardHeader className="bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-pink-500/10 pb-4">
        <CardTitle className="flex items-center gap-2">
          <Sword className="h-5 w-5 text-purple-500" />
          <span>Place Your Bet</span>
        </CardTitle>
        <CardDescription>
          Choose a side, cast your spell, and fuel the battle
        </CardDescription>
      </CardHeader>

      <CardContent className="pt-6 space-y-4">
        <div className="space-y-2">
          <Label>Choose Your Champion</Label>
          <RadioGroup
            value={selectedSide}
            onValueChange={(value) =>
              setSelectedSide(value as 'left' | 'right')
            }
            className="flex flex-col sm:flex-row gap-2"
          >
            <div className="flex-1">
              <RadioGroupItem value="left" id="left" className="peer sr-only" />
              <Label
                htmlFor="left"
                className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-transparent p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-blue-500 peer-data-[state=checked]:bg-blue-500/10 [&:has([data-state=checked])]:border-blue-500 cursor-pointer"
              >
                <Bolt className="mb-2 h-6 w-6 text-blue-500" />
                <span className="font-semibold">{leftSideLabel}</span>
              </Label>
            </div>

            <span className="text-center self-center text-muted-foreground hidden sm:inline">
              VS
            </span>

            <div className="flex-1">
              <RadioGroupItem
                value="right"
                id="right"
                className="peer sr-only"
              />
              <Label
                htmlFor="right"
                className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-transparent p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-red-500 peer-data-[state=checked]:bg-red-500/10 [&:has([data-state=checked])]:border-red-500 cursor-pointer"
              >
                <Bolt className="mb-2 h-6 w-6 text-red-500" />
                <span className="font-semibold">{rightSideLabel}</span>
              </Label>
            </div>
          </RadioGroup>
        </div>

        <div className="space-y-2">
          <Label htmlFor="betAmount">Bet Amount (Min: {minimumBet} ALGO)</Label>
          <Input
            id="betAmount"
            type="text"
            inputMode="decimal"
            value={betAmount}
            onChange={handleAmountChange}
            placeholder={`e.g., ${minimumBet}`}
            className="bg-background/50 border-muted focus-visible:border-purple-500/50 focus-visible:ring-purple-500/20"
          />
        </div>

        <div className="space-y-2">
          <div className="flex justify-between">
            <Label htmlFor="spell">Cast Your Spell (10 words max)</Label>
            <span className={`text-xs ${getWordCountColor()}`}>
              {wordCount}/10 words
            </span>
          </div>
          <div className="relative">
            <Textarea
              id="spell"
              placeholder="Enter a 10-word spell to influence the battle..."
              value={spellText}
              onChange={handleSpellChange}
              className="min-h-20 resize-none bg-background/50 border-muted focus-visible:border-purple-500/50 focus-visible:ring-purple-500/20"
            />
            {wordCount > 10 && (
              <div className="absolute top-0 right-0 bg-red-500/10 text-red-500 text-xs px-2 py-1 rounded-bl-md">
                Too many words!
              </div>
            )}
          </div>
        </div>

        {feedbackMessage && (
          <div
            className={`flex items-center gap-2 p-3 rounded-md text-sm ${feedbackMessage.type === 'success' ? 'bg-green-500/10 text-green-700' : 'bg-red-500/10 text-red-700'}`}
          >
            {feedbackMessage.type === 'success' ? (
              <CheckCircle2 className="h-5 w-5" />
            ) : (
              <AlertCircle className="h-5 w-5" />
            )}
            <p>{feedbackMessage.message}</p>
          </div>
        )}
      </CardContent>

      <CardFooter className="flex justify-center pb-6 pt-2">
        <Button
          onClick={handleSubmit}
          disabled={
            !selectedSide ||
            !spellText.trim() ||
            wordCount > 10 ||
            isSubmitting ||
            !betAmount ||
            Number.parseFloat(betAmount) < minimumBet
          }
          className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold py-2 shadow-lg transition-all duration-200 hover:shadow-purple-500/20"
          size="lg"
        >
          <motion.div
            className="flex items-center justify-center gap-2"
            whileTap={{ scale: 0.97 }}
            animate={
              isSubmitting
                ? {
                    opacity: [1, 0.7, 1],
                    transition: {
                      repeat: Number.POSITIVE_INFINITY,
                      duration: 1,
                    },
                  }
                : {}
            }
          >
            <Rocket className="h-5 w-5" />
            {isSubmitting ? 'Betting...' : 'WRECK THEM!'}
          </motion.div>
        </Button>
      </CardFooter>
    </Card>
  );
}
