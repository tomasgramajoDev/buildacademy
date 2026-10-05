import {selected,evaluate} from './data.js';
import {analyzeMeasurements} from './measurements.js';
export const extraTopics=['temperature','boot','upgrade','basics','software'];
export function classifyPCQuestion(question,previous=null){
 const q=question.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
 if(/forzar|fuerza|no entra|no encaja/.test(q))return 'care';
 if(/pinout|voltaje|actualizar.*bios/.test(q))return 'manual';
 if(/cuello|fps|rendimiento|lenta|lento|tirones|limita/.test(q))return 'performance';
 if(/temperatura|calienta|calor/.test(q))return 'temperature';
 if(/no enciende|no prende|no da (imagen|video)|pantalla negra|no arranca/.test(q))return 'boot';
 if(/mejorar|actualizar|upgrade|comprar/.test(q))return 'upgrade';
 if(/que es|para que sirve|diferencia entre/.test(q)&&/cpu|gpu|ram|memoria|procesador|grafica|ssd|disco/.test(q))return 'basics';
 if(/windows|linux|driver|controlador|sistema operativo/.test(q))return 'software';
 if(/compat|sirven.*juntas/.test(q))return 'compatibility';
 if(/cable|fuente|aliment|eps/.test(q))return 'power';
 if(/ram|memoria/.test(q))return 'ram';
 if(/ssd|m\.2|sata|disco/.test(q))return 'ssd';
 if(/cooler|pasta|refriger/.test(q))return 'cooler';
 if(/procesador|cpu/.test(q))return 'cpu';
 if(/gpu|grafica|video/.test(q))return 'gpu';
 if(/gabinete/.test(q))return 'case';
 if(/manual|bios/.test(q))return 'manual';
 if(/empezar|organizar|primer armado/.test(q))return 'planning';
 if(/paso|ahora|sigue/.test(q))return 'current';
 if(previous&&/^(y )?(por que|como lo (compruebo|reviso)|explicame mas)[? .¿]*$/.test(q.replace(/^¿/,'')))return previous;
 return 'unknown';
}
export function pcExplanation(topic,config,context={}){
 const p=selected(config);
 if(topic==='performance'){
  const intro=`Tu configuración combina ${p.cpu.name} con ${p.gpu.name}. Un cuello de botella aparece cuando una parte limita el ritmo de una tarea: el procesador prepara trabajo y la gráfica dibuja los cuadros. El límite cambia según el juego, la resolución y los ajustes.`;
  const issues=evaluate(config).filter(r=>r.status==='fail');
  if(issues.length)return `${intro}\n\nPrimero resolvé las incompatibilidades de esta configuración: ${issues.map(x=>x.name).join(', ')}. No corresponde estimar su rendimiento como equipo funcional.`;
  let evidence='No cargaste mediciones: con los nombres de las piezas no puedo confirmar que tengas un cuello de botella ni dar un porcentaje.';
  if(context.measurements){try{const report=analyzeMeasurements(context.measurements,{fpsCap:context.fpsCap});evidence=`En tus ${report.count} muestras: ${report.averages.fps} FPS medios, GPU ${report.averages.gpu}% y núcleo de CPU más ocupado ${report.averages.cpuMax}%.\n${report.findings.join('\n')}\n${report.method}`}catch{evidence='La captura no tiene datos válidos suficientes. Importá al menos 30 muestras de la misma tarea.'}}
  const uses={competitive:'Para FPS altos, revisá el tiempo de CPU y la carga de cada núcleo, además de la GPU.',visual:'Para mayor resolución y calidad visual, compará la carga de GPU y el consumo de memoria gráfica.',creation:'En edición y render, medí la operación concreta: algunas tareas usan más CPU y otras aceleración de GPU.',general:'En el uso cotidiano, revisá qué aplicación tarda y si hay presión de RAM o actividad de disco.'};
  return `${intro}\n\n${evidence}\n\n${uses[context.usage]||uses.general} Compará la misma escena bajando resolución: si los FPS mejoran, puede haber un límite gráfico. Si casi no cambian, investigá CPU, límite de FPS, temperaturas y el propio programa antes de comprar piezas.`;
 }
 const answers={
 temperature:'La temperatura depende del modelo, la carga y la ventilación. Compará las lecturas con los límites oficiales de tu CPU y GPU; no hay una cifra única para todas las PCs. Revisá si bajan las frecuencias durante la tarea. Para inspeccionar ventiladores, polvo o montaje, apagá y desconectá el equipo; seguí el manual del cooler. No cambies voltajes como primer intento.',
 boot:`Si la PC no muestra imagen, verificá que el monitor esté en la entrada correcta y el cable conectado a ${p.gpu.name}. Apagá y desconectá antes de revisar RAM o cables internos. Consultá los indicadores de diagnóstico de ${p.board.name} y su manual. No puentees pines al azar. Si hay olor a quemado o daño visible, dejá de encenderla y pedí revisión técnica.`,
 upgrade:'La mejor mejora depende de lo que hoy te limita. Definí la tarea y el resultado que buscás, medí el equipo y revisá compatibilidad, dimensiones, fuente y presupuesto antes de comprar. Una GPU más potente no garantiza más FPS si el límite está en otro lugar. Contame qué programa o juego usás y qué problema notás; podés cargar mediciones en Tu configuración.',
 basics:`El procesador (CPU) ejecuta las instrucciones; la placa de video (GPU) procesa gráficos; la RAM guarda temporalmente lo que estás usando; el SSD almacena archivos incluso al apagar. Más capacidad y más velocidad no significan lo mismo. En tu selección: ${p.cpu.name} y ${p.gpu.name}. La motherboard conecta estas piezas y determina qué tipos admite.`,
 software:'Después de verificar el montaje, instalá el sistema operativo desde su fuente oficial y los controladores de los fabricantes de tu motherboard y placa de video. Evitá paquetes de drivers de sitios desconocidos. Si un problema empezó tras una actualización, anotá la versión y el error antes de cambiar varias cosas a la vez. La versión adecuada depende de tu sistema y del modelo exacto.'
 };
 return answers[topic]||null;
}
