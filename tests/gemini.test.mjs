import test from 'node:test';
import assert from 'node:assert/strict';
import {createGeminiProvider} from '../consultation/gemini.js';
import {createConsultationProvider} from '../consultation/provider.js';
import {createConsultationBot} from '../consultation/chatbot.js';
const input={instructions:'Policy',data:{question:'¿Por qué?'},schema:{type:'object',properties:{allowed:{type:'boolean'}},required:['allowed'],additionalProperties:false},maxTokens:100};
test('Gemini mantiene instrucciones separadas y envía clave sólo en header',async()=>{
 let payload;const complete=createGeminiProvider({apiKey:'test-secret',fetchImpl:async(url,options)=>{
  assert.equal(url,'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent');assert.ok(!url.includes('test-secret'));
  assert.equal(options.headers['x-goog-api-key'],'test-secret');assert.ok(!options.body.includes('test-secret'));payload=JSON.parse(options.body);
  return {ok:true,json:async()=>({candidates:[{finishReason:'STOP',content:{parts:[{text:'{"allowed":true}'}]}}],usageMetadata:{promptTokenCount:12,candidatesTokenCount:5,thoughtsTokenCount:2}})};
 }});
 const r=await complete(input);assert.equal(r.value.allowed,true);assert.deepEqual(r.usage,{inputTokens:12,outputTokens:7});assert.equal(payload.systemInstruction.parts[0].text,'Policy');assert.equal(payload.generationConfig.thinkingConfig.thinkingBudget,0);assert.equal(payload.generationConfig.maxOutputTokens,100);assert.deepEqual(payload.generationConfig.responseJsonSchema,input.schema);assert.equal(payload.tools,undefined);
});
test('Gemini rechaza respuestas truncadas, bloqueadas, no textuales o JSON inválido',async()=>{
 for(const body of [{promptFeedback:{blockReason:'SAFETY'}},{candidates:[{finishReason:'MAX_TOKENS',content:{parts:[{text:'{"allowed":true}'}]}}]},{candidates:[{finishReason:'STOP',content:{parts:[{functionCall:{name:'run'}}]}}]},{candidates:[{finishReason:'STOP',content:{parts:[{text:'not json'}]}}]}]){
  const complete=createGeminiProvider({apiKey:'test',fetchImpl:async()=>({ok:true,json:async()=>body})});await assert.rejects(()=>complete(input));
 }
});
test('cuota de Gemini no se confunde con respuesta ni filtra el body del error',async()=>{
 let calls=0;const complete=createGeminiProvider({apiKey:'test',fetchImpl:async()=>{calls++;return {ok:false,status:429,json:()=>assert.fail('No leer cuerpo del error')}}});
 await assert.rejects(()=>complete(input),e=>e.code==='PROVIDER_RATE_LIMIT'&&e.status===429);assert.equal(calls,1);
 const bot=createConsultationBot({complete,loadContext:async()=>({buildId:'b',contextId:'c',mode:'assembly',revision:'1',title:'Paso',status:'step',evidence:[{id:'i',text:'No forzar.'}]}),admit:async()=>true,settle:async()=>{}});
 assert.equal((await bot.reply({buildId:'b',contextId:'c',mode:'assembly',message:'¿Por qué?'},{userId:'u'})).status,'rate_limited');
});
test('credencial vacía y modelos no evaluados se rechazan, sin fallback',()=>{
 assert.throws(()=>createGeminiProvider({apiKey:''}));assert.throws(()=>createGeminiProvider({apiKey:'test',model:'other/path'}));assert.throws(()=>createConsultationProvider({provider:'unknown',apiKey:'test'}));
 assert.throws(()=>createConsultationProvider({provider:'gemini',apiKey:''}));
});
test('ausencia de metadatos de tokens se informa como desconocida',async()=>{
 const complete=createGeminiProvider({apiKey:'test',fetchImpl:async()=>({ok:true,json:async()=>({candidates:[{finishReason:'STOP',content:{parts:[{text:'{"allowed":false}'}]}}]})})});assert.equal((await complete(input)).usage,undefined);
});
