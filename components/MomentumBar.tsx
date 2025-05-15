"use client";

import { motion } from "framer-motion";

interface MomentumBarProps {
  momentum: number; // 0-100
  leftColor?: string;
  rightColor?: string;
  indicatorColor?: string;
  height?: string;
  showPercentages?: boolean;
  className?: string;
}

export function MomentumBar({
  momentum,
  leftColor = "bg-blue-500",
  rightColor = "bg-red-500",
  indicatorColor = "bg-white",
  height = "h-4",
  showPercentages = true,
  className = "",
}: MomentumBarProps) {
  // Ensure momentum is within 0-100 range
  const clampedMomentum = Math.max(0, Math.min(100, momentum));
  
  // Calculate momentum percentages
  const leftPercent = 100 - clampedMomentum;
  const rightPercent = clampedMomentum;
  
  // Determine colors based on proximity to edges
  const getLeftColorClass = () => {
    if (leftPercent <= 10) return "bg-blue-700"; // Near edge - deeper blue
    if (leftPercent <= 30) return "bg-blue-600"; // Getting closer - brighter blue
    return leftColor;
  };
  
  const getRightColorClass = () => {
    if (rightPercent <= 10) return "bg-red-700"; // Near edge - deeper red
    if (rightPercent <= 30) return "bg-red-600"; // Getting closer - brighter red
    return rightColor;
  };
  
  return (
    <div className={`w-full ${className}`}>
      <div className={`relative ${height} bg-muted rounded-full overflow-hidden`}>
        <motion.div 
          className={`absolute top-0 left-0 h-full ${getLeftColorClass()}`}
          initial={{ width: `${leftPercent}%` }}
          animate={{ width: `${leftPercent}%` }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
        />
        <motion.div 
          className={`absolute top-0 right-0 h-full ${getRightColorClass()}`}
          initial={{ width: `${rightPercent}%` }}
          animate={{ width: `${rightPercent}%` }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
        />
        <motion.div 
          className={`absolute top-0 h-full w-1 ${indicatorColor}`}
          style={{ left: `${leftPercent}%` }}
          initial={{ x: "-50%" }}
          animate={{ x: "-50%" }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
        />
      </div>
      
      {showPercentages && (
        <div className="flex justify-between mt-1 text-xs text-muted-foreground">
          <span>{leftPercent}%</span>
          <span>{rightPercent}%</span>
        </div>
      )}
    </div>
  );
} 