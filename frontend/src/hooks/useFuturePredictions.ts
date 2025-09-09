import { useState, useCallback } from 'react';
import { FlotationData, FuturePredictionResponse } from '../types';
import { flotationAPI } from '../services/api';

export const useFuturePredictions = () => {
  const [futurePredictions, setFuturePredictions] = useState<FuturePredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const fetchFuturePredictions = useCallback(async (isInitialLoad = false) => {
    // This function will be called with currentData from the component
    return { futurePredictions, setFuturePredictions, loading, setLoading, refreshing, setRefreshing };
  }, []);

  const fetchPredictions = useCallback(async (currentData: FlotationData | null, isInitialLoad = false) => {
    if (!currentData) return;
    
    // Only show full loading state on initial load
    if (isInitialLoad) {
      setLoading(true);
    } else {
      setRefreshing(true);
    }
    
    try {
      const inputData = {
        Feed_Pb: currentData.Feed_Pb,
        Feed_Zn: currentData.Feed_Zn,
        Pb_Conditioner_KEX_Flowrate: currentData.Pb_Conditioner_KEX_Flowrate,
        Pb_Rougher1_SIPX_Flowrate: currentData.Pb_Rougher1_SIPX_Flowrate,
        Pb_Rougher1_AirFlow: currentData.Pb_Rougher1_AirFlow,
        Pb_Rougher1_Level: currentData.Pb_Rougher1_Level,
      };
      
      const futureData = await flotationAPI.getFuturePredictions(inputData);
      setFuturePredictions(futureData);
    } catch (error) {
      console.error('Failed to fetch future predictions:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  return {
    futurePredictions,
    setFuturePredictions,
    loading,
    refreshing,
    fetchPredictions
  };
};
