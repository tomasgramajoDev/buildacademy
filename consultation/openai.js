// Server-side only. Never import into the browser bundle.
export function createOpenAIProvider({apiKey=process.env.OPENAI_API_KEY,model=process.env.CONSULTATION_MODEL||'gpt-4.1-mini-2025-04-14',fetchImpl=fetch,timeoutMs=20000}={}){
 if(!apiKey)throw new Error('Falta OPENAI_API_KEY en el servidor.');
 return async function complete({instructions,data,schema,name,maxTokens}){
  const response=await fetchImpl('https://api.openai.com/v1/responses',{
   method:'POST',signal:AbortSignal.timeout(timeoutMs),headers:{Authorization:`Bearer ${apiKey}`,'Content-Type':'application/json'},
   body:JSON.stringify({model,store:false,instructions,input:[{role:'user',content:JSON.stringify(data)}],max_output_tokens:maxTokens,text:{format:{type:'json_schema',name,strict:true,schema}}})
  });
  if(!response.ok)throw new Error(`Proveedor no disponible (${response.status}).`);
  const result=await response.json();
  if(result.status!=='completed')throw new Error('Respuesta incompleta del proveedor.');
  const content=(result.output||[]).filter(x=>x.type==='message').flatMap(x=>x.content||[]);
  if(content.some(x=>x.type==='refusal'))throw new Error('El proveedor rechazó la respuesta.');
  const text=content.filter(x=>x.type==='output_text').map(x=>x.text).join('');
  return {value:JSON.parse(text),usage:{inputTokens:result.usage?.input_tokens||0,outputTokens:result.usage?.output_tokens||0},model};
 };
}
