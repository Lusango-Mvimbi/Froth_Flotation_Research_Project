import { useState, useCallback } from 'react';
import { FlotationData, FuturePredictionResponse } from '../types';
import { flotationAPI } from '../services/api';

// Global state to coordinate API calls across components
let globalFuturePredictions: FuturePredictionResponse | null = null;
let globalLoading = false;
let globalRefreshing = false;
let lastFetchTime = 0;
let fetchTimeout: NodeJS.Timeout | null = null;
const FETCH_COOLDOWN = 2000; // 2 seconds minimum between API calls

// Global listeners for state changes
const listeners = new Set<() => void>();

const notifyListeners = () => {
  listeners.forEach(listener => listener());
};

export const useFuturePredictions = () => {
  const [, forceUpdate] = useState({});

  // Register this component as a listener
  const updateComponent = useCallback(() => {
    forceUpdate({});
  }, []);

  // Add listener on mount, remove on unmount
  useState(() => {
    listeners.add(updateComponent);
    return () => {
      listeners.delete(updateComponent);
    };
  });

  const fetchPredictions = useCallback(async (currentData: FlotationData | null, isInitialLoad = false) => {
    if (!currentData) return;
    
    const now = Date.now();
    
    // If we're already loading or recently fetched, skip
    if (globalLoading || (now - lastFetchTime < FETCH_COOLDOWN)) {
      return;
    }
    
    // Clear any existing timeout
    if (fetchTimeout) {
      clearTimeout(fetchTimeout);
    }
    
    // Set loading state
    if (isInitialLoad) {
      globalLoading = true;
    } else {
      globalRefreshing = true;
    }
    notifyListeners();
    
    try {
      const inputData = {
        Feed_Pb: currentData.Feed_Pb,
        Pb_Conditioner_KEX_Flowrate: currentData.Pb_Conditioner_KEX_Flowrate,
        Pb_Rougher1_SIPX_Flowrate: currentData.Pb_Rougher1_SIPX_Flowrate,
        Pb_Rougher1_AirFlow: currentData.Pb_Rougher1_AirFlow,
        Pb_Rougher1_Level: currentData.Pb_Rougher1_Level,
      };
      
      const futureData = await flotationAPI.getFuturePredictions(inputData);
      globalFuturePredictions = futureData;
      lastFetchTime = now;
    } catch (error) {
      console.error('Failed to fetch future predictions:', error);
    } finally {
      globalLoading = false;
      globalRefreshing = false;
      notifyListeners();
    }
  }, []);

  return {
    futurePredictions: globalFuturePredictions,
    setFuturePredictions: (data: FuturePredictionResponse | null) => {
      globalFuturePredictions = data;
      notifyListeners();
    },
    loading: globalLoading,
    refreshing: globalRefreshing,
    fetchPredictions
  };
};

