// Local developer demo only: synthetic fixtures, in-memory history and quota.
import {createInterface} from 'node:readline/promises';
import {readFileSync} from 'node:fs';
import {createConsultationBot} from './chatbot.js';
import {createConsultationProvider} from './provider.js';

const contexts={
 compatibility:JSON.parse(readFileSync(new URL('./example-context.json',import.meta.url))),
 assembly:{buildId:'demo-build',contextId:'cpu-install',mode:'assembly',revision:'demo-1',title:'Colocación del procesador',status:'step',evidence:[{id:'instruction',text:'Comprobar la orientación en el manual del modelo exacto antes de insertar el procesador. Si no encaja, detener el montaje sin forzarlo.'}],history:[]}
};
const args=process.argv.slice(2);
if(args.length&&!(args.length===2&&args[0]==='--question'))throw new Error('Uso: npm run chat:demo [-- --question "Tu pregunta"]');
let mode='compatibility',used=0,nextCall=0,stopped=false;
const provider=createConsultationProvider();
const bot=createConsultationBot({
 complete:async input=>{
  const delay=Math.max(0,nextCall-Date.now());
  if(delay)await new Promise(resolve=>setTimeout(resolve,delay));
  nextCall=Date.now()+15000;
  try{return await provider(input)}catch(error){
   // Stop instead of looping after quota/network/authentication failures.
   stopped=true;console.error(`Servicio no disponible${Number.isInteger(error.status)?` (HTTP ${error.status})`:''}. No se reintenta automáticamente.`);throw error;
  }
 },
 loadContext:async()=>structuredClone(contexts[mode]),
 admit:async()=>!stopped&&used+3<=30?{demo:true}:null,
 settle:async({usage})=>{used+=usage.calls}
});
function showContext(){console.log(`\nEjemplo: ${contexts[mode].title}. ${mode==='compatibility'?'Ryzen 5 5600X + ASUS TUF B550M-PLUS, BIOS instalada desconocida.':'Paso genérico: verificar orientación y no forzar el procesador.'}`)}
async function ask(message){
 console.log('Consultando y revisando la respuesta… Puede tardar hasta un minuto.');
 const c=contexts[mode];
 try{
  const result=await bot.reply({buildId:c.buildId,contextId:c.contextId,mode,message},{userId:'local-demo'});
  console.log(`\nAsistente: ${result.answer}\n[${result.status} · entrada ${result.usage.inputTokens} / salida ${result.usage.outputTokens} tokens · ${used}/30 llamadas en esta sesión]`);
  if(result.status==='answered')c.history=[...c.history,{role:'user',content:message},{role:'assistant',content:result.answer}].slice(-6);
  if(result.status==='rate_limited')stopped=true;
 }catch{console.log('Pregunta inválida. Usá entre 1 y 2000 caracteres.')}
}
console.log('Compass · prueba de consultas por terminal\nUsa Gemini con datos ficticios. No está conectado al armado de la web.\nNo ingreses claves ni datos personales. Hasta 30 llamadas por sesión, separadas por 15 segundos.');
showContext();
if(args.length){await ask(args[1]);if(stopped)process.exitCode=1}
else{
 if(!process.stdin.isTTY)throw new Error('Abrí una terminal interactiva o usá --question.');
 const rl=createInterface({input:process.stdin,output:process.stdout});
 console.log('Comandos: /armado · /compatibilidad · /reiniciar · /salir');
 try{while(!stopped){
  let message;try{message=(await rl.question('\nVos: ')).trim()}catch{break}
  if(!message)continue;
  if(message==='/salir')break;
  if(message==='/armado'||message==='/compatibilidad'){mode=message==='/armado'?'assembly':'compatibility';contexts[mode].history=[];showContext();continue}
  if(message==='/reiniciar'){contexts[mode].history=[];console.log('Historial reiniciado; la cuota de esta sesión no se reinicia.');continue}
  if(message.startsWith('/')){console.log('Comandos: /armado · /compatibilidad · /reiniciar · /salir');continue}
  await ask(message);
 }}finally{rl.close()}
}
