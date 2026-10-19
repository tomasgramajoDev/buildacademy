import {createGeminiProvider} from './gemini.js';
import {createOpenAIProvider} from './openai.js';
// Gemini is the default. No automatic fallback to a billable OpenAI account.
export function createConsultationProvider({provider=process.env.CONSULTATION_PROVIDER||'gemini',...options}={}){
 if(provider==='gemini')return createGeminiProvider(options);
 if(provider==='openai')return createOpenAIProvider(options);
 throw new Error('CONSULTATION_PROVIDER debe ser gemini u openai.');
}
