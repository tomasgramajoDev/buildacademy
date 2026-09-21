import {WebWorkerMLCEngineHandler} from './vendor/webllm.js';
const handler=new WebWorkerMLCEngineHandler();
self.onmessage=message=>handler.onmessage(message);
