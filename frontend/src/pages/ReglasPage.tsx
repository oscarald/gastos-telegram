import { useState } from 'react';
import Modal from '../components/ui/Modal';
import Button from '../components/ui/Button';
import { Field, Input, Select } from '../components/ui/Field';
import { Alerta, Badge, Card, EstadoVacio } from '../components/ui/Card';
import { IconoBorrar, IconoEditar, IconoMas } from '../components/ui/Iconos';
import { Cargando } from '../components/ui/Modal';
import { useAsync } from '../hooks/useAsync';
import { categoriasService, reglasService } from '../services';
import type { Categoria, Regla, ReglaInput } from '../types';

interface Props {
  regla: Regla | null;
  categorias: Categoria[];
  onCerrar: () => void;
  onGuardar: (payload: ReglaInput) => Promise<void>;
}

function ReglaFormModal({ regla, categorias, onCerrar, onGuardar }: Props) {
  const [palabraClave, setPalabraClave] = useState(() => regla?.palabra_clave ?? '');
  const [categoriaId, setCategoriaId] = useState(() => (regla ? String(regla.categoria_id) : ''));
  const [prioridad, setPrioridad] = useState(() => String(regla?.prioridad ?? 0));
  const [activa, setActiva] = useState(() => regla?.activa ?? true);
  const [error, setError] = useState<string | null>(null);
  const [guardando, setGuardando] = useState(false);

  const enviar = async (evento: React.FormEvent) => {
    evento.preventDefault();
    setError(null);
    if (!palabraClave.trim()) {
      setError('La palabra clave es obligatoria.');
      return;
    }
    if (!categoriaId) {
      setError('Selecciona la categoria que se asignara.');
      return;
    }
    setGuardando(true);
    try {
      await onGuardar({
        palabra_clave: palabraClave.trim(),
        categoria_id: Number(categoriaId),
        prioridad: Number(prioridad) || 0,
        activa,
      });
      onCerrar();
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : 'No se pudo guardar la regla');
    } finally {
      setGuardando(false);
    }
  };

  const activas = categorias.filter((categoria) => categoria.activa);

  return (
    <Modal
      abierto
      titulo={regla ? 'Editar regla' : 'Nueva regla'}
      descripcion="La palabra clave se busca dentro de la descripcion del gasto."
      onCerrar={onCerrar}
      pie={
        <>
          <Button variante="secundario" onClick={onCerrar}>
            Cancelar
          </Button>
          <Button type="submit" form="form-regla" cargando={guardando}>
            Guardar
          </Button>
        </>
      }
    >
      <form id="form-regla" onSubmit={enviar} className="space-y-4">
        {error ? <Alerta mensaje={error} /> : null}

        <Field label="Palabra clave" htmlFor="palabra-clave">
          <Input
            id="palabra-clave"
            value={palabraClave}
            onChange={(evento) => setPalabraClave(evento.target.value)}
            placeholder="almuerzo"
            maxLength={100}
            required
          />
        </Field>

        <Field label="Categoria asignada" htmlFor="categoria-regla">
          <Select
            id="categoria-regla"
            value={categoriaId}
            onChange={(evento) => setCategoriaId(evento.target.value)}
            required
          >
            <option value="">Selecciona una categoria</option>
            {activas.map((categoria) => (
              <option key={categoria.id} value={categoria.id}>
                {categoria.nombre}
              </option>
            ))}
          </Select>
        </Field>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field
            label="Prioridad"
            htmlFor="prioridad"
            hint="A mayor numero, mayor precedencia frente a otras coincidencias."
          >
            <Input
              id="prioridad"
              type="number"
              value={prioridad}
              onChange={(evento) => setPrioridad(evento.target.value)}
            />
          </Field>

          <Field label="Estado" htmlFor="activa-regla">
            <Select
              id="activa-regla"
              value={activa ? '1' : '0'}
              onChange={(evento) => setActiva(evento.target.value === '1')}
            >
              <option value="1">Activa</option>
              <option value="0">Desactivada</option>
            </Select>
          </Field>
        </div>
      </form>
    </Modal>
  );
}

