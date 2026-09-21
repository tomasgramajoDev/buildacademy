import {steps,selected,evaluate} from './data.js';
const MODEL='Qwen2.5-1.5B-Instruct-q4f16_1-MLC';
export function assistantContext(config,step){
 const parts=selected(config),s=steps[step];if(!s)throw new Error('Paso inválido');
 return {step:step+1,title:s.title,instructions:s.description,check:s.check,parts:Object.fromEntries(Object.entries(parts).map(([k,v])=>[k,v.name])),rules:evaluate(config),sources:Object.values(parts).filter(v=>v.source).map(v=>({name:v.name,url:v.source})),manual:parts.board.manual};
}
export function guideAnswer(question,config,step){
 const p=selected(config),q=question.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
 if(/forzar|fuerza|entra|encaja/.test(q))return 'Detené el montaje si una pieza no entra. Comprobá modelo, orientación y mecanismo de retención en su manual. No puedo comprobar el estado físico del conector desde este chat.';
 if(/cable|fuente|aliment|eps|pcie/.test(q))return `${p.board.power}. ${p.gpu.name} requiere ${p.gpu.pcie8} conector PCIe de 8 pines. CPU usa EPS 4+4 y GPU PCIe 6+2: no los intercambies. Trabajá sin corriente y utilizá únicamente cables compatibles con la fuente exacta. Consultá los manuales enlazados.`;
 if(/compat|sirven|funcion/.test(q))return evaluate(config).filter(r=>r.status!=='pass').map(r=>`${r.name}: ${r.detail}`).join('\n\n');
 if(/\bram\b|memoria/.test(q))return `La placa ${p.board.name} utiliza ${p.board.memory}. Para un par de módulos consultá las ranuras recomendadas por el manual. Alineá la muesca y comprobá las trabas; no uses el color como criterio.`;
 if(/m\.2|ssd|sata/.test(q))return evaluate(config).find(r=>r.name==='Protocolo del SSD').detail;
 if(/cooler|pasta|refriger/.test(q))return `${p.cooler.name}: ${p.cooler.height?`${p.cooler.height} mm de altura. `:''}Comprobá el kit para ${p.board.socket}. ${p.cooler.id==='redux'?'El NH-U12S redux actual trae pasta aplicada; no agregues otra capa sobre ella.':'Consultá si tu modelo trae pasta aplicada y seguí su manual.'} Revisá la protección de la base y conectá su ventilador a CPU_FAN según el manual.`;
 if(/paso|ahora|sigue|hacer/.test(q))return `${steps[step].title}\n\n${steps[step].description}\n\nRevisión: ${steps[step].check}`;
 return 'En modo guía puedo explicar el paso actual, RAM, SSD, cooler, cables o alertas de compatibilidad. Activá la IA local para interpretar otras formas de preguntar sobre estos temas. Los manuales de tus piezas son la referencia para el montaje físico.';
}
export function requiresControlledAnswer(question){return /cable|fuente|aliment|\beps\b|\bpci.?e\b|forzar|fuerza|encaja|no entra|pasta|refriger|cooler|\bbios\b|volt|\bpines?\b|socket|compat|m\.2|\bssd\b|\bsata\b|\bram\b|memoria/i.test(question)}
export const topics=['current','planning','preparation','cpu','ram','ssd','cooler','case','gpu','power','compatibility','performance','care','manual','unknown'];
export function parseIntent(raw){
 const value=JSON.parse(raw);
 if(!value||!topics.includes(value.topic))throw new Error('Tema no reconocido');
 return value.topic;
}
export function answerForTopic(topic,config,step){
 const p=selected(config),stepMap={preparation:0,cpu:1,ram:2,ssd:3,cooler:4,case:5,gpu:6,power:7};
 if(topic==='planning')return 'Primero cargá tus componentes en Compatibilidad y resolvé las alertas. Después prepará el espacio y recorré los ocho pasos de la guía 3D, uno por vez. Leé el manual correspondiente antes de manipular cada pieza y marcá un paso como revisado solo después de comprobarlo. Podés preguntarme por una pieza o volver al paso actual.';
 if(topic==='care')return 'Podés avanzar de a un paso, con el equipo desconectado y las piezas apoyadas en una superficie firme. Manipulá las placas por los bordes. Si algo no encaja, detenete y revisá orientación y mecanismo en el manual; no lo fuerces. La animación es esquemática y no comprueba tu montaje físico.';
 if(topic==='compatibility')return guideAnswer('compatibilidad',config,step);
 if(topic==='performance')return 'La sección de rendimiento orienta qué medir según el uso. Podés importar una captura de FPS, carga de GPU, núcleo de CPU más ocupado, RAM y VRAM. Sus resultados son señales exploratorias: las especificaciones solas no permiten confirmar un cuello de botella ni calcular un porcentaje.';
 if(topic==='manual')return `Consultá el procedimiento del modelo exacto. No hay información verificada aquí para inferir pinouts, voltajes o una actualización de BIOS. Manual de ${p.board.name}: ${p.board.manual}`;
 if(topic==='unknown')return 'No tengo una respuesta verificada para esa consulta. Puedo ayudarte a preparar el armado, explicar un paso, revisar alertas de compatibilidad o consultar RAM, SSD, cooler, gabinete, gráfica y alimentación. Indicá la pieza o el paso que te genera dudas.';
 if(topic==='ram'||topic==='ssd'||topic==='cooler'||topic==='power')return guideAnswer({ram:'RAM',ssd:'SSD',cooler:'cooler',power:'cables'}[topic],config,step);
 const index=topic==='current'?step:stepMap[topic];
 if(index===undefined)return answerForTopic('unknown',config,step);
 const item=steps[index];return `${item.title}\n\n${item.description}\n\nPor qué: ${item.why}\n\nRevisión: ${item.check}`;
}
export function mountAssistant(getState){
 const $=s=>document.querySelector(s),panel=$('#assistant-panel'),log=$('#chat-log');let engine=null,busy=false,loading=false,history=[];
 const status=text=>$('#ai-status').textContent=text;
 function message(role,text){const node=document.createElement('div');node.className=`chat-message ${role}`;const label=document.createElement('strong');label.textContent=role==='user'?'Vos':'Guía contextual · sin IA';const body=document.createElement('p');body.textContent=text;node.append(label,body);log.append(node);log.scrollTop=log.scrollHeight;return body}
 $('#assistant-open').onclick=()=>{panel.hidden=false;$('#chat-input').focus()};$('#assistant-close').onclick=()=>{panel.hidden=true;$('#assistant-open').focus()};
 $('#chat-clear').onclick=()=>{history=[];log.replaceChildren();message('assistant','Consultá el paso actual o preguntame por tus componentes. El contexto se actualiza con tu configuración.')};
 $('#ai-load').onclick=async()=>{
 if(loading||engine)return;loading=true;$('#ai-load').disabled=true;
 try{
 if(!navigator.gpu)throw new Error('Este navegador no ofrece WebGPU. Podés usar la guía contextual o abrir el sitio en Chrome/Edge con aceleración gráfica.');
 status('Preparando IA local… La primera descarga es de aproximadamente 1 GB.');
 const {CreateWebWorkerMLCEngine}=await import('./vendor/webllm.js');
 engine=await CreateWebWorkerMLCEngine(new Worker(new URL('./ai-worker.js',import.meta.url),{type:'module'}),MODEL,{initProgressCallback:p=>status(`Cargando IA: ${Math.round(p.progress*100)}%. La primera descarga puede tardar varios minutos. Podés usar la guía mientras tanto.`)});
 status('IA local lista · Qwen2.5 1.5B · Tus consultas no se envían a un servidor.');$('#ai-load').textContent='IA activada';
 }catch(e){status(`No se pudo activar: ${e.message}`);$('#ai-load').disabled=false}finally{loading=false}
 };
 $('#chat-form').onsubmit=async e=>{e.preventDefault();if(busy)return;const question=$('#chat-input').value.trim();if(!question)return;const snapshot=getState(),ctx=assistantContext(snapshot.config,snapshot.step);$('#chat-input').value='';message('user',question);busy=true;$('#chat-send').disabled=true;
 const output=message('assistant','Preparando respuesta…');
 try{
 if(!engine||requiresControlledAnswer(question)){
 output.previousElementSibling.textContent='Guía contextual · instrucciones controladas';
 if(/bios|volt|pin|socket/i.test(question)&&!/cable|fuente|aliment|eps|pci.?e|compat/i.test(question)){output.textContent=`Para ${ctx.parts.board}, verificá el procedimiento y el diagrama del modelo exacto en su manual. No voy a inferir pinouts, voltajes ni una actualización de BIOS desde este chat.\n${ctx.manual}`}
 else output.textContent=guideAnswer(question,snapshot.config,snapshot.step);return}
 const system=`Clasificá la consulta del usuario en un único tema. No respondas la consulta. Temas: current=paso actual; planning=organizar aprendizaje o primer armado; preparation=espacio y herramientas; cpu=procesador; ram=memorias; ssd=almacenamiento; cooler=refrigeración; case=gabinete; gpu=gráfica; power=cables y alimentación; compatibility=compatibilidad; performance=rendimiento; care=miedo, cuidados o pieza que no encaja; manual=BIOS, voltajes, pinout; unknown=otro tema o datos no disponibles. Paso actual: ${ctx.title}. Devolvé JSON con topic.`;
 const messages=[{role:'system',content:system},...history.slice(-4),{role:'user',content:question}];
 output.previousElementSibling.textContent='IA · interpretando pregunta';
 const completion=await engine.chat.completions.create({messages,temperature:0,max_tokens:60,response_format:{type:'json_object',schema:JSON.stringify({type:'object',properties:{topic:{type:'string',enum:topics}},required:['topic'],additionalProperties:false})}});
 const topic=parseIntent(completion.choices[0]?.message?.content||'');
 output.previousElementSibling.textContent='IA interpreta · guía del proyecto';
 output.textContent=answerForTopic(topic,snapshot.config,snapshot.step);
 history.push({role:'user',content:question},{role:'assistant',content:JSON.stringify({topic})});
 }catch(err){output.previousElementSibling.textContent='Guía contextual · sin IA';output.textContent=`La IA no pudo responder. ${guideAnswer(question,snapshot.config,snapshot.step)}`;status(`Error de interpretación: ${err.message}`)}finally{busy=false;$('#chat-send').disabled=false;log.scrollTop=log.scrollHeight}
 };
 document.querySelectorAll('[data-question]').forEach(b=>b.onclick=()=>{$('#chat-input').value=b.dataset.question;$('#chat-form').requestSubmit()});
 message('assistant','Te acompaño con el paso y las piezas seleccionadas. Podés consultar la guía contextual ahora o activar la IA local para interpretar tus preguntas. Las respuestas provienen de las guías del proyecto.');
 return {resetContext(){history=[];if(!busy&&!loading)status(engine?'Configuración actualizada · IA local lista.':'Configuración actualizada · Guía contextual disponible.')}};
}
