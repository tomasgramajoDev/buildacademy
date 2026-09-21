// Limited, explicit normalization of supplied specs. A parsed value is not a verified value.
const schemas={
 gpu:{length:['largo','length'],thickness:['espesor','thickness'],minPsu:['fuente recomendada','recommended psu'],pcie8:['conectores pcie 8','pcie 8 pin'],vram:['vram']},
 case:{gpuMax:['gpu maxima','maximum gpu length'],coolerMax:['cooler maximo','maximum cpu cooler height'],psuMax:['fuente maxima','maximum psu length']},
 cooler:{height:['altura','height']},
 psu:{watts:['potencia','watts'],length:['largo','length'],atx24:['atx24'],eps8:['eps8'],pcie8:['pcie8']}
};
const normalized=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
export function extractSpecifications(category,text){
 if(!schemas[category]||typeof text!=='string'||text.length>20000)throw new Error('Tipo o texto inválido.');
 const result={};const lines=text.split(/\r?\n/);
 for(const [field,aliases] of Object.entries(schemas[category])){
  const values=[];for(const line of lines){const match=line.match(/^([^:]+):\s*(\d+(?:[.,]\d+)?)\s*(mm|w|gb)?\s*$/i);if(match&&[normalized(field),...aliases].includes(normalized(match[1])))values.push(Number(match[2].replace(',','.')))}
  if(new Set(values).size>1)throw new Error(`Valores contradictorios para ${field}.`);if(values.length)result[field]=values[0];
 }
 return result;
}
export function normalizePart(category,name,source,fields){
 if(!schemas[category]||typeof name!=='string'||name.trim().length<3||name.length>100||/[<>&"']/.test(name))throw new Error('Ingresá un nombre de 3 a 100 caracteres sin etiquetas HTML.');
 let url;try{url=new URL(source)}catch{throw new Error('Ingresá la URL de la ficha de referencia.')}
 if(url.protocol!=='https:'||url.username||url.password)throw new Error('La fuente debe ser una URL HTTPS sin credenciales.');
 const result={name:name.trim()+' · datos aportados',source:url.href,provided:true};
 for(const key of Object.keys(schemas[category])){const v=fields[key];if(!Number.isFinite(v)||v<0||v>10000)throw new Error(`Falta un valor válido para ${key}.`);if(['pcie8','eps8','atx24'].includes(key)&&(!Number.isInteger(v)||v>20))throw new Error(`Cantidad inválida: ${key}`);if(!['pcie8','eps8','atx24'].includes(key)&&v===0)throw new Error(`La medida ${key} debe ser positiva.`);result[key]=v}
 if(category==='case'){result.formats=['ATX'];result.psuFormat='ATX'}
 if(category==='psu')result.format='ATX';
 if(category==='cooler'){if(!Array.isArray(fields.sockets)||!fields.sockets.length||!fields.sockets.every(s=>['AM5','LGA1700'].includes(s)))throw new Error('Seleccioná los sockets declarados por el kit.');result.sockets=[...new Set(fields.sockets)]}
 return result;
}
export const specExamples={gpu:'Largo: 240 mm\nEspesor: 44.07 mm\nFuente recomendada: 550 W\nConectores PCIe 8: 1\nVRAM: 8 GB',case:'GPU máxima: 360 mm\nCooler máximo: 170 mm\nFuente máxima: 220 mm',cooler:'Altura: 158 mm',psu:'Potencia: 650 W\nLargo: 140 mm\nATX24: 1\nEPS8: 2\nPCIe8: 2'};
