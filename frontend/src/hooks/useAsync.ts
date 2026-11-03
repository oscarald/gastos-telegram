import { useCallback, useEffect, useRef, useState } from 'react';

export interface EstadoAsync<T> {
  datos: T | null;
  cargando: boolean;
  error: string | null;
  recargar: () => void;
}

/**
 * Carga asincrona reutilizable.
 *
 * `dependencias` indica cuando hay que volver a pedir los datos (filtros,
 * identificadores, etc.). `recargar()` fuerza una nueva peticion.
 */
export function useAsync<T>(
  cargador: () => Promise<T>,
  dependencias: readonly unknown[] = [],
): EstadoAsync<T> {
  const [datos, setDatos] = useState<T | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [version, setVersion] = useState(0);

  const refCargador = useRef(cargador);

  useEffect(() => {
    refCargador.current = cargador;
  });

  useEffect(() => {
    let vigente = true;
    refCargador.current().then(
      (resultado) => {
        if (!vigente) return;
        setDatos(resultado);
        setError(null);
        setCargando(false);
      },
      (fallo: unknown) => {
        if (!vigente) return;
        setError(fallo instanceof Error ? fallo.message : 'Error inesperado');
        setCargando(false);
      },
    );
    return () => {
      vigente = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [version, ...dependencias]);

  const recargar = useCallback(() => {
    setVersion((valor) => valor + 1);
  }, []);

  return { datos, cargando, error, recargar };
}
