'use client';

import useSWR from 'swr';
import { useCallback, useMemo } from 'react';

export interface UIVMConnection {
  deploymentId: string;
  environmentType: string;
  connectionDetails: any;
  vncUrl: string;
  isVisible: boolean;
  status: 'connecting' | 'connected' | 'disconnected';
  boundingBox: {
    top: number;
    left: number;
    width: number;
    height: number;
  };
}

export const initialVMConnectionData: UIVMConnection = {
  deploymentId: '',
  environmentType: '',
  connectionDetails: null,
  vncUrl: '',
  isVisible: false,
  status: 'disconnected',
  boundingBox: {
    top: 0,
    left: 0,
    width: 0,
    height: 0,
  },
};

type Selector<T> = (state: UIVMConnection) => T;

export function useVMConnectionSelector<Selected>(
  selector: Selector<Selected>,
) {
  const { data: localVMConnection } = useSWR<UIVMConnection>(
    'vm-connection',
    null,
    {
      fallbackData: initialVMConnectionData,
    },
  );

  const selectedValue = useMemo(() => {
    if (!localVMConnection) return selector(initialVMConnectionData);
    return selector(localVMConnection);
  }, [localVMConnection, selector]);

  return selectedValue;
}

export function useVMConnection() {
  const { data: localVMConnection, mutate: setLocalVMConnection } =
    useSWR<UIVMConnection>('vm-connection', null, {
      fallbackData: initialVMConnectionData,
    });

  const vmConnection = useMemo(() => {
    if (!localVMConnection) return initialVMConnectionData;
    return localVMConnection;
  }, [localVMConnection]);

  const setVMConnection = useCallback(
    (
      updaterFn:
        | UIVMConnection
        | ((currentVMConnection: UIVMConnection) => UIVMConnection),
    ) => {
      setLocalVMConnection((currentVMConnection) => {
        const vmConnectionToUpdate =
          currentVMConnection || initialVMConnectionData;

        if (typeof updaterFn === 'function') {
          return updaterFn(vmConnectionToUpdate);
        }

        return updaterFn;
      });
    },
    [setLocalVMConnection],
  );

  return useMemo(
    () => ({
      vmConnection,
      setVMConnection,
    }),
    [vmConnection, setVMConnection],
  );
}
