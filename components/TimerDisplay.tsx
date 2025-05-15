"use client";

import * as React from "react";
import { Clock } from "lucide-react";

interface TimerDisplayProps {
  endTime: Date;
  className?: string;
  iconSize?: number;
  showIcon?: boolean;
}

export function TimerDisplay({
  endTime,
  className = "",
  iconSize = 4,
  showIcon = true,
}: TimerDisplayProps) {
  const [timeLeft, setTimeLeft] = React.useState<{
    hours: number;
    minutes: number;
    seconds: number;
  }>({
    hours: 0,
    minutes: 0,
    seconds: 0,
  });

  React.useEffect(() => {
    const calculateTimeLeft = () => {
      const difference = endTime.getTime() - new Date().getTime();
      
      if (difference <= 0) {
        return {
          hours: 0,
          minutes: 0,
          seconds: 0,
        };
      }
      
      return {
        hours: Math.floor((difference / (1000 * 60 * 60)) % 24),
        minutes: Math.floor((difference / 1000 / 60) % 60),
        seconds: Math.floor((difference / 1000) % 60),
      };
    };

    setTimeLeft(calculateTimeLeft());
    
    const timer = setInterval(() => {
      setTimeLeft(calculateTimeLeft());
    }, 1000);

    return () => clearInterval(timer);
  }, [endTime]);

  const formatTime = (value: number) => {
    return value.toString().padStart(2, "0");
  };

  // Visual indicators based on time left
  const getTimeClass = () => {
    const totalSeconds = timeLeft.hours * 3600 + timeLeft.minutes * 60 + timeLeft.seconds;
    
    if (totalSeconds < 60) return "text-red-500"; // Less than 1 minute
    if (totalSeconds < 300) return "text-amber-500"; // Less than 5 minutes
    return "text-foreground";
  };

  return (
    <div className={`flex items-center gap-2 ${getTimeClass()} ${className}`}>
      {showIcon && <Clock className={`h-${iconSize} w-${iconSize} text-muted-foreground`} />}
      <div className="font-mono text-sm">
        {formatTime(timeLeft.hours)}:{formatTime(timeLeft.minutes)}:{formatTime(timeLeft.seconds)}
      </div>
    </div>
  );
} 