import { Select } from './ui/Field';
import { MESES, mesActual } from '../utils/formato';

interface Props {
  anio: number;
  mes: number;
  onAnio: (valor: number) => void;
  onMes: (valor: number) => void;
}

export default function MesAnoSelector({ anio, mes, onAnio, onMes }: Props) {
  const actual = mesActual();
  const anios = Array.from({ length: 5 }, (_, indice) => actual.anio + 2 - indice);

  return (
    <div className="flex gap-2">
      <Select value={mes} onChange={(evento) => onMes(Number(evento.target.value))} className="w-36">
        {MESES.map((nombre, indice) => (
          <option key={nombre} value={indice + 1}>
            {nombre}
          </option>
        ))}
      </Select>
      <Select value={anio} onChange={(evento) => onAnio(Number(evento.target.value))} className="w-28">
        {anios.map((valor) => (
          <option key={valor} value={valor}>
            {valor}
          </option>
        ))}
      </Select>
    </div>
  );
}
