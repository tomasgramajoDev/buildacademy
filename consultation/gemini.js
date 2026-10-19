// Server-side only. Credentials are sent only to Google's API in a header.
export function createGeminiProvider({apiKey=process.env.GEMINI_API_KEY,model=process.env.GEMINI_MODEL||'gemini-2.5-flash',fetchImpl=fetch,timeoutMs=30000}={}){
 if(typeof apiKey!=='string'||!apiKey.trim())throw new Error('Falta GEMINI_API_KEY en el servidor.');
 // The provider is deliberately restricted to the evaluated Flash family.
 if(!['gemini-2.5-flash','gemini-2.5-flash-lite'].includes(model))throw new Error('Modelo Gemini no evaluado para este adaptador.');
 return async function complete({instructions,data,schema,maxTokens}){
  const response=await fetchImpl(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`,{
   method:'POST',signal:AbortSignal.timeout(timeoutMs),headers:{'x-goog-api-key':apiKey.trim(),'Content-Type':'application/json'},
   body:JSON.stringify({systemInstruction:{parts:[{text:instructions}]},contents:[{role:'user',parts:[{text:JSON.stringify(data)}]}],generationConfig:{candidateCount:1,temperature:0,maxOutputTokens:maxTokens,thinkingConfig:{thinkingBudget:0},responseMimeType:'application/json',responseJsonSchema:schema}})
  });
  if(!response.ok){
   const error=new Error(`Gemini no disponible (HTTP ${response.status}).`);
   error.code=response.status===429?'PROVIDER_RATE_LIMIT':'PROVIDER_ERROR';error.status=response.status;
   throw error; // Never expose the upstream body, which could echo request data.
  }
  const result=await response.json(),candidate=result.candidates?.[0];
  if(result.promptFeedback?.blockReason||result.candidates?.length!==1||candidate?.finishReason!=='STOP')throw new Error('Gemini no devolvió una respuesta completa.');
  const parts=candidate.content?.parts;
  if(!Array.isArray(parts)||!parts.length||parts.some(p=>p.thought||typeof p.text!=='string'))throw new Error('Respuesta inesperada de Gemini.');
  const value=JSON.parse(parts.map(p=>p.text).join(''));
  const u=result.usageMetadata;
  const usage=u&&Number.isFinite(u.promptTokenCount)&&Number.isFinite(u.candidatesTokenCount)?{inputTokens:u.promptTokenCount,outputTokens:u.candidatesTokenCount+(u.thoughtsTokenCount||0)}:undefined;
  return {value,usage,model};
 };
}
