"use client";

import * as React from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Trophy } from "lucide-react";
import { MomentumBar } from "./MomentumBar";
import { TimerDisplay } from "./TimerDisplay";

interface ArenaProps {
  leftAvatar: {
    src: string;
    alt: string;
    fallback: string;
  };
  rightAvatar: {
    src: string;
    alt: string;
    fallback: string;
  };
  momentum: number; // 0-100
  potAmount: string;
  endTime: Date;
  battleImageUrl?: string;
}

export function Arena({
  leftAvatar,
  rightAvatar,
  momentum,
  potAmount,
  endTime,
  battleImageUrl,
}: ArenaProps) {
  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="bg-background border border-border rounded-xl p-6 shadow-sm">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <Trophy className="h-5 w-5 text-amber-500" />
            <span className="font-medium text-foreground">Current Pot: {potAmount}</span>
          </div>
          <TimerDisplay endTime={endTime} />
        </div>
        
        <div className="flex items-center justify-between mb-8">
          <div className="flex flex-col items-center">
            <div className="relative mb-2">
              <Avatar className="h-16 w-16 border-2 border-blue-500">
                <AvatarImage src={leftAvatar.src} alt={leftAvatar.alt} />
                <AvatarFallback>{leftAvatar.fallback}</AvatarFallback>
              </Avatar>
              <span className="absolute bottom-0 right-0 h-3 w-3 rounded-full bg-emerald-500 ring-2 ring-background" />
            </div>
            <span className="text-sm font-medium text-foreground">{leftAvatar.alt}</span>
          </div>
          
          <div className="flex-1 mx-4">
            <MomentumBar momentum={momentum} />
          </div>
          
          <div className="flex flex-col items-center">
            <div className="relative mb-2">
              <Avatar className="h-16 w-16 border-2 border-red-500">
                <AvatarImage src={rightAvatar.src} alt={rightAvatar.alt} />
                <AvatarFallback>{rightAvatar.fallback}</AvatarFallback>
              </Avatar>
              <span className="absolute bottom-0 right-0 h-3 w-3 rounded-full bg-emerald-500 ring-2 ring-background" />
            </div>
            <span className="text-sm font-medium text-foreground">{rightAvatar.alt}</span>
          </div>
        </div>
        
        <div className="aspect-video bg-muted rounded-lg overflow-hidden flex items-center justify-center">
          {battleImageUrl ? (
            <img 
              src={battleImageUrl} 
              alt="AI-generated battle" 
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="text-muted-foreground text-sm">AI-generated battle image will appear here</div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function ArenaExample() {
  return (
    <Arena
      leftAvatar={{
        src: "https://pbs.twimg.com/profile_images/1683325380441128960/yRsRRjGO_400x400.jpg",
        alt: "Elon Musk",
        fallback: "EM",
      }}
      rightAvatar={{
        src: "https://pbs.twimg.com/profile_images/1590968738358079488/IY9Gx6Ok_400x400.jpg",
        alt: "SBF",
        fallback: "SBF",
      }}
      momentum={65}
      potAmount="12,345.67 ALGO"
      endTime={new Date(Date.now() + 3600000)} // 1 hour from now
    />
  );
} 