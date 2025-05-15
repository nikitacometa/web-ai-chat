"use client";

import * as React from "react";
import { useState } from "react";
import { motion } from "framer-motion";
import { Sword, Coins, Rocket, Bolt } from "lucide-react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";

interface BetDrawerProps {
  leftSideLabel: string;
  rightSideLabel: string;
  minimumBet: number;
  onPlaceBet?: (side: string, spell: string) => void;
  className?: string;
}

export function BetDrawer({
  leftSideLabel,
  rightSideLabel,
  minimumBet,
  onPlaceBet,
  className = "",
}: BetDrawerProps) {
  const [selectedSide, setSelectedSide] = useState<string>("");
  const [spellText, setSpellText] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [wordCount, setWordCount] = useState(0);

  const handleSpellChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const text = e.target.value;
    setSpellText(text);
    // Count words (split by spaces and filter out empty strings)
    const words = text.trim().split(/\s+/).filter(word => word.length > 0);
    setWordCount(words.length);
  };

  const handleSubmit = () => {
    if (!selectedSide || !spellText.trim() || isSubmitting) return;
    
    setIsSubmitting(true);
    
    // Simulate transaction processing
    setTimeout(() => {
      onPlaceBet?.(selectedSide, spellText.trim());
      setIsSubmitting(false);
      // Optional: Reset form
      // setSelectedSide("");
      // setSpellText("");
    }, 1500);
  };

  // Word count indicator color
  const getWordCountColor = () => {
    if (wordCount > 10) return "text-red-500";
    if (wordCount >= 7) return "text-amber-500";
    return "text-muted-foreground";
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
        {/* Side Selection */}
        <div className="space-y-2">
          <Label>Choose Your Champion</Label>
          <RadioGroup 
            value={selectedSide} 
            onValueChange={setSelectedSide}
            className="flex flex-col sm:flex-row gap-2"
          >
            <div className="flex-1">
              <RadioGroupItem 
                value="left" 
                id="left" 
                className="peer sr-only" 
              />
              <Label
                htmlFor="left"
                className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-transparent p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-blue-500 peer-data-[state=checked]:bg-blue-500/10 [&:has([data-state=checked])]:border-blue-500 cursor-pointer"
              >
                <Bolt className="mb-2 h-6 w-6 text-blue-500" />
                <span className="font-semibold">{leftSideLabel}</span>
              </Label>
            </div>
            
            <span className="text-center self-center text-muted-foreground hidden sm:inline">VS</span>
            
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
        
        {/* Spell Entry */}
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
        
        {/* Minimum Bet Information */}
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Coins className="h-5 w-5 text-amber-500" />
            <span className="text-sm font-medium">Minimum Bet:</span>
          </div>
          <div className="font-mono font-bold text-right">
            {minimumBet.toFixed(2)} <span className="text-xs font-normal">ALGO</span>
          </div>
        </div>
      </CardContent>
      
      <CardFooter className="flex justify-center pb-6 pt-2">
        <Button 
          onClick={handleSubmit}
          disabled={!selectedSide || !spellText.trim() || wordCount > 10 || isSubmitting}
          className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold py-2 shadow-lg transition-all duration-200 hover:shadow-purple-500/20"
          size="lg"
        >
          <motion.div 
            className="flex items-center justify-center gap-2"
            whileTap={{ scale: 0.97 }}
            animate={isSubmitting ? { 
              opacity: [1, 0.7, 1], 
              transition: { 
                repeat: Infinity, 
                duration: 1 
              } 
            } : {}}
          >
            <Rocket className="h-5 w-5" />
            {isSubmitting ? "Betting..." : "WRECK THEM!"}
          </motion.div>
        </Button>
      </CardFooter>
    </Card>
  );
}

export default function BetDrawerExample() {
  return (
    <BetDrawer
      leftSideLabel="Elon Musk"
      rightSideLabel="SBF"
      minimumBet={0.1}
    />
  );
} 