/**
 * Nova Trader - Bento Grid Layout System
 * Multi-sized cards for data portability and spatial organization
 */
import React from 'react';
import { Box, useTheme } from '@mui/joy';

interface BentoGridProps {
  children: React.ReactNode;
  columns?: number;
  gap?: number;
}

interface BentoItemProps {
  children: React.ReactNode;
  colSpan?: number;
  rowSpan?: number;
  minHeight?: string | number;
}

export function BentoGrid({
  children,
  columns = 12,
  gap = 2
}: BentoGridProps) {
  const theme = useTheme();

  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: `repeat(${columns}, 1fr)`,
        gap: theme.spacing(gap),
        width: '100%',
        // Visible grid for spatial orientation
        position: 'relative',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage: `
            linear-gradient(to right, ${theme.palette.divider} 1px, transparent 1px),
            linear-gradient(to bottom, ${theme.palette.divider} 1px, transparent 1px)
          `,
          backgroundSize: `calc(100% / ${columns}) ${theme.spacing(gap)}`,
          opacity: 0.1,
          pointerEvents: 'none',
          zIndex: 0,
        },
      }}
    >
      {children}
    </Box>
  );
}

export function BentoItem({
  children,
  colSpan = 1,
  rowSpan = 1,
  minHeight = '200px'
}: BentoItemProps) {
  return (
    <Box
      sx={{
        gridColumn: `span ${colSpan}`,
        gridRow: `span ${rowSpan}`,
        minHeight,
        position: 'relative',
        zIndex: 1,
      }}
    >
      {children}
    </Box>
  );
}