export default function ReglasPage() {
  const { datos: reglas, cargando, error, recargar } = useAsync(
    async () => (await reglasService.listar()).data,
    [],
  );
  const { datos: categorias } = useAsync(
    async () => (await categoriasService.listar()).data,
    [],
  );

  const [modalAbierto, setModalAbierto] = useState(false);
  const [reglaEditando, setReglaEditando] = useState<Regla | null>(null);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [errorAccion, setErrorAccion] = useState<string | null>(null);

  const guardar = async (payload: ReglaInput) => {
    setErrorAccion(null);
    try {
      if (reglaEditando) {
        await reglasService.actualizar(reglaEditando.id, payload);
        setMensaje('Regla actualizada');
      } else {
        await reglasService.crear(payload);
        setMensaje('Regla creada');
      }
      recargar();
    } catch (fallo) {
      setErrorAccion(fallo instanceof Error ? fallo.message : 'No se pudo guardar la regla');
      throw fallo;
    }
  };

  const alternarActiva = async (regla: Regla) => {
    try {
      await reglasService.actualizar(regla.id, { activa: !regla.activa });
      recargar();
    } catch (fallo) {
      setErrorAccion(fallo instanceof Error ? fallo.message : 'No se pudo actualizar la regla');
    }
  };

  const eliminar = async (regla: Regla) => {
    const confirmado = window.confirm(`Eliminar la regla "${regla.palabra_clave}"?`);
    if (!confirmado) return;
    try {
      await reglasService.eliminar(regla.id);
      setMensaje('Regla eliminada');
      recargar();
    } catch (fallo) {
      setErrorAccion(fallo instanceof Error ? fallo.message : 'No se pudo eliminar la regla');
    }
  };

  return (
    <div className="space-y-5">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-semibold text-zinc-50">Reglas de categorizacion</h1>
          <p className="text-sm text-zinc-500">
            El motor busca estas palabras dentro de la descripcion y aplica la categoria con mayor
            prioridad.
          </p>
        </div>
        <Button
          onClick={() => {
            setReglaEditando(null);
            setModalAbierto(true);
          }}
          icono={<IconoMas />}
        >
          Nueva regla
        </Button>
      </header>

      {error ? <Alerta mensaje={error} /> : null}
      {errorAccion ? <Alerta mensaje={errorAccion} onCerrar={() => setErrorAccion(null)} /> : null}
      {mensaje ? <Alerta mensaje={mensaje} tipo="exito" onCerrar={() => setMensaje(null)} /> : null}

      <Card>
        {cargando && !reglas ? (
          <Cargando texto="Cargando reglas..." />
        ) : reglas && reglas.length > 0 ? (
          <ul className="divide-y divide-surface-800/70">
            {reglas.map((regla) => (
              <li key={regla.id} className="flex flex-wrap items-center gap-3 py-3 first:pt-0 last:pb-0">
                <code className="rounded-lg bg-surface-950 px-2.5 py-1 text-sm text-emerald-300">
                  {regla.palabra_clave}
                </code>
                <span className="text-zinc-600">-&gt;</span>
                <Badge color={regla.categoria_color}>{regla.categoria}</Badge>
                <span className="rounded-full bg-surface-800 px-2 py-0.5 text-xs text-zinc-400">
                  prioridad {regla.prioridad}
                </span>
                {!regla.activa ? (
                  <span className="rounded-full bg-surface-800 px-2 py-0.5 text-[10px] uppercase text-zinc-500">
                    inactiva
                  </span>
                ) : null}
                <div className="ml-auto flex gap-1">
                  <Button variante="secundario" tamano="sm" onClick={() => alternarActiva(regla)}>
                    {regla.activa ? 'Desactivar' : 'Activar'}
                  </Button>
                  <button
                    type="button"
                    onClick={() => {
                      setReglaEditando(regla);
                      setModalAbierto(true);
                    }}
                    className="rounded-lg p-2 text-zinc-400 transition hover:bg-surface-700 hover:text-zinc-100"
                    aria-label={`Editar ${regla.palabra_clave}`}
                  >
                    <IconoEditar />
                  </button>
                  <button
                    type="button"
                    onClick={() => eliminar(regla)}
                    className="rounded-lg p-2 text-zinc-400 transition hover:bg-red-500/20 hover:text-red-300"
                    aria-label={`Eliminar ${regla.palabra_clave}`}
                  >
                    <IconoBorrar />
                  </button>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <EstadoVacio
            titulo="Todavia no hay reglas"
            descripcion="Crea reglas como 'almuerzo' -> Alimentacion para clasificar los gastos automaticamente."
          />
        )}
      </Card>

      {modalAbierto ? (
        <ReglaFormModal
          regla={reglaEditando}
          categorias={categorias ?? []}
          onCerrar={() => setModalAbierto(false)}
          onGuardar={guardar}
        />
      ) : null}
    </div>
  );
}
