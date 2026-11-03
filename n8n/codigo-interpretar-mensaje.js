// Codigo del nodo "Interpretar mensaje" del flujo n8n.
// Extrae monto, descripcion, fecha y metodo de pago de un mensaje de Telegram.
//
// Zona horaria de referencia: America/La_Paz (UTC-04:00, sin horario de verano).

const OFFSET_MINUTOS = -240;

const pad = (valor) => String(valor).padStart(2, '0');

function ahoraEnLaPaz() {
  return new Date(Date.now() + OFFSET_MINUTOS * 60000);
}

function isoEnLaPaz(fecha) {
  return (
    `${fecha.getUTCFullYear()}-${pad(fecha.getUTCMonth() + 1)}-${pad(fecha.getUTCDate())}` +
    `T${pad(fecha.getUTCHours())}:${pad(fecha.getUTCMinutes())}:${pad(fecha.getUTCSeconds())}-04:00`
  );
}

function fechaDesdeTexto(texto, ahora) {
  const hoy = isoEnLaPaz(ahora);

  if (/\bante\s*ayer\b|\banteayer\b/i.test(texto)) {
    const ayer = new Date(ahora.getTime() - 48 * 3600000);
    return isoEnLaPaz(ayer);
  }

  if (/\bayer\b/i.test(texto)) {
    const ayer = new Date(ahora.getTime() - 24 * 3600000);
    return isoEnLaPaz(ayer);
  }

  if (/\bhoy\b/i.test(texto)) {
    return hoy;
  }

  const explicita = texto.match(/\b(\d{1,2})[\/-](\d{1,2})(?:[\/-](\d{2,4}))?\b/);
  if (explicita) {
    let anio = explicita[3] ? Number(explicita[3]) : ahora.getUTCFullYear();
    if (anio < 100) {
      anio += 2000;
    }
    const mes = Number(explicita[2]);
    const dia = Number(explicita[1]);
    if (mes >= 1 && mes <= 12 && dia >= 1 && dia <= 31) {
      return `${anio}-${pad(mes)}-${pad(dia)}T12:00:00-04:00`;
    }
  }

  return null;
}

function metodoDePagoDesdeTexto(texto) {
  if (/tarjeta\s+de\s+(debito|débitos|debítos)/i.test(texto)) return 'Tarjeta de débito';
  if (/tarjeta\s+de\s+(credito|crédito|créditos)/i.test(texto)) return 'Tarjeta de crédito';
  if (/\bdebit\b|\bdebit[oó]s?\b/i.test(texto)) return 'Tarjeta de débito';
  if (/\bcredit\b|\bcredit[oó]s?\b/i.test(texto)) return 'Tarjeta de crédito';
  if (/\befectivo\b|\bplata\b/i.test(texto)) return 'Efectivo';
  if (/\bqr\b/i.test(texto)) return 'QR';
  if (/\btransferencia\b|\btransferi\b|\btransf\b/i.test(texto)) return 'Transferencia';
  return null;
}

const mensaje = $json.message ?? {};
const texto = String(mensaje.text ?? mensaje.caption ?? '').trim();
const chatId = mensaje.chat?.id ?? null;
const messageId = mensaje.message_id ?? null;

if (!texto) {
  return [{ ok: false, chatId, messageId, error: 'El mensaje esta vacio.' }];
}

const patronMonto =
  /(?:bs\.?|bolivianos?|\$)?\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{1,2})?|\d+(?:[.,]\d{1,2})?)/i;
const coincidencia = texto.match(patronMonto);

if (!coincidencia) {
  return [
    {
      ok: false,
      chatId,
      messageId,
      error: 'No encontre el monto. Ejemplo: "almuerzo 50 bs".',
    },
  ];
}

const previo = texto.slice(0, coincidencia.index).trimEnd();
if (previo.endsWith('-')) {
  return [
    {
      ok: false,
      chatId,
      messageId,
      error: 'El monto debe ser un numero mayor que cero.',
    },
  ];
}

let montoTexto = coincidencia[1];
if (montoTexto.includes(',')) {
  montoTexto = montoTexto.replace(/\./g, '').replace(',', '.');
} else {
  montoTexto = montoTexto.replace(/,/g, '.');
}

const monto = Number(montoTexto);
if (!Number.isFinite(monto) || monto <= 0) {
  return [
    {
      ok: false,
      chatId,
      messageId,
      error: 'El monto debe ser un numero mayor que cero.',
    },
  ];
}

let descripcion = texto.replace(coincidencia[0], ' ');
descripcion = descripcion.replace(/\b(bs\.?|bolivianos?)\b/gi, ' ');
descripcion = descripcion.replace(/\s+/g, ' ').trim();
if (!descripcion) {
  descripcion = 'Gasto sin descripcion';
}

const ahora = ahoraEnLaPaz();

return [
  {
    ok: true,
    chatId,
    messageId,
    monto,
    descripcion,
    fecha: fechaDesdeTexto(texto, ahora),
    metodo_pago: metodoDePagoDesdeTexto(texto),
  },
];
