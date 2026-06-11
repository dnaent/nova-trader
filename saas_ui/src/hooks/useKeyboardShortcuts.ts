/**
 * Nova Trader - Keyboard Trading Shortcuts Hook
 * Ultra-fast keyboard shortcuts for professional trading
 */
import { useEffect, useCallback } from 'react';

interface KeyboardShortcuts {
  onQuickBuy?: (symbol?: string) => void;
  onQuickSell?: (symbol?: string) => void;
  onEmergencyStop?: () => void;
  onFocusSymbol?: () => void;
  onToggleAI?: () => void;
  onSwitchTab?: (tab: string) => void;
}

export function useKeyboardShortcuts({
  onQuickBuy,
  onQuickSell,
  onEmergencyStop,
  onFocusSymbol,
  onToggleAI,
  onSwitchTab
}: KeyboardShortcuts) {

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    // Ignore shortcuts when typing in inputs
    if (
      event.target instanceof HTMLInputElement ||
      event.target instanceof HTMLTextAreaElement ||
      event.target instanceof HTMLSelectElement
    ) {
      return;
    }

    const { key, ctrlKey, altKey, shiftKey } = event;

    // F1-F12 Function Keys for Ultra-Fast Trading
    switch (key) {
      case 'F1':
        event.preventDefault();
        onSwitchTab?.('overview');
        break;
      case 'F2':
        event.preventDefault();
        onSwitchTab?.('orders');
        break;
      case 'F3':
        event.preventDefault();
        onSwitchTab?.('risk');
        break;
      case 'F4':
        event.preventDefault();
        onSwitchTab?.('brokers');
        break;
      case 'F5':
        event.preventDefault();
        onSwitchTab?.('latency');
        break;
      case 'F12':
        event.preventDefault();
        onEmergencyStop?.();
        break;
    }

    // Ctrl + Key Combinations for Trading Actions
    if (ctrlKey) {
      switch (key.toLowerCase()) {
        case 'b':
          event.preventDefault();
          onQuickBuy?.();
          break;
        case 's':
          event.preventDefault();
          onQuickSell?.();
          break;
        case 'e':
          event.preventDefault();
          onEmergencyStop?.();
          break;
        case 'f':
          event.preventDefault();
          onFocusSymbol?.();
          break;
        case 'a':
          event.preventDefault();
          onToggleAI?.();
          break;
      }
    }

    // Alt + Key for Quick Navigation
    if (altKey) {
      switch (key) {
        case '1':
          event.preventDefault();
          onSwitchTab?.('overview');
          break;
        case '2':
          event.preventDefault();
          onSwitchTab?.('orders');
          break;
        case '3':
          event.preventDefault();
          onSwitchTab?.('risk');
          break;
        case '4':
          event.preventDefault();
          onSwitchTab?.('training');
          break;
        case '5':
          event.preventDefault();
          onSwitchTab?.('analytics');
          break;
        case '6':
          event.preventDefault();
          onSwitchTab?.('brokers');
          break;
        case '7':
          event.preventDefault();
          onSwitchTab?.('latency');
          break;
        case '8':
          event.preventDefault();
          onSwitchTab?.('engine');
          break;
      }
    }

    // Emergency Keys (no modifiers required)
    switch (key) {
      case 'Escape':
        event.preventDefault();
        onEmergencyStop?.();
        break;
    }

  }, [onQuickBuy, onQuickSell, onEmergencyStop, onFocusSymbol, onToggleAI, onSwitchTab]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);

  return {
    shortcuts: {
      'F1': 'Overview Dashboard',
      'F2': 'Order Management',
      'F3': 'Risk Monitor',
      'F4': 'AI Training',
      'F5': 'Analytics',
      'F12': 'Emergency Stop',
      'Ctrl+B': 'Quick Buy',
      'Ctrl+S': 'Quick Sell',
      'Ctrl+E': 'Emergency Stop',
      'Ctrl+F': 'Focus Symbol Input',
      'Ctrl+A': 'Toggle AI Copilot',
      'Alt+1-8': 'Switch Tabs',
      'Escape': 'Emergency Stop'
    }
  };
}