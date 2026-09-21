export function intersectionOverUnion(a,b){const w=Math.max(0,Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x)),h=Math.max(0,Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y));const i=w*h;return i/(a.w*a.h+b.w*b.h-i)||0}
export function decodeYOLO(data,dims,classes,transform,threshold=.5){
 if(dims.length!==3||dims[0]!==1||dims[1]!==classes.length+4||data.length!==dims[1]*dims[2])throw new Error('La salida del modelo no coincide con el contrato YOLO sin NMS.');
 if(!(threshold>=0&&threshold<=1))throw new Error('Umbral inválido');
 const {width,height,scale,padX,padY}=transform,boxes=[],n=dims[2];
 if(![width,height,scale].every(v=>Number.isFinite(v)&&v>0)||![padX,padY].every(Number.isFinite))throw new Error('Transformación inválida');
 for(let i=0;i<n;i++){
  let confidence=0,cls=-1;for(let k=0;k<classes.length;k++){const score=data[(k+4)*n+i];if(score>confidence){confidence=score;cls=k}}
  if(confidence<threshold||confidence>1||cls<0)continue;
  const [cx,cy,w,h]=[data[i],data[n+i],data[2*n+i],data[3*n+i]];
  if(![cx,cy,w,h].every(Number.isFinite)||w<=0||h<=0)continue;
  const x=Math.max(0,Math.min(width,(cx-w/2-padX)/scale)),y=Math.max(0,Math.min(height,(cy-h/2-padY)/scale));
  const right=Math.max(0,Math.min(width,(cx+w/2-padX)/scale)),bottom=Math.max(0,Math.min(height,(cy+h/2-padY)/scale));
  if(right<=x||bottom<=y)continue;
  boxes.push({type:classes[cls],x,y,w:right-x,h:bottom-y,confidence,origin:'model'});
 }
 boxes.sort((a,b)=>b.confidence-a.confidence);const kept=[];
 for(const b of boxes){if(!kept.some(a=>a.type===b.type&&intersectionOverUnion(a,b)>.45))kept.push(b);if(kept.length===100)break}
 return kept;
}
export async function getVisionMetadata(){const response=await fetch('./models/manifest.json');if(!response.ok)throw new Error('No hay un modelo de visión publicado.');return response.json()}
let sessionPromise=null;
export async function detectConnectors(img,metadata,threshold=.5){
 if(!metadata.ready||!Array.isArray(metadata.classes)||metadata.classes.length<1||!metadata.classes.every(c=>/^[A-Za-z0-9_]{1,40}$/.test(c)))throw new Error('El modelo todavía no está disponible.');
 const size=metadata.inputSize;if(![320,416,640].includes(size))throw new Error('Tamaño de entrada no admitido.');
 const width=img.naturalWidth,height=img.naturalHeight;if(!width||!height)throw new Error('Elegí una imagen válida.');
 const scale=Math.min(size/width,size/height),rw=Math.round(width*scale),rh=Math.round(height*scale),padX=Math.floor((size-rw)/2),padY=Math.floor((size-rh)/2);
 const canvas=document.createElement('canvas');canvas.width=canvas.height=size;const ctx=canvas.getContext('2d',{willReadFrequently:true});ctx.fillStyle='rgb(114,114,114)';ctx.fillRect(0,0,size,size);ctx.drawImage(img,0,0,width,height,padX,padY,rw,rh);
 const rgba=ctx.getImageData(0,0,size,size).data,floats=new Float32Array(size*size*3);for(let i=0;i<size*size;i++){floats[i]=rgba[i*4]/255;floats[size*size+i]=rgba[i*4+1]/255;floats[2*size*size+i]=rgba[i*4+2]/255}
 const ort=await import('./vendor/ort/ort.wasm.min.mjs');ort.env.wasm.wasmPaths=new URL('./vendor/ort/',import.meta.url).href;ort.env.wasm.numThreads=1;
 if(!sessionPromise)sessionPromise=ort.InferenceSession.create('./models/connectors.onnx',{executionProviders:['wasm']}).catch(e=>{sessionPromise=null;throw e});
 const session=await sessionPromise,input=new ort.Tensor('float32',floats,[1,3,size,size]);
 let output;try{output=await session.run({[session.inputNames[0]]:input});const tensor=output[session.outputNames[0]];return decodeYOLO(tensor.data,tensor.dims,metadata.classes,{width,height,scale,padX,padY},threshold)}finally{input.dispose();for(const value of Object.values(output||{}))value.dispose()}
}
