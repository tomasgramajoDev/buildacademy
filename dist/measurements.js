// Heuristic screening of user measurements, never a universal bottleneck percentage.
export function analyzeMeasurements(samples,{fpsCap=false}={}){
 if(!Array.isArray(samples)||samples.length<30||samples.length>10000)throw new Error('Se requieren entre 30 y 10.000 muestras de la misma tarea.');
 const fields=['fps','gpu','cpuMax','ram','vram'];
 for(const s of samples){for(const f of fields)if(!Number.isFinite(s[f])||s[f]<0||s[f]>(f==='fps'?2000:100))throw new Error(`Cada muestra requiere ${fields.join(', ')}; usos entre 0 y 100 y FPS entre 0 y 2000.`)}
 const avg=f=>samples.reduce((a,s)=>a+s[f],0)/samples.length,ratio=fn=>samples.filter(fn).length/samples.length;
 const findings=[];
 if(fpsCap)findings.push('Hay límite de FPS o sincronización vertical: una carga baja no demuestra un cuello de botella. Repetí la prueba sin ese límite para diagnosticar.');
 else{
 if(ratio(s=>s.gpu>=95)>=.7)findings.push('Posible límite de GPU: al menos el 70% de las muestras tiene uso de GPU ≥95%. Compará la misma escena bajando resolución/calidad.');
 if(ratio(s=>s.cpuMax>=90&&s.gpu<85)>=.5)findings.push('Posible límite de CPU: un núcleo/hilo alcanza ≥90% mientras la GPU queda por debajo del 85% en al menos la mitad de las muestras. Revisá procesos y tiempos de cuadro.');
 }
 if(ratio(s=>s.ram>=90)>=.5)findings.push('Presión de RAM: uso ≥90% en al menos la mitad de las muestras. Confirmá paginación y cerrá procesos para comparar.');
 if(ratio(s=>s.vram>=90)>=.5)findings.push('Presión de VRAM: ocupación ≥90% en al menos la mitad de las muestras. La memoria reservada no siempre equivale a memoria necesaria; compará texturas más bajas.');
 if(!findings.length)findings.push('No aparece una señal sostenida con estos umbrales. No descarta límites de disco, temperatura, potencia, motor del juego o sincronización.');
 return {count:samples.length,averages:Object.fromEntries(fields.map(f=>[f,Math.round(avg(f)*10)/10])),findings,method:'Reglas exploratorias, no diagnóstico causal. Medí una escena repetible sin menús ni pantallas de carga. No predice rendimiento de otra PC.'};
}
