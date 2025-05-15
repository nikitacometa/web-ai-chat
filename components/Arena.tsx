'use client';

import * as React from 'react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Trophy } from 'lucide-react';
import { MomentumBar } from './MomentumBar';
import { TimerDisplay } from './TimerDisplay';

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
      <div
        className="bg-background border border-border rounded-xl p-6 shadow-sm"
        data-testid="arena-container"
      >
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <Trophy className="h-5 w-5 text-amber-500" />
            <span
              className="font-medium text-foreground"
              data-testid="arena-pot-amount"
            >
              Current Pot: {potAmount}
            </span>
          </div>
          <TimerDisplay endTime={endTime} data-testid="arena-timer-display" />
        </div>

        <div className="flex items-center justify-between mb-8">
          <div className="flex flex-col items-center">
            <div className="relative mb-2">
              <Avatar className="h-16 w-16 border-2 border-blue-500">
                <AvatarImage
                  src={leftAvatar.src}
                  alt={leftAvatar.alt}
                  data-testid="arena-left-avatar-img"
                />
                <AvatarFallback>{leftAvatar.fallback}</AvatarFallback>
              </Avatar>
              <span className="absolute bottom-0 right-0 h-3 w-3 rounded-full bg-emerald-500 ring-2 ring-background" />
            </div>
            <span className="text-sm font-medium text-foreground">
              {leftAvatar.alt}
            </span>
          </div>

          <div className="flex-1 mx-4">
            <MomentumBar momentum={momentum} data-testid="arena-momentum-bar" />
          </div>

          <div className="flex flex-col items-center">
            <div className="relative mb-2">
              <Avatar className="h-16 w-16 border-2 border-red-500">
                <AvatarImage
                  src={rightAvatar.src}
                  alt={rightAvatar.alt}
                  data-testid="arena-right-avatar-img"
                />
                <AvatarFallback>{rightAvatar.fallback}</AvatarFallback>
              </Avatar>
              <span className="absolute bottom-0 right-0 h-3 w-3 rounded-full bg-emerald-500 ring-2 ring-background" />
            </div>
            <span className="text-sm font-medium text-foreground">
              {rightAvatar.alt}
            </span>
          </div>
        </div>

        <div
          className="aspect-video bg-muted rounded-lg overflow-hidden flex items-center justify-center"
          data-testid="arena-battle-image-container"
        >
          {battleImageUrl ? (
            <img
              src={battleImageUrl}
              alt="AI-generated battle"
              className="w-full h-full object-cover"
              data-testid="arena-battle-image"
            />
          ) : (
            <div
              className="text-muted-foreground text-sm"
              data-testid="arena-battle-image-fallback"
            >
              AI-generated battle image will appear here
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// New ArenaFallback component
export function ArenaFallback({ message }: { message?: string }) {
  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="bg-background border border-border rounded-xl p-6 shadow-sm animate-pulse">
        <div className="flex items-center justify-between mb-6">
          <div className="h-6 bg-muted rounded w-1/3" />{' '}
          {/* Pot Amount Placeholder */}
          <div className="h-6 bg-muted rounded w-1/4" />{' '}
          {/* Timer Placeholder */}
        </div>
        <div className="flex items-center justify-between mb-8">
          <div className="flex flex-col items-center">
            <div className="h-16 w-16 bg-muted rounded-full mb-2" />{' '}
            {/* Avatar Placeholder */}
            <div className="h-4 bg-muted rounded w-20" />{' '}
            {/* Name Placeholder */}
          </div>
          <div className="flex-1 mx-4 h-4 bg-muted rounded" />{' '}
          {/* Momentum Bar Placeholder */}
          <div className="flex flex-col items-center">
            <div className="h-16 w-16 bg-muted rounded-full mb-2" />{' '}
            {/* Avatar Placeholder */}
            <div className="h-4 bg-muted rounded w-20" />{' '}
            {/* Name Placeholder */}
          </div>
        </div>
        <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
          <p className="text-muted-foreground text-sm">
            {message || 'Loading game arena...'}
          </p>
        </div>
      </div>
    </div>
  );
}